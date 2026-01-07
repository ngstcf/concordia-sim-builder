# Copyright 2024 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Nested simulation prefab for running mini-simulations within a larger simulation.

This prefab implements the "PhoneGameMaster" pattern from the Concordia paper,
where agents can run and observe nested simulations as part of their decision-making
process. For example, an agent might simulate a conversation with a friend to
decide what to bring to a party.

The nested simulation:
1. Receives context from the parent simulation
2. Runs a mini-simulation with specified agents and parameters
3. Extracts key observations and outcomes
4. Reports back to the parent simulation
"""

import dataclasses
from collections.abc import Mapping
from typing import Any, Optional
import datetime

from concordia.language_model import language_model
from concordia.associative_memory import basic_associative_memory
from concordia.prefabs.simulation import generic as simulation
from concordia.typing import prefab as prefab_lib
from concordia.agents import entity_agent_with_logging
from concordia.components import agent as agent_components
from concordia.typing import entity_component
from concordia.typing import entity as entity_lib


@dataclasses.dataclass
class NestedSimulationConfig(prefab_lib.Prefab):
    """Configuration for a nested simulation."""

    description: str = (
        'A nested simulation that runs a mini-simulation within the main '
        'simulation. The nested simulation receives context from its parent, '
        'runs a separate scenario with specified agents, and extracts key '
        'observations to report back.')

    params: Mapping[str, Any] = dataclasses.field(default_factory=lambda: {
        'name': 'nested_simulation',
        'parent_context': '',
        'nested_config': None,
        'max_steps': 5,
        'extraction_prompt': 'What were the key observations from this simulation?',
    })

    def build(
        self,
        model: language_model.LanguageModel,
        memory_bank: basic_associative_memory.AssociativeMemoryBank,
    ) -> entity_agent_with_logging.EntityAgentWithLogging:
        """Build a nested simulation observer agent.

        This agent doesn't participate in the main simulation like a normal entity.
        Instead, it acts as a bridge that can run nested simulations and report
        back their results.

        Args:
            model: The language model to use.
            memory_bank: The memory bank to use.

        Returns:
            An entity that can run nested simulations.
        """
        entity_name = self.params.get('name', 'nested_simulation')
        parent_context = self.params.get('parent_context', '')
        nested_config = self.params.get('nested_config')
        max_steps = self.params.get('max_steps', 5)
        extraction_prompt = self.params.get(
            'extraction_prompt',
            'What were the key observations from this simulation?'
        )

        # Create basic agent components
        memory_key = agent_components.memory.DEFAULT_MEMORY_COMPONENT_KEY
        memory = agent_components.memory.AssociativeMemory(memory_bank=memory_bank)

        instructions_key = 'Instructions'
        instructions = agent_components.instructions.Instructions(
            agent_name=entity_name,
            pre_act_label='\nInstructions',
        )

        observation_key = (
            agent_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY)
        observation = agent_components.observation.LastNObservations(
            history_length=100,
            pre_act_label=(
                '\nEvents so far (ordered from least recent to most recent)'
            ),
        )

        # Create a component that can run nested simulations
        nested_sim_component = NestedSimulationComponent(
            model=model,
            parent_context=parent_context,
            nested_config=nested_config,
            max_steps=max_steps,
            extraction_prompt=extraction_prompt,
        )

        components_of_agent = {
            instructions_key: instructions,
            observation_key: observation,
            memory_key: memory,
            'NestedSimulation': nested_sim_component,
        }

        agent = entity_agent_with_logging.EntityAgentWithLogging(
            agent_name=entity_name,
            act_component=nested_sim_component,
            context_components=components_of_agent,
        )

        return agent


class NestedSimulationComponent(
    entity_component.ContextComponent,
    entity_component.ComponentWithLogging
):
    """Component that can run nested simulations and extract observations.

    This component provides agents with the ability to run mini-simulations
    as part of their decision-making process, following the PhoneGameMaster
    pattern from the Concordia paper.
    """

    def __init__(
        self,
        model: language_model.LanguageModel,
        parent_context: str,
        nested_config: Any,
        max_steps: int = 5,
        extraction_prompt: str = 'What were the key observations?',
        pre_act_label: str = '\nNested Simulation',
    ):
        """Initialize the nested simulation component.

        Args:
            model: Language model to use
            parent_context: Context from parent simulation
            nested_config: Configuration for the nested simulation
            max_steps: Maximum steps for nested simulation
            extraction_prompt: Prompt for extracting key observations
            pre_act_label: Label for pre-act output
        """
        self._model = model
        self._parent_context = parent_context
        self._nested_config = nested_config
        self._max_steps = max_steps
        self._extraction_prompt = extraction_prompt
        self._pre_act_label = pre_act_label
        self._name = "nested_simulation"
        self._nested_result = None

    def get_name(self) -> str:
        """Return the component name."""
        return self._name

    def get_state(self) -> str:
        """Return the current state."""
        if self._nested_result:
            return (
                f"Nested simulation completed. "
                f"Result: {self._nested_result}"
            )
        return "Nested simulation available but not yet run."

    def set_state(self, state: str) -> None:
        """Set state from string (for deserialization)."""
        # Parse state to restore nested_result if available
        if "completed" in state and "Result:" in state:
            # Extract result from state string
            self._nested_result = {"status": "completed", "summary": state.split("Result: ")[1] if "Result: " in state else state}

    def pre_act(
        self,
        component_name: str,
        action_spec: Optional[entity_lib.ActionSpec] = None,
    ) -> str:
        """Provide current state before acting."""
        return self.get_state()

    def post_act(self, event: str) -> str:
        """Process event after acting (optional)."""
        return ""  # No post-processing needed

    def run_nested_simulation(
        self,
        embedder,
        additional_context: str = ''
    ) -> dict:
        """Run the nested simulation.

        Args:
            embedder: Sentence embedder to use
            additional_context: Additional context from the parent simulation

        Returns:
            Dictionary containing:
                - summary: Summary of the nested simulation
                - key_observations: List of key observations
                - outcome: Final outcome of the simulation
        """
        from backend.services.simulation_builder import build_simulation

        # Build the nested simulation
        nested_sim = build_simulation(
            config=self._nested_config,
            model=self._model,
            embedder=embedder
        )

        # Run the nested simulation
        # We'll run it for a limited number of steps
        outcome = nested_sim.play(max_steps=self._max_steps)

        # Extract observations
        key_observations = self._extract_observations(outcome)

        # Generate summary
        summary = self._generate_summary(outcome, additional_context)

        self._nested_result = {
            'summary': summary,
            'key_observations': key_observations,
            'outcome': str(outcome),
        }

        return self._nested_result

    def _extract_observations(self, outcome: Any) -> list[str]:
        """Extract key observations from the nested simulation outcome.

        Args:
            outcome: The outcome object from the nested simulation

        Returns:
            List of key observations
        """
        # This is a simplified version - in practice you'd parse the
        # actual simulation transcript more carefully
        observations = []

        # Extract from simulation history if available
        if hasattr(outcome, 'history'):
            for event in outcome.history[-10:]:  # Last 10 events
                if hasattr(event, 'observation'):
                    observations.append(event.observation)

        return observations

    def _generate_summary(
        self,
        outcome: Any,
        additional_context: str
    ) -> str:
        """Generate a summary of the nested simulation.

        Args:
            outcome: The outcome from the nested simulation
            additional_context: Additional context from parent

        Returns:
            A summary string
        """
        prompt = f"""
{self._extraction_prompt}

Parent context: {self._parent_context}
Additional context: {additional_context}

Nested simulation outcome: {outcome}

Please provide a concise summary of what happened in the nested simulation
and what the key takeaways are.
"""

        try:
            summary = self._model.sample_text(prompt)
            return summary
        except Exception as e:
            # If summarization fails, return a basic summary
            return f"Nested simulation completed with {len(self._extract_observations(outcome))} observations."


# Register the prefab
def get_prefab() -> NestedSimulationConfig:
    """Get the nested simulation prefab."""
    return NestedSimulationConfig()
