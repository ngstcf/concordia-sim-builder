import { useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';

interface QuestionChoice {
  text: string;
}

interface Question {
  id: string;
  statement: string;
  dimension: string;
  preprompt: string;
  choices: string[];
  ascending_scale: boolean;
}

interface Questionnaire {
  id: string;
  name: string;
  description: string;
  questionnaire_type: string;
  observation_preprompt: string;
  questions: Question[];
}

const QUESTIONNAIRE_TYPES = [
  { value: 'multiple_choice', label: 'Multiple Choice (Likert Scale)' },
  { value: 'open_ended', label: 'Open Ended (Free Text)' },
  { value: 'mixed', label: 'Mixed (Both Types)' },
];

const LIKERT_PRESETS = {
  agree_5: ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
  frequency_5: ['Never', 'Rarely', 'Sometimes', 'Often', 'Always'],
  satisfaction_5: ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied'],
  likelihood_5: ['Very Unlikely', 'Unlikely', 'Neutral', 'Likely', 'Very Likely'],
};

export default function QuestionnaireBuilder() {
  const { config, setGameMaster } = useSimulation();

  const loadQuestionnaires = (): Questionnaire[] => {
    const raw = config.game_master.parameters?.questionnaires || [];
    return raw.map((q: any, qi: number) => ({
      ...q,
      id: q.id || `q-${qi}`,
      questions: (q.questions || []).map((qn: any, qni: number) => ({
        ...qn,
        id: qn.id || `qn-${qi}-${qni}`,
      })),
    }));
  };

  const [questionnaires, setQuestionnaires] = useState<Questionnaire[]>(loadQuestionnaires);
  const [expandedQ, setExpandedQ] = useState<string | null>(
    questionnaires.length > 0 ? questionnaires[0].id : null
  );

  useEffect(() => {
    setQuestionnaires(loadQuestionnaires());
  }, [config.game_master.parameters?.questionnaires]);

  const syncToConfig = (updated: Questionnaire[]) => {
    const clean = updated.map(({ id, ...q }) => ({
      ...q,
      questions: q.questions.map(({ id: _id, ...qn }) => qn),
    }));
    setGameMaster({
      ...config.game_master,
      parameters: { ...config.game_master.parameters, questionnaires: clean },
    });
  };

  const addQuestionnaire = () => {
    const newQ: Questionnaire = {
      id: `q-${Date.now()}`,
      name: `Survey ${questionnaires.length + 1}`,
      description: '',
      questionnaire_type: 'multiple_choice',
      observation_preprompt: 'Please answer the following questions honestly.',
      questions: [],
    };
    const updated = [...questionnaires, newQ];
    setQuestionnaires(updated);
    syncToConfig(updated);
    setExpandedQ(newQ.id);
  };

  const removeQuestionnaire = (id: string) => {
    const updated = questionnaires.filter(q => q.id !== id);
    setQuestionnaires(updated);
    syncToConfig(updated);
    if (expandedQ === id) setExpandedQ(null);
  };

  const updateQuestionnaire = (id: string, patch: Partial<Questionnaire>) => {
    const updated = questionnaires.map(q => (q.id === id ? { ...q, ...patch } : q));
    setQuestionnaires(updated);
    syncToConfig(updated);
  };

  const addQuestion = (qId: string) => {
    const q = questionnaires.find(q => q.id === qId);
    if (!q) return;
    const newQuestion: Question = {
      id: `qn-${Date.now()}`,
      statement: '',
      dimension: '',
      preprompt: 'On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),',
      choices: [...LIKERT_PRESETS.agree_5],
      ascending_scale: true,
    };
    updateQuestionnaire(qId, { questions: [...q.questions, newQuestion] });
  };

  const updateQuestion = (qId: string, qnId: string, patch: Partial<Question>) => {
    const q = questionnaires.find(q => q.id === qId);
    if (!q) return;
    updateQuestionnaire(qId, {
      questions: q.questions.map(qn => (qn.id === qnId ? { ...qn, ...patch } : qn)),
    });
  };

  const removeQuestion = (qId: string, qnId: string) => {
    const q = questionnaires.find(q => q.id === qId);
    if (!q) return;
    updateQuestionnaire(qId, { questions: q.questions.filter(qn => qn.id !== qnId) });
  };

  const moveQuestion = (qId: string, index: number, direction: 'up' | 'down') => {
    const q = questionnaires.find(q => q.id === qId);
    if (!q) return;
    const target = direction === 'up' ? index - 1 : index + 1;
    if (target < 0 || target >= q.questions.length) return;
    const updated = [...q.questions];
    [updated[index], updated[target]] = [updated[target], updated[index]];
    updateQuestionnaire(qId, { questions: updated });
  };

  const applyLikertPreset = (qId: string, qnId: string, preset: keyof typeof LIKERT_PRESETS) => {
    const choices = LIKERT_PRESETS[preset];
    updateQuestion(qId, qnId, {
      choices: [...choices],
      preprompt: `On a scale of 1 (${choices[0]}) to ${choices.length} (${choices[choices.length - 1]}),`,
    });
  };

  return (
    <div className="mt-4 bg-teal-50 p-4 rounded-md border border-teal-200">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="text-sm font-medium text-gray-900">Questionnaire Builder</h4>
          <p className="text-xs text-gray-500">
            Design surveys and interview questions for respondent agents
          </p>
        </div>
        <button
          type="button"
          onClick={addQuestionnaire}
          className="text-sm bg-teal-100 text-teal-700 px-3 py-1.5 rounded-md hover:bg-teal-200"
        >
          + Add Questionnaire
        </button>
      </div>

      {questionnaires.length === 0 ? (
        <div className="text-center py-6 bg-white rounded-md border border-dashed border-teal-300">
          <p className="text-sm text-gray-500">No questionnaires configured.</p>
          <p className="text-xs text-gray-400 mt-1">
            Add a questionnaire to define interview or survey questions.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {questionnaires.map((q) => (
            <div key={q.id} className="bg-white rounded-md border border-gray-200 overflow-hidden">
              {/* Questionnaire header */}
              <div
                className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50"
                onClick={() => setExpandedQ(expandedQ === q.id ? null : q.id)}
              >
                <div>
                  <span className="text-sm font-medium text-gray-900">{q.name}</span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs px-1.5 py-0.5 bg-teal-100 text-teal-700 rounded">
                      {QUESTIONNAIRE_TYPES.find(t => t.value === q.questionnaire_type)?.label || q.questionnaire_type}
                    </span>
                    <span className="text-xs text-gray-500">
                      {q.questions.length} question{q.questions.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); removeQuestionnaire(q.id); }}
                    className="p-1 text-red-400 hover:text-red-600"
                    title="Remove questionnaire"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                  <svg
                    className={`w-4 h-4 text-gray-400 transform transition-transform ${expandedQ === q.id ? 'rotate-180' : ''}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>

              {/* Questionnaire body */}
              {expandedQ === q.id && (
                <div className="px-4 pb-4 pt-1 border-t border-gray-100 space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Name</label>
                      <input
                        type="text"
                        className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                        value={q.name}
                        onChange={(e) => updateQuestionnaire(q.id, { name: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
                      <select
                        className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                        value={q.questionnaire_type}
                        onChange={(e) => updateQuestionnaire(q.id, { questionnaire_type: e.target.value })}
                      >
                        {QUESTIONNAIRE_TYPES.map(t => (
                          <option key={t.value} value={t.value}>{t.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Description</label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                      value={q.description}
                      onChange={(e) => updateQuestionnaire(q.id, { description: e.target.value })}
                      placeholder="Brief description of this questionnaire"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Observation Pre-prompt</label>
                    <textarea
                      rows={2}
                      className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                      value={q.observation_preprompt}
                      onChange={(e) => updateQuestionnaire(q.id, { observation_preprompt: e.target.value })}
                      placeholder="Instructions shown before the questionnaire"
                    />
                  </div>

                  {/* Questions */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-xs font-medium text-gray-700">Questions</label>
                      <button
                        type="button"
                        onClick={() => addQuestion(q.id)}
                        className="text-xs text-teal-600 hover:text-teal-800"
                      >
                        + Add Question
                      </button>
                    </div>

                    {q.questions.length === 0 ? (
                      <p className="text-xs text-gray-400 italic text-center py-3">
                        No questions yet. Click "+ Add Question" to create one.
                      </p>
                    ) : (
                      <div className="space-y-3">
                        {q.questions.map((qn, qnIndex) => (
                          <div
                            key={qn.id}
                            className="bg-gray-50 p-3 rounded-md border border-gray-200"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs font-medium text-gray-500">
                                Q{qnIndex + 1}
                              </span>
                              <div className="flex items-center gap-1">
                                <button
                                  type="button"
                                  onClick={() => moveQuestion(q.id, qnIndex, 'up')}
                                  disabled={qnIndex === 0}
                                  className="p-0.5 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                                >
                                  ▲
                                </button>
                                <button
                                  type="button"
                                  onClick={() => moveQuestion(q.id, qnIndex, 'down')}
                                  disabled={qnIndex === q.questions.length - 1}
                                  className="p-0.5 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                                >
                                  ▼
                                </button>
                                <button
                                  type="button"
                                  onClick={() => removeQuestion(q.id, qn.id)}
                                  className="p-0.5 text-red-400 hover:text-red-600 ml-1"
                                >
                                  ✕
                                </button>
                              </div>
                            </div>

                            <div className="space-y-2">
                              <div>
                                <label className="block text-xs text-gray-600 mb-1">Statement</label>
                                <textarea
                                  rows={2}
                                  className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                  value={qn.statement}
                                  onChange={(e) => updateQuestion(q.id, qn.id, { statement: e.target.value })}
                                  placeholder="e.g., I am satisfied with my current role."
                                />
                              </div>

                              <div className="grid grid-cols-2 gap-2">
                                <div>
                                  <label className="block text-xs text-gray-600 mb-1">Dimension</label>
                                  <input
                                    type="text"
                                    className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                    value={qn.dimension}
                                    onChange={(e) => updateQuestion(q.id, qn.id, { dimension: e.target.value })}
                                    placeholder="e.g., job_satisfaction"
                                  />
                                </div>
                                <div>
                                  <label className="block text-xs text-gray-600 mb-1">Scale Preset</label>
                                  <select
                                    className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                    value=""
                                    onChange={(e) => {
                                      if (e.target.value) {
                                        applyLikertPreset(q.id, qn.id, e.target.value as keyof typeof LIKERT_PRESETS);
                                      }
                                    }}
                                  >
                                    <option value="">Apply preset...</option>
                                    <option value="agree_5">Agreement (5-point)</option>
                                    <option value="frequency_5">Frequency (5-point)</option>
                                    <option value="satisfaction_5">Satisfaction (5-point)</option>
                                    <option value="likelihood_5">Likelihood (5-point)</option>
                                  </select>
                                </div>
                              </div>

                              <div>
                                <label className="block text-xs text-gray-600 mb-1">Pre-prompt</label>
                                <input
                                  type="text"
                                  className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                  value={qn.preprompt}
                                  onChange={(e) => updateQuestion(q.id, qn.id, { preprompt: e.target.value })}
                                  placeholder="Instructions before the choices"
                                />
                              </div>

                              {/* Choices */}
                              {q.questionnaire_type !== 'open_ended' && (
                                <div>
                                  <div className="flex items-center justify-between mb-1">
                                    <label className="block text-xs text-gray-600">Choices</label>
                                    <button
                                      type="button"
                                      onClick={() => {
                                        updateQuestion(q.id, qn.id, {
                                          choices: [...qn.choices, `Choice ${qn.choices.length + 1}`],
                                        });
                                      }}
                                      className="text-xs text-teal-600 hover:text-teal-800"
                                    >
                                      + Add
                                    </button>
                                  </div>
                                  <div className="space-y-1">
                                    {qn.choices.map((choice, ci) => (
                                      <div key={ci} className="flex items-center gap-2">
                                        <span className="text-xs text-gray-400 w-4 text-right">{ci + 1}.</span>
                                        <input
                                          type="text"
                                          className="flex-1 border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                          value={choice}
                                          onChange={(e) => {
                                            const updated = [...qn.choices];
                                            updated[ci] = e.target.value;
                                            updateQuestion(q.id, qn.id, { choices: updated });
                                          }}
                                        />
                                        {qn.choices.length > 2 && (
                                          <button
                                            type="button"
                                            onClick={() => {
                                              updateQuestion(q.id, qn.id, {
                                                choices: qn.choices.filter((_, i) => i !== ci),
                                              });
                                            }}
                                            className="text-red-400 hover:text-red-600 text-xs"
                                          >
                                            ✕
                                          </button>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              <div className="flex items-center gap-2">
                                <input
                                  type="checkbox"
                                  id={`asc-${qn.id}`}
                                  className="h-3.5 w-3.5 text-teal-600 border-gray-300 rounded"
                                  checked={qn.ascending_scale}
                                  onChange={(e) => updateQuestion(q.id, qn.id, { ascending_scale: e.target.checked })}
                                />
                                <label htmlFor={`asc-${qn.id}`} className="text-xs text-gray-600">
                                  Ascending scale (first choice = lowest value)
                                </label>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
