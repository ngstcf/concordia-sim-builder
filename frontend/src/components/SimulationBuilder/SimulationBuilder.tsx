/**
 * SimulationBuilder Component
 * Main UI for creating and configuring simulations
 */
import { useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import {
  validateConfig,
  getPeaceNegotiationTemplate,
  getCoffeeShopTemplate,
  getPlanningAgentTemplate,
  getScriptedEntityTemplate,
  getDialogicConversationTemplate,
  getStrategicGameTemplate,
  getInterviewerTemplate,
  getFormativeMemoriesTemplate,
  getMarketplaceTemplate,
  getStateFormationTemplate,
  getLaborActionTemplate,
  getFisheryManagementTemplate,
  getDisasterResponseTemplate,
  getInequalityMobilityTemplate,
  getContextAwareModeratorTemplate,
  getVaccineHesitancyTemplate,
  getNestedSimulationTemplate,
  getGroundedVariablesTemplate,
  getPhishingAttackSimulationTemplate,
  getUrbanGentrificationTemplate,
  getRationalNegotiatorsTemplate,
  getSocialMediaDiscourseTemplate,
  getPuppetWizardOfOzTemplate,
  getConversationalDebateTemplate,
  getSpaceshipCrisisTemplate,
  getSimultaneousAuctionTemplate,
} from '../../utils/api';
import ScenarioConfig from './ScenarioConfig';
import AgentList from './AgentList';
import GameMasterConfig from './GameMasterConfig';
import MemoryEditor from '../shared/MemoryEditor';
import JsonImportExport from '../shared/JsonImportExport';

// Template definitions
const TEMPLATES = [
  { id: 'coffee', name: 'Coffee Shop Demo', description: 'Quick 5-step demo', category: 'Basic' },
  { id: 'peace', name: 'Peace Negotiation', description: 'Russia-Ukraine talks (20 steps)', category: 'Basic' },
  { id: 'planning', name: 'Planning Agent', description: 'Strategic product launch', category: 'Prefab Types' },
  { id: 'scripted-entity', name: 'Scripted Entity', description: 'Focus group moderator (exact responses)', category: 'Prefab Types' },
  { id: 'context-aware-moderator', name: 'Context-Aware Moderator', description: 'Support group with adaptive responses', category: 'Prefab Types' },
  { id: 'vaccine-hesitancy', name: 'Vaccine Hesitancy Study', description: 'Psychological component research demo', category: 'Research' },
  { id: 'nested-simulation', name: 'Nested Simulation Demo', description: 'PhoneGameMaster pattern (mini-sims)', category: 'Advanced' },
  { id: 'grounded-variables', name: 'Grounded Variables Demo', description: 'Track metrics during simulation', category: 'Advanced' },
  { id: 'phishing-attack-simulation', name: 'Phishing Attack Simulation', description: 'Cybersecurity tabletop exercise', category: 'Research' },
  { id: 'urban-gentrification', name: 'Urban Gentrification', description: 'Housing policy & neighborhood change', category: 'Research' },
  { id: 'dialogic', name: 'Dialogic Conversation', description: 'Therapy session', category: 'Prefab Types' },
  { id: 'strategic', name: 'Strategic Game', description: 'Prisoner\'s Dilemma', category: 'Prefab Types' },
  { id: 'interviewer', name: 'Interviewer', description: 'Employee survey', category: 'Prefab Types' },
  { id: 'formative', name: 'Formative Memories', description: 'High school reunion', category: 'Prefab Types' },
  { id: 'marketplace', name: 'Marketplace', description: 'Farmers market trading', category: 'Prefab Types' },
  { id: 'rational-negotiators', name: 'Rational Negotiators', description: 'Budget negotiation (rational prefab)', category: 'New in v2.4' },
  { id: 'conversational-debate', name: 'Philosophy Roundtable', description: 'AI ethics debate (conversational prefab)', category: 'New in v2.4' },
  { id: 'social-media-discourse', name: 'Social Media Debate', description: 'Policy debate (async engine)', category: 'New in v2.4' },
  { id: 'simultaneous-auction', name: 'Sealed-Bid Auction', description: 'Art auction (simultaneous engine)', category: 'New in v2.4' },
  { id: 'puppet-wizard-of-oz', name: 'Wizard-of-Oz CS Training', description: 'Human-in-the-loop (puppet prefab)', category: 'New in v2.4' },
  { id: 'spaceship-crisis', name: 'Spaceship Crisis', description: 'Ship emergency (contrib GM)', category: 'New in v2.4' },
  { id: 'state-formation', name: 'State Formation', description: 'Building institutions (SDG 16)', category: 'SDG Scenarios' },
  { id: 'labor-action', name: 'Labor Strike', description: 'Collective bargaining (SDG 8)', category: 'SDG Scenarios' },
  { id: 'fishery-management', name: 'Fishery Management', description: 'Tragedy of commons (SDG 14)', category: 'SDG Scenarios' },
  { id: 'disaster-response', name: 'Flood Evacuation', description: 'Emergency response (SDG 11/13)', category: 'SDG Scenarios' },
  { id: 'inequality-mobility', name: 'Educational Opportunity', description: 'Social mobility (SDG 10)', category: 'SDG Scenarios' },
];

const TEMPLATE_LOADERS: Record<string, () => Promise<{ config: any }>> = {
  coffee: getCoffeeShopTemplate,
  peace: getPeaceNegotiationTemplate,
  planning: getPlanningAgentTemplate,
  'scripted-entity': getScriptedEntityTemplate,
  'context-aware-moderator': getContextAwareModeratorTemplate,
  'vaccine-hesitancy': getVaccineHesitancyTemplate,
  'nested-simulation': getNestedSimulationTemplate,
  'grounded-variables': getGroundedVariablesTemplate,
  'phishing-attack-simulation': getPhishingAttackSimulationTemplate,
  'urban-gentrification': getUrbanGentrificationTemplate,
  dialogic: getDialogicConversationTemplate,
  strategic: getStrategicGameTemplate,
  interviewer: getInterviewerTemplate,
  formative: getFormativeMemoriesTemplate,
  marketplace: getMarketplaceTemplate,
  'rational-negotiators': getRationalNegotiatorsTemplate,
  'conversational-debate': getConversationalDebateTemplate,
  'social-media-discourse': getSocialMediaDiscourseTemplate,
  'simultaneous-auction': getSimultaneousAuctionTemplate,
  'puppet-wizard-of-oz': getPuppetWizardOfOzTemplate,
  'spaceship-crisis': getSpaceshipCrisisTemplate,
  'state-formation': getStateFormationTemplate,
  'labor-action': getLaborActionTemplate,
  'fishery-management': getFisheryManagementTemplate,
  'disaster-response': getDisasterResponseTemplate,
  'inequality-mobility': getInequalityMobilityTemplate,
};

export default function SimulationBuilder() {
  const { config, setConfig, setValidation } = useSimulation();
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [loadingTemplate, setLoadingTemplate] = useState(false);

  // Auto-validate on config change - only when we have a premise and agents
  useEffect(() => {
    const validate = async () => {
      // Only validate if we have meaningful content
      if (!config.premise || config.agents.length === 0) {
        setValidation(null);
        return;
      }

      try {
        const result = await validateConfig(config);
        setValidation(result);
      } catch (err) {
        console.error('Validation error:', err);
        // Don't show validation errors on auto-validate - just log it
      }
    };

    const timeoutId = setTimeout(validate, 500);
    return () => clearTimeout(timeoutId);
  }, [config, setValidation]);

  const loadTemplate = async (templateId: string) => {
    if (!templateId) return;

    setLoadingTemplate(true);
    try {
      const loader = TEMPLATE_LOADERS[templateId];
      if (loader) {
        const template = await loader();
        setConfig(template.config);
      }
    } catch (err) {
      console.error('Failed to load template:', err);
    } finally {
      setLoadingTemplate(false);
      setSelectedTemplate('');
    }
  };

  // Group templates by category
  const basicTemplates = TEMPLATES.filter(t => t.category === 'Basic');
  const newTemplates = TEMPLATES.filter(t => t.category === 'New in v2.4');
  const prefabTemplates = TEMPLATES.filter(t => t.category === 'Prefab Types');
  const researchTemplates = TEMPLATES.filter(t => t.category === 'Research');
  const advancedTemplates = TEMPLATES.filter(t => t.category === 'Advanced');
  const sdgTemplates = TEMPLATES.filter(t => t.category === 'SDG Scenarios');

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
          {/* Template Dropdown */}
          <div className="flex items-center space-x-2">
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              disabled={loadingTemplate}
              className="block w-64 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md border bg-white"
            >
              <option value="">Load a template...</option>
              <optgroup label="Basic Templates">
                {basicTemplates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} - {t.description}
                  </option>
                ))}
              </optgroup>
              <optgroup label="New in v2.4 (Engines & Prefabs)">
                {newTemplates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} - {t.description}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Prefab Type Examples">
                {prefabTemplates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} - {t.description}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Research Studies">
                {researchTemplates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} - {t.description}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Advanced Features">
                {advancedTemplates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} - {t.description}
                  </option>
                ))}
              </optgroup>
              <optgroup label="SDG Scenarios">
                {sdgTemplates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} - {t.description}
                  </option>
                ))}
              </optgroup>
            </select>
            {selectedTemplate && (
              <button
                onClick={() => loadTemplate(selectedTemplate)}
                disabled={loadingTemplate}
                className="px-4 py-2 border border-blue-300 rounded-md shadow-sm text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loadingTemplate ? 'Loading...' : 'Load'}
              </button>
            )}
          </div>
          <JsonImportExport />
        </div>
      </div>

      {/* Main Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Scenario & Agents */}
        <div className="lg:col-span-2 space-y-6">
          {/* Scenario Configuration */}
          <ScenarioConfig />

          {/* Agents */}
          <AgentList />
        </div>

        {/* Right Column - Game Master & Memories */}
        <div className="space-y-6">
          {/* Game Master Configuration */}
          <GameMasterConfig />

          {/* Shared Memories */}
          <MemoryEditor />
        </div>
      </div>
    </div>
  );
}
