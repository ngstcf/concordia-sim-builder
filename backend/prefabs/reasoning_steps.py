"""
Factory for creating custom reasoning step components from JSON config.
Wraps Concordia's QuestionOfRecentMemories to allow UI-configured
reasoning questions injected into minimal__Entity via extra_components.
"""
from concordia.components.agent import question_of_recent_memories
from concordia.language_model import language_model


def create_reasoning_step_component(
    model: language_model.LanguageModel,
    agent_name: str,
    config: dict,
    index: int = 0,
):
    """Create a QuestionOfRecentMemories component from a config dict.

    Args:
        model: Language model instance.
        agent_name: Name of the agent.
        config: Dict with keys:
            - question: str (required) - The reasoning question
            - answer_prefix: str (optional) - Prefix for the answer
            - num_memories: int (optional, default 10) - Memories to retrieve
            - add_to_memory: bool (optional, default False)
        index: Component index for unique naming.

    Returns:
        A QuestionOfRecentMemories component instance.
    """
    question = config.get('question', 'What should I consider?')
    answer_prefix = config.get('answer_prefix', f'{agent_name} thinks: ')
    num_memories = config.get('num_memories', 10)
    add_to_memory = config.get('add_to_memory', False)
    label = config.get('label', f'Reasoning Step {index + 1}')

    question_formatted = question.replace('{agent_name}', agent_name)
    answer_prefix_formatted = answer_prefix.replace('{agent_name}', agent_name)

    return question_of_recent_memories.QuestionOfRecentMemories(
        model=model,
        pre_act_label=f'\n{label}',
        question=question_formatted,
        answer_prefix=answer_prefix_formatted,
        add_to_memory=add_to_memory,
        num_memories_to_retrieve=num_memories,
    )
