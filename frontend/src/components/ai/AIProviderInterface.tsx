/**
 * AI Provider Interface
 * Multi-provider AI content generation with specialized capabilities
 */

import React, { useState, useEffect } from 'react';
import {
  Brain,
  Search,
  Lightbulb,
  FileText,
  Upload,
  Download,
  Settings,
  Zap,
  Globe,
  BookOpen,
  Target,
  TrendingUp,
  Eye,
  Code,
  MessageSquare,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign
} from 'lucide-react';

interface AIProvider {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  model?: string;
  specialization: string;
  icon: React.ReactNode;
  color: string;
  available: boolean;
}

interface GenerationRequest {
  prompt: string;
  provider?: string;
  contextType: string;
  maxTokens: number;
  temperature: number;
  model?: string;
}

interface ResearchRequest {
  topic: string;
  chapterType: string;
  specialty: string;
  depth: string;
}

const AIProviderInterface: React.FC = () => {
  const [activeTab, setActiveTab] = useState('providers');
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [usageAnalytics, setUsageAnalytics] = useState<any>(null);

  // AI Providers Configuration
  const aiProviders: AIProvider[] = [
    {
      id: 'gemini',
      name: 'Gemini 2.5 Pro',
      description: 'Advanced reasoning with Deep Search & Deep Think capabilities',
      capabilities: ['Deep Search', 'Deep Think', 'Complex Analysis', 'Research Integration'],
      model: 'gemini-2.5-pro',
      specialization: 'Research Analysis & Evidence Synthesis',
      icon: <Brain className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-blue-500 to-purple-600',
      available: true
    },
    {
      id: 'claude',
      name: 'Claude Opus 4.1',
      description: 'Extended reasoning for comprehensive text refinement',
      capabilities: ['Extended Reasoning', 'Text Refinement', 'Structured Writing', 'Clinical Narrative'],
      model: 'claude-3-opus-20240229',
      specialization: 'Text Refinement & Clinical Writing',
      icon: <FileText className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-orange-500 to-red-600',
      available: true
    },
    {
      id: 'perplexity',
      name: 'Perplexity Pro',
      description: 'Real-time research with citations and visual integration',
      capabilities: ['Real-time Search', 'Citations', 'Visual Integration', 'Current Guidelines'],
      specialization: 'Real-time Research & Visual Integration',
      icon: <Search className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-green-500 to-teal-600',
      available: true
    },
    {
      id: 'openai',
      name: 'OpenAI GPT-4',
      description: 'Reliable general-purpose AI for diverse medical tasks',
      capabilities: ['General Purpose', 'Code Generation', 'Data Analysis', 'Summarization'],
      specialization: 'General Medical Tasks & Analysis',
      icon: <Lightbulb className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-gray-600 to-gray-800',
      available: true
    }
  ];

  const [researchRequest, setResearchRequest] = useState<ResearchRequest>({
    topic: '',
    chapterType: 'disease_overview',
    specialty: 'neurosurgery',
    depth: 'comprehensive'
  });

  useEffect(() => {
    fetchProviders();
    fetchUsageAnalytics();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await fetch('/api/ai/providers');
      const data = await response.json();
      setProviders(data.providers || aiProviders);
    } catch (error) {
      console.error('Failed to fetch providers:', error);
      setProviders(aiProviders);
    }
  };

  const fetchUsageAnalytics = async () => {
    try {
      const response = await fetch('/api/research/analytics/usage');
      const data = await response.json();
      setUsageAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch usage analytics:', error);
    }
  };

  const generateContent = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const endpoint = selectedProvider ? `/api/ai/${selectedProvider}/${
        selectedProvider === 'gemini' ? 'deep-search' :
        selectedProvider === 'claude' ? 'opus-extended' :
        selectedProvider === 'perplexity' ? 'research' : 'generate'
      }` : '/api/ai/generate';

      const requestData: GenerationRequest = {
        prompt,
        provider: selectedProvider || undefined,
        contextType: 'medical',
        maxTokens: 2000,
        temperature: 0.7
      };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      const data = await response.json();
      if (data.success) {
        setResponse(data.content || data.response);
      } else {
        setResponse(`Error: ${data.error}`);
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const generateIntelligentChapter = async () => {
    if (!researchRequest.topic.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/research/intelligent-chapter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(researchRequest)
      });

      const data = await response.json();
      if (data.chapter) {
        setResponse(data.chapter.content);
      } else {
        setResponse(`Error: ${data.error || 'Chapter generation failed'}`);
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const multiProviderSynthesis = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/ai/multi-provider-synthesis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          providers: ['gemini', 'claude', 'perplexity'],
          contextType: 'medical'
        })
      });

      const data = await response.json();
      if (data.success) {
        setResponse(data.synthesized_content);
      } else {
        setResponse(`Error: ${data.error}`);
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const renderProviderCards = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {aiProviders.map(provider => (
        <div
          key={provider.id}
          className={`bg-white rounded-lg border-2 transition-all cursor-pointer hover:shadow-lg ${
            selectedProvider === provider.id ? 'border-blue-500 shadow-md' : 'border-gray-200'
          }`}
          onClick={() => setSelectedProvider(selectedProvider === provider.id ? '' : provider.id)}
        >
          <div className={`p-4 rounded-t-lg text-white ${provider.color}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {provider.icon}
                <div>
                  <h3 className="font-semibold">{provider.name}</h3>
                  <p className="text-sm opacity-90">{provider.specialization}</p>
                </div>
              </div>
              {provider.available && (
                <CheckCircle className="w-5 h-5" />
              )}
            </div>
          </div>

          <div className="p-4">
            <p className="text-gray-600 text-sm mb-3">{provider.description}</p>

            <div className="space-y-2">
              <h4 className="font-medium text-sm">Capabilities:</h4>
              <div className="flex flex-wrap gap-1">
                {provider.capabilities.map(capability => (
                  <span
                    key={capability}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                  >
                    {capability}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderGenerationInterface = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Medical Content Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your medical content request..."
              className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={generateContent}
              disabled={loading || !prompt.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? <Clock className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              <span>Generate Content</span>
            </button>

            <button
              onClick={multiProviderSynthesis}
              disabled={loading || !prompt.trim()}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <Brain className="w-4 h-4" />
              <span>Multi-Provider Synthesis</span>
            </button>
          </div>

          {selectedProvider && (
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">
                  Selected: {aiProviders.find(p => p.id === selectedProvider)?.name}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Response Section */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Response
            </label>
            <div className="h-32 p-3 border border-gray-300 rounded-lg bg-gray-50 overflow-y-auto">
              {loading ? (
                <div className="flex items-center space-x-2 text-gray-500">
                  <Clock className="w-4 h-4 animate-spin" />
                  <span>Generating content...</span>
                </div>
              ) : response ? (
                <pre className="whitespace-pre-wrap text-sm">{response}</pre>
              ) : (
                <p className="text-gray-400 text-sm">Response will appear here...</p>
              )}
            </div>
          </div>

          {response && (
            <div className="flex gap-2">
              <button
                onClick={() => navigator.clipboard.writeText(response)}
                className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
              >
                Copy
              </button>
              <button
                onClick={() => setResponse('')}
                className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
              >
                Clear
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderIntelligentChapter = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-purple-600" />
          <span>Intelligent Chapter Generation</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Topic</label>
              <input
                type="text"
                value={researchRequest.topic}
                onChange={(e) => setResearchRequest(prev => ({ ...prev, topic: e.target.value }))}
                placeholder="e.g., Brain Tumors, Stroke Management..."
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Chapter Type</label>
              <select
                value={researchRequest.chapterType}
                onChange={(e) => setResearchRequest(prev => ({ ...prev, chapterType: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="disease_overview">Disease Overview</option>
                <option value="surgical_technique">Surgical Technique</option>
                <option value="anatomy_physiology">Anatomy & Physiology</option>
                <option value="case_study">Case Study</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Specialty</label>
              <select
                value={researchRequest.specialty}
                onChange={(e) => setResearchRequest(prev => ({ ...prev, specialty: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="neurosurgery">Neurosurgery</option>
                <option value="cardiology">Cardiology</option>
                <option value="oncology">Oncology</option>
                <option value="neurology">Neurology</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Depth</label>
              <select
                value={researchRequest.depth}
                onChange={(e) => setResearchRequest(prev => ({ ...prev, depth: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="comprehensive">Comprehensive (4,000-6,000 words)</option>
                <option value="detailed">Detailed (3,000-4,500 words)</option>
                <option value="concise">Concise (1,500-2,500 words)</option>
              </select>
            </div>

            <button
              onClick={generateIntelligentChapter}
              disabled={loading || !researchRequest.topic.trim()}
              className="w-full px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {loading ? <Clock className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
              <span>Generate Intelligent Chapter</span>
            </button>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-purple-50 rounded-lg">
              <h4 className="font-medium text-purple-800 mb-2">AI Orchestration Strategy</h4>
              <div className="space-y-2 text-sm text-purple-700">
                <div className="flex items-center space-x-2">
                  <Brain className="w-4 h-4" />
                  <span>Gemini: Research analysis & evidence synthesis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>Claude: Text refinement & clinical writing</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Search className="w-4 h-4" />
                  <span>Perplexity: Current guidelines & visual integration</span>
                </div>
              </div>
            </div>

            {usageAnalytics && (
              <div className="p-4 bg-green-50 rounded-lg">
                <h4 className="font-medium text-green-800 mb-2 flex items-center space-x-2">
                  <DollarSign className="w-4 h-4" />
                  <span>Cost Analytics</span>
                </h4>
                <div className="space-y-1 text-sm text-green-700">
                  <div>Today's Usage: ${usageAnalytics.daily_cost?.toFixed(2) || '0.00'}</div>
                  <div>Budget: $15.00/day per service</div>
                  <div>Efficiency: {((usageAnalytics.efficiency_score || 0) * 100).toFixed(1)}%</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const tabItems = [
    { id: 'providers', label: 'AI Providers', icon: Brain },
    { id: 'generate', label: 'Content Generation', icon: Zap },
    { id: 'chapter', label: 'Intelligent Chapters', icon: BookOpen }
  ];

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === item.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'providers' && renderProviderCards()}
        {activeTab === 'generate' && renderGenerationInterface()}
        {activeTab === 'chapter' && renderIntelligentChapter()}
      </div>
    </div>
  );
};

export default AIProviderInterface;