/**
 * MemoryEditor Component
 * Edit shared memories for the simulation
 */
import { useSimulation } from '../../contexts/SimulationContext';

export default function MemoryEditor() {
  const { config, addSharedMemory, removeSharedMemory, updateSharedMemory } = useSimulation();

  const handleAddMemory = () => {
    addSharedMemory('New memory...');
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">Shared Memories</h3>
        <button
          onClick={handleAddMemory}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          + Add Memory
        </button>
      </div>

      {config.shared_memories.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">
          No shared memories. Add world knowledge here.
        </p>
      ) : (
        <div className="space-y-2">
          {config.shared_memories.map((memory, index) => (
            <div key={index} className="flex items-start space-x-2">
              <textarea
                rows={2}
                className="flex-1 text-sm border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={memory}
                onChange={(e) => updateSharedMemory(index, e.target.value)}
              />
              <button
                onClick={() => removeSharedMemory(index)}
                className="text-red-600 hover:text-red-800 mt-1"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
