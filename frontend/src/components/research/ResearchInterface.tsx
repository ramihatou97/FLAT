/**
 * Research Interface
 * PubMed and Google Scholar integration for medical literature search
 */

import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  BookOpen,
  ExternalLink,
  Calendar,
  User,
  Quote,
  TrendingUp,
  Download,
  Eye,
  Settings,
  Database,
  Globe,
  FileText,
  Star,
  Tag,
  Zap,
  Brain,
  Clock
} from 'lucide-react';

interface Article {
  title: string;
  authors: string[];
  abstract: string;
  journal?: string;
  publication_year?: string;
  publication_month?: string;
  pmid?: string;
  doi?: string;
  link?: string;
  cited_by_count?: number;
  keywords?: string[];
  mesh_terms?: string[];
  source: 'pubmed' | 'google_scholar';
  publication_info?: any;
}

interface SearchResult {
  success: boolean;
  results: Article[];
  total_count: number;
  query: string;
  source?: string;
  sources_searched?: string[];
  source_results?: Record<string, any>;
}

interface ResearchSources {
  available_sources: Record<string, {
    name: string;
    description: string;
    available: boolean;
    features: string[];
  }>;
  article_types: string[];
  specialties: string[];
}

const ResearchInterface: React.FC = () => {
  const [activeTab, setActiveTab] = useState('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSources, setSelectedSources] = useState<string[]>(['pubmed']);
  const [maxResults, setMaxResults] = useState(10);
  const [yearFrom, setYearFrom] = useState<number | undefined>();
  const [yearTo, setYearTo] = useState<number | undefined>();
  const [articleTypes, setArticleTypes] = useState<string[]>([]);
  const [sources, setSources] = useState<ResearchSources | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  useEffect(() => {
    fetchAvailableSources();
  }, []);

  const fetchAvailableSources = async () => {
    try {
      const response = await fetch('/api/research/sources/available');
      const data = await response.json();
      setSources(data);
    } catch (error) {
      console.error('Failed to fetch sources:', error);
    }
  };

  const searchLiterature = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const searchData = {
        query: searchQuery,
        sources: selectedSources,
        max_results_per_source: maxResults,
        year_from: yearFrom,
        year_to: yearTo
      };

      const response = await fetch('/api/research/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchData)
      });

      const data: SearchResult = await response.json();
      if (data.success) {
        setSearchResults(data.results);
      } else {
        alert('Search failed: ' + (data as any).error);
      }
    } catch (error) {
      alert('Search failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const searchPubMed = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        query: searchQuery,
        max_results: maxResults.toString()
      });

      if (yearFrom) params.append('year_from', yearFrom.toString());
      if (yearTo) params.append('year_to', yearTo.toString());
      if (articleTypes.length > 0) {
        articleTypes.forEach(type => params.append('article_types', type));
      }

      const response = await fetch(`/api/research/pubmed/search?${params}`);
      const data: SearchResult = await response.json();

      if (data.success) {
        setSearchResults(data.results);
      } else {
        alert('PubMed search failed: ' + (data as any).error);
      }
    } catch (error) {
      alert('PubMed search failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const searchGoogleScholar = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        query: searchQuery,
        max_results: maxResults.toString()
      });

      if (yearFrom) params.append('year_from', yearFrom.toString());
      if (yearTo) params.append('year_to', yearTo.toString());

      const response = await fetch(`/api/research/scholar/search?${params}`);
      const data: SearchResult = await response.json();

      if (data.success) {
        setSearchResults(data.results);
      } else {
        alert('Google Scholar search failed: ' + (data as any).error);
      }
    } catch (error) {
      alert('Google Scholar search failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const getArticleDetails = async (pmid: string) => {
    try {
      const response = await fetch(`/api/research/article/${pmid}`);
      const data = await response.json();
      setSelectedArticle(data);
    } catch (error) {
      console.error('Failed to get article details:', error);
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'pubmed':
        return <Database className="w-4 h-4 text-blue-500" />;
      case 'google_scholar':
        return <Globe className="w-4 h-4 text-green-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const getSourceBadge = (source: string) => {
    const colors = {
      pubmed: 'bg-blue-100 text-blue-800',
      google_scholar: 'bg-green-100 text-green-800'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[source] || 'bg-gray-100 text-gray-800'}`}>
        {source === 'google_scholar' ? 'Google Scholar' : source.toUpperCase()}
      </span>
    );
  };

  const formatDate = (year?: string, month?: string) => {
    if (!year) return '';
    return month ? `${month} ${year}` : year;
  };

  const renderSearchForm = () => (
    <div className="space-y-6">
      {/* Search Input */}
      <div className="bg-white p-6 rounded-lg border">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter medical terms, conditions, procedures..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && searchLiterature()}
              />
            </div>
          </div>

          {/* Search Options */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Results
              </label>
              <select
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
                <option value={50}>50 results</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Year From
              </label>
              <input
                type="number"
                value={yearFrom || ''}
                onChange={(e) => setYearFrom(e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="e.g., 2020"
                min="1900"
                max={new Date().getFullYear()}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Year To
              </label>
              <input
                type="number"
                value={yearTo || ''}
                onChange={(e) => setYearTo(e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="e.g., 2024"
                min="1900"
                max={new Date().getFullYear()}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Sources Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Sources
            </label>
            <div className="flex flex-wrap gap-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={selectedSources.includes('pubmed')}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedSources(prev => [...prev, 'pubmed']);
                    } else {
                      setSelectedSources(prev => prev.filter(s => s !== 'pubmed'));
                    }
                  }}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">PubMed</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={selectedSources.includes('google_scholar')}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedSources(prev => [...prev, 'google_scholar']);
                    } else {
                      setSelectedSources(prev => prev.filter(s => s !== 'google_scholar'));
                    }
                  }}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">Google Scholar</span>
              </label>
            </div>
          </div>

          {/* Article Types (PubMed specific) */}
          {selectedSources.includes('pubmed') && sources && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Article Types (PubMed)
              </label>
              <div className="flex flex-wrap gap-2">
                {sources.article_types.map(type => (
                  <label key={type} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={articleTypes.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setArticleTypes(prev => [...prev, type]);
                        } else {
                          setArticleTypes(prev => prev.filter(t => t !== type));
                        }
                      }}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm capitalize">{type}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Search Buttons */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={searchLiterature}
              disabled={loading || !searchQuery.trim() || selectedSources.length === 0}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? <Clock className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              <span>Multi-Source Search</span>
            </button>

            <button
              onClick={searchPubMed}
              disabled={loading || !searchQuery.trim()}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <Database className="w-4 h-4" />
              <span>PubMed Only</span>
            </button>

            <button
              onClick={searchGoogleScholar}
              disabled={loading || !searchQuery.trim()}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <Globe className="w-4 h-4" />
              <span>Scholar Only</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSearchResults = () => (
    <div className="space-y-4">
      {searchResults.length === 0 ? (
        <div className="bg-white p-8 rounded-lg border text-center">
          <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No search results. Enter a query and search to see articles.</p>
        </div>
      ) : (
        <>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">
                Search Results ({searchResults.length} articles)
              </h3>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">Sort by:</span>
                <select className="px-3 py-1 border border-gray-300 rounded text-sm">
                  <option>Relevance</option>
                  <option>Publication Date</option>
                  <option>Citation Count</option>
                </select>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {searchResults.map((article, index) => (
              <div key={index} className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        {getSourceIcon(article.source)}
                        {getSourceBadge(article.source)}
                        {article.pmid && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                            PMID: {article.pmid}
                          </span>
                        )}
                      </div>

                      <h4 className="text-lg font-semibold text-gray-900 mb-2 leading-tight">
                        {article.title}
                      </h4>

                      {/* Authors and Publication Info */}
                      <div className="flex items-center flex-wrap gap-4 text-sm text-gray-600 mb-2">
                        {article.authors.length > 0 && (
                          <div className="flex items-center space-x-1">
                            <User className="w-3 h-3" />
                            <span>
                              {article.authors.slice(0, 3).join(', ')}
                              {article.authors.length > 3 && ` +${article.authors.length - 3} more`}
                            </span>
                          </div>
                        )}

                        {article.journal && (
                          <div className="flex items-center space-x-1">
                            <BookOpen className="w-3 h-3" />
                            <span>{article.journal}</span>
                          </div>
                        )}

                        {(article.publication_year || article.publication_month) && (
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{formatDate(article.publication_year, article.publication_month)}</span>
                          </div>
                        )}

                        {article.cited_by_count !== undefined && article.cited_by_count > 0 && (
                          <div className="flex items-center space-x-1">
                            <Quote className="w-3 h-3" />
                            <span>{article.cited_by_count} citations</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      {article.pmid && (
                        <button
                          onClick={() => getArticleDetails(article.pmid)}
                          className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded"
                          title="View details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      )}

                      {(article.doi || article.link) && (
                        <a
                          href={article.doi ? `https://doi.org/${article.doi}` : article.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded"
                          title="Open article"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Abstract */}
                  {article.abstract && (
                    <div>
                      <p className="text-gray-700 text-sm leading-relaxed">
                        {article.abstract.length > 300
                          ? `${article.abstract.substring(0, 300)}...`
                          : article.abstract
                        }
                      </p>
                    </div>
                  )}

                  {/* Keywords and MeSH Terms */}
                  {(article.keywords?.length > 0 || article.mesh_terms?.length > 0) && (
                    <div className="space-y-2">
                      {article.keywords?.length > 0 && (
                        <div className="flex items-center space-x-2">
                          <Tag className="w-3 h-3 text-gray-400" />
                          <span className="text-xs text-gray-500">Keywords:</span>
                          <div className="flex flex-wrap gap-1">
                            {article.keywords.slice(0, 5).map(keyword => (
                              <span
                                key={keyword}
                                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {article.mesh_terms?.length > 0 && (
                        <div className="flex items-center space-x-2">
                          <Star className="w-3 h-3 text-gray-400" />
                          <span className="text-xs text-gray-500">MeSH:</span>
                          <div className="flex flex-wrap gap-1">
                            {article.mesh_terms.slice(0, 3).map(term => (
                              <span
                                key={term}
                                className="px-2 py-1 bg-blue-100 text-blue-600 text-xs rounded-full"
                              >
                                {term}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );

  const renderSources = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Research Sources</h2>
        <p className="text-gray-600">
          Available medical literature databases and research tools
        </p>
      </div>

      {sources && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(sources.available_sources).map(([key, source]) => (
            <div key={key} className="bg-white p-6 rounded-lg border">
              <div className="flex items-center space-x-3 mb-4">
                {getSourceIcon(key)}
                <div>
                  <h3 className="text-lg font-semibold">{source.name}</h3>
                  <p className="text-sm text-gray-600">{source.description}</p>
                </div>
                {source.available && (
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                    Available
                  </span>
                )}
              </div>

              <div>
                <h4 className="font-medium mb-2">Features:</h4>
                <ul className="space-y-1">
                  {source.features.map(feature => (
                    <li key={feature} className="text-sm text-gray-600 flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const tabItems = [
    { id: 'search', label: 'Literature Search', icon: Search },
    { id: 'results', label: 'Search Results', icon: FileText },
    { id: 'sources', label: 'Research Sources', icon: Database }
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
        {activeTab === 'search' && renderSearchForm()}
        {activeTab === 'results' && renderSearchResults()}
        {activeTab === 'sources' && renderSources()}
      </div>

      {/* Article Details Modal */}
      {selectedArticle && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Article Details</h3>
                <button
                  onClick={() => setSelectedArticle(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <h4 className="text-lg font-medium">{selectedArticle.title}</h4>

                {selectedArticle.authors.length > 0 && (
                  <div>
                    <span className="font-medium">Authors: </span>
                    <span>{selectedArticle.authors.join(', ')}</span>
                  </div>
                )}

                {selectedArticle.abstract && (
                  <div>
                    <span className="font-medium">Abstract: </span>
                    <p className="mt-2 text-gray-700">{selectedArticle.abstract}</p>
                  </div>
                )}

                {selectedArticle.keywords?.length > 0 && (
                  <div>
                    <span className="font-medium">Keywords: </span>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {selectedArticle.keywords.map(keyword => (
                        <span
                          key={keyword}
                          className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded-full"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedArticle.mesh_terms?.length > 0 && (
                  <div>
                    <span className="font-medium">MeSH Terms: </span>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {selectedArticle.mesh_terms.map(term => (
                        <span
                          key={term}
                          className="px-2 py-1 bg-blue-100 text-blue-600 text-sm rounded-full"
                        >
                          {term}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchInterface;