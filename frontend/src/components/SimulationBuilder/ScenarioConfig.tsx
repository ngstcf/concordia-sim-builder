/**
 * ScenarioConfig Component
 * Configure the basic simulation scenario
 */
import { useSimulation } from '../../contexts/SimulationContext';

export default function ScenarioConfig() {
  const { config, setConfig } = useSimulation();

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Scenario Configuration</h3>

      <div className="space-y-4">
        {/* Premise */}
        <div>
          <label htmlFor="premise" className="block text-sm font-medium text-gray-700">
            Premise <span className="text-red-500">*</span>
          </label>
          <textarea
            id="premise"
            rows={4}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="Describe the initial scenario..."
            value={config.premise}
            onChange={(e) => setConfig({ ...config, premise: e.target.value })}
          />
          <p className="mt-1 text-xs text-gray-500">
            The initial scenario description that sets up your simulation
          </p>
        </div>

        {/* Max Steps */}
        <div>
          <label htmlFor="max_steps" className="block text-sm font-medium text-gray-700">
            Max Steps
          </label>
          <input
            type="number"
            id="max_steps"
            min={1}
            max={1000}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={config.max_steps}
            onChange={(e) => setConfig({ ...config, max_steps: parseInt(e.target.value) || 10 })}
          />
        </div>

        {/* Engine Type */}
        <div>
          <label htmlFor="engine_type" className="block text-sm font-medium text-gray-700">
            Engine Type
          </label>
          <select
            id="engine_type"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            value={config.engine_type}
            onChange={(e) => setConfig({ ...config, engine_type: e.target.value as any })}
          >
            <option value="sequential">Sequential (Turn-based)</option>
            <option value="simultaneous">Simultaneous (All at once)</option>
            <option value="asynchronous">Asynchronous (Parallel with ordering)</option>
            <option value="interview">Interview (Q&A)</option>
            <option value="survey">Survey (No memory updates)</option>
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {{
              sequential: 'Agents take turns one at a time. Best for dialogue and negotiations.',
              simultaneous: 'All agents act at once. Best for voting, auctions, and coordination games.',
              asynchronous: 'Agents act in parallel with ordering constraints. Best for social media simulations.',
              step_controller: 'Manual control: pause, play, step-by-step. Best for research and debugging.',
              interview: 'Q&A format with interviewer and respondents.',
              survey: 'Like interview but without memory updates between questions.',
            }[config.engine_type] || 'Select an engine type'}
          </p>
        </div>
      </div>
    </div>
  );
}
