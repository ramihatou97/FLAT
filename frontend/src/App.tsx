/**
 * Main Application Component
 * Personal Medical Platform with Search and AI Synthesis
 */

import React, { useState } from 'react';
import {
  Brain,
  Search,
  FileText,
  Settings,
  Home,
  BookOpen,
  Lightbulb,
  Database,
  Upload,
  Activity
} from 'lucide-react';

// Import components
import SemanticSearchInterface from './components/search/SemanticSearchInterface';
import PersonalChapterEditor from './components/neurosurgical/AliveChapterEditor';
import NeurosurgicalDashboard from './components/neurosurgical/NeurosurgicalDashboard';
import AIProviderInterface from './components/ai/AIProviderInterface';
import ResearchInterface from './components/research/ResearchInterface';
import DocumentLibrary from './components/library/DocumentLibrary';
import NeurosurgicalMonitoringDashboard from './components/monitoring/NeurosurgicalMonitoringDashboard';

// Navigation Component
const Navigation: React.FC<{ activeTab: string; setActiveTab: (tab: string) => void }> = ({ 
  activeTab, 
  setActiveTab 
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'search', label: 'Search', icon: Search },
    { id: 'chapters', label: 'Chapters', icon: BookOpen },
    { id: 'synthesis', label: 'AI Synthesis', icon: Lightbulb },
    { id: 'research', label: 'Research', icon: Database },
    { id: 'library', label: 'Library', icon: Upload },
    { id: 'monitoring', label: 'System Health', icon: Activity },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Medical Platform</h1>
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
            v3.0
          </span>
        </div>

        {/* Navigation */}
        <div className="flex items-center space-x-1">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center space-x-2 transition-colors ${
                  activeTab === item.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        {/* Settings */}
        <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </nav>
  );
};

// Dashboard Component
const Dashboard: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Welcome to Your Personal Medical Platform
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Advanced neurosurgical encyclopedia with AI-powered search and intelligent content synthesis.
          Your personal medical knowledge companion.
        </p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
          <Search className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Semantic Search</h3>
          <p className="text-gray-600 text-sm">
            AI-powered search across medical literature with concept expansion and intelligent suggestions.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
          <Lightbulb className="w-8 h-8 text-orange-600 mb-4" />
          <h3 className="text-lg font-semibold mb-2">AI Synthesis</h3>
          <p className="text-gray-600 text-sm">
            Multi-provider AI orchestration with Gemini, Claude, Perplexity, and GPT-4 for comprehensive content generation.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
          <Database className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Medical Research</h3>
          <p className="text-gray-600 text-sm">
            Search PubMed, Google Scholar, and medical databases with advanced filtering and evidence quality scoring.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
          <Upload className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Document Library</h3>
          <p className="text-gray-600 text-sm">
            Upload and manage medical books, chapters, papers, and references with intelligent processing and search.
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Platform Capabilities</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">4</div>
            <div className="text-sm text-gray-600">AI Providers</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">2</div>
            <div className="text-sm text-gray-600">Research Sources</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">8</div>
            <div className="text-sm text-gray-600">Document Types</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">12</div>
            <div className="text-sm text-gray-600">Medical Specialties</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">System Status</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-medium">Multi-provider AI orchestration ready</p>
              <p className="text-xs text-gray-500">Gemini, Claude, Perplexity, GPT-4 integrated</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-medium">Research APIs connected</p>
              <p className="text-xs text-gray-500">PubMed and Google Scholar available</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-medium">Document library initialized</p>
              <p className="text-xs text-gray-500">Ready for medical document uploads</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-medium">Intelligent chapter generation available</p>
              <p className="text-xs text-gray-500">AI-orchestrated medical content synthesis</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'search':
        return <SemanticSearchInterface />;
      case 'chapters':
        return <PersonalChapterEditor chapterId="sample-chapter" />;
      case 'synthesis':
        return (
          <div className="p-6">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Synthesis Engine</h2>
              <p className="text-gray-600">
                Multi-provider AI content generation with specialized capabilities and intelligent orchestration
              </p>
            </div>
            <AIProviderInterface />
          </div>
        );
      case 'research':
        return (
          <div className="p-6">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Medical Research</h2>
              <p className="text-gray-600">
                Search PubMed, Google Scholar, and other medical literature databases
              </p>
            </div>
            <ResearchInterface />
          </div>
        );
      case 'library':
        return (
          <div className="p-6">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Document Library</h2>
              <p className="text-gray-600">
                Upload and manage medical books, chapters, papers, and reference materials
              </p>
            </div>
            <DocumentLibrary />
          </div>
        );
      case 'monitoring':
        return (
          <div className="p-6">
            <NeurosurgicalMonitoringDashboard />
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
