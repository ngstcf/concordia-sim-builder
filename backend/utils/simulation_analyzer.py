"""
Simulation Analyzer - LLM-powered deep content analysis tool

This module provides automated analysis of simulation logs using LLM to generate
comprehensive reports. It uses the full simulation metadata (premise, agents,
goals, memories, components, shared memories, engine type) to produce
context-aware analysis rather than generic summaries.

Usage:
    from backend.utils.simulation_analyzer import SimulationAnalyzer

    analyzer = SimulationAnalyzer(llm_client)
    report = analyzer.analyze_simulation(log_path)
    analyzer.save_report(report, output_path)
"""

import os
import re
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path
from bs4 import BeautifulSoup


class SimulationAnalyzer:
    """
    Automated simulation analysis tool using LLM.

    Uses simulation metadata (agents, goals, components, memories) alongside
    the HTML log to produce analysis grounded in the simulation's design intent.
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def analyze_simulation(self, log_path: str, metadata_path: Optional[str] = None) -> Dict[str, Any]:
        print(f"[Analyzer] Starting analysis of {log_path}")

        log_content = self._read_log_file(log_path)
        metadata = self._load_metadata(metadata_path or log_path.replace('.html', '.metadata.json'))
        parsed_data = self._parse_html_log(log_content)

        analysis = {
            'metadata': self._extract_simulation_metadata(metadata, parsed_data),
            'executive_summary': self._generate_executive_summary(parsed_data, metadata),
            'timeline': self._extract_timeline(parsed_data),
            'team_effectiveness': self._analyze_team_effectiveness(parsed_data, metadata),
            'insights': self._generate_insights(parsed_data, metadata),
            'recommendations': self._generate_recommendations(parsed_data, metadata),
            'analysis_date': datetime.now().isoformat()
        }

        print(f"[Analyzer] Analysis complete")
        return analysis

    # ── File I/O ──

    def _read_log_file(self, log_path: str) -> str:
        with open(log_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_metadata(self, metadata_path: str) -> Optional[Dict]:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    # ── HTML Parsing ──

    def _parse_html_log(self, html_content: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html_content, 'html.parser')
        return {
            'title': self._extract_title(soup),
            'steps': self._extract_steps(soup),
            'agent_actions': self._extract_agent_actions(soup),
            'final_outcomes': self._extract_final_outcomes(soup),
            'nested_simulations': self._extract_nested_simulations(soup)
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_elem = soup.find('h1')
        if title_elem:
            return title_elem.get_text(strip=True)
        title_elem = soup.find('title')
        if title_elem:
            return title_elem.get_text(strip=True)
        premise_elem = soup.find(class_=re.compile(r'premise|scenario|context', re.I))
        if premise_elem:
            return premise_elem.get_text(strip=True)[:500]
        return "Unknown Simulation"

    def _extract_steps(self, soup: BeautifulSoup) -> List[Dict]:
        steps = []
        details_tags = soup.find_all('details')

        for details in details_tags:
            summary = details.find('summary')
            if not summary:
                continue
            summary_text = summary.get_text(strip=True)
            step_num_match = re.search(r'step\s*(\d+)', summary_text, re.I)
            if not step_num_match:
                continue
            step_num = int(step_num_match.group(1))
            content_parts = []
            for elem in details.find_all(text=True):
                if elem.parent.name != 'summary':
                    content_parts.append(elem.strip())
            step_text = ' '.join(content_parts).strip()
            full_content = f"{summary_text}\n\n{step_text}"
            steps.append({
                'step_number': step_num,
                'summary': summary_text,
                'content': step_text[:3000] if step_text else '',
                'full_content': full_content[:6000]
            })

        seen_steps = set()
        unique_steps = []
        for step in sorted(steps, key=lambda x: x['step_number']):
            if step['step_number'] not in seen_steps:
                seen_steps.add(step['step_number'])
                unique_steps.append(step)
        return unique_steps

    def _extract_agent_actions(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        actions = {}
        details_tags = soup.find_all('details')

        for details in details_tags:
            summary = details.find('summary')
            if not summary:
                continue
            summary_text = summary.get_text(strip=True)
            agent_match = re.search(r'(?:Step\s+\d+\s+)?([^—\s]+)(?:\s+---|$)', summary_text)
            if agent_match:
                agent_name = agent_match.group(1).strip()
                agent_name = re.sub(r'\s+', ' ', agent_name)
                agent_name = agent_name.split(' ')[0] if ' ' in agent_name and len(agent_name) < 50 else agent_name
                if agent_name and len(agent_name) < 50:
                    if agent_name not in actions:
                        actions[agent_name] = []
                    content_parts = []
                    for elem in details.find_all(text=True):
                        if elem.parent.name != 'summary':
                            text = elem.strip()
                            if text:
                                content_parts.append(text)
                    action_text = ' '.join(content_parts[:10]).strip()
                    if action_text and len(action_text) > 20:
                        actions[agent_name].append(action_text[:1500])

        if not actions:
            action_sections = soup.find_all(class_=re.compile(r'action|observation|act', re.I))
            for section in action_sections:
                text = section.get_text(strip=True)
                agent_match = re.search(r'([A-Z][a-z]+)\s+(?:said|did|acted|responded)', text)
                if agent_match:
                    agent_name = agent_match.group(1)
                    if agent_name not in actions:
                        actions[agent_name] = []
                    actions[agent_name].append(text[:500])
        return actions

    def _extract_final_outcomes(self, soup: BeautifulSoup) -> List[str]:
        outcomes = []
        conclusion_sections = soup.find_all(class_=re.compile(r'conclusion|decision|outcome|final', re.I))
        for section in conclusion_sections:
            text = section.get_text(strip=True)
            if len(text) > 50:
                outcomes.append(text[:1000])
        return outcomes

    def _extract_nested_simulations(self, soup: BeautifulSoup) -> List[Dict]:
        nested = []
        nested_sections = soup.find_all(class_=re.compile(r'nested|subsimulation|inner', re.I))
        for section in nested_sections:
            text = section.get_text(strip=True)
            if len(text) > 100:
                nested.append({
                    'content': text[:2000],
                    'premise': text[:500]
                })
        return nested

    # ── Metadata helpers ──

    def _extract_simulation_metadata(self, metadata: Optional[Dict], parsed_data: Dict) -> Dict:
        if metadata:
            return {
                'timestamp': metadata.get('timestamp'),
                'premise': metadata.get('premise'),
                'agents': metadata.get('agents', []),
                'game_master': metadata.get('game_master'),
                'title': parsed_data.get('title', 'Unknown')
            }
        return {
            'title': parsed_data.get('title', 'Unknown'),
            'premise': 'Not available',
            'agents': []
        }

    def _build_scenario_context(self, metadata: Optional[Dict]) -> str:
        """Build a rich scenario context block from metadata for prompt injection."""
        if not metadata:
            return "No simulation metadata available."

        parts = []

        premise = metadata.get('premise', '')
        if premise:
            parts.append(f"**Premise:** {premise}")

        gm = metadata.get('game_master', {})
        if gm:
            gm_info = f"**Game Master:** {gm.get('name', 'Unknown')} (prefab: {gm.get('prefab', 'unknown')})"
            parts.append(gm_info)
            gvars = gm.get('grounded_variables')
            if gvars:
                var_names = [v.get('name', '?') for v in gvars if isinstance(v, dict)]
                if var_names:
                    parts.append(f"**Grounded Variables Tracked:** {', '.join(var_names)}")

        agents = metadata.get('agents', [])
        if agents:
            parts.append(f"\n**Agents ({len(agents)}):**")
            for a in agents:
                line = f"- **{a.get('name', '?')}** (prefab: {a.get('prefab', '?')})"
                goal = a.get('goal', '')
                if goal:
                    line += f"\n  Goal: \"{goal}\""
                comps = a.get('components', {})
                if comps:
                    comp_names = list(comps.keys()) if isinstance(comps, dict) else []
                    if comp_names:
                        line += f"\n  Components: {', '.join(comp_names)}"
                mem_count = a.get('memories_count', 0)
                if mem_count:
                    line += f" | Memories: {mem_count}"
                nested = a.get('nested_simulation')
                if nested:
                    line += f"\n  Has nested simulation ({nested.get('max_steps', '?')} steps)"
                parts.append(line)

        gt = metadata.get('game_theoretic')
        if gt:
            scores = gt.get('scores', {})
            if scores:
                score_str = ', '.join(f"{k}: {v}" for k, v in scores.items())
                parts.append(f"\n**Game-Theoretic Scores:** {score_str}")
            actions = gt.get('actions_by_player', {})
            if actions:
                for player, acts in actions.items():
                    parts.append(f"  {player}'s actions: {acts}")

        return '\n'.join(parts)

    # ── Formatting helpers ──

    def _format_timeline_for_prompt(self, steps: List[Dict], max_steps: int = 20) -> str:
        if not steps:
            return "No steps data available"
        formatted = []
        for step in steps[:max_steps]:
            summary_text = step.get('summary', step.get('content', ''))[:500]
            formatted.append(f"Step {step['step_number']}: {summary_text}")
        if len(steps) > max_steps:
            formatted.append(f"... ({len(steps) - max_steps} additional steps omitted)")
        return "\n".join(formatted)

    def _format_actions_for_prompt(self, actions: Dict[str, List[str]]) -> str:
        if not actions:
            return "No specific agent actions captured"
        formatted = []
        for agent, action_list in actions.items():
            formatted.append(f"\n**{agent}** ({len(action_list)} actions):")
            for a in action_list[:5]:
                formatted.append(f"  - {a[:300]}")
        return "\n".join(formatted)

    def _format_agents_for_prompt(self, metadata: Optional[Dict]) -> str:
        if not metadata or not metadata.get('agents'):
            return "Agent information not available"
        agents = []
        for agent in metadata.get('agents', []):
            line = f"- **{agent.get('name')}**: {agent.get('goal', 'No goal specified')}"
            comps = agent.get('components', {})
            if comps and isinstance(comps, dict):
                line += f" [components: {', '.join(comps.keys())}]"
            agents.append(line)
        return "\n".join(agents)

    # ── LLM Analysis Sections ──

    def _generate_executive_summary(self, parsed_data: Dict, metadata: Optional[Dict]) -> str:
        scenario = self._build_scenario_context(metadata)
        steps = parsed_data.get('steps', [])

        prompt = f"""You are analyzing the results of a multi-agent simulation run on the Concordia platform. Concordia simulations place LLM-driven agents with distinct goals, memories, and psychological components into a shared scenario and let them interact over multiple steps. The Game Master (GM) narrates the world state and mediates agent actions.

