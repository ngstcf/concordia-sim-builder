import { useState, useRef } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import { generatePersonas, generatePersonasCensus, parseDistribution } from '../../utils/api';
import AgentEditor from './AgentEditor';

const PREFAB_BADGES: Record<string, { label: string; color: string }> = {
  basic: { label: 'Basic', color: 'bg-blue-100 text-blue-700' },
  basic_with_plan: { label: 'Planner', color: 'bg-blue-100 text-blue-700' },
  minimal: { label: 'Minimal', color: 'bg-gray-100 text-gray-700' },
  basic_scripted: { label: 'Scripted', color: 'bg-amber-100 text-amber-700' },
  context_aware_scripted: { label: 'Scripted+', color: 'bg-amber-100 text-amber-700' },
  conversational: { label: 'Dialogue', color: 'bg-green-100 text-green-700' },
  rational: { label: 'Rational', color: 'bg-purple-100 text-purple-700' },
  puppet: { label: 'Puppet', color: 'bg-red-100 text-red-700' },
  basic_with_image: { label: 'Multimodal', color: 'bg-pink-100 text-pink-700' },
};

function getPrefabBadge(prefab: string) {
  const key = prefab.replace('__Entity', '');
  return PREFAB_BADGES[key] || { label: key, color: 'bg-gray-100 text-gray-600' };
}

interface GeneratedPersona {
  name: string;
  goal: string;
  memories: string[];
  description: string;
  selected: boolean;
}

