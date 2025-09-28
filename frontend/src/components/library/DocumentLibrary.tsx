/**
 * Document Library Interface
 * Upload and manage medical documents, books, chapters, papers
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Upload,
  FileText,
  BookOpen,
  File,
  Search,
  Filter,
  Download,
  Trash2,
  Eye,
  Plus,
  Folder,
  Tag,
  Calendar,
  User,
  ExternalLink,
  BarChart3,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';

interface Document {
  id: string;
  title: string;
  document_type: string;
  authors: string[];
  specialty?: string;
  subspecialty?: string;
  journal?: string;
  publication_date?: string;
  doi?: string;
  pmid?: string;
  isbn?: string;
  keywords: string[];
  status: 'processing' | 'ready' | 'error';
  created_at: string;
  file_size: number;
  file_type: string;
}

interface DocumentStats {
  total_documents: number;
  by_type: Record<string, number>;
  by_specialty: Record<string, number>;
  total_size_mb: number;
  recent_uploads: number;
}

const DocumentLibrary: React.FC = () => {
  const [activeTab, setActiveTab] = useState('library');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [stats, setStats] = useState<DocumentStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterSpecialty, setFilterSpecialty] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Document types and specialties
  const documentTypes = [
    { value: 'book', label: 'Medical Book', description: 'Complete medical textbook' },
    { value: 'chapter', label: 'Book Chapter', description: 'Individual chapter from medical book' },
    { value: 'paper', label: 'Research Paper', description: 'Peer-reviewed research article' },
    { value: 'reference', label: 'Reference Material', description: 'Quick reference guide or manual' },
    { value: 'guideline', label: 'Clinical Guideline', description: 'Medical practice guideline' },
    { value: 'case_study', label: 'Case Study', description: 'Clinical case report' },
    { value: 'review', label: 'Review Article', description: 'Systematic or narrative review' },
    { value: 'thesis', label: 'Thesis/Dissertation', description: 'Academic thesis or dissertation' }
  ];

  const specialties = [
    'neurosurgery', 'cardiology', 'oncology', 'neurology',
    'radiology', 'pathology', 'internal_medicine', 'surgery',
    'pediatrics', 'psychiatry', 'emergency_medicine', 'anesthesiology'
  ];

  useEffect(() => {
    fetchDocuments();
    fetchStats();
  }, [searchTerm, filterType, filterSpecialty]);

  const fetchDocuments = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (filterType) params.append('document_type', filterType);
      if (filterSpecialty) params.append('specialty', filterSpecialty);
      params.append('limit', '20');

      const response = await fetch(`/api/library/?${params}`);
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/library/stats/overview');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleFileUpload = async (files: FileList) => {
    if (!files.length) return;

    const file = files[0];
    setLoading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', file.name.replace(/\.[^/.]+$/, ''));
      formData.append('document_type', 'book'); // Default type
      formData.append('authors', JSON.stringify([]));
      formData.append('keywords', JSON.stringify([]));

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await fetch('/api/library/upload', {
        method: 'POST',
        body: formData
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        const data = await response.json();
        await fetchDocuments();
        await fetchStats();
        alert('Document uploaded successfully!');
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.detail}`);
      }
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const deleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      const response = await fetch(`/api/library/${documentId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await fetchDocuments();
        await fetchStats();
        alert('Document deleted successfully!');
      } else {
        const error = await response.json();
        alert(`Delete failed: ${error.detail}`);
      }
    } catch (error) {
      alert(`Delete failed: ${error.message}`);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <File className="w-4 h-4 text-gray-500" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'book':
        return <BookOpen className="w-4 h-4 text-blue-500" />;
      case 'chapter':
        return <FileText className="w-4 h-4 text-purple-500" />;
      case 'paper':
        return <File className="w-4 h-4 text-green-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderUploadArea = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Upload Medical Documents</h2>
        <p className="text-gray-600">
          Upload medical books, chapters, papers, and reference materials to your personal library
        </p>
      </div>

      {/* Upload Area */}
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFileUpload(e.dataTransfer.files);
        }}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Drop files here or click to upload
        </h3>
        <p className="text-gray-500 mb-4">
          Supports PDF, DOCX, TXT, and MD files up to 50MB
        </p>
        {loading && (
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt,.md"
        onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
        className="hidden"
      />

      {/* Document Types Grid */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Supported Document Types</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {documentTypes.map(type => (
            <div key={type.value} className="bg-white p-4 rounded-lg border hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-2">
                {getTypeIcon(type.value)}
                <h4 className="font-medium">{type.label}</h4>
              </div>
              <p className="text-sm text-gray-600">{type.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderLibrary = () => (
    <div className="space-y-6">
      {/* Search and Filter */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            {documentTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>

          <select
            value={filterSpecialty}
            onChange={(e) => setFilterSpecialty(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Specialties</option>
            {specialties.map(specialty => (
              <option key={specialty} value={specialty}>
                {specialty.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Library Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{stats.total_documents}</div>
                <div className="text-sm text-gray-600">Total Documents</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-purple-500" />
              <div>
                <div className="text-2xl font-bold">{stats.by_type?.book || 0}</div>
                <div className="text-sm text-gray-600">Books</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center space-x-2">
              <File className="w-5 h-5 text-green-500" />
              <div>
                <div className="text-2xl font-bold">{stats.by_type?.paper || 0}</div>
                <div className="text-sm text-gray-600">Papers</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-orange-500" />
              <div>
                <div className="text-2xl font-bold">{stats.total_size_mb?.toFixed(1) || 0}</div>
                <div className="text-sm text-gray-600">MB Storage</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Documents List */}
      <div className="bg-white rounded-lg border">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">Document Library</h3>
        </div>

        <div className="divide-y">
          {documents.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No documents found. Upload some documents to get started.</p>
            </div>
          ) : (
            documents.map(doc => (
              <div key={doc.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className="flex items-center space-x-2">
                      {getTypeIcon(doc.document_type)}
                      {getStatusIcon(doc.status)}
                    </div>

                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 truncate">{doc.title}</h4>

                      <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                        <span className="capitalize">
                          {doc.document_type.replace('_', ' ')}
                        </span>

                        {doc.authors.length > 0 && (
                          <span className="flex items-center space-x-1">
                            <User className="w-3 h-3" />
                            <span>{doc.authors.slice(0, 2).join(', ')}</span>
                            {doc.authors.length > 2 && <span>+{doc.authors.length - 2} more</span>}
                          </span>
                        )}

                        {doc.publication_date && (
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{doc.publication_date}</span>
                          </span>
                        )}

                        <span>{formatFileSize(doc.file_size)}</span>
                      </div>

                      {doc.keywords.length > 0 && (
                        <div className="flex items-center space-x-1 mt-2">
                          <Tag className="w-3 h-3 text-gray-400" />
                          <div className="flex flex-wrap gap-1">
                            {doc.keywords.slice(0, 3).map(keyword => (
                              <span
                                key={keyword}
                                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                              >
                                {keyword}
                              </span>
                            ))}
                            {doc.keywords.length > 3 && (
                              <span className="text-xs text-gray-400">
                                +{doc.keywords.length - 3} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {(doc.doi || doc.pmid) && (
                        <div className="flex items-center space-x-4 mt-2 text-xs">
                          {doc.doi && (
                            <a
                              href={`https://doi.org/${doc.doi}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center space-x-1 text-blue-600 hover:text-blue-800"
                            >
                              <ExternalLink className="w-3 h-3" />
                              <span>DOI: {doc.doi}</span>
                            </a>
                          )}
                          {doc.pmid && (
                            <a
                              href={`https://pubmed.ncbi.nlm.nih.gov/${doc.pmid}/`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center space-x-1 text-blue-600 hover:text-blue-800"
                            >
                              <ExternalLink className="w-3 h-3" />
                              <span>PMID: {doc.pmid}</span>
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => window.open(`/api/library/${doc.id}/content`, '_blank')}
                      disabled={doc.status !== 'ready'}
                      className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded disabled:opacity-50"
                      title="View document"
                    >
                      <Eye className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => deleteDocument(doc.id)}
                      className="p-2 text-red-600 hover:text-red-900 hover:bg-red-50 rounded"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );

  const tabItems = [
    { id: 'upload', label: 'Upload Documents', icon: Upload },
    { id: 'library', label: 'Document Library', icon: BookOpen }
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
        {activeTab === 'upload' && renderUploadArea()}
        {activeTab === 'library' && renderLibrary()}
      </div>
    </div>
  );
};

export default DocumentLibrary;