**SIMULATION SETUP:**
{scenario}

**SIMULATION LOG ({len(steps)} steps):**
{self._format_timeline_for_prompt(steps)}

**AGENT ACTIONS:**
{self._format_actions_for_prompt(parsed_data.get('agent_actions', {}))}

**EXPLICIT OUTCOMES:**
{chr(10).join(parsed_data.get('final_outcomes', [])[:5]) or 'No explicit outcomes section found in the log.'}

**NESTED SIMULATIONS:** {len(parsed_data.get('nested_simulations', []))} inner simulations were run before the main simulation.

---

Write a 3-4 paragraph executive summary covering:

1. **Scenario and stakes** — What was being simulated, who the agents were, and what was at stake. Reference the premise and agent goals.
2. **Key events and turning points** — The most significant moments: when positions shifted, when new information surfaced, when decisions were made. Cite specific step numbers.
3. **Goal attainment** — For each agent, did they achieve their stated goal? Partially? Not at all? Be specific — if an agent's goal was "secure at least $1.2M," state whether they did.
4. **Emergent dynamics** — Behavior that was not explicitly programmed but emerged from agent interactions: alliances, betrayals, creative solutions, deadlocks, emotional shifts. If psychological components (cognitive biases, emotions, values) were configured, note whether their effects were visible in agent behavior.

