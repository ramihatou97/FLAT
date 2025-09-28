/**
 * Personal Chapter Editor Component
 * Advanced editor for dynamic neurosurgical chapters with AI assistance
 * Personal use - no collaboration features
 */

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Chip,
  IconButton,
  Divider,
  Alert,
  LinearProgress,
  Tooltip,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
} from '@mui/material';
import {
  Save,
  Publish,
  AutoAwesome,
  Update,
  Visibility,
  Edit,
  Add,
  Delete,
  ExpandMore,
  Warning,
  CheckCircle,
  Schedule,
  Person,
  Source,
  Analytics,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { Editor } from '@tinymce/tinymce-react';

// Types
interface ChapterSection {
  id: string;
  title: string;
  content: string;
  order: number;
  lastUpdated: Date;
  updateSource?: string;
  confidence: number;
  needsReview: boolean;
  aiGenerated: boolean;
}

interface ContentUpdate {
  id: string;
  type: 'addition' | 'modification' | 'contradiction' | 'deletion';
  section: string;
  content: string;
  source: string;
  confidence: number;
  timestamp: Date;
  approved: boolean;
  reviewRequired: boolean;
}

interface PersonalChapter {
  id: string;
  title: string;
  slug: string;
  subtitle?: string;
  summary: string;
  sections: ChapterSection[];
  monitoringKeywords: string[];
  updateFrequency: 'daily' | 'weekly' | 'monthly';
  autoUpdateEnabled: boolean;
  lastUpdated: Date;
  qualityScore: number;
  completenessScore: number;
  accuracyScore: number;
  freshnessScore: number;
  pendingUpdates: ContentUpdate[];
  status: 'draft' | 'review' | 'published' | 'archived';
}

interface EditorProps {
  chapter: PersonalChapter;
  onSave: (chapter: PersonalChapter) => Promise<void>;
  onPublish: (chapter: PersonalChapter) => Promise<void>;
  onRequestAIAssistance: (prompt: string, context: string) => Promise<string>;
  onApproveUpdate: (updateId: string) => Promise<void>;
  onRejectUpdate: (updateId: string) => Promise<void>;
  readOnly?: boolean;
}

// Styled components
const EditorContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: '100vh',
  backgroundColor: theme.palette.background.default,
}));

const MainEditor = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
}));

const SidePanel = styled(Paper)(({ theme }) => ({
  width: 350,
  display: 'flex',
  flexDirection: 'column',
  borderRadius: 0,
  borderLeft: `1px solid ${theme.palette.divider}`,
}));

const EditorHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
}));

const QualityIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  padding: theme.spacing(1),
  backgroundColor: theme.palette.background.default,
  borderRadius: theme.shape.borderRadius,
}));

const UpdateBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: theme.palette.warning.main,
    color: theme.palette.warning.contrastText,
  },
}));

// Quality Score Component
const QualityScores: React.FC<{ chapter: AliveChapter }> = ({ chapter }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        Chapter Quality Metrics
      </Typography>
      
      <QualityIndicator>
        <Analytics fontSize="small" />
        <Box sx={{ flex: 1 }}>
          <Typography variant="body2">Overall Quality</Typography>
          <LinearProgress
            variant="determinate"
            value={chapter.qualityScore}
            color={getScoreColor(chapter.qualityScore)}
            sx={{ height: 6, borderRadius: 3 }}
          />
          <Typography variant="caption">{chapter.qualityScore}%</Typography>
        </Box>
      </QualityIndicator>

      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, mt: 1 }}>
        <Box>
          <Typography variant="caption">Completeness</Typography>
          <LinearProgress
            variant="determinate"
            value={chapter.completenessScore}
            color={getScoreColor(chapter.completenessScore)}
            size="small"
          />
        </Box>
        <Box>
          <Typography variant="caption">Accuracy</Typography>
          <LinearProgress
            variant="determinate"
            value={chapter.accuracyScore}
            color={getScoreColor(chapter.accuracyScore)}
            size="small"
          />
        </Box>
        <Box>
          <Typography variant="caption">Freshness</Typography>
          <LinearProgress
            variant="determinate"
            value={chapter.freshnessScore}
            color={getScoreColor(chapter.freshnessScore)}
            size="small"
          />
        </Box>
      </Box>
    </Box>
  );
};

