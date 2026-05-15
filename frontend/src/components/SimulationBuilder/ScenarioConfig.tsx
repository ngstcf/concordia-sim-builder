/**
 * ScenarioConfig Component
 * Configure the basic simulation scenario
 */
import { useSimulation } from '../../contexts/SimulationContext';

export default function ScenarioConfig() {
  const { config, setConfig } = useSimulation();
  const clock = config.clock || { clock_type: 'fixed_increment' as const, increment_minutes: 15 };

  const variableRulesText = (() => {
    if (!clock.variable_increment_rules) return '';
    return Object.entries(clock.variable_increment_rules)
      .map(([h, m]) => `${h}:${m}`)
      .join(', ');
  })();

  const updateClock = (updates: Record<string, any>) => {
    setConfig({
      ...config,
      clock: {
        ...clock,
        ...updates,
      },
    });
  };

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
            onChange={(e) => {
              const newSteps = parseInt(e.target.value) || 10;
              const oldSteps = config.max_steps;
              const scenes = config.game_master.parameters?.scenes;
              if (scenes && Array.isArray(scenes) && scenes.length > 0) {
                const updatedScenes = scenes.map((s: any) => {
                  const updated = { ...s };
                  if (scenes.length === 1) {
                    updated.num_rounds = newSteps;
                  } else if (s.num_rounds === oldSteps || (s.num_rounds && s.num_rounds > newSteps)) {
                    updated.num_rounds = Math.max(1, Math.round(s.num_rounds * newSteps / oldSteps));
                  }
                  if (updated.scene_type?.action_spec?.call_to_action) {
                    updated.scene_type = {
                      ...updated.scene_type,
                      action_spec: {
                        ...updated.scene_type.action_spec,
                        call_to_action: updated.scene_type.action_spec.call_to_action.replace(
                          /\b\d+\s+rounds?\b/gi,
                          `${updated.num_rounds} rounds`
                        ),
                      },
                    };
                  }
                  return updated;
                });
                setConfig({
                  ...config,
                  max_steps: newSteps,
                  game_master: {
                    ...config.game_master,
                    parameters: { ...config.game_master.parameters, scenes: updatedScenes },
                  },
                });
              } else {
                setConfig({ ...config, max_steps: newSteps });
              }
            }}
          />
        </div>

        {/* Checkpoint Interval */}
        <div>
          <label htmlFor="checkpoint_interval" className="block text-sm font-medium text-gray-700">
            Checkpoint Interval
          </label>
          <input
            type="number"
            id="checkpoint_interval"
            min={1}
            max={100}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={config.checkpoint_interval ?? 5}
            onChange={(e) => setConfig({ ...config, checkpoint_interval: parseInt(e.target.value) || 5 })}
          />
          <p className="mt-1 text-xs text-gray-500">
            Save partial results every N steps. Checkpoints are saved to the logs folder for recovery.
          </p>
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
            <option value="step_controller">Step Controller (Manual control)</option>
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

        {/* Clock Type */}
        <div>
          <label htmlFor="clock_type" className="block text-sm font-medium text-gray-700">
            Clock Type
          </label>
          <select
            id="clock_type"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            value={clock.clock_type}
            onChange={(e) => {
              const clockType = e.target.value as 'fixed_increment' | 'multi_interval' | 'generative';
              const nextClock: any = {
                ...clock,
                clock_type: clockType,
              };
              if (clockType === 'generative') {
                delete nextClock.variable_increment_rules;
              }
              setConfig({ ...config, clock: nextClock });
            }}
          >
            <option value="fixed_increment">FixedIncrementClock (fixed time step)</option>
            <option value="multi_interval">MultiIntervalClock (variable intervals)</option>
            <option value="generative">GenerativeClock (LLM-managed clock)</option>
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {{
              fixed_increment: 'Every step advances simulation time by a fixed number of minutes.',
              multi_interval: 'Time increment varies by hour-based rules (e.g., daytime vs nighttime cadence).',
              generative: 'The Game Master LLM determines how time advances from narrative context.',
            }[clock.clock_type] || 'Select a clock type'}
          </p>
        </div>

        {/* Clock Start Time */}
        <div>
          <label htmlFor="clock_start_time" className="block text-sm font-medium text-gray-700">
            Clock Start Time
          </label>
          <input
            type="text"
            id="clock_start_time"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={clock.start_time || ''}
            placeholder="Tuesday, March 3, 2026 at 8:30 AM"
            onChange={(e) => updateClock({ start_time: e.target.value })}
          />
        </div>

        {/* Fixed / Multi increment minutes */}
        {(clock.clock_type === 'fixed_increment' || clock.clock_type === 'multi_interval') && (
          <div>
            <label htmlFor="clock_increment_minutes" className="block text-sm font-medium text-gray-700">
              Base Increment (minutes)
            </label>
            <input
              type="number"
              id="clock_increment_minutes"
              min={1}
              max={1440}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              value={clock.increment_minutes ?? 15}
              onChange={(e) => updateClock({ increment_minutes: parseInt(e.target.value, 10) || 15 })}
            />
          </div>
        )}

        {/* Multi interval rules */}
        {clock.clock_type === 'multi_interval' && (
          <div>
            <label htmlFor="clock_variable_rules" className="block text-sm font-medium text-gray-700">
              Variable Increment Rules
            </label>
            <input
              type="text"
              id="clock_variable_rules"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              value={variableRulesText}
              placeholder="0:180, 8:15, 20:30, 23:45"
              onChange={(e) => {
                const parsed: Record<number, number> = {};
                const input = e.target.value.trim();
                if (input.length > 0) {
                  for (const segment of input.split(',')) {
                    const [hourRaw, minutesRaw] = segment.split(':').map((s) => s.trim());
                    const hour = Number(hourRaw);
                    const minutes = Number(minutesRaw);
                    if (
                      Number.isInteger(hour) &&
                      Number.isInteger(minutes) &&
                      hour >= 0 &&
                      hour <= 23 &&
                      minutes > 0
                    ) {
                      parsed[hour] = minutes;
                    }
                  }
                }
                updateClock({ variable_increment_rules: Object.keys(parsed).length > 0 ? parsed : undefined });
              }}
            />
            <p className="mt-1 text-xs text-gray-500">
              Format: `hour:minutes` pairs separated by commas. Example: `0:180, 8:15, 20:30, 23:45`.
            </p>
          </div>
        )}

        {/* Generative clock description */}
        {clock.clock_type === 'generative' && (
          <div>
            <label htmlFor="clock_description" className="block text-sm font-medium text-gray-700">
              Clock Description
            </label>
            <textarea
              id="clock_description"
              rows={3}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              value={clock.clock_description || ''}
              placeholder="Describe how time should progress in this world."
              onChange={(e) => updateClock({ clock_description: e.target.value })}
            />
          </div>
        )}
      </div>
    </div>
  );
}
