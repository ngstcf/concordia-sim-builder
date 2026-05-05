/**
 * JsonImportExport Component
 * Save, load, import, and export simulation configurations
 */
import { useRef, useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import {
  listSavedConfigs,
  saveConfig,
  loadSavedConfig,
  deleteSavedConfig,
} from '../../utils/api';
import type { SavedConfigSummary } from '../../utils/api';
import type { SimulationConfig, LLMSettings } from '../../types/simulation';

interface ExportedConfig {
  config: SimulationConfig;
  llm_settings: LLMSettings;
  gm_llm_settings?: LLMSettings | null;
}

function isValidConfig(data: unknown): data is ExportedConfig {
  if (typeof data !== 'object' || data === null) return false;
  const obj = data as Record<string, unknown>;

  if (typeof obj.config !== 'object' || obj.config === null) return false;
  const cfg = obj.config as Record<string, unknown>;
  if (typeof cfg.premise !== 'string') return false;
  if (!Array.isArray(cfg.agents)) return false;
  if (typeof cfg.game_master !== 'object' || cfg.game_master === null) return false;

  if (typeof obj.llm_settings !== 'object' || obj.llm_settings === null) return false;
  const llm = obj.llm_settings as Record<string, unknown>;
  if (typeof llm.provider !== 'string') return false;
  if (typeof llm.model_name !== 'string') return false;

  return true;
}

function isLegacyConfig(data: unknown): data is SimulationConfig {
  if (typeof data !== 'object' || data === null) return false;
  const obj = data as Record<string, unknown>;
  return typeof obj.premise === 'string' && Array.isArray(obj.agents) && typeof obj.game_master === 'object';
}

export default function JsonImportExport() {
  const { config, setConfig, llmSettings, setLLMSettings, gmLlmSettings, setGmLlmSettings } = useSimulation();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showSaved, setShowSaved] = useState(false);
  const [savedConfigs, setSavedConfigs] = useState<SavedConfigSummary[]>([]);
  const [saving, setSaving] = useState(false);
  const [loadingSlug, setLoadingSlug] = useState<string | null>(null);
  const [lastLoadedName, setLastLoadedName] = useState<string | null>(null);

  useEffect(() => {
    if (showSaved) {
      listSavedConfigs().then(setSavedConfigs).catch(() => {});
    }
  }, [showSaved]);

  const handleSave = async () => {
    const name = prompt('Configuration name:', lastLoadedName || '');
    if (!name?.trim()) return;

    setSaving(true);
    try {
      await saveConfig({
        name: name.trim(),
        config,
        llm_settings: llmSettings,
        gm_llm_settings: gmLlmSettings,
      });
      setLastLoadedName(name.trim());
      if (showSaved) {
        const updated = await listSavedConfigs();
        setSavedConfigs(updated);
      }
    } catch {
      alert('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleLoad = async (slug: string) => {
    setLoadingSlug(slug);
    try {
      const data = await loadSavedConfig(slug);
      setConfig(data.config);
      if (data.llm_settings) {
        setLLMSettings(data.llm_settings);
      }
      setGmLlmSettings(data.gm_llm_settings ?? null);
      setLastLoadedName(data.name);
      setShowSaved(false);
    } catch {
      alert('Failed to load configuration');
    } finally {
      setLoadingSlug(null);
    }
  };

  const handleDelete = async (slug: string, name: string) => {
    if (!confirm(`Delete "${name}"?`)) return;
    try {
      await deleteSavedConfig(slug);
      setSavedConfigs(prev => prev.filter(c => c.slug !== slug));
    } catch {
      alert('Failed to delete configuration');
    }
  };

  const handleExport = () => {
    const exported: ExportedConfig = {
      config,
      llm_settings: llmSettings,
    };
    if (gmLlmSettings) {
      exported.gm_llm_settings = gmLlmSettings;
    }
    const dataStr = JSON.stringify(exported, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `simulation-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);

        if (isValidConfig(data)) {
          setConfig(data.config);
          setLLMSettings(data.llm_settings);
          setGmLlmSettings(data.gm_llm_settings ?? null);
        } else if (isLegacyConfig(data)) {
          setConfig(data);
        } else {
          alert('Invalid configuration file. Expected a simulation config with premise, agents, and game_master.');
        }
      } catch {
        alert('Invalid JSON file');
      }
    };
    reader.readAsText(file);

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <>
      <div className="relative inline-block text-left">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-4 py-2 border border-green-300 rounded-md shadow-sm text-sm font-medium text-green-700 bg-green-50 hover:bg-green-100 disabled:opacity-50 mr-2"
        >
          {saving ? 'Saving...' : 'Save'}
        </button>
        <button
          onClick={() => setShowSaved(true)}
          className="px-4 py-2 border border-blue-300 rounded-md shadow-sm text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 mr-2"
        >
          My Configs
        </button>
        <button
          onClick={handleExport}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 mr-2"
        >
          Export
        </button>
        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Import
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          className="hidden"
          onChange={handleImport}
        />
      </div>

      {/* Saved Configurations Modal */}
      {showSaved && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[70vh] flex flex-col">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
              <h3 className="text-lg font-medium text-gray-900">My Configurations</h3>
              <button onClick={() => setShowSaved(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {savedConfigs.length === 0 ? (
                <p className="text-center text-gray-500 py-8 text-sm">
                  No saved configurations yet. Use the Save button to save your current setup.
                </p>
              ) : (
                <div className="space-y-2">
                  {savedConfigs.map(cfg => (
                    <div
                      key={cfg.slug}
                      className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex-1 min-w-0 mr-3">
                        <p className="text-sm font-medium text-gray-900 truncate">{cfg.name}</p>
                        <p className="text-xs text-gray-500">
                          {cfg.agent_count} agent{cfg.agent_count !== 1 ? 's' : ''}
                          {' · '}
                          {cfg.engine_type}
                          {cfg.saved_at && (
                            <> {' · '} {cfg.saved_at.replace('T', ' ')}</>
                          )}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          onClick={() => handleLoad(cfg.slug)}
                          disabled={loadingSlug === cfg.slug}
                          className="px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50"
                        >
                          {loadingSlug === cfg.slug ? 'Loading...' : 'Load'}
                        </button>
                        <button
                          onClick={() => handleDelete(cfg.slug, cfg.name)}
                          className="px-2 py-1.5 text-xs text-red-600 hover:text-red-800 hover:bg-red-50 rounded"
                          title="Delete"
                        >
                          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="border-t border-gray-200 px-6 py-3 flex-shrink-0">
              <p className="text-xs text-gray-500 text-center">
                Saved configurations include scenario setup and LLM settings.
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
