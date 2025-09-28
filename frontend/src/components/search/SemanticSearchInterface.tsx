/**
 * Semantic Search Interface Component
 * Advanced medical content search with AI-powered features
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Search, 
  Filter, 
  Clock, 
  BookOpen, 
  FileText, 
  Brain,
  Loader2,
  Sparkles
} from 'lucide-react';

interface SearchResult {
  id: string;
  title: string;
  content: string;
  content_type: string;
  relevance_score: number;
  medical_concepts: string[];
  source: string;
  metadata: Record<string, any>;
}

interface SearchResponse {
  results: SearchResult[];
  total_found: number;
  processing_time_ms: number;
  clusters: Array<{
    name: string;
    count: number;
    results: string[];
  }>;
  suggestions: string[];
}

interface SearchFilters {
  content_types: string[];
  specialty_filter: string;
  expand_medical_terms: boolean;
  use_ai_expansion: boolean;
  include_related: boolean;
}

const SemanticSearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    content_types: [],
    specialty_filter: '',
    expand_medical_terms: true,
    use_ai_expansion: true,
    include_related: true
  });
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // Content type options
  const contentTypes = [
    { value: 'chapter', label: 'Medical Chapters', icon: BookOpen },
    { value: 'research_paper', label: 'Research Papers', icon: FileText },
    { value: 'pdf_document', label: 'PDF Documents', icon: FileText },
    { value: 'clinical_trial', label: 'Clinical Trials', icon: Brain },
    { value: 'case_study', label: 'Case Studies', icon: FileText }
  ];

  // Medical specialties
  const specialties = [
    'neurosurgery', 'cardiology', 'oncology', 'orthopedics', 
    'radiology', 'anesthesiology', 'emergency_medicine', 'internal_medicine'
  ];

  // Fetch search suggestions
  const fetchSuggestions = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`/api/search/suggestions?query=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  }, []);

  // Debounced suggestion fetching
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSuggestions(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query, fetchSuggestions]);

  // Perform search
  const performSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const searchParams = new URLSearchParams({
        query_text: searchQuery,
        max_results: '20',
        expand_medical_terms: filters.expand_medical_terms.toString(),
        use_ai_expansion: filters.use_ai_expansion.toString(),
        include_related: filters.include_related.toString()
      });

      if (filters.content_types.length > 0) {
        filters.content_types.forEach(type => {
          searchParams.append('content_types', type);
        });
      }

      if (filters.specialty_filter) {
        searchParams.append('specialty_filter', filters.specialty_filter);
      }

      const response = await fetch('/api/search/semantic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: searchParams
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data);

      // Add to recent searches
      setRecentSearches(prev => {
        const updated = [searchQuery, ...prev.filter(s => s !== searchQuery)];
        return updated.slice(0, 5);
      });

    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle search submission
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch();
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setSuggestions([]);
    performSearch(suggestion);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Search Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <Brain className="w-8 h-8 text-blue-600" />
          Medical Knowledge Search
        </h1>
        <p className="text-gray-600">
          AI-powered semantic search across medical literature and chapters
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search medical content... (e.g., 'brain tumor surgery', 'craniotomy techniques')"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            />
            {filters.use_ai_expansion && (
              <Sparkles className="absolute right-3 top-1/2 transform -translate-y-1/2 text-purple-500 w-5 h-5" />
            )}
          </div>

          {/* Search Suggestions */}
          {suggestions.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Search Filters */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-600" />
            <span className="font-medium text-gray-700">Search Filters</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Content Types */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content Types
              </label>
              <div className="space-y-2">
                {contentTypes.map(type => (
                  <label key={type.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.content_types.includes(type.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFilters(prev => ({
                            ...prev,
                            content_types: [...prev.content_types, type.value]
                          }));
                        } else {
                          setFilters(prev => ({
                            ...prev,
                            content_types: prev.content_types.filter(t => t !== type.value)
                          }));
                        }
                      }}
                      className="mr-2"
                    />
                    <type.icon className="w-4 h-4 mr-1" />
                    <span className="text-sm">{type.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Medical Specialty */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Medical Specialty
              </label>
              <select
                value={filters.specialty_filter}
                onChange={(e) => setFilters(prev => ({ ...prev, specialty_filter: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="">All Specialties</option>
                {specialties.map(specialty => (
                  <option key={specialty} value={specialty}>
                    {specialty.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>

            {/* AI Options */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Enhancement
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.expand_medical_terms}
                    onChange={(e) => setFilters(prev => ({ ...prev, expand_medical_terms: e.target.checked }))}
                    className="mr-2"
                  />
                  <span className="text-sm">Expand Medical Terms</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.use_ai_expansion}
                    onChange={(e) => setFilters(prev => ({ ...prev, use_ai_expansion: e.target.checked }))}
                    className="mr-2"
                  />
                  <span className="text-sm">AI Query Expansion</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.include_related}
                    onChange={(e) => setFilters(prev => ({ ...prev, include_related: e.target.checked }))}
                    className="mr-2"
                  />
                  <span className="text-sm">Include Related Content</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Search Button */}
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Search Medical Content
            </>
          )}
        </button>
      </form>

      {/* Recent Searches */}
      {recentSearches.length > 0 && (
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center gap-2 mb-3">
            <Clock className="w-4 h-4 text-gray-600" />
            <span className="font-medium text-gray-700">Recent Searches</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((search, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(search)}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
              >
                {search}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search Results */}
      {results && (
        <div className="space-y-6">
          {/* Results Summary */}
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">
                  Found {results.total_found} results
                </h3>
                <p className="text-gray-600">
                  Search completed in {results.processing_time_ms.toFixed(0)}ms
                </p>
              </div>
              {results.clusters.length > 0 && (
                <div className="text-sm text-gray-600">
                  {results.clusters.map(cluster => (
                    <span key={cluster.name} className="mr-4">
                      {cluster.name}: {cluster.count}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Search Results List */}
          <div className="space-y-4">
            {results.results.map((result) => (
              <div key={result.id} className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <h4 className="text-xl font-semibold text-blue-600 hover:text-blue-800 cursor-pointer">
                    {result.title}
                  </h4>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span className="bg-gray-100 px-2 py-1 rounded">
                      {result.content_type.replace('_', ' ')}
                    </span>
                    <span>
                      {(result.relevance_score * 100).toFixed(0)}% match
                    </span>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-3 line-clamp-3">
                  {result.content}
                </p>
                
                {result.medical_concepts.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {result.medical_concepts.slice(0, 5).map((concept, index) => (
                      <span
                        key={index}
                        className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs"
                      >
                        {concept}
                      </span>
                    ))}
                  </div>
                )}
                
                <div className="text-sm text-gray-500">
                  Source: {result.source}
                </div>
              </div>
            ))}
          </div>

          {/* Search Suggestions */}
          {results.suggestions.length > 0 && (
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-medium text-gray-700 mb-3">Related Searches</h4>
              <div className="flex flex-wrap gap-2">
                {results.suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SemanticSearchInterface;
