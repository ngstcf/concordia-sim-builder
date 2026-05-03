"""
Post-processing utility for extracting grounded variable updates from completed simulations.

This module works around Concordia's limitation where SwitchAct never calls post_act()
on context components by analyzing simulation logs after completion and extracting
variable updates using LLM-based analysis.
"""

import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from concordia.language_model import language_model


class GroundedVariablesPostProcessor:
    """Extracts grounded variable updates from completed simulation logs."""

    def __init__(
        self,
        model: language_model.LanguageModel,
        variable_configs: List[Dict[str, Any]],
    ):
        """Initialize the post-processor.

        Args:
            model: Language model for analyzing events
            variable_configs: List of variable configuration dictionaries
        """
        self._model = model
        self._variable_configs = variable_configs
        self._current_values: Dict[str, Any] = {}

        # Initialize current values from configs
        for config in variable_configs:
            name = config["name"]
            if config.get("default_value") is not None:
                self._current_values[name] = config["default_value"]
            elif config.get("variable_type") == "boolean":
                self._current_values[name] = False
            elif config.get("variable_type") in ["numerical", "percentage"]:
                self._current_values[name] = config.get("min_value", 0)
            else:
                self._current_values[name] = "unknown"

    def extract_events_from_html(self, html_path: str) -> List[Dict[str, Any]]:
        """Extract events from simulation HTML log.

        Supports both v2.4+ structured logs (ENTRIES JSON) and legacy HTML (<details> tags).

        Args:
            html_path: Path to simulation HTML file

        Returns:
            List of events with step numbers and descriptions
        """
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            print(f"[WARNING] Error reading HTML file: {e}")
            return []

        events = self._extract_events_from_entries(html_content)
        if events:
            return events

        return self._extract_events_from_html_tags(html_content)

    def _extract_entries_json(self, html_content: str) -> tuple:
        """Extract ENTRIES and CONTENT_STORE JSON from script tags."""
        entries_match = re.search(r'const ENTRIES = (\[.*?\]);\s*$', html_content, re.DOTALL | re.MULTILINE)
        content_store_match = re.search(r'const CONTENT_STORE = (\{.*?\});\s*$', html_content, re.DOTALL | re.MULTILINE)
        if not entries_match:
            return [], {}
        try:
            entries = json.loads(entries_match.group(1))
            content_store = json.loads(content_store_match.group(1)) if content_store_match else {}
            return entries, content_store
        except (json.JSONDecodeError, ValueError):
            return [], {}

    def _resolve_ref(self, value, content_store: Dict) -> Any:
        """Resolve _ref pointers in deduplicated data."""
        if isinstance(value, dict):
            if '_ref' in value:
                return content_store.get(value['_ref'], str(value))
            return {k: self._resolve_ref(v, content_store) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve_ref(v, content_store) for v in value]
        return value

    def _extract_events_from_entries(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract events from v2.4+ ENTRIES JSON format."""
        entries, content_store = self._extract_entries_json(html_content)
        if not entries:
            return []

        events_by_step: Dict[int, List[str]] = {}

        for entry in entries:
            step = entry.get('step', 0)
            if step <= 0:
                continue

            entry_type = entry.get('entry_type', '')
            summary = entry.get('summary', '')
            dedup_data = entry.get('deduplicated_data', {})

            if entry_type == 'step':
                text = summary.strip()
                prefix_pattern = re.compile(r'Step\s+\d+\s+.*?---\s*Event:\s*', re.IGNORECASE)
                text = prefix_pattern.sub('', text).strip()
                if len(text) > 20:
                    events_by_step.setdefault(step, []).append(text)

            elif entry_type == 'entity':
                resolved = self._resolve_ref(dedup_data, content_store)
                value_data = resolved.get('value', {})
                if isinstance(value_data, dict):
                    act_data = value_data.get('__act__', {})
                    act_text = act_data.get('Value', '') if isinstance(act_data, dict) else str(act_data) if act_data else ''
                    entity_name = entry.get('entity_name', '')
                    if act_text and entity_name:
                        events_by_step.setdefault(step, []).append(f"{entity_name}: {act_text}")

        events = []
        for step_num in sorted(events_by_step.keys()):
            combined = " | ".join(events_by_step[step_num])
            if combined:
                events.append({"step": step_num, "description": combined})

        return events

    def _extract_events_from_html_tags(self, html_content: str) -> List[Dict[str, Any]]:
        """Legacy fallback: extract events from <details> HTML tags (pre-v2.4)."""
        events = []
        events_by_step: Dict[int, List[str]] = {}

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            details_tags = soup.find_all('details')

            for details in details_tags:
                summary = details.find('summary')
                if not summary:
                    continue

                summary_text = summary.get_text()
                step_match = re.search(r'[Ss]tep\s+(\d+)', summary_text)
                if not step_match:
                    continue

                step_num = int(step_match.group(1))
                full_text = summary.get_text(separator=' ', strip=True)

                if len(full_text) > 50:
                    if step_num not in events_by_step:
                        events_by_step[step_num] = []
                    events_by_step[step_num].append(full_text)

            for step_num in sorted(events_by_step.keys()):
                step_events = events_by_step[step_num]
                step_events.sort(key=len, reverse=True)

                unique_events = []
                for event in step_events:
                    is_duplicate = False
                    for existing in unique_events:
                        similarity = len(set(event.split()) & set(existing.split())) / max(len(set(event.split())), len(set(existing.split())))
                        if similarity > 0.9:
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        unique_events.append(event)

                if unique_events:
                    event_text = unique_events[0]

                    critical_decision_pattern = rf'Step\s+{step_num}:\s*CRITICAL\s+DECISION\s+POINT'
                    match = re.search(critical_decision_pattern, event_text, re.IGNORECASE)

                    if match:
                        start_idx = match.start()
                        remaining = event_text[start_idx:]
                        next_step_pattern = rf'-\s*Step\s+{step_num + 1}:\s*CRITICAL\s+DECISION'
                        next_match = re.search(next_step_pattern, remaining, re.IGNORECASE)
                        if next_match:
                            remaining = remaining[:next_match.start()]
                        event_text = remaining.strip()
                    else:
                        premise_end_patterns = [
                            r'IMPORTANT:\s+The\s+Council\s+will\s+take\s+ACTION',
                            r'CRITICAL\s+DECISION\s+POINTS:\s*-',
                            r'Step\s+1:\s*CRITICAL\s+DECISION\s+POINT'
                        ]
                        for pattern in premise_end_patterns:
                            match = re.search(pattern, event_text, re.IGNORECASE)
                            if match:
                                event_text = event_text[match.end():].strip()
                                event_text = re.split(rf'-\s*Step\s+{step_num + 1}:', event_text, flags=re.IGNORECASE)[0].strip()
                                break

                    events.append({
                        "step": step_num,
                        "description": event_text
                    })

        except Exception as e:
            print(f"[WARNING] Error extracting events from HTML tags: {e}")

        return events

    def extract_variable_updates_from_batch(
        self,
        events: List[Dict[str, Any]],
        current_values: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Use LLM to extract variable updates from multiple events at once.

        This is much more efficient than processing events one-by-one.

        Args:
            events: List of events with 'step' and 'description' keys
            current_values: Current variable values

        Returns:
            List of dictionaries mapping variable names to new values for each event
        """
        # Build variable descriptions
        variable_descriptions = []
        for config in self._variable_configs:
            name = config["name"]
            var_type = config["variable_type"]
            current = current_values.get(name, "unknown")

            desc = f"{name} ({var_type}, current: {current})"
            if config.get("description"):
                desc += f": {config['description']}"
            if config.get("update_rule"):
                desc += f" [Update rule: {config['update_rule']}]"
            if config.get("min_value") is not None:
                desc += f" [Range: {config['min_value']} - {config.get('max_value', 'unlimited')}]"
            if config.get("allowed_values"):
                desc += f" [Allowed: {config['allowed_values']}]"

            variable_descriptions.append(desc)

        # Build events text
        events_text = ""
        for i, event in enumerate(events):
            events_text += f"\nSTEP {event['step']}: {event['description']}\n"

        prompt = f"""You are analyzing simulation events to identify which grounded variables should change at each step.

GROUNDED VARIABLES:
{chr(10).join(variable_descriptions)}

EVENTS TO ANALYZE:
{events_text}

TASK: For EACH step, identify which variables should change based on BOTH explicit mentions and INFERRED changes.

ANALYSIS GUIDELINES:
1. EXPLICIT CHANGES: The event directly states a value (e.g., "rent increases to $1900")
2. INFERRED CHANGES: The event describes actions that would logically affect variables based on update rules
3. CUMULATIVE EFFECTS: Variables may change gradually over multiple steps

EXAMPLES OF INFERENCE:
- If Council "approves 100 new housing units" → new_housing_units_permitted increases by 100
- If Council "rejects rent control" → rent_control_active remains false, rents may increase
- If there's "intense community organizing" → community_cohesion_index may increase
- If "businesses are closing due to rents" → small_business_survival_rate decreases
- If "new luxury development approved" → median_monthly_rent may increase

BE AGGRESSIVE WITH INFERENCE:
- If the event describes a relevant action, infer the variable change
- Use the update_rule as a guide for what affects each variable
- Consider both immediate and secondary effects

RESPONSE FORMAT: Return a JSON object where each key is a step number (as a string) and each value is an object with variable_name:new_value pairs.
Include ALL variables that changed (explicitly or inferred). If no variables changed at a step, use an empty object {{}}.

EXAMPLE:
{{
  "5": {{"median_monthly_rent": 1950, "low_income_displacement_rate": 20, "new_housing_units_permitted": 145}},
  "6": {{}},
  "7": {{"inclusionary_zoning_active": true, "affordable_housing_units": 150, "community_cohesion_index": 70}}
}}

IMPORTANT:
- For numerical variables: Use specific numbers (e.g., "1950", "65")
- For percentage variables: Use numbers 0-100 (e.g., "65", "20")
- For boolean variables: Use true or false (JSON booleans)
- For categorical variables: Use the exact allowed value string
- Keys MUST be strings (e.g., "5", "10", not 5, 10)

Return valid JSON only:"""

        try:
            response = self._model.sample_text(
                prompt,
                max_tokens=8000,
                temperature=0.0
            )

            # Parse JSON response
            updates_by_step = {}
            response = response.strip()

            # Try to extract JSON if there's extra text
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                response = json_match.group(0)

            try:
                updates_by_step = json.loads(response)
            except json.JSONDecodeError:
                # Fallback: try to parse manually
                print(f"[WARNING] Failed to parse JSON response, trying manual parse")
                for line in response.split('\n'):
                    line = line.strip()
                    if not line or line.startswith(('EVENT', 'STEP', 'RESPONSE')):
                        continue

            return updates_by_step

        except Exception as e:
            print(f"[WARNING] Batch LLM extraction failed: {e}")
            return {}

    def extract_variable_updates_from_event(
        self,
        event: str,
        current_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to extract variable updates from a single event.

        DEPRECATED: Use extract_variable_updates_from_batch() for better performance.

        Args:
            event: Event description
            current_values: Current variable values

        Returns:
            Dictionary of variable name -> new value
        """
        # Build prompt for LLM
        variable_descriptions = []
        for config in self._variable_configs:
            name = config["name"]
            var_type = config["variable_type"]
            current = current_values.get(name, "unknown")

            desc = f"{name} ({var_type}, current: {current})"
            if config.get("description"):
                desc += f": {config['description']}"
            if config.get("update_rule"):
                desc += f" [Update rule: {config['update_rule']}]"
            if config.get("min_value") is not None:
                desc += f" [Range: {config['min_value']} - {config.get('max_value', 'unlimited')}]"
            if config.get("allowed_values"):
                desc += f" [Allowed: {config['allowed_values']}]"

            variable_descriptions.append(desc)

        prompt = f"""You are analyzing a simulation event to identify which grounded variables should change.

EVENT: {event}

GROUNDED VARIABLES:
{chr(10).join(variable_descriptions)}

TASK: Identify which variables should change based on this event. Consider:
1. Did the event explicitly mention a variable value?
2. Did the event describe a change that would logically affect a variable?
3. Does the update rule suggest a change?

RESPONSE FORMAT: Comma-separated list of "variable_name=new_value" pairs.
Only include variables that ACTUALLY changed. If no variables changed, respond with "None".

EXAMPLES:
- Event: "The Council votes to approve new luxury apartments. Rents are expected to rise."
  Response: median_monthly_rent=1950

- Event: "The Council implements rent control, capping increases at 2% annually."
  Response: median_monthly_rent=1800

- Event: "Residents attend a meeting but no decisions are made."
  Response: None

IMPORTANT:
- For numerical variables: Use specific numbers (e.g., "1950", "65")
- For percentage variables: Use numbers 0-100 (e.g., "65", "20")
- For boolean variables: Use "true" or "false"
- For categorical variables: Use the exact allowed value string

Respond now:"""

        try:
            response = self._model.sample_text(
                prompt,
                max_tokens=500,
                temperature=0.0  # Use low temperature for consistent extraction
            )

            # Parse response
            updates = {}
            response = response.strip()

            if response.lower() != "none" and response:
                for update in response.split(','):
                    if '=' in update:
                        name, value = update.split('=', 1)
                        name = name.strip()
                        value = value.strip()

                        # Validate and parse the value
                        parsed = self._parse_value(name, value)
                        if parsed is not None:
                            updates[name] = parsed

            return updates

        except Exception as e:
            print(f"[WARNING] LLM extraction failed: {e}")
            return {}

    def _parse_value(self, name: str, value_str: str) -> Optional[Any]:
        """Parse a string value to the appropriate type."""
        config = next(
            (c for c in self._variable_configs if c["name"] == name),
            None
        )
        if not config:
            return None

        value_str = value_str.strip()
        var_type = config.get("variable_type", "numerical")

        try:
            if var_type == "boolean":
                if value_str.lower() in ['true', 'yes', '1']:
                    return True
                elif value_str.lower() in ['false', 'no', '0']:
                    return False
                else:
                    return bool(value_str)

            elif var_type in ["numerical", "percentage"]:
                return float(value_str)

            elif var_type == "categorical":
                # Validate against allowed values
                allowed = config.get("allowed_values")
                if allowed and value_str not in allowed:
                    # Return current value if invalid
                    return self._current_values.get(name)
                return value_str

            return value_str

        except (ValueError, TypeError):
            return None

    def validate_value(self, name: str, value: Any) -> Optional[Any]:
        """Validate a value against the variable configuration."""
        config = next(
            (c for c in self._variable_configs if c["name"] == name),
            None
        )
        if not config:
            return None

        var_type = config.get("variable_type", "numerical")

        try:
            if var_type == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ['true', 'yes', '1']
                return bool(value)

            elif var_type == "numerical":
                num_value = float(value)
                min_val = config.get("min_value")
                max_val = config.get("max_value")
                if min_val is not None and num_value < min_val:
                    num_value = min_val
                if max_val is not None and num_value > max_val:
                    num_value = max_val
                return num_value

            elif var_type == "percentage":
                num_value = float(value)
                return max(0, min(100, num_value))

            elif var_type == "categorical":
                str_value = str(value)
                allowed = config.get("allowed_values")
                if allowed and str_value not in allowed:
                    return self._current_values.get(name)
                return str_value

            return value

        except (ValueError, TypeError):
            return self._current_values.get(name)

    def process_simulation(
        self,
        html_path: str,
        metadata_path: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Process a completed simulation and extract variable updates.

        Args:
            html_path: Path to simulation HTML file
            metadata_path: Optional path to metadata file (will be updated if provided)

        Returns:
            Dictionary mapping variable names to their history across steps
        """
        print(f"\n{'='*70}")
        print(f"[POST-PROCESSOR] Processing simulation: {html_path}")

        # Extract model information
        model_class = self._model.__class__.__name__
        actual_model = self._model

        # Unwrap TemperatureConfiguredModel if present
        if model_class == "TemperatureConfiguredModel":
            actual_model = self._model._model
            model_class = actual_model.__class__.__name__

        print(f"[POST-PROCESSOR] LLM Provider: {model_class}")

        # Try to get model name/details
        model_info = "Unknown"
        if hasattr(actual_model, 'model_name'):
            model_info = actual_model.model_name
        elif hasattr(actual_model, '_model_name'):
            model_info = actual_model._model_name
        elif hasattr(actual_model, 'name'):
            model_info = actual_model.name
        elif hasattr(actual_model, 'llm'):
            # Some models wrap the LLM in a property
            try:
                model_info = str(actual_model.llm)
                # Clean up the string representation
                if '<' in model_info and '>' in model_info:
                    model_info = model_info.split('<')[1].split('>')[0]
            except:
                model_info = str(actual_model.llm)

        print(f"[POST-PROCESSOR] Model: {model_info}")

        print(f"[POST-PROCESSOR] Variables to track: {len(self._variable_configs)}")
        for config in self._variable_configs:
            print(f"  - {config['name']} ({config['variable_type']})")

        print(f"[POST-PROCESSOR] Extracting events from HTML log...")

        events = self.extract_events_from_html(html_path)
        print(f"[POST-PROCESSOR] Found {len(events)} events")

        if not events:
            print("[WARNING] No events found - cannot extract variable updates")
            return {}

        # Track history
        history: Dict[str, List[Dict[str, Any]]] = {
            config["name"]: [] for config in self._variable_configs
        }

        # Process events in batches for efficiency
        BATCH_SIZE = 10
        all_updates_by_step = {}

        for i in range(0, len(events), BATCH_SIZE):
            batch = events[i:i + BATCH_SIZE]
            batch_start = batch[0]["step"]
            batch_end = batch[-1]["step"]

            print(f"\n[POST-PROCESSOR] Processing batch {i//BATCH_SIZE + 1}/{(len(events) + BATCH_SIZE - 1)//BATCH_SIZE}")
            print(f"  Steps {batch_start} - {batch_end} ({len(batch)} events)")

            updates_by_step = self.extract_variable_updates_from_batch(
                batch,
                self._current_values
            )

            if updates_by_step:
                all_updates_by_step.update(updates_by_step)
                print(f"  Found updates for {len([s for s in updates_by_step.values() if s])} steps")
            else:
                print(f"  No updates found in this batch")

        # Now apply all updates and build history
        print("\n[POST-PROCESSOR] Building history from extracted updates...")
        last_step = 0

        for event in events:
            step = event["step"]

            # Fill in missing steps with current values
            if step > last_step + 1:
                for s in range(last_step + 1, step):
                    for name in history.keys():
                        history[name].append({"step": s, "value": self._current_values[name]})

            # Get updates for this step
            step_updates = all_updates_by_step.get(str(step), {})

            if step_updates:
                # Apply updates
                for name, new_value in step_updates.items():
                    validated = self.validate_value(name, new_value)
                    if validated is not None:
                        old_value = self._current_values.get(name)
                        self._current_values[name] = validated
                        print(f"  Step {step}: {name}: {old_value} -> {validated}")

            # Record current values for this step
            for name in history.keys():
                history[name].append({
                    "step": step,
                    "value": self._current_values[name]
                })

            last_step = step

        # Update metadata file if provided
        if metadata_path:
            self._update_metadata_file(metadata_path, history)

        print(f"\n[POST-PROCESSOR] ✓ Processing complete")
        return history

    def _update_metadata_file(
        self,
        metadata_path: str,
        history: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """Update the metadata file with extracted variable history.

        Args:
            metadata_path: Path to metadata JSON file
            history: Extracted variable history
        """
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Update grounded_variables history
            if "game_master" in metadata and "grounded_variables" in metadata["game_master"]:
                for var_config in metadata["game_master"]["grounded_variables"]:
                    name = var_config["name"]
                    if name in history:
                        var_config["history"] = history[name]
                        print(f"[METADATA] Updated history for {name}: {len(history[name])} steps")

                # Save updated metadata
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

                print(f"[METADATA] ✓ Updated: {metadata_path}")
            else:
                print("[WARNING] Metadata file does not contain grounded_variables section")

        except Exception as e:
            print(f"[ERROR] Failed to update metadata file: {e}")


def extract_grounded_variables_from_simulation(
    model: language_model.LanguageModel,
    html_path: str,
    metadata_path: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Convenience function to extract grounded variables from a simulation.

    Args:
        model: Language model to use for analysis
        html_path: Path to simulation HTML file
        metadata_path: Path to metadata JSON file

    Returns:
        Dictionary mapping variable names to their history
    """
    # Load variable configs from metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    variable_configs = []
    if "game_master" in metadata and "grounded_variables" in metadata["game_master"]:
        for var in metadata["game_master"]["grounded_variables"]:
            variable_configs.append({
                "name": var["name"],
                "variable_type": var["variable_type"],
                "description": var.get("description", ""),
                "default_value": var.get("default_value"),
                "min_value": var.get("min_value"),
                "max_value": var.get("max_value"),
                "allowed_values": var.get("allowed_values"),
                "update_rule": var.get("update_rule"),
            })

    if not variable_configs:
        print("[ERROR] No grounded_variables found in metadata")
        return {}

    # Create post-processor and process
    processor = GroundedVariablesPostProcessor(model, variable_configs)
    return processor.process_simulation(html_path, metadata_path)