// Pending Updates Component
const PendingUpdates: React.FC<{
  updates: ContentUpdate[];
  onApprove: (updateId: string) => void;
  onReject: (updateId: string) => void;
}> = ({ updates, onApprove, onReject }) => {
  const [selectedUpdate, setSelectedUpdate] = useState<ContentUpdate | null>(null);

  const getUpdateIcon = (type: string) => {
    switch (type) {
      case 'addition': return <Add color="success" />;
      case 'modification': return <Edit color="primary" />;
      case 'contradiction': return <Warning color="error" />;
      case 'deletion': return <Delete color="error" />;
      default: return <Update />;
    }
  };

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Pending Updates ({updates.length})
      </Typography>
      
      {updates.map((update) => (
        <Accordion key={update.id} sx={{ mb: 1 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
              {getUpdateIcon(update.type)}
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" fontWeight="bold">
                  {update.type.charAt(0).toUpperCase() + update.type.slice(1)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {update.section} • {update.confidence}% confidence
                </Typography>
              </Box>
              {update.reviewRequired && (
                <Chip label="Review Required" size="small" color="warning" />
              )}
            </Box>
          </AccordionSummary>
          
          <AccordionDetails>
            <Typography variant="body2" paragraph>
              <strong>Source:</strong> {update.source}
            </Typography>
            <Typography variant="body2" paragraph>
              {update.content}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
              <Button
                size="small"
                variant="contained"
                color="success"
                onClick={() => onApprove(update.id)}
                startIcon={<CheckCircle />}
              >
                Approve
              </Button>
              <Button
                size="small"
                variant="outlined"
                color="error"
                onClick={() => onReject(update.id)}
              >
                Reject
              </Button>
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
      
      {updates.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
          No pending updates
        </Typography>
      )}
    </Box>
  );
};

// Section Editor Component
const SectionEditor: React.FC<{
  section: ChapterSection;
  onUpdate: (section: ChapterSection) => void;
  onRequestAI: (prompt: string, context: string) => Promise<string>;
}> = ({ section, onUpdate, onRequestAI }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState(section.content);
  const [aiDialogOpen, setAiDialogOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiLoading, setAiLoading] = useState(false);

  const handleSave = useCallback(() => {
    onUpdate({
      ...section,
      content,
      lastUpdated: new Date(),
    });
    setIsEditing(false);
  }, [section, content, onUpdate]);

  const handleAIAssistance = useCallback(async () => {
    if (!aiPrompt.trim()) return;
    
    setAiLoading(true);
    try {
      const aiResponse = await onRequestAI(aiPrompt, section.content);
      setContent(aiResponse);
      setAiDialogOpen(false);
      setAiPrompt('');
    } catch (error) {
      console.error('AI assistance failed:', error);
    } finally {
      setAiLoading(false);
    }
  }, [aiPrompt, section.content, onRequestAI]);

  return (
    <Paper sx={{ mb: 2, p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">{section.title}</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {section.aiGenerated && (
            <Chip label="AI Generated" size="small" color="primary" />
          )}
          {section.needsReview && (
            <Chip label="Needs Review" size="small" color="warning" />
          )}
          <Tooltip title="AI Assistance">
            <IconButton size="small" onClick={() => setAiDialogOpen(true)}>
              <AutoAwesome />
            </IconButton>
          </Tooltip>
          <Tooltip title={isEditing ? "Save" : "Edit"}>
            <IconButton
              size="small"
              onClick={isEditing ? handleSave : () => setIsEditing(true)}
            >
              {isEditing ? <Save /> : <Edit />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {isEditing ? (
        <Editor
          value={content}
          onEditorChange={setContent}
          init={{
            height: 400,
            menubar: false,
            plugins: [
              'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
              'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
              'insertdatetime', 'media', 'table', 'preview', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
            content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
          }}
        />
      ) : (
        <Box
          sx={{ minHeight: 200, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}
          dangerouslySetInnerHTML={{ __html: content }}
        />
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            label={`Confidence: ${section.confidence}%`}
            size="small"
            color={section.confidence >= 80 ? 'success' : section.confidence >= 60 ? 'warning' : 'error'}
          />
          {section.updateSource && (
            <Chip label={`Source: ${section.updateSource}`} size="small" variant="outlined" />
          )}
        </Box>
        <Typography variant="caption" color="text.secondary">
          Last updated: {section.lastUpdated.toLocaleDateString()}
        </Typography>
      </Box>

      {/* AI Assistance Dialog */}
      <Dialog open={aiDialogOpen} onClose={() => setAiDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>AI Content Assistance</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Describe what you want to improve or add to this section"
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            placeholder="e.g., Add more details about surgical complications, Update with latest research findings, Improve readability..."
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAiDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleAIAssistance}
            variant="contained"
            disabled={!aiPrompt.trim() || aiLoading}
            startIcon={aiLoading ? <Schedule /> : <AutoAwesome />}
          >
            {aiLoading ? 'Generating...' : 'Generate'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

// Main Personal Chapter Editor Component
export const PersonalChapterEditor: React.FC<EditorProps> = ({
  chapter,
  onSave,
  onPublish,
  onRequestAIAssistance,
  onApproveUpdate,
  onRejectUpdate,
  readOnly = false,
}) => {
  const [editedChapter, setEditedChapter] = useState<PersonalChapter>(chapter);
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);

  // Update chapter when prop changes
  useEffect(() => {
    setEditedChapter(chapter);
  }, [chapter]);

  // Handle save
  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      await onSave(editedChapter);
    } catch (error) {
      console.error('Save failed:', error);
    } finally {
      setSaving(false);
    }
  }, [editedChapter, onSave]);

  // Handle publish
  const handlePublish = useCallback(async () => {
    setPublishing(true);
    try {
      await onPublish(editedChapter);
    } catch (error) {
      console.error('Publish failed:', error);
    } finally {
      setPublishing(false);
    }
  }, [editedChapter, onPublish]);

  // Update section
  const handleSectionUpdate = useCallback((updatedSection: ChapterSection) => {
    setEditedChapter(prev => ({
      ...prev,
      sections: prev.sections.map(section =>
        section.id === updatedSection.id ? updatedSection : section
      ),
    }));
  }, []);

  // Handle chapter metadata updates
  const handleMetadataUpdate = useCallback((field: string, value: any) => {
    setEditedChapter(prev => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  return (
    <EditorContainer>
      <MainEditor>
        {/* Header */}
        <EditorHeader>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box sx={{ flex: 1 }}>
              <TextField
                fullWidth
                variant="standard"
                value={editedChapter.title}
                onChange={(e) => handleMetadataUpdate('title', e.target.value)}
                sx={{ mb: 1, '& .MuiInput-input': { fontSize: '1.5rem', fontWeight: 'bold' } }}
                disabled={readOnly}
              />
              <TextField
                fullWidth
                variant="standard"
                placeholder="Chapter subtitle (optional)"
                value={editedChapter.subtitle || ''}
                onChange={(e) => handleMetadataUpdate('subtitle', e.target.value)}
                sx={{ mb: 2 }}
                disabled={readOnly}
              />
              
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                <Chip
                  label={editedChapter.status.toUpperCase()}
                  color={
                    editedChapter.status === 'published' ? 'success' :
                    editedChapter.status === 'review' ? 'warning' : 'default'
                  }
                />
                <Chip
                  label={`Auto-update: ${editedChapter.autoUpdateEnabled ? 'ON' : 'OFF'}`}
                  variant="outlined"
                />
                <Chip
                  label={`Update frequency: ${editedChapter.updateFrequency}`}
                  variant="outlined"
                />
              </Box>
            </Box>

            {!readOnly && (
              <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
                <Button
                  variant="outlined"
                  onClick={handleSave}
                  disabled={saving}
                  startIcon={<Save />}
                >
                  {saving ? 'Saving...' : 'Save'}
                </Button>
                <Button
                  variant="contained"
                  onClick={handlePublish}
                  disabled={publishing || editedChapter.status === 'published'}
                  startIcon={<Publish />}
                >
                  {publishing ? 'Publishing...' : 'Publish'}
                </Button>
              </Box>
            )}
          </Box>

          {editedChapter.pendingUpdates.length > 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <UpdateBadge badgeContent={editedChapter.pendingUpdates.length}>
                <Update />
              </UpdateBadge>
              <Box sx={{ ml: 1 }}>
                {editedChapter.pendingUpdates.length} pending update(s) require review
              </Box>
            </Alert>
          )}
        </EditorHeader>

        {/* Content Editor */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {editedChapter.sections
            .sort((a, b) => a.order - b.order)
            .map((section) => (
              <SectionEditor
                key={section.id}
                section={section}
                onUpdate={handleSectionUpdate}
                onRequestAI={onRequestAIAssistance}
              />
            ))}
        </Box>
      </MainEditor>

      {/* Side Panel */}
      <SidePanel>
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" gutterBottom>
            Chapter Analytics
          </Typography>
          <QualityScores chapter={editedChapter} />
        </Box>

        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          <PendingUpdates
            updates={editedChapter.pendingUpdates}
            onApprove={onApproveUpdate}
            onReject={onRejectUpdate}
          />

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" gutterBottom>
            Monitoring Keywords
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {editedChapter.monitoringKeywords.map((keyword, index) => (
              <Chip key={index} label={keyword} size="small" variant="outlined" />
            ))}
          </Box>

          <Typography variant="subtitle2" gutterBottom>
            Collaborators
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {editedChapter.collaborators.map((collaborator, index) => (
              <Chip
                key={index}
                label={collaborator}
                size="small"
                icon={<Person />}
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
      </SidePanel>
    </EditorContainer>
  );
};

export default PersonalChapterEditor;
