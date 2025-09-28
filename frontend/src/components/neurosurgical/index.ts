/**
 * Neurosurgical Components Index
 * Export all neurosurgical encyclopedia components
 */

// Main Components
export { default as AnatomicalViewer } from './AnatomicalViewer';
export { default as AliveChapterEditor } from './AliveChapterEditor';
export { default as NeurosurgicalDashboard } from './NeurosurgicalDashboard';

// Component Types
export type {
  AnatomicalStructure,
  SurgicalProcedure,
  ViewerProps,
} from './AnatomicalViewer';

export type {
  ChapterSection,
  ContentUpdate,
  AliveChapter,
  EditorProps,
} from './AliveChapterEditor';

export type {
  DashboardMetrics,
  ChapterStats,
  SystemHealth,
  RecentActivity,
} from './NeurosurgicalDashboard';
