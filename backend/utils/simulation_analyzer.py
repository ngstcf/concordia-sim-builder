"""
Simulation Analyzer - LLM-powered deep content analysis tool

This module provides automated analysis of simulation logs using LLM to generate
comprehensive reports similar to manual expert analysis.

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

    Extracts structured insights from simulation logs including:
    - Timeline of events and agent actions
    - Team effectiveness assessment
    - Security insights and recommendations
    - Attack chain modeling (for security simulations)
    - Human factors analysis
    """

    def __init__(self, llm_client):
        """
        Initialize analyzer with LLM client.

        Args:
            llm_client: Language model instance with sample_text method
        """
        self.llm = llm_client

    def analyze_simulation(self, log_path: str, metadata_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a simulation log.

        Args:
            log_path: Path to HTML simulation log
            metadata_path: Optional path to JSON metadata file

        Returns:
            Dictionary containing structured analysis report
        """
        print(f"[Analyzer] Starting analysis of {log_path}")

        # Extract data from log
        log_content = self._read_log_file(log_path)
        metadata = self._load_metadata(metadata_path or log_path.replace('.html', '.metadata.json'))

        # Parse simulation content
        parsed_data = self._parse_html_log(log_content)

        # Build analysis sections
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

    def _read_log_file(self, log_path: str) -> str:
        """Read simulation log file."""
        with open(log_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_metadata(self, metadata_path: str) -> Optional[Dict]:
        """Load metadata from JSON file."""
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _parse_html_log(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML log to extract structured data.

        Args:
            html_content: Raw HTML content

        Returns:
            Dictionary with parsed sections
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract key sections
        return {
            'title': self._extract_title(soup),
            'steps': self._extract_steps(soup),
            'agent_actions': self._extract_agent_actions(soup),
            'final_outcomes': self._extract_final_outcomes(soup),
            'nested_simulations': self._extract_nested_simulations(soup)
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract simulation title/premise."""
        title_elem = soup.find('h1') or soup.find('title')
        return title_elem.get_text(strip=True) if title_elem else "Unknown Simulation"

    def _extract_steps(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all steps from the simulation."""
        steps = []

        # Look for step containers (adjust selectors based on actual HTML structure)
        step_containers = soup.find_all(class_=re.compile(r'step|phase|round', re.I))

        for container in step_containers:
            step_text = container.get_text(strip=True)
            # Try to extract step number
            step_num_match = re.search(r'step\s*(\d+)', step_text, re.I)
            step_num = int(step_num_match.group(1)) if step_num_match else len(steps) + 1

            steps.append({
                'step_number': step_num,
                'content': step_text[:1000],  # Truncate for analysis
                'full_content': step_text
            })

        return steps

    def _extract_agent_actions(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract agent actions by agent name."""
        actions = {}

        # Look for agent action sections
        action_sections = soup.find_all(class_=re.compile(r'action|observation|act', re.I))

        for section in action_sections:
            text = section.get_text(strip=True)

            # Try to identify agent name
            agent_match = re.search(r'(Sarah|Marcus|Elena|David|Agent|Player)', text, re.I)
            if agent_match:
                agent_name = agent_match.group(1)
                if agent_name not in actions:
                    actions[agent_name] = []
                actions[agent_name].append(text[:500])

        return actions

    def _extract_final_outcomes(self, soup: BeautifulSoup) -> List[str]:
        """Extract final outcomes/decisions."""
        outcomes = []

        # Look for conclusion/decision sections
        conclusion_sections = soup.find_all(class_=re.compile(r'conclusion|decision|outcome|final', re.I))

        for section in conclusion_sections:
            text = section.get_text(strip=True)
            if len(text) > 50:  # Filter out noise
                outcomes.append(text[:1000])

        return outcomes

    def _extract_nested_simulations(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract nested simulation content."""
        nested = []

        # Look for nested simulation markers
        nested_sections = soup.find_all(class_=re.compile(r'nested|subsimulation|inner', re.I))

        for section in nested_sections:
            text = section.get_text(strip=True)
            if len(text) > 100:
                nested.append({
                    'content': text[:2000],
                    'premise': text[:500]  # First part likely contains premise
                })

        return nested

    def _extract_simulation_metadata(self, metadata: Optional[Dict], parsed_data: Dict) -> Dict:
        """Extract and structure simulation metadata."""
        if metadata:
            return {
                'timestamp': metadata.get('timestamp'),
                'premise': metadata.get('premise'),
                'agents': metadata.get('agents', []),
                'game_master': metadata.get('game_master'),
                'title': parsed_data.get('title', 'Unknown')
            }

        # Fallback to parsed data
        return {
            'title': parsed_data.get('title', 'Unknown'),
            'premise': 'Not available',
            'agents': []
        }

    def _generate_executive_summary(self, parsed_data: Dict, metadata: Optional[Dict]) -> str:
        """Generate executive summary using LLM."""
        prompt = self._build_summary_prompt(parsed_data, metadata)

        try:
            summary = self.llm.sample_text(
                prompt,
                max_tokens=2000,
                temperature=0.3
            )
            return summary.strip()
        except Exception as e:
            print(f"[Analyzer] Error generating summary: {e}")
            return "Summary generation failed"

    def _build_summary_prompt(self, parsed_data: Dict, metadata: Optional[Dict]) -> str:
        """Build prompt for executive summary generation."""
        premise = metadata.get('premise', '') if metadata else parsed_data.get('title', '')

        prompt = f"""Analyze this simulation and provide a comprehensive executive summary:

**Simulation Premise:**
{premise}

**Timeline Overview:**
{self._format_timeline_for_prompt(parsed_data.get('steps', []))}

**Key Outcomes:**
{chr(10).join(parsed_data.get('final_outcomes', [])[:5])}

**Nested Simulations:**
{len(parsed_data.get('nested_simulations', []))} nested simulations were run.

Provide a 3-4 paragraph executive summary covering:
1. What scenario was simulated and why
2. Key events and outcomes (including any multi-phase developments)
3. Team effectiveness and decision quality
4. Critical insights or recommendations

Format as professional analysis prose."""

        return prompt

    def _format_timeline_for_prompt(self, steps: List[Dict]) -> str:
        """Format steps for prompt inclusion."""
        if not steps:
            return "No steps data available"

        formatted = []
        for step in steps[:10]:  # Limit to avoid token limits
            formatted.append(f"Step {step['step_number']}: {step['content'][:200]}...")

        return "\n".join(formatted)

    def _extract_timeline(self, parsed_data: Dict) -> List[Dict]:
        """Extract structured timeline from parsed data."""
        timeline = []

        for step in parsed_data.get('steps', []):
            timeline.append({
                'step': step['step_number'],
                'summary': step['content'][:300],
                'details': step['content']
            })

        return timeline

    def _analyze_team_effectiveness(self, parsed_data: Dict, metadata: Optional[Dict]) -> Dict:
        """Analyze team effectiveness using LLM."""
        prompt = f"""Analyze the team effectiveness in this simulation:

**Agents:**
{self._format_agents_for_prompt(metadata)}

**Agent Actions:**
{self._format_actions_for_prompt(parsed_data.get('agent_actions', {}))}

**Timeline:**
{self._format_timeline_for_prompt(parsed_data.get('steps', []))}

For each agent, provide:
1. Role and primary focus
2. Key contributions (specific actions/decisions)
3. Effectiveness rating (1-5 stars) with justification
4. Strengths demonstrated
5. One key insight they provided

Format as structured markdown with agent sections."""

        try:
            analysis = self.llm.sample_text(
                prompt,
                max_tokens=3000,
                temperature=0.3
            )
            return {
                'analysis': analysis.strip(),
                'agents_analyzed': len(metadata.get('agents', [])) if metadata else 0
            }
        except Exception as e:
            print(f"[Analyzer] Error analyzing team effectiveness: {e}")
            return {'analysis': 'Team effectiveness analysis failed', 'agents_analyzed': 0}

    def _format_agents_for_prompt(self, metadata: Optional[Dict]) -> str:
        """Format agents list for prompt."""
        if not metadata or not metadata.get('agents'):
            return "Agent information not available"

        agents = []
        for agent in metadata.get('agents', []):
            agents.append(f"- {agent.get('name')}: {agent.get('goal', 'No goal specified')}")

        return "\n".join(agents)

    def _format_actions_for_prompt(self, actions: Dict[str, List[str]]) -> str:
        """Format agent actions for prompt."""
        if not actions:
            return "No specific agent actions captured"

        formatted = []
        for agent, action_list in actions.items():
            formatted.append(f"\n{agent}:\n" + "\n".join(f"  - {a[:200]}" for a in action_list[:3]))

        return "\n".join(formatted)

    def _generate_insights(self, parsed_data: Dict, metadata: Optional[Dict]) -> Dict:
        """Generate key insights using LLM."""
        prompt = f"""Extract and analyze key insights from this simulation:

**Premise:**
{metadata.get('premise', '') if metadata else ''}

**Nested Simulations:**
{len(parsed_data.get('nested_simulations', []))} nested simulations were conducted.

**Timeline:**
{self._format_timeline_for_prompt(parsed_data.get('steps', []))}

**Final Outcomes:**
{chr(10).join(parsed_data.get('final_outcomes', [])[:3])}

Provide insights in these categories:

1. **Technical Analysis**: Technical findings, vulnerabilities, or mechanisms identified
2. **Human Factors**: Psychological manipulation, user behavior, organizational culture
3. **Decision Quality**: Quality of decisions made, alternatives considered
4. **Attack/Failure Modes**: How attacks succeeded or failures occurred (if applicable)
5. **Learning Outcomes**: What worked well, what could be improved

Format as structured markdown with clear section headers."""

        try:
            insights = self.llm.sample_text(
                prompt,
                max_tokens=3000,
                temperature=0.3
            )
            return {
                'analysis': insights.strip(),
                'categories': ['technical', 'human_factors', 'decision_quality', 'attack_modes', 'learning']
            }
        except Exception as e:
            print(f"[Analyzer] Error generating insights: {e}")
            return {'analysis': 'Insights generation failed', 'categories': []}

    def _generate_recommendations(self, parsed_data: Dict, metadata: Optional[Dict]) -> Dict:
        """Generate actionable recommendations using LLM."""
        prompt = f"""Based on this simulation, generate actionable recommendations:

**Premise:**
{metadata.get('premise', '') if metadata else ''}

**Insights from Analysis:**
(Consider what vulnerabilities were exposed, what gaps identified, what failures occurred)

**Timeline:**
{self._format_timeline_for_prompt(parsed_data.get('steps', []))}

Provide specific, actionable recommendations organized by timeframe:

**Immediate Actions (0-30 days)**
- 3-5 high-priority actions that should be taken immediately
- Include priority, effort level, and expected impact for each

**Medium-Term Actions (30-90 days)**
- 3-5 actions for the next quarter
- Focus on addressing root causes

**Long-Term Actions (90+ days)**
- 2-3 strategic initiatives
- Focus on transformation and culture change

Format each recommendation as:
- **[Action Name]**
  - Priority: High/Medium/Low
  - Effort: Low/Medium/High/Very High
  - Impact: [Expected outcome]
  - Description: [2-3 sentences]"""

        try:
            recommendations = self.llm.sample_text(
                prompt,
                max_tokens=2500,
                temperature=0.3
            )
            return {
                'recommendations': recommendations.strip(),
                'timeframes': ['immediate', 'medium_term', 'long_term']
            }
        except Exception as e:
            print(f"[Analyzer] Error generating recommendations: {e}")
            return {'recommendations': 'Recommendations generation failed', 'timeframes': []}

    def save_report(self, analysis: Dict[str, Any], output_path: str) -> None:
        """
        Save analysis report as markdown file.

        Args:
            analysis: Analysis dictionary from analyze_simulation()
            output_path: Path to save markdown report
        """
        markdown = self._format_markdown_report(analysis)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"[Analyzer] Report saved to {output_path}")

    def _format_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """Format analysis as markdown report."""
        md = []

        # Title and metadata
        md.append(f"# Simulation Analysis Report")
        md.append(f"")
        md.append(f"**Simulation:** {analysis['metadata'].get('title', 'Unknown')}")
        md.append(f"**Analysis Date:** {analysis['analysis_date']}")
        md.append(f"**Premise:** {analysis['metadata'].get('premise', 'Not available')}")
        md.append(f"")

        # Executive Summary
        md.append(f"## Executive Summary")
        md.append(f"")
        md.append(f"{analysis['executive_summary']}")
        md.append(f"")

        # Timeline
        md.append(f"## Timeline of Events")
        md.append(f"")
        for event in analysis['timeline'][:15]:  # Limit to 15 events
            md.append(f"### Step {event['step']}")
            md.append(f"{event['summary']}")
            md.append(f"")

        # Team Effectiveness
        md.append(f"## Team Effectiveness Analysis")
        md.append(f"")
        md.append(f"{analysis['team_effectiveness']['analysis']}")
        md.append(f"")

        # Insights
        md.append(f"## Key Insights")
        md.append(f"")
        md.append(f"{analysis['insights']['analysis']}")
        md.append(f"")

        # Recommendations
        md.append(f"## Recommendations")
        md.append(f"")
        md.append(f"{analysis['recommendations']['recommendations']}")
        md.append(f"")

        # Footer
        md.append(f"---")
        md.append(f"*Report generated by Simulation Analyzer*")
        md.append(f"*Analysis Date: {analysis['analysis_date']}*")

        return "\n".join(md)


def analyze_simulation_from_api(llm_client, simulation_id: str, log_path: str) -> Dict[str, Any]:
    """
    Convenience function to analyze simulation from API data.

    Args:
        llm_client: Language model instance
        simulation_id: Simulation identifier
        log_path: Path to HTML log file

    Returns:
        Analysis dictionary
    """
    analyzer = SimulationAnalyzer(llm_client)
    return analyzer.analyze_simulation(log_path)


def save_analysis_report(analysis: Dict[str, Any], output_dir: str) -> str:
    """
    Convenience function to save analysis report with auto-generated filename.

    Args:
        analysis: Analysis dictionary
        output_dir: Directory to save report

    Returns:
        Full path to saved report
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"simulation_analysis_{timestamp}.md"
    output_path = os.path.join(output_dir, filename)

    analyzer = SimulationAnalyzer(llm_client=None)  # Dummy init for save method
    analyzer.save_report(analysis, output_path)

    return output_path
