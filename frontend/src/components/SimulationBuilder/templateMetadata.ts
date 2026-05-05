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
  getStepControllerDemoTemplate,
  getContribGmComponentsDemoTemplate,
  getFormativeMemoriesDemoTemplate,
  getMeasurementsDemoTemplate,
  getNestedSimStrategyTemplate,
  getDevilsAdvocatePolicyTemplate,
  getMusicCareerCrossroadsTemplate,
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
  agentNames: string[];
  keywords?: string;
}

export type TemplateCategory = 'Quick Start' | 'Prefab Demos' | 'Research' | 'General Scenarios' | 'Advanced Scenarios' | 'SDG Scenarios';

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
  'step-controller': { bg: 'bg-sky-100',    text: 'text-sky-700' },
  'contrib-gm':     { bg: 'bg-fuchsia-100', text: 'text-fuchsia-700' },
  'formative-mem':   { bg: 'bg-lime-100',   text: 'text-lime-700' },
  measurements:     { bg: 'bg-yellow-100',  text: 'text-yellow-700' },
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
  'step-controller': 'Step Controller',
  'contrib-gm':     'Contrib GM',
  'formative-mem':   'Formative Mem',
  measurements:     'Measurements',
};

export const CATEGORY_COLORS: Record<string, string> = {
  'Quick Start':        'bg-gray-200 text-gray-800',
  'Prefab Demos':       'bg-blue-200 text-blue-800',
  'Research':           'bg-purple-200 text-purple-800',
  'General Scenarios':  'bg-emerald-200 text-emerald-800',
  'Advanced Scenarios': 'bg-amber-200 text-amber-800',
  'SDG Scenarios':      'bg-teal-200 text-teal-800',
};

