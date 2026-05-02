import { useState, useMemo } from 'react';
import {
  TEMPLATES,
  TEMPLATE_LOADERS,
  TAG_COLORS,
  TAG_LABELS,
  CATEGORY_COLORS,
  ALL_CATEGORIES,
  FEATURE_TAGS,
  ENGINE_TAGS,
} from './templateMetadata';
import type { TemplateMetadata, TemplateCategory } from './templateMetadata';

interface TemplatePickerProps {
  onLoadTemplate: (config: any) => void;
}

export default function TemplatePicker({ onLoadTemplate }: TemplatePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [activeTagFilters, setActiveTagFilters] = useState<Set<string>>(new Set());
  const [activeCategoryFilters, setActiveCategoryFilters] = useState<Set<TemplateCategory>>(new Set());
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateMetadata | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'agents' | 'steps'>('name');

  const filtered = useMemo(() => {
    let result = TEMPLATES;

    if (search) {
      const q = search.toLowerCase();
      result = result.filter(t =>
        t.name.toLowerCase().includes(q) ||
        t.description.toLowerCase().includes(q) ||
        t.tags.some(tag => TAG_LABELS[tag]?.toLowerCase().includes(q))
      );
    }

    if (activeTagFilters.size > 0) {
      result = result.filter(t =>
        Array.from(activeTagFilters).every(tag => t.tags.includes(tag))
      );
    }

    if (activeCategoryFilters.size > 0) {
      result = result.filter(t => activeCategoryFilters.has(t.category as TemplateCategory));
    }

    if (sortBy === 'agents') {
      result = [...result].sort((a, b) => a.agentCount - b.agentCount);
    } else if (sortBy === 'steps') {
      result = [...result].sort((a, b) => a.stepCount - b.stepCount);
    } else {
      result = [...result].sort((a, b) => a.name.localeCompare(b.name));
    }

    return result;
  }, [search, activeTagFilters, activeCategoryFilters, sortBy]);

  const toggleTag = (tag: string) => {
    setActiveTagFilters(prev => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });
  };

  const toggleCategory = (cat: TemplateCategory) => {
    setActiveCategoryFilters(prev => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  const handleLoad = async (template: TemplateMetadata) => {
    const loader = TEMPLATE_LOADERS[template.id];
    if (!loader) return;
    setLoading(true);
    setLoadError('');
    try {
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Request timed out. Is the backend server running?')), 10000)
      );
      const result = await Promise.race([loader(), timeoutPromise]) as { config: any };
      onLoadTemplate(result.config);
      setIsOpen(false);
      setSelectedTemplate(null);
      setSearch('');
      setActiveTagFilters(new Set());
      setActiveCategoryFilters(new Set());
    } catch (err: any) {
      const message = err?.message || 'Failed to load template';
      setLoadError(message.includes('Network Error') ? 'Backend server is not running. Start it with: python main.py' : message);
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setSearch('');
    setActiveTagFilters(new Set());
    setActiveCategoryFilters(new Set());
  };

  const hasFilters = search || activeTagFilters.size > 0 || activeCategoryFilters.size > 0;

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="px-4 py-2 border border-blue-300 rounded-md shadow-sm text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 flex items-center gap-2"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
        Browse Templates
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Simulation Templates</h3>
            <button onClick={() => { setIsOpen(false); setSelectedTemplate(null); }} className="text-gray-400 hover:text-gray-600">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Search */}
          <div className="mt-3 relative">
            <svg className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search templates by name, description, or feature..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              autoFocus
            />
          </div>

          {/* Filters */}
          <div className="mt-3 space-y-2">
            {/* Categories */}
            <div className="flex flex-wrap gap-1.5">
              <span className="text-xs text-gray-500 self-center mr-1">Category:</span>
              {ALL_CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => toggleCategory(cat)}
                  className={`text-xs px-2.5 py-1 rounded-full transition font-medium ${
                    activeCategoryFilters.has(cat)
                      ? CATEGORY_COLORS[cat] + ' ring-2 ring-offset-1 ring-gray-400'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Feature tags */}
            <div className="flex flex-wrap gap-1.5">
              <span className="text-xs text-gray-500 self-center mr-1">Features:</span>
              {FEATURE_TAGS.map(tag => {
                const colors = TAG_COLORS[tag];
                return (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={`text-xs px-2.5 py-1 rounded-full transition font-medium ${
                      activeTagFilters.has(tag)
                        ? `${colors.bg} ${colors.text} ring-2 ring-offset-1 ring-gray-400`
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {TAG_LABELS[tag]}
                  </button>
                );
              })}
            </div>

            {/* Engine tags */}
            <div className="flex flex-wrap gap-1.5 items-center">
              <span className="text-xs text-gray-500 self-center mr-1">Engine:</span>
              {ENGINE_TAGS.map(tag => {
                const colors = TAG_COLORS[tag];
                return (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={`text-xs px-2.5 py-1 rounded-full transition font-medium ${
                      activeTagFilters.has(tag)
                        ? `${colors.bg} ${colors.text} ring-2 ring-offset-1 ring-gray-400`
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {TAG_LABELS[tag]}
                  </button>
                );
              })}

              <div className="ml-auto flex items-center gap-2">
                {hasFilters && (
                  <button onClick={clearFilters} className="text-xs text-gray-500 hover:text-gray-700 underline">
                    Clear filters
                  </button>
                )}
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value as any)}
                  className="text-xs border border-gray-200 rounded px-2 py-1"
                >
                  <option value="name">Sort: A-Z</option>
                  <option value="agents">Sort: Agents</option>
                  <option value="steps">Sort: Steps</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-4">
          {filtered.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-sm">No templates match your filters.</p>
              <button onClick={clearFilters} className="mt-2 text-sm text-blue-600 hover:text-blue-800 underline">
                Clear all filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {filtered.map(template => (
                <button
                  key={template.id}
                  onClick={() => setSelectedTemplate(
                    selectedTemplate?.id === template.id ? null : template
                  )}
                  className={`text-left p-4 rounded-lg border-2 transition hover:shadow-md ${
                    selectedTemplate?.id === template.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  {/* Card header */}
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <h4 className="text-sm font-semibold text-gray-900 leading-tight">{template.name}</h4>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full whitespace-nowrap flex-shrink-0 ${CATEGORY_COLORS[template.category]}`}>
                      {template.category}
                    </span>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-gray-600 mb-2 line-clamp-2">{template.description}</p>

                  {/* Meta row */}
                  <div className="flex items-center gap-3 text-[11px] text-gray-500 mb-2">
                    <span title="Number of agents">{template.agentCount} agent{template.agentCount !== 1 ? 's' : ''}</span>
                    <span title="Max steps">{template.stepCount} steps</span>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1">
                    {template.tags
                      .filter(t => t !== 'sequential')
                      .map(tag => {
                        const colors = TAG_COLORS[tag] || { bg: 'bg-gray-100', text: 'text-gray-600' };
                        return (
                          <span key={tag} className={`text-[10px] px-1.5 py-0.5 rounded-full ${colors.bg} ${colors.text}`}>
                            {TAG_LABELS[tag] || tag}
                          </span>
                        );
                      })}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer with preview/load */}
        <div className="border-t border-gray-200 px-6 py-3 flex-shrink-0">
          {loadError && (
          <div className="mb-2 bg-red-50 border border-red-200 rounded-md px-3 py-2">
            <p className="text-sm text-red-700">{loadError}</p>
          </div>
        )}
        {selectedTemplate ? (
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0 mr-4">
                <p className="text-sm font-medium text-gray-900 truncate">{selectedTemplate.name}</p>
                <p className="text-xs text-gray-500">
                  {selectedTemplate.agentCount} agents, {selectedTemplate.stepCount} steps, {selectedTemplate.engineType} engine, GM: {selectedTemplate.gmPrefab.replace('__GameMaster', '')}
                </p>
              </div>
              <button
                onClick={() => handleLoad(selectedTemplate)}
                disabled={loading}
                className="px-5 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {loading ? 'Loading...' : 'Load Template'}
              </button>
            </div>
          ) : (
            <p className="text-sm text-gray-500 text-center">
              Select a template to preview, then click Load Template.
              <span className="ml-2 text-gray-400">{filtered.length} of {TEMPLATES.length} shown</span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