Ground every claim in specific evidence from the log. If information is missing or ambiguous, say so."""

        try:
            return self.llm.sample_text(prompt, max_tokens=8000, temperature=0.3).strip()
        except Exception as e:
            print(f"[Analyzer] Error generating summary: {e}")
            return "Summary generation failed"

    def _analyze_team_effectiveness(self, parsed_data: Dict, metadata: Optional[Dict]) -> Dict:
        scenario = self._build_scenario_context(metadata)

        prompt = f"""You are analyzing individual agent performance in a Concordia multi-agent simulation. Each agent is an LLM-driven character with a specific goal, memories, and optional psychological components (personality traits, cognitive biases, emotions, values).

**SIMULATION SETUP:**
{scenario}

**AGENT ACTIONS:**
{self._format_actions_for_prompt(parsed_data.get('agent_actions', {}))}

**TIMELINE:**
{self._format_timeline_for_prompt(parsed_data.get('steps', []))}

---

For EACH agent in the simulation, provide:

### [Agent Name]
**Role & Design Intent:** What this agent was designed to do (from their goal and components).
**Goal Achievement:** Did they achieve their stated goal? Quote the goal and assess against it.
**Behavioral Consistency:** Did their actions align with their configured memories and components? For example:
  - If they had a cognitive_bias (e.g., loss_aversion), did it manifest in their decisions?
  - If they had personality_traits (Big Five), did their communication style match?
  - If they had an emotion component, did it color their responses?
  - If they had values, did those guide their moral reasoning?