export const TEMPLATES: TemplateMetadata[] = [
  { id: 'coffee', name: 'Coffee Shop Demo', description: 'Quick 5-step demo with two agents chatting', category: 'Quick Start', tags: ['sequential'], agentCount: 2, stepCount: 5, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Alice', 'Bob'], keywords: 'coffee shop casual conversation' },
  { id: 'peace', name: 'Peace Negotiation', description: 'Russia-Ukraine diplomatic talks with mediator', category: 'Quick Start', tags: ['sequential', 'components', 'player-context'], agentCount: 2, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Agent R', 'Agent U'], keywords: 'diplomacy ceasefire war conflict UN mediator' },
  { id: 'planning', name: 'Planning Agent', description: 'Strategic product launch with planning prefab', category: 'Prefab Demos', tags: ['sequential', 'components', 'player-context'], agentCount: 3, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Sarah Chen', 'Marcus Rodriguez', 'Emily Watson'], keywords: 'product launch strategy planning' },
  { id: 'scripted-entity', name: 'Scripted Entity', description: 'Focus group moderator with exact scripted responses', category: 'Prefab Demos', tags: ['sequential', 'components', 'scripted'], agentCount: 5, stepCount: 10, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Dr. Chen', 'Jordan', 'Sam', 'Maria', 'Alex'], keywords: 'focus group research scripted moderator' },
  { id: 'context-aware-moderator', name: 'Context-Aware Moderator', description: 'Support group with context-adaptive scripted responses', category: 'Prefab Demos', tags: ['sequential', 'components', 'scripted', 'player-context'], agentCount: 4, stepCount: 12, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Sarah', 'Marcus', 'Elena', 'David'], keywords: 'support group therapy adaptive moderator' },
  { id: 'vaccine-hesitancy', name: 'Vaccine Hesitancy Study', description: 'Psychological components research with Big Five traits and cognitive biases', category: 'Research', tags: ['sequential', 'components', 'player-context'], agentCount: 5, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Dr. Sarah Chen', 'Mike Johnson', 'Maria Garcia', 'James Wilson', 'Lisa Thompson'], keywords: 'vaccine health public opinion psychology' },
  { id: 'nested-simulation', name: 'Nested Simulation Demo', description: 'Agents run mini-simulations to plan ahead', category: 'Advanced Scenarios', tags: ['sequential', 'nested-sim'], agentCount: 2, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Alice', 'Bob'], keywords: 'nested simulation planning' },
  { id: 'grounded-variables', name: 'Grounded Variables Demo', description: 'Track quantitative metrics during simulation', category: 'Advanced Scenarios', tags: ['sequential', 'grounded-vars', 'player-context'], agentCount: 3, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Project Manager', 'Senior Developer', 'Junior Developer'], keywords: 'metrics tracking variables software project' },
  { id: 'phishing-attack-simulation', name: 'Phishing Attack Simulation', description: 'Cybersecurity tabletop exercise with nested employee sims', category: 'Research', tags: ['sequential', 'nested-sim', 'player-context'], agentCount: 4, stepCount: 25, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Sarah', 'Marcus', 'Elena', 'David'], keywords: 'cybersecurity phishing social engineering tabletop' },
  { id: 'urban-gentrification', name: 'Urban Gentrification', description: 'Housing policy with grounded variables and critical decision points', category: 'Research', tags: ['sequential', 'grounded-vars', 'player-context', 'critical-decisions'], agentCount: 6, stepCount: 30, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Maria Rodriguez', 'James Chen', 'Fatima Al-Hassan', 'David Kim', 'Alex Thompson', 'Robert Schwartz'], keywords: 'housing rent gentrification displacement urban policy' },
  { id: 'dialogic', name: 'Dialogic Conversation', description: 'CBT therapy session with dialogic game master', category: 'Prefab Demos', tags: ['sequential', 'components', 'player-context'], agentCount: 2, stepCount: 12, engineType: 'sequential', gmPrefab: 'dialogic__GameMaster', agentNames: ['Dr. Michael Brooks', 'Jennifer Park'], keywords: 'therapy CBT counseling mental health dialogue' },
  { id: 'strategic', name: 'Strategic Game', description: "Prisoner's Dilemma with game-theoretic scoring", category: 'Prefab Demos', tags: ['sequential', 'components', 'scenes', 'game-theory', 'player-context'], agentCount: 2, stepCount: 4, engineType: 'sequential', gmPrefab: 'game_theoretic_and_dramaturgic__GameMaster', agentNames: ['Alex', 'Sam'], keywords: "prisoner's dilemma game theory cooperation defection" },
  { id: 'interviewer', name: 'Interviewer', description: 'Structured employee satisfaction survey', category: 'Prefab Demos', tags: ['interview', 'components', 'questionnaire'], agentCount: 1, stepCount: 5, engineType: 'interview', gmPrefab: 'interviewer__GameMaster', agentNames: ['Jordan Lee'], keywords: 'survey interview questionnaire employee satisfaction HR' },
  { id: 'formative', name: 'Formative Memories', description: 'High school reunion with formative memory generation', category: 'Prefab Demos', tags: ['sequential', 'components', 'player-context'], agentCount: 3, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Jake Morrison', 'Priya Sharma', "Mike O'Brien"], keywords: 'reunion backstory memories high school' },
  { id: 'marketplace', name: 'Marketplace', description: 'Farmers market trading with scenes and game-theoretic scoring', category: 'Prefab Demos', tags: ['sequential', 'components', 'scenes', 'game-theory', 'player-context'], agentCount: 3, stepCount: 10, engineType: 'sequential', gmPrefab: 'game_theoretic_and_dramaturgic__GameMaster', agentNames: ['David Chen'], keywords: 'market trading buy sell farmers market' },
  { id: 'rational-negotiators', name: 'Rational Negotiators', description: 'Budget negotiation using rational goal-optimizing prefab', category: 'General Scenarios', tags: ['sequential', 'components', 'player-context'], agentCount: 2, stepCount: 8, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Priya', 'Jordan'], keywords: 'budget negotiation rational utility corporate' },
  { id: 'conversational-debate', name: 'Philosophy Roundtable', description: 'AI ethics debate using conversational prefab', category: 'General Scenarios', tags: ['sequential', 'components', 'player-context'], agentCount: 3, stepCount: 12, engineType: 'sequential', gmPrefab: 'dialogic__GameMaster', agentNames: ['Dr. Chen', 'Mr. Patel', 'Ms. Jackson'], keywords: 'AI ethics university roundtable debate education philosophy' },
  { id: 'social-media-discourse', name: 'Social Media Debate', description: 'Policy debate using asynchronous engine', category: 'General Scenarios', tags: ['async', 'components', 'player-context'], agentCount: 4, stepCount: 12, engineType: 'asynchronous', gmPrefab: 'generic__GameMaster', agentNames: ['Maya_GreenFuture', 'Tony_PizzaKing', 'Lisa_DataNerd', 'CM_Rodriguez'], keywords: 'social media online debate climate policy' },
  { id: 'simultaneous-auction', name: 'Sealed-Bid Auction', description: 'Art auction where all agents bid simultaneously', category: 'General Scenarios', tags: ['simultaneous', 'components', 'player-context'], agentCount: 4, stepCount: 6, engineType: 'simultaneous', gmPrefab: 'generic__GameMaster', agentNames: ['Victoria', 'Marcus', 'Yuki', 'Henri'], keywords: 'auction bidding art simultaneous sealed bid' },
  { id: 'puppet-wizard-of-oz', name: 'Wizard-of-Oz CS Training', description: 'Human-in-the-loop using puppet prefab for controlled responses', category: 'General Scenarios', tags: ['simultaneous', 'components', 'player-context'], agentCount: 3, stepCount: 10, engineType: 'simultaneous', gmPrefab: 'generic__GameMaster', agentNames: ['CS_Trainee', 'Karen', 'Grandpa_Joe'], keywords: 'customer service training puppet human-in-the-loop wizard' },
  { id: 'spaceship-crisis', name: 'Spaceship Crisis', description: 'Ship emergency with contrib game master', category: 'General Scenarios', tags: ['sequential', 'components', 'player-context'], agentCount: 3, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Commander Hayes', 'Dr. Kovac', 'Dr. Okafor'], keywords: 'spaceship emergency crisis sci-fi survival' },
  { id: 'state-formation', name: 'State Formation', description: 'Building governance institutions (SDG 16)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 4, stepCount: 25, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Marcus Chen', 'Sofia Rodriguez', 'James Morrison', 'Viktor Petrov'], keywords: 'governance institutions constitution law SDG 16' },
  { id: 'labor-action', name: 'Labor Strike', description: 'Collective bargaining and worker rights (SDG 8)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 4, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Elena Vasquez', 'David Kim', 'Amina Johnson', 'Richard Sterling'], keywords: 'labor union strike workers rights SDG 8 bargaining' },
  { id: 'fishery-management', name: 'Fishery Management', description: 'Tragedy of the commons resource management (SDG 14)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 4, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Hiroshi Tanaka', 'Maria Santos', 'Okonkwo Nnamdi', 'Dr. Lisa Chen'], keywords: 'fishery ocean commons sustainability SDG 14 marine' },
  { id: 'disaster-response', name: 'Flood Evacuation', description: 'Emergency response coordination (SDG 11/13)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 5, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Sarah Williams', 'Robert Thompson', 'Javier Rodriguez', "Eleanor O'Brien", 'Pastor Moses'], keywords: 'flood disaster emergency evacuation SDG 11 13 climate' },
  { id: 'inequality-mobility', name: 'Educational Opportunity', description: 'Social mobility and educational access (SDG 10)', category: 'SDG Scenarios', tags: ['sequential', 'components', 'player-context', 'sdg'], agentCount: 4, stepCount: 25, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Alexandra Van Buren', 'Marcus Williams', 'Priya Sharma', 'Dr. Patricia Green'], keywords: 'education inequality social mobility SDG 10 university' },
  { id: 'step-controller-demo', name: 'Hostage Negotiation (Step Control)', description: 'Play/pause/step through a crisis negotiation one action at a time', category: 'Advanced Scenarios', tags: ['step-controller', 'grounded-vars', 'player-context', 'components'], agentCount: 3, stepCount: 20, engineType: 'step_controller', gmPrefab: 'generic__GameMaster', agentNames: ['Negotiator Chen', 'Red', 'Blue'], keywords: 'hostage negotiation crisis step-by-step' },
  { id: 'contrib-gm-demo', name: 'Colony Survival (Contrib GM)', description: 'All 5 contrib GM components: death, working memory, NPC events, location filter, system health', category: 'Advanced Scenarios', tags: ['sequential', 'contrib-gm', 'grounded-vars', 'player-context', 'components'], agentCount: 4, stepCount: 20, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Commander Yara Osei', 'Engineer Tomás Reyes', 'Dr. Aisha Nkomo', 'Pilot Jin-ho Park'], keywords: 'colony survival death NPC events space' },
  { id: 'formative-memories-demo', name: 'Bookstore Reunion (Formative Mem)', description: 'Generate backstories with the Generate Backstory button before running', category: 'Advanced Scenarios', tags: ['sequential', 'formative-mem', 'player-context', 'components'], agentCount: 3, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Sam Torres', 'Maya Johansson', 'Jordan Achebe'], keywords: 'bookstore reunion backstory formative memories' },
  { id: 'measurements-demo', name: 'Ethics Board (Measurements)', description: 'Run and check Component Logs tab for per-component measurement channels', category: 'Advanced Scenarios', tags: ['sequential', 'measurements', 'grounded-vars', 'player-context', 'components'], agentCount: 4, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Dr. Elaine Marsh', 'Dr. Raj Patel', 'Maria Santos', 'Dr. Kevin Liu'], keywords: 'ethics board measurements metrics logging' },
  { id: 'nested-sim-strategy', name: 'Diplomatic Crisis (Nested Sim)', description: 'Ambassador runs a back-channel mini-simulation before the formal UN session', category: 'Advanced Scenarios', tags: ['sequential', 'nested-sim', 'grounded-vars', 'player-context', 'components'], agentCount: 3, stepCount: 15, engineType: 'sequential', gmPrefab: 'generic__GameMaster', agentNames: ['Ambassador Nakamura', 'Deputy Ambassador Wei', 'Ambassador Chen'], keywords: 'diplomacy UN nested simulation back-channel strategy' },
  { id: 'devils-advocate-policy', name: 'AI Policy Red Team', description: 'Government advisory panel stress-tests a draft AI regulation framework with an assigned devil\'s advocate', category: 'Research', tags: ['sequential', 'grounded-vars', 'player-context', 'components'], agentCount: 3, stepCount: 15, engineType: 'sequential', gmPrefab: 'dialogic__GameMaster', agentNames: ['Dr. Okafor', 'Kwame Mensah', 'Ms. Tanaka'], keywords: 'AI regulation policy red team devil advocate governance adversarial debate' },
  { id: 'music-career-crossroads', name: 'Music Career Crossroads', description: 'A 26-year-old musician deliberates whether to commit to music, pivot careers, or build a hybrid path toward financial independence', category: 'Research', tags: ['sequential', 'grounded-vars', 'player-context', 'components', 'critical-decisions'], agentCount: 5, stepCount: 20, engineType: 'sequential', gmPrefab: 'dialogic__GameMaster', agentNames: ['Jordan Kim', 'Sandra Kim', 'Dev Okafor', 'Rae Castillo', 'Marcus Wei'], keywords: 'music career decision financial independence pivot creative arts deliberation' },
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
  'step-controller-demo': getStepControllerDemoTemplate,
  'contrib-gm-demo': getContribGmComponentsDemoTemplate,
  'formative-memories-demo': getFormativeMemoriesDemoTemplate,
  'measurements-demo': getMeasurementsDemoTemplate,
  'nested-sim-strategy': getNestedSimStrategyTemplate,
  'devils-advocate-policy': getDevilsAdvocatePolicyTemplate,
  'music-career-crossroads': getMusicCareerCrossroadsTemplate,
};

export const ALL_CATEGORIES: TemplateCategory[] = ['Quick Start', 'Prefab Demos', 'Research', 'General Scenarios', 'Advanced Scenarios', 'SDG Scenarios'];

export const FEATURE_TAGS = ['components', 'player-context', 'grounded-vars', 'nested-sim', 'scenes', 'questionnaire', 'scripted', 'game-theory', 'critical-decisions', 'sdg', 'step-controller', 'contrib-gm', 'formative-mem', 'measurements'] as const;
export const ENGINE_TAGS = ['sequential', 'simultaneous', 'async', 'interview', 'step-controller'] as const;
