/**
 * SimulationBuilder Component
 * Main UI for creating and configuring simulations
 */
import { useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import { validateConfig } from '../../utils/api';
import ScenarioConfig from './ScenarioConfig';
import AgentList from './AgentList';
import AvailableActionsEditor from './AvailableActionsEditor';
import GameMasterConfig from './GameMasterConfig';
import TemplatePicker from './TemplatePicker';
import PlayerContextEditor from './PlayerContextEditor';
import MemoryEditor from '../shared/MemoryEditor';
import JsonImportExport from '../shared/JsonImportExport';

export default function SimulationBuilder() {
  const { config, setConfig, setValidation } = useSimulation();

  useEffect(() => {
    const validate = async () => {
      if (!config.premise || config.agents.length === 0) {
        setValidation(null);
        return;
      }

      try {
        const result = await validateConfig(config);
        setValidation(result);
      } catch (err) {
        console.error('Validation error:', err);
      }
    };

    const timeoutId = setTimeout(validate, 500);
    return () => clearTimeout(timeoutId);
  }, [config, setValidation]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Simulation Builder</h2>
          <p className="mt-1 text-sm text-gray-500">
            Configure your agent-based simulation
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <TemplatePicker onLoadTemplate={setConfig} />
          <JsonImportExport />
        </div>
      </div>

      {/* Main Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Scenario & Agents */}
        <div className="lg:col-span-2 space-y-6">
          <ScenarioConfig />
          <AgentList />
          <AvailableActionsEditor />
        </div>

        {/* Right Column - Game Master & Memories */}
        <div className="space-y-6">
          <GameMasterConfig />
          <MemoryEditor />
          <PlayerContextEditor />
        </div>
      </div>
    </div>
  );
}