**Key Contributions:** 2-3 specific actions or statements that shaped the simulation outcome.
**Surprising Behavior:** Anything unexpected — actions that contradicted their goal, creative solutions not in their memories, or failure modes.

After the individual assessments, add:

### Interaction Dynamics
- Which agent pairings produced the most interesting interactions and why?
- Were there any coalitions, conflicts, or persuasion attempts? Who initiated them?
- How did the Game Master shape the flow? Was it neutral or directive?"""

        try:
            analysis = self.llm.sample_text(prompt, max_tokens=8000, temperature=0.3)
            return {
                'analysis': analysis.strip(),
                'agents_analyzed': len(metadata.get('agents', [])) if metadata else 0
            }
        except Exception as e:
            print(f"[Analyzer] Error analyzing team effectiveness: {e}")
            return {'analysis': 'Team effectiveness analysis failed', 'agents_analyzed': 0}

    def _generate_insights(self, parsed_data: Dict, metadata: Optional[Dict]) -> Dict:
        scenario = self._build_scenario_context(metadata)
        has_game_theory = bool(metadata and metadata.get('game_theoretic'))
        has_grounded_vars = bool(metadata and metadata.get('game_master', {}).get('grounded_variables'))
        has_nested = bool(parsed_data.get('nested_simulations'))
        has_components = any(
            a.get('components') for a in (metadata or {}).get('agents', [])
        )

        prompt = f"""You are a research analyst examining results from a Concordia multi-agent simulation. Your task is to extract insights that would be valuable to a researcher or educator studying this scenario.

**SIMULATION SETUP:**
{scenario}

**TIMELINE:**
{self._format_timeline_for_prompt(parsed_data.get('steps', []))}

**OUTCOMES:**
{chr(10).join(parsed_data.get('final_outcomes', [])[:3]) or 'No explicit outcomes section.'}

---

Provide insights in the following categories. Skip any category that does not apply to this simulation.

1. **Agent Decision-Making Patterns**
   How did agents reason through decisions? Were there visible differences between agents with different prefabs (e.g., rational vs. basic, planning vs. reactive)? Did agents reference their memories or goals in their reasoning?

2. **Psychological Component Effects**{' (components were configured on agents)' if has_components else ' (no components configured — note this)'}
   Did cognitive biases produce the expected reasoning distortions? Did personality traits shape communication style? Did emotions escalate or de-escalate? Did values create the expected moral trade-offs? If no components were used, note what adding them might reveal.

3. **Information Dynamics**
   How did information flow between agents? Was private information (from player_specific_context or memories) revealed strategically? Did information asymmetry create realistic bargaining leverage?

4. **Emergent Social Phenomena**
   Cooperation, competition, trust-building, coalition formation, persuasion, free-riding, norm enforcement — which phenomena emerged? Were they consistent with the theoretical framework the simulation was designed to test?

{"5. **Game-Theoretic Outcomes**" + chr(10) + "   Compare actual choices and scores to theoretical predictions (Nash equilibrium, Pareto optimality, etc.)." if has_game_theory else ""}

{"6. **Grounded Variable Trajectories**" + chr(10) + "   Did the tracked variables evolve in ways consistent with the simulation events? Were update rules followed by the GM?" if has_grounded_vars else ""}

{"7. **Nested Simulation Integration**" + chr(10) + "   Did agents use findings from their inner simulations in the outer simulation? Was the extraction prompt effective?" if has_nested else ""}

8. **Methodological Observations**
   What worked well in this simulation design? What would you change for a re-run? Are there confounds or limitations in the setup?"""

        try:
            insights = self.llm.sample_text(prompt, max_tokens=8000, temperature=0.3)
            return {'analysis': insights.strip()}
        except Exception as e:
            print(f"[Analyzer] Error generating insights: {e}")
            return {'analysis': 'Insights generation failed'}

    def _generate_recommendations(self, parsed_data: Dict, metadata: Optional[Dict]) -> Dict:
        scenario = self._build_scenario_context(metadata)

        prompt = f"""You are advising a researcher or educator who just ran a Concordia multi-agent simulation. Based on the simulation setup and results, suggest concrete next steps.

