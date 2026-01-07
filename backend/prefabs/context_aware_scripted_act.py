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

"""Context-aware scripted acting component.

Unlike the standard ScriptedActComponent which forces exact responses,
this component uses script lines as adaptive prompts that guide the LLM
while allowing contextual responses.
"""

from collections.abc import Sequence, Mapping

from concordia.document import interactive_document
from concordia.language_model import language_model
from concordia.typing import entity as entity_lib
from concordia.typing import entity_component
from typing_extensions import override


class ContextAwareScriptedActComponent(
    entity_component.ActingComponent, entity_component.ComponentWithLogging
):
  """An acting component that uses a script as adaptive prompts.

  This component processes scripts similarly to ScriptedActComponent, but
  instead of forcing exact responses, it uses the script line as a prompt
  template that the LLM can adapt based on conversation context.

  This creates more natural dialogue where the agent can:
  - React to what other participants say
  - Reference previous conversation
  - Maintain conversational flow
  - Still follow the intended script structure

  The script is a list of dictionaries, where each entry contains:
    - 'name': The entity name (for filtering)
    - 'line': The prompt/template for this action
  """

  def __init__(
      self,
      model: language_model.LanguageModel,
      script: list[Mapping[str, str]],
      component_order: Sequence[str] | None = None,
      prefix_entity_name: bool = True,
      end_statement: str | None = None,
  ):
    """Initializes the agent.

    Args:
      model: The language model to use for generating the action attempt.
      script: The script to execute. This is a list of dictionaries, where
        each entry is a dictionary containing the name of the entity that
        the line is associated with and the prompt/template to use.
      component_order: The order in which the component contexts will be
        assembled when calling the act component.
      prefix_entity_name: Whether to prefix the entity name to the output.
      end_statement: Optional statement to use when script is exhausted.
        If None, a generic closing statement will be used.
    """
    super().__init__()
    self._model = model
    self._prefix_entity_name = prefix_entity_name
    if component_order is None:
      self._component_order = None
    else:
      self._component_order = tuple(component_order)

    self._script = script
    self._lines = []
    self._line_index = 0
    # Default end statement if none provided
    self._end_statement = end_statement or (
      "I believe we've covered everything we needed to discuss today. "
      "Thank you all for your participation. This concludes our session."
    )

  def _context_for_action(
      self,
      contexts: entity_component.ComponentContextMapping,
  ) -> str:
    if self._component_order is None:
      return '\n'.join(
          context for context in contexts.values() if context
      )
    else:
      order = self._component_order + tuple(sorted(
          set(contexts.keys()) - set(self._component_order)))
      return '\n'.join(
          contexts[name] for name in order if contexts[name]
      )

  @override
  def get_action_attempt(
      self,
      contexts: entity_component.ComponentContextMapping,
      action_spec: entity_lib.ActionSpec,
  ) -> str:
    prompt = interactive_document.InteractiveDocument(self._model)
    context = self._context_for_action(contexts)
    prompt.statement(context + '\n')

    # Filter lines for this entity (done once)
    if not self._lines:
      for line in self._script:
        if line['name'] == self.get_entity().name:
          self._lines.append(line['line'])

    # If we have more scripted lines, use the current one as a prompt
    if self._line_index < len(self._lines):
      current_prompt = self._lines[self._line_index]

      # Add the scripted line as guidance/instruction (not forced)
      prompt.statement(
          f'\nGuidance for your response: {current_prompt}\n'
          f'You should adapt this guidance based on the conversation context above. '
          f'Respond naturally while following the intent of this guidance.'
      )

      call_to_action = action_spec.call_to_action.format(
          name=self.get_entity().name
      )

      output = ''
      if self._prefix_entity_name:
        output = self.get_entity().name + ' '

      # Generate response based on context + script guidance (NOT forced)
      llm_output = prompt.open_question(
          call_to_action,
          max_tokens=2200,
          answer_prefix=output,
          terminators=(),
          question_label='Response',
      )

      output += llm_output
      self._line_index += 1

      self._log(output, prompt, current_prompt)
      return output
    else:
      # Script exhausted - check if we've already said our closing statement
      if self._line_index < len(self._lines) + 1:
        # First time after script exhausted - say closing statement
        output = ''
        if self._prefix_entity_name:
          output = self.get_entity().name + ' '
        output += self._end_statement
        self._log(output, prompt, "[End of script - using closing statement]")
        self._line_index = len(self._lines) + 1  # Mark that closing was delivered
        return output
      else:
        # Already said closing - stay silent to let simulation end
        return ''

  def _log(self,
           result: str,
           prompt: interactive_document.InteractiveDocument,
           script_guidance: str):
    self._logging_channel({
        'Summary': f'Action: {result}',
        'Value': result,
        'Prompt': prompt.view().text().splitlines(),
        'Script guidance used': script_guidance,
        'Line index': self._line_index,
    })

  def get_state(self) -> entity_component.ComponentState:
    """Converts the component to a dictionary."""
    return {
        'script': self._script,
        'line_index': self._line_index,
        'remaining_lines': self._lines[self._line_index:],
    }

  def set_state(self, state: entity_component.ComponentState) -> None:
    self._script = state['script']
    self._line_index = state['line_index']
    # Reconstruct lines from script
    self._lines = [
        line['line'] for line in self._script
        if line['name'] == self.get_entity().name
    ]
