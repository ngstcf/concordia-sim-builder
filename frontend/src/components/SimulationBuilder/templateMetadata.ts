import {
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

export interface TemplateMetadata {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  agentCount: number;
  stepCount: number;
  engineType: string;
  gmPrefab: string;
}

export type TemplateCategory = 'Basic' | 'Prefab Types' | 'Research' | 'Advanced' | 'New in v2.4' | 'SDG Scenarios';

export const TAG_COLORS: Record<string, { bg: string; text: string }> = {
  sequential:       { bg: 'bg-gray-100',    text: 'text-gray-700' },
  simultaneous:     { bg: 'bg-blue-100',    text: 'text-blue-700' },
  async:            { bg: 'bg-purple-100',  text: 'text-purple-700' },
  interview:        { bg: 'bg-teal-100',    text: 'text-teal-700' },
  components:       { bg: 'bg-green-100',   text: 'text-green-700' },
  'grounded-vars':  { bg: 'bg-orange-100',  text: 'text-orange-700' },
  'player-context': { bg: 'bg-rose-100',    text: 'text-rose-700' },
  'nested-sim':     { bg: 'bg-violet-100',  text: 'text-violet-700' },
  scenes:           { bg: 'bg-indigo-100',  text: 'text-indigo-700' },
  scripted:         { bg: 'bg-amber-100',   text: 'text-amber-700' },
  'game-theory':    { bg: 'bg-red-100',     text: 'text-red-700' },
  questionnaire:    { bg: 'bg-cyan-100',    text: 'text-cyan-700' },
  'critical-decisions': { bg: 'bg-pink-100', text: 'text-pink-700' },
  sdg:              { bg: 'bg-emerald-100', text: 'text-emerald-700' },
};

export const TAG_LABELS: Record<string, string> = {
  sequential:       'Sequential',
  simultaneous:     'Simultaneous',
  async:            'Async',
  interview:        'Interview',
  components:       'Components',
  'grounded-vars':  'Grounded Vars',
  'player-context': 'Player Context',
  'nested-sim':     'Nested Sim',
  scenes:           'Scenes',
  scripted:         'Scripted',
  'game-theory':    'Game Theory',
  questionnaire:    'Questionnaire',
  'critical-decisions': 'Critical Decisions',
  sdg:              'SDG',
};

export const CATEGORY_COLORS: Record<string, string> = {
  'Basic':          'bg-gray-200 text-gray-800',
  'Prefab Types':   'bg-blue-200 text-blue-800',
  'Research':       'bg-purple-200 text-purple-800',
  'Advanced':       'bg-amber-200 text-amber-800',
  'New in v2.4':    'bg-emerald-200 text-emerald-800',
  'SDG Scenarios':  'bg-teal-200 text-teal-800',
};

export const TEMPLATES: TemplateMetadata[] = [
  { id: 'coffee', name: 'Coffee Shop Demo', description: 'Quick 5-step demo with two agents chatting', category: 'Basic', tags: ['sequential'], agentCount: 2, stepCount: 5, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'peace', name: 'Peace Negotiation', description: 'Russia-Ukraine diplomatic talks with mediator', category: 'Basic', tags: ['sequential', 'components', 'player-context'], agentCount: 2, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'planning', name: 'Planning Agent', description: 'Strategic product launch with planning prefab', category: 'Prefab Types', tags: ['sequential', 'components', 'player-context'], agentCount: 3, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'scripted-entity', name: 'Scripted Entity', description: 'Focus group moderator with exact scripted responses', category: 'Prefab Types', tags: ['sequential', 'components', 'scripted'], agentCount: 5, stepCount: 10, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'context-aware-moderator', name: 'Context-Aware Moderator', description: 'Support group with context-adaptive scripted responses', category: 'Prefab Types', tags: ['sequential', 'components', 'scripted', 'player-context'], agentCount: 4, stepCount: 12, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'vaccine-hesitancy', name: 'Vaccine Hesitancy Study', description: 'Psychological components research with Big Five traits and cognitive biases', category: 'Research', tags: ['sequential', 'components', 'player-context'], agentCount: 5, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'nested-simulation', name: 'Nested Simulation Demo', description: 'Agents run mini-simulations to plan ahead', category: 'Advanced', tags: ['sequential', 'nested-sim'], agentCount: 2, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'grounded-variables', name: 'Grounded Variables Demo', description: 'Track quantitative metrics during simulation', category: 'Advanced', tags: ['sequential', 'grounded-vars', 'player-context'], agentCount: 3, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'phishing-attack-simulation', name: 'Phishing Attack Simulation', description: 'Cybersecurity tabletop exercise with nested employee sims', category: 'Research', tags: ['sequential', 'nested-sim', 'player-context'], agentCount: 4, stepCount: 25, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'urban-gentrification', name: 'Urban Gentrification', description: 'Housing policy with grounded variables and critical decision points', category: 'Research', tags: ['sequential', 'grounded-vars', 'player-context', 'critical-decisions'], agentCount: 6, stepCount: 30, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'dialogic', name: 'Dialogic Conversation', description: 'CBT therapy session with dialogic game master', category: 'Prefab Types', tags: ['sequential', 'components', 'player-context'], agentCount: 2, stepCount: 12, engineType: 'sequential', gmPrefab: 'dialogic__GameMaster' },
  { id: 'strategic', name: 'Strategic Game', description: "Prisoner's Dilemma with game-theoretic scoring", category: 'Prefab Types', tags: ['sequential', 'components', 'scenes', 'game-theory', 'player-context'], agentCount: 2, stepCount: 4, engineType: 'sequential', gmPrefab: 'game_theoretic_and_dramaturgic__GameMaster' },
  { id: 'interviewer', name: 'Interviewer', description: 'Structured employee satisfaction survey', category: 'Prefab Types', tags: ['interview', 'components', 'questionnaire'], agentCount: 1, stepCount: 5, engineType: 'interview', gmPrefab: 'interviewer__GameMaster' },
  { id: 'formative', name: 'Formative Memories', description: 'High school reunion with formative memory generation', category: 'Prefab Types', tags: ['sequential', 'components', 'player-context'], agentCount: 3, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'marketplace', name: 'Marketplace', description: 'Farmers market trading with scenes and game-theoretic scoring', category: 'Prefab Types', tags: ['sequential', 'components', 'scenes', 'game-theory', 'player-context'], agentCount: 3, stepCount: 10, engineType: 'sequential', gmPrefab: 'game_theoretic_and_dramaturgic__GameMaster' },
  { id: 'rational-negotiators', name: 'Rational Negotiators', description: 'Budget negotiation using rational goal-optimizing prefab', category: 'New in v2.4', tags: ['sequential', 'components', 'player-context'], agentCount: 2, stepCount: 8, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'conversational-debate', name: 'Philosophy Roundtable', description: 'AI ethics debate using conversational prefab', category: 'New in v2.4', tags: ['sequential', 'components', 'player-context'], agentCount: 3, stepCount: 12, engineType: 'sequential', gmPrefab: 'dialogic__GameMaster' },
  { id: 'social-media-discourse', name: 'Social Media Debate', description: 'Policy debate using asynchronous engine', category: 'New in v2.4', tags: ['async', 'components', 'player-context'], agentCount: 4, stepCount: 12, engineType: 'asynchronous', gmPrefab: 'generic__GameMaster' },
  { id: 'simultaneous-auction', name: 'Sealed-Bid Auction', description: 'Art auction where all agents bid simultaneously', category: 'New in v2.4', tags: ['simultaneous', 'components', 'player-context'], agentCount: 4, stepCount: 6, engineType: 'simultaneous', gmPrefab: 'generic__GameMaster' },
  { id: 'puppet-wizard-of-oz', name: 'Wizard-of-Oz CS Training', description: 'Human-in-the-loop using puppet prefab for controlled responses', category: 'New in v2.4', tags: ['simultaneous', 'components', 'player-context'], agentCount: 3, stepCount: 10, engineType: 'simultaneous', gmPrefab: 'generic__GameMaster' },
  { id: 'spaceship-crisis', name: 'Spaceship Crisis', description: 'Ship emergency with contrib game master', category: 'New in v2.4', tags: ['sequential', 'components', 'player-context'], agentCount: 3, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'state-formation', name: 'State Formation', description: 'Building governance institutions (SDG 16)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 4, stepCount: 25, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'labor-action', name: 'Labor Strike', description: 'Collective bargaining and worker rights (SDG 8)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 4, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'fishery-management', name: 'Fishery Management', description: 'Tragedy of the commons resource management (SDG 14)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 4, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'disaster-response', name: 'Flood Evacuation', description: 'Emergency response coordination (SDG 11/13)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 5, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
  { id: 'inequality-mobility', name: 'Educational Opportunity', description: 'Social mobility and educational access (SDG 10)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 4, stepCount: 25, engineType: 'sequential', gmPrefab: 'generic__GameMaster' },
];

export const TEMPLATE_LOADERS: Record<string, () => Promise<{ config: any }>> = {
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

export const ALL_CATEGORIES: TemplateCategory[] = ['Basic', 'Prefab Types', 'Research', 'Advanced', 'New in v2.4', 'SDG Scenarios'];

export const FEATURE_TAGS = ['components', 'player-context', 'grounded-vars', 'nested-sim', 'scenes', 'questionnaire', 'scripted', 'game-theory', 'critical-decisions', 'sdg'] as const;
export const ENGINE_TAGS = ['sequential', 'simultaneous', 'async', 'interview'] as const;
