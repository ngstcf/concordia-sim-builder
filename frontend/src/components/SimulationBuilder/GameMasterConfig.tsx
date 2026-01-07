/**
 * GameMasterConfig Component
 * Configure the game master
 */
import { useSimulation } from '../../contexts/SimulationContext';

export default function GameMasterConfig() {
  const { config, setGameMaster } = useSimulation();

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Game Master</h3>

      <div className="space-y-4">
        {/* Name */}
        <div>
          <label htmlFor="gm-name" className="block text-sm font-medium text-gray-700">
            Name
          </label>
          <input
            type="text"
            id="gm-name"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={config.game_master.name}
            onChange={(e) => setGameMaster({ ...config.game_master, name: e.target.value })}
          />
        </div>

        {/* Prefab */}
        <div>
          <label htmlFor="gm-prefab" className="block text-sm font-medium text-gray-700">
            Prefab Type
          </label>
          <select
            id="gm-prefab"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            value={config.game_master.prefab}
            onChange={(e) => setGameMaster({ ...config.game_master, prefab: e.target.value })}
          >
            <option value="generic__GameMaster">Generic (Narrative)</option>
            <option value="dialogic__GameMaster">Dialogic (Conversation)</option>
            <option value="game_theoretic_and_dramaturgic__GameMaster">Game-Theoretic</option>
            <option value="interviewer__GameMaster">Interviewer</option>
          </select>
        </div>

        {/* Acting Order */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Acting Order
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="acting_order"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                checked={config.game_master.acting_order === 'game_master_choice'}
                onChange={() => setGameMaster({ ...config.game_master, acting_order: 'game_master_choice' as any })}
              />
              <span className="ml-2 text-sm text-gray-700">Game Master Choice</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="acting_order"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                checked={config.game_master.acting_order === 'fixed'}
                onChange={() => setGameMaster({ ...config.game_master, acting_order: 'fixed' as any })}
              />
              <span className="ml-2 text-sm text-gray-700">Fixed Order</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="acting_order"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                checked={config.game_master.acting_order === 'random'}
                onChange={() => setGameMaster({ ...config.game_master, acting_order: 'random' as any })}
              />
              <span className="ml-2 text-sm text-gray-700">Random</span>
            </label>
          </div>
        </div>

        {/* Parameters (JSON) */}
        <div>
          <label htmlFor="gm-parameters" className="block text-sm font-medium text-gray-700">
            Parameters (JSON) - Optional
          </label>
          <p className="mt-1 text-xs text-gray-500">
            Advanced configuration (e.g., scene settings for game-theoretic games).{' '}
            <span className="text-amber-600 font-medium">
              Note: For game-theoretic games, num_rounds must equal max_steps (not multiplied).
            </span>
          </p>
          <textarea
            id="gm-parameters"
            rows={8}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono text-xs"
            value={config.game_master.parameters ? JSON.stringify(config.game_master.parameters, null, 2) : ''}
            onChange={(e) => {
              try {
                const params = e.target.value ? JSON.parse(e.target.value) : {};
                setGameMaster({ ...config.game_master, parameters: params });
              } catch (err) {
                // Invalid JSON - don't update
                console.error('Invalid JSON:', err);
              }
            }}
            placeholder='{"scenes": [{"scene_type": {"name": "decision", "game_master_name": "GM Name", "action_spec": {"call_to_action": "What does {name} do?", "options": ["COOPERATE", "DEFECT"]}}, "participants": ["Agent1", "Agent2"], "num_rounds": 4}]}'
          />
        </div>
      </div>
    </div>
  );
}