**SIMULATION SETUP:**
{scenario}

**TIMELINE ({len(parsed_data.get('steps', []))} steps):**
{self._format_timeline_for_prompt(parsed_data.get('steps', []), max_steps=10)}

---

Provide recommendations in three categories:

**1. Re-run Variations (test different hypotheses)**
Suggest 3-4 specific modifications to the simulation configuration that would test interesting hypotheses. For each:
- What to change (be specific: which agent, which parameter, what value)
- What hypothesis it tests
- What you'd expect to observe

Examples of good modifications:
- "Change Agent X's cognitive_bias from confirmation_bias to anchoring_bias to test whether the type of bias matters more than its presence"
- "Remove player_specific_context from all agents to test whether private information drives the key dynamics or whether goals alone are sufficient"
- "Switch from sequential to simultaneous engine to test whether turn order creates agenda-setting power"
- "Add a values component to Agent Y with core_values ['fairness', 'reciprocity'] to test whether explicit values change negotiation outcomes"

**2. Design Improvements (improve this simulation)**
Suggest 2-3 changes to the simulation design that would produce richer or more realistic results:
- Agent configuration improvements (goals, memories, components)
- Scenario structure improvements (steps, engine type, acting order)
- Missing elements (grounded variables, critical decision points, additional agents)

**3. Research Extensions (go deeper)**
Suggest 2-3 ways to build on this simulation for academic research:
- What theoretical framework does this scenario connect to?
- What research question could a series of runs (with systematic variation) answer?
- What data extraction or analysis approach would strengthen the findings?"""

        try:
            recommendations = self.llm.sample_text(prompt, max_tokens=8000, temperature=0.3)
            return {'recommendations': recommendations.strip()}
        except Exception as e:
            print(f"[Analyzer] Error generating recommendations: {e}")
            return {'recommendations': 'Recommendations generation failed'}

    # ── Timeline extraction ──

    def _extract_timeline(self, parsed_data: Dict) -> List[Dict]:
        timeline = []
        for step in parsed_data.get('steps', []):
            summary = step.get('summary', step.get('content', ''))[:500]
            details = step.get('full_content', step.get('content', ''))
            timeline.append({
                'step': step['step_number'],
                'summary': summary,
                'details': details
            })
        return timeline

    # ── Report export ──

    def save_report(self, analysis: Dict[str, Any], output_path: str) -> None:
        markdown = self._format_markdown_report(analysis)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"[Analyzer] Report saved to {output_path}")

    def _format_markdown_report(self, analysis: Dict[str, Any]) -> str:
        md = []
        md.append("# Simulation Analysis Report")
        md.append("")
        md.append(f"**Simulation:** {analysis['metadata'].get('title', 'Unknown')}")
        md.append(f"**Analysis Date:** {analysis['analysis_date']}")
        md.append(f"**Premise:** {analysis['metadata'].get('premise', 'Not available')}")
        md.append("")
        md.append("## Executive Summary")
        md.append("")
        md.append(analysis['executive_summary'])
        md.append("")
        md.append("## Timeline of Events")
        md.append("")
        for event in analysis['timeline'][:20]:
            md.append(f"### Step {event['step']}")
            md.append(event['summary'])
            md.append("")
        md.append("## Agent Analysis")
        md.append("")
        md.append(analysis['team_effectiveness']['analysis'])
        md.append("")
        md.append("## Key Insights")
        md.append("")
        md.append(analysis['insights']['analysis'])
        md.append("")
        md.append("## Recommendations")
        md.append("")
        md.append(analysis['recommendations']['recommendations'])
        md.append("")
        md.append("---")
        md.append("*Report generated by Concordia Simulation Analyzer*")
        md.append(f"*Analysis Date: {analysis['analysis_date']}*")
        return "\n".join(md)


def analyze_simulation_from_api(llm_client, simulation_id: str, log_path: str) -> Dict[str, Any]:
    analyzer = SimulationAnalyzer(llm_client)
    return analyzer.analyze_simulation(log_path)


def save_analysis_report(analysis: Dict[str, Any], output_dir: str) -> str:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"simulation_analysis_{timestamp}.md"
    output_path = os.path.join(output_dir, filename)
    analyzer = SimulationAnalyzer(llm_client=None)
    analyzer.save_report(analysis, output_path)
    return output_path