export default function AgentList() {
  const { config, addAgent, removeAgent, reorderAgents, llmSettings } = useSimulation();
  const [editingAgent, setEditingAgent] = useState<string | null>(null);
  const dragItem = useRef<number | null>(null);
  const dragOverItem = useRef<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  // Persona generator state
  const [showGenerator, setShowGenerator] = useState(false);
  const [genTab, setGenTab] = useState<'llm' | 'census'>('llm');
  const [genContext, setGenContext] = useState('');
  const [genAxes, setGenAxes] = useState('');
  const [genCount, setGenCount] = useState(5);
  const [genMemories, setGenMemories] = useState(5);
  const [generating, setGenerating] = useState(false);
  const [generatedPersonas, setGeneratedPersonas] = useState<GeneratedPersona[]>([]);
  const [genError, setGenError] = useState('');

  // Census generator state
  const [censusJson, setCensusJson] = useState('{\n  "age": {"18-25": 0.3, "26-40": 0.4, "41-60": 0.2, "60+": 0.1},\n  "income": {"low": 0.4, "medium": 0.35, "high": 0.25}\n}');
  const [censusCount, setCensusCount] = useState(10);
  const [censusSeed, setCensusSeed] = useState<string>('');
  const [censusEnrich, setCensusEnrich] = useState(false);
  const [censusContext, setCensusContext] = useState('');
  const [censusSummary, setCensusSummary] = useState<Record<string, Record<string, number>> | null>(null);

  const handleAddAgent = () => {
    const newAgent = {
      id: `agent-${Date.now()}`,
      name: `Agent ${config.agents.length + 1}`,
      prefab: 'basic__Entity',
      memories: [],
      randomize_choices: true,
    };
    addAgent(newAgent);
    setEditingAgent(newAgent.id);
  };

  const handleDuplicate = (agentId: string) => {
    const source = config.agents.find(a => a.id === agentId);
    if (!source) return;
    const dup = {
      ...source,
      id: `agent-${Date.now()}`,
      name: `${source.name} (copy)`,
      memories: [...source.memories],
      components: source.components ? { ...source.components } : undefined,
    };
    addAgent(dup);
  };

  const handleDragStart = (index: number) => {
    dragItem.current = index;
  };

  const handleDragEnter = (index: number) => {
    dragOverItem.current = index;
    setDragOverIndex(index);
  };

  const handleDragEnd = () => {
    if (dragItem.current !== null && dragOverItem.current !== null && dragItem.current !== dragOverItem.current) {
      reorderAgents(dragItem.current, dragOverItem.current);
    }
    dragItem.current = null;
    dragOverItem.current = null;
    setDragOverIndex(null);
  };

  const handleGenerate = async () => {
    if (!genContext.trim() || !genAxes.trim()) return;
    if (!llmSettings.model_name) {
      setGenError('Please configure an LLM provider and model in the Run panel first.');
      return;
    }
    setGenerating(true);
    setGenError('');
    setGeneratedPersonas([]);
    try {
      const result = await generatePersonas({
        context: genContext,
        diversity_axes: genAxes.split(',').map(a => a.trim()).filter(Boolean),
        num_personas: genCount,
        num_memories: genMemories,
        llm_settings: llmSettings,
      });
      setGeneratedPersonas(result.personas.map(p => ({ ...p, selected: true })));
    } catch (err: any) {
      setGenError(err?.response?.data?.detail || err?.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateCensus = async () => {
    if (!censusJson.trim()) return;
    setGenerating(true);
    setGenError('');
    setGeneratedPersonas([]);
    setCensusSummary(null);
    try {
      const parsed = await parseDistribution('json', censusJson);
      const result = await generatePersonasCensus({
        distribution: parsed,
        num_agents: censusCount,
        context: censusContext,
        enrich_with_llm: censusEnrich,
        num_memories: genMemories,
        seed: censusSeed ? parseInt(censusSeed) : null,
        llm_settings: censusEnrich ? llmSettings : undefined,
      });
      setGeneratedPersonas(result.personas.map(p => ({ ...p, selected: true })));
      setCensusSummary(result.distribution_summary);
    } catch (err: any) {
      setGenError(err?.response?.data?.detail || err?.message || 'Census generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleCsvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    if (file.name.endsWith('.csv')) {
      try {
        const parsed = await parseDistribution('csv', text);
        setCensusJson(JSON.stringify(parsed.dimensions || parsed.joint_profiles, null, 2));
      } catch (err: any) {
        setGenError('Failed to parse CSV: ' + (err?.response?.data?.detail || err?.message));
      }
    } else {
      setCensusJson(text);
    }
    e.target.value = '';
  };

  const handleAddGenerated = () => {
    const selected = generatedPersonas.filter(p => p.selected);
    selected.forEach((persona, i) => {
      addAgent({
        id: `agent-${Date.now()}-${i}`,
        name: persona.name,
        prefab: 'basic__Entity',
        goal: persona.goal || undefined,
        memories: persona.memories,
        randomize_choices: true,
      });
    });
    setShowGenerator(false);
    setGeneratedPersonas([]);
    setGenContext('');
    setGenAxes('');
  };

  const togglePersonaSelection = (index: number) => {
    setGeneratedPersonas(prev =>
      prev.map((p, i) => i === index ? { ...p, selected: !p.selected } : p)
    );
  };

  const memoryCount = (agent: typeof config.agents[0]) => agent.memories?.length || 0;
  const componentCount = (agent: typeof config.agents[0]) =>
    agent.components ? Object.keys(agent.components).length : 0;

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">
          Agents ({config.agents.length})
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowGenerator(true)}
            className="inline-flex items-center px-3 py-2 border border-green-300 text-sm leading-4 font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100"
          >
            <svg className="mr-1.5 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Generate
          </button>
          <button
            onClick={handleAddAgent}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Agent
          </button>
        </div>
      </div>

      {config.agents.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-md border-2 border-dashed border-gray-300">
          <p className="text-sm text-gray-500">No agents yet. Add your first agent to get started.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {config.agents.map((agent, index) => {
            const badge = getPrefabBadge(agent.prefab);
            const mCount = memoryCount(agent);
            const cCount = componentCount(agent);

            return (
              <div
                key={agent.id}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragEnter={() => handleDragEnter(index)}
                onDragEnd={handleDragEnd}
                onDragOver={(e) => e.preventDefault()}
                className={`flex items-center justify-between p-3 rounded-md transition-colors cursor-grab active:cursor-grabbing ${
                  dragOverIndex === index
                    ? 'bg-blue-50 border-2 border-blue-300 border-dashed'
                    : 'bg-gray-50 hover:bg-gray-100 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <svg className="w-4 h-4 text-gray-300 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="9" cy="5" r="1.5"/><circle cx="15" cy="5" r="1.5"/>
                    <circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/>
                    <circle cx="9" cy="19" r="1.5"/><circle cx="15" cy="19" r="1.5"/>
                  </svg>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900 truncate">{agent.name}</p>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${badge.color}`}>
                        {badge.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      {agent.goal && (
                        <p className="text-xs text-gray-500 truncate max-w-[200px]">
                          {agent.goal}
                        </p>
                      )}
                      {mCount > 0 && (
                        <span className="text-xs text-gray-400" title={`${mCount} memories`}>
                          {mCount} mem
                        </span>
                      )}
                      {cCount > 0 && (
                        <span className="text-xs text-gray-400" title={`${cCount} components`}>
                          {cCount} comp
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-1 flex-shrink-0">
                  <button
                    onClick={() => handleDuplicate(agent.id)}
                    className="text-gray-400 hover:text-gray-600 p-1.5 rounded"
                    title="Duplicate agent"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setEditingAgent(agent.id)}
                    className="text-blue-600 hover:text-blue-800 p-1.5 rounded text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => removeAgent(agent.id)}
                    className="text-red-500 hover:text-red-700 p-1.5 rounded"
                    title="Remove agent"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {editingAgent && (
        <AgentEditor
          agentId={editingAgent}
          onClose={() => setEditingAgent(null)}
        />
      )}

      {/* Persona Generator Modal */}
      {showGenerator && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[85vh] flex flex-col">
            <div className="px-6 py-4 border-b border-gray-200 flex-shrink-0">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                  <svg className="h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Generate Agent Personas
                </h3>
                <button onClick={() => { setShowGenerator(false); setGeneratedPersonas([]); setCensusSummary(null); }} className="text-gray-400 hover:text-gray-600">
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              {generatedPersonas.length === 0 && (
                <div className="flex gap-1 mt-3">
                  <button
                    onClick={() => setGenTab('llm')}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition ${
                      genTab === 'llm' ? 'bg-green-100 text-green-800' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    LLM Generation
                  </button>
                  <button
                    onClick={() => setGenTab('census')}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition ${
                      genTab === 'census' ? 'bg-green-100 text-green-800' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    Census / Distribution
                  </button>
                </div>
              )}
            </div>

            <div className="flex-1 overflow-y-auto px-6 py-4">
              {generatedPersonas.length === 0 && genTab === 'llm' ? (
                <div className="space-y-4">
                  <p className="text-xs text-gray-500">
                    Uses Concordia's persona generators to create diverse agent populations from a scenario description.
                  </p>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Scenario Context</label>
                    <textarea
                      rows={3}
                      className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                      value={genContext}
                      onChange={e => setGenContext(e.target.value)}
                      placeholder="A small coastal town debating a new fishing regulation that would limit daily catch quotas..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Diversity Axes (comma-separated)</label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                      value={genAxes}
                      onChange={e => setGenAxes(e.target.value)}
                      placeholder="age, occupation, stance on regulation, economic status"
                    />
                    <p className="text-xs text-gray-500 mt-1">Dimensions along which personas will differ.</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Number of Personas</label>
                      <input
                        type="number" min={1} max={20}
                        className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm"
                        value={genCount}
                        onChange={e => setGenCount(parseInt(e.target.value) || 5)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Memories per Persona</label>
                      <input
                        type="number" min={1} max={15}
                        className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm"
                        value={genMemories}
                        onChange={e => setGenMemories(parseInt(e.target.value) || 5)}
                      />
                    </div>
                  </div>
                  {genError && (
                    <div className="bg-red-50 border border-red-200 rounded-md p-3">
                      <p className="text-sm text-red-700">{genError}</p>
                    </div>
                  )}
                </div>
              ) : generatedPersonas.length === 0 && genTab === 'census' ? (
                <div className="space-y-4">
                  <p className="text-xs text-gray-500">
                    Sample agents from a demographic distribution. Upload a JSON/CSV or edit the distribution below.
                  </p>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="block text-sm font-medium text-gray-700">Distribution (JSON)</label>
                      <label className="text-xs text-blue-600 hover:text-blue-800 cursor-pointer">
                        Upload CSV/JSON
                        <input type="file" accept=".csv,.json" className="hidden" onChange={handleCsvUpload} />
                      </label>
                    </div>
                    <textarea
                      rows={6}
                      className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-xs font-mono focus:outline-none focus:ring-green-500 focus:border-green-500"
                      value={censusJson}
                      onChange={e => setCensusJson(e.target.value)}
                      placeholder='{"age": {"18-25": 0.3, "26-40": 0.4}, "income": {"low": 0.5, "high": 0.5}}'
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Marginals: {`{"dim": {"cat": prob}}`} or joint: {`[{"weight": 0.3, "dim": "val"}]`}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Scenario Context (optional)</label>
                    <textarea
                      rows={2}
                      className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                      value={censusContext}
                      onChange={e => setCensusContext(e.target.value)}
                      placeholder="A neighborhood in Macau undergoing urban development..."
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Number of Agents</label>
                      <input
                        type="number" min={1} max={100}
                        className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm"
                        value={censusCount}
                        onChange={e => setCensusCount(parseInt(e.target.value) || 10)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Seed (optional)</label>
                      <input
                        type="text"
                        className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm"
                        value={censusSeed}
                        onChange={e => setCensusSeed(e.target.value.replace(/\D/g, ''))}
                        placeholder="For reproducibility"
                      />
                    </div>
                  </div>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={censusEnrich}
                      onChange={e => setCensusEnrich(e.target.checked)}
                      className="h-4 w-4 text-green-600 rounded"
                    />
                    Enrich with LLM (generate natural-language memories)
                  </label>
                  {genError && (
                    <div className="bg-red-50 border border-red-200 rounded-md p-3">
                      <p className="text-sm text-red-700">{genError}</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  {censusSummary && (
                    <div className="bg-gray-50 rounded-md p-3 text-xs">
                      <p className="font-medium text-gray-700 mb-1">Distribution Summary</p>
                      <div className="flex flex-wrap gap-3">
                        {Object.entries(censusSummary).map(([dim, counts]) => (
                          <div key={dim}>
                            <span className="font-medium text-gray-600">{dim}:</span>{' '}
                            {Object.entries(counts).map(([cat, n]) => `${cat} (${n})`).join(', ')}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-700 font-medium">
                      Generated {generatedPersonas.length} personas
                      <span className="text-gray-500 font-normal ml-1">
                        ({generatedPersonas.filter(p => p.selected).length} selected)
                      </span>
                    </p>
                    <button
                      onClick={() => setGeneratedPersonas(prev => prev.map(p => ({ ...p, selected: !prev.every(pp => pp.selected) })))}
                      className="text-xs text-blue-600 hover:text-blue-800"
                    >
                      Toggle All
                    </button>
                  </div>
                  {generatedPersonas.map((persona, idx) => (
                    <div
                      key={idx}
                      onClick={() => togglePersonaSelection(idx)}
                      className={`p-3 rounded-md border-2 cursor-pointer transition ${
                        persona.selected
                          ? 'border-green-400 bg-green-50'
                          : 'border-gray-200 bg-white opacity-60'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <input
                          type="checkbox"
                          checked={persona.selected}
                          onChange={() => togglePersonaSelection(idx)}
                          className="mt-1 h-4 w-4 text-green-600 rounded"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-gray-900">{persona.name}</p>
                          {persona.goal && <p className="text-xs text-gray-600 mt-0.5">{persona.goal}</p>}
                          {persona.description && <p className="text-xs text-gray-500 mt-1 italic">{persona.description}</p>}
                          <p className="text-[11px] text-gray-400 mt-1">{persona.memories.length} memories</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="px-6 py-3 border-t border-gray-200 flex justify-end gap-3 flex-shrink-0">
              {generatedPersonas.length > 0 ? (
                <>
                  <button
                    onClick={() => { setGeneratedPersonas([]); setCensusSummary(null); }}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleAddGenerated}
                    disabled={!generatedPersonas.some(p => p.selected)}
                    className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Add {generatedPersonas.filter(p => p.selected).length} Agent{generatedPersonas.filter(p => p.selected).length !== 1 ? 's' : ''}
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => { setShowGenerator(false); setGeneratedPersonas([]); setCensusSummary(null); }}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  {genTab === 'llm' ? (
                    <button
                      onClick={handleGenerate}
                      disabled={generating || !genContext.trim() || !genAxes.trim()}
                      className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {generating ? 'Generating...' : 'Generate Personas'}
                    </button>
                  ) : (
                    <button
                      onClick={handleGenerateCensus}
                      disabled={generating || !censusJson.trim()}
                      className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {generating ? 'Sampling...' : `Sample ${censusCount} Agents`}
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
