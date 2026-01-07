/**
 * TimelineVisualization Component
 * Displays interactive timeline of simulation events
 */
import { useState, useEffect } from 'react';
import { getSimulationAnalytics } from '../../utils/api';

interface TimelineEvent {
  step: number;
  description: string;
  type: string;
}

interface AnalyticsData {
  filename: string;
  file_size: number;
  modified: number;
  total_steps: number;
  agents: string[];
  agent_actions: Record<string, number>;
  total_observations: number;
  interactions: any[];
  timeline: TimelineEvent[];
  word_count: number;
  character_count: number;
}

interface TimelineVisualizationProps {
  filename: string | null;
}

export default function TimelineVisualization({ filename }: TimelineVisualizationProps) {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);
  const [filter, setFilter] = useState<'all' | 'steps'>('all');

  useEffect(() => {
    if (filename) {
      loadAnalytics();
    } else {
      setAnalytics(null);
      setSelectedEvent(null);
    }
  }, [filename]);

  const loadAnalytics = async () => {
    if (!filename) return;

    setLoading(true);
    setError(null);
    try {
      const data = await getSimulationAnalytics(filename);
      setAnalytics(data);
    } catch (err: any) {
      console.error('Error loading timeline:', err);
      setError(err.message || 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  const getFilteredEvents = (): TimelineEvent[] => {
    if (!analytics) return [];

    if (filter === 'steps') {
      return analytics.timeline.filter(event => event.type === 'step');
    }

    return analytics.timeline;
  };

  if (!filename) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline Visualization</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            Load a simulation to see the event timeline
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline Visualization</h3>
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-3 text-sm text-gray-600">Loading timeline...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Timeline Visualization</h3>
          <button
            onClick={loadAnalytics}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Retry
          </button>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  const filteredEvents = getFilteredEvents();

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Timeline Visualization</h3>
        <div className="flex items-center gap-3">
          {/* Filter */}
          <select
            className="text-sm border border-gray-300 rounded-lg py-1.5 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'steps')}
          >
            <option value="all">All Events</option>
            <option value="steps">Steps Only</option>
          </select>

          <button
            onClick={loadAnalytics}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="p-5">
        {/* Stats Bar */}
        <div className="flex items-center gap-6 mb-6 pb-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span className="text-sm text-gray-600">
              {analytics.total_steps} Steps
            </span>
          </div>
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-gray-600">
              {filteredEvents.length} Events
            </span>
          </div>
        </div>

        {/* Timeline */}
        {filteredEvents.length === 0 ? (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="mt-4 text-sm text-gray-500">No timeline events found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredEvents.map((event, index) => (
              <div
                key={event.step}
                className={`relative pl-8 pb-3 ${
                  index !== filteredEvents.length - 1 ? 'border-l-2 border-gray-200' : ''
                }`}
              >
                {/* Timeline Dot */}
                <div className="absolute left-0 top-0 w-4 h-4 rounded-full border-2 border-blue-500 bg-white"></div>

                {/* Event Card */}
                <div
                  className={`bg-gray-50 rounded-lg p-4 cursor-pointer transition-all ${
                    selectedEvent?.step === event.step
                      ? 'ring-2 ring-blue-500 bg-blue-50'
                      : 'hover:bg-gray-100'
                  }`}
                  onClick={() => setSelectedEvent(selectedEvent?.step === event.step ? null : event)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          Step {event.step}
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 capitalize">
                          {event.type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 line-clamp-2">
                        {event.description}
                      </p>
                    </div>
                    <svg
                      className={`ml-2 h-5 w-5 text-gray-400 transition-transform ${
                        selectedEvent?.step === event.step ? 'transform rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>

                  {/* Expanded Details */}
                  {selectedEvent?.step === event.step && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-sm text-gray-600">
                        {event.description}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
