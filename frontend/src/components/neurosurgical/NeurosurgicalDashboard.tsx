/**
 * NeurosurgicalDashboard Component
 * Comprehensive dashboard for neurosurgical encyclopedia management
 * Features real-time analytics, content monitoring, and system health
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  Update,
  Visibility,
  Edit,
  Warning,
  CheckCircle,
  Schedule,
  Analytics,
  Book,
  Science,
  People,
  Speed,
  CloudDone,
  Error,
  Refresh,
  NotificationsActive,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

// Types
interface DashboardMetrics {
  totalChapters: number;
  publishedChapters: number;
  pendingUpdates: number;
  activeUsers: number;
  avgQualityScore: number;
  avgFreshnessScore: number;
  totalViews: number;
  monthlyGrowth: number;
}

interface ChapterStats {
  id: string;
  title: string;
  status: 'draft' | 'review' | 'published';
  qualityScore: number;
  views: number;
  lastUpdated: Date;
  pendingUpdates: number;
  collaborators: number;
}

interface SystemHealth {
  apiStatus: 'healthy' | 'degraded' | 'critical';
  databaseStatus: 'healthy' | 'degraded' | 'critical';
  aiServicesStatus: 'healthy' | 'degraded' | 'critical';
  updateMonitorStatus: 'healthy' | 'degraded' | 'critical';
  lastHealthCheck: Date;
}

interface RecentActivity {
  id: string;
  type: 'chapter_updated' | 'chapter_published' | 'update_approved' | 'user_joined';
  description: string;
  timestamp: Date;
  user: string;
  chapterTitle?: string;
}

// Styled components
const DashboardContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.default,
  minHeight: '100vh',
}));

const MetricCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  },
}));

const StatusIndicator = styled(Box)<{ status: 'healthy' | 'degraded' | 'critical' }>(({ theme, status }) => ({
  width: 12,
  height: 12,
  borderRadius: '50%',
  backgroundColor:
    status === 'healthy' ? theme.palette.success.main :
    status === 'degraded' ? theme.palette.warning.main :
    theme.palette.error.main,
}));

// Mock data (in production, this would come from APIs)
const mockMetrics: DashboardMetrics = {
  totalChapters: 156,
  publishedChapters: 142,
  pendingUpdates: 23,
  activeUsers: 89,
  avgQualityScore: 87.5,
  avgFreshnessScore: 82.3,
  totalViews: 45678,
  monthlyGrowth: 12.5,
};

const mockChapterStats: ChapterStats[] = [
  {
    id: '1',
    title: 'Brain Tumor Management',
    status: 'published',
    qualityScore: 92,
    views: 1234,
    lastUpdated: new Date('2024-01-15'),
    pendingUpdates: 3,
    collaborators: 5,
  },
  {
    id: '2',
    title: 'Spinal Stenosis Treatment',
    status: 'review',
    qualityScore: 85,
    views: 856,
    lastUpdated: new Date('2024-01-14'),
    pendingUpdates: 1,
    collaborators: 3,
  },
  // Add more mock data...
];

const mockSystemHealth: SystemHealth = {
  apiStatus: 'healthy',
  databaseStatus: 'healthy',
  aiServicesStatus: 'degraded',
  updateMonitorStatus: 'healthy',
  lastHealthCheck: new Date(),
};

const mockRecentActivity: RecentActivity[] = [
  {
    id: '1',
    type: 'chapter_updated',
    description: 'Brain Tumor Management chapter updated with new research',
    timestamp: new Date('2024-01-15T10:30:00'),
    user: 'Dr. Smith',
    chapterTitle: 'Brain Tumor Management',
  },
  {
    id: '2',
    type: 'update_approved',
    description: 'Approved update for surgical complications section',
    timestamp: new Date('2024-01-15T09:15:00'),
    user: 'Dr. Johnson',
  },
  // Add more mock data...
];

// Metrics Overview Component
const MetricsOverview: React.FC<{ metrics: DashboardMetrics }> = ({ metrics }) => {
  const metricCards = [
    {
      title: 'Total Chapters',
      value: metrics.totalChapters,
      icon: <Book />,
      color: 'primary',
      trend: '+5 this month',
    },
    {
      title: 'Published',
      value: metrics.publishedChapters,
      icon: <CheckCircle />,
      color: 'success',
      trend: `${((metrics.publishedChapters / metrics.totalChapters) * 100).toFixed(1)}% published`,
    },
    {
      title: 'Pending Updates',
      value: metrics.pendingUpdates,
      icon: <Update />,
      color: 'warning',
      trend: 'Requires review',
    },
    {
      title: 'Active Users',
      value: metrics.activeUsers,
      icon: <People />,
      color: 'info',
      trend: `+${metrics.monthlyGrowth}% this month`,
    },
    {
      title: 'Avg Quality Score',
      value: `${metrics.avgQualityScore}%`,
      icon: <Analytics />,
      color: 'success',
      trend: '+2.3% improvement',
    },
    {
      title: 'Total Views',
      value: metrics.totalViews.toLocaleString(),
      icon: <Visibility />,
      color: 'primary',
      trend: '+15% this week',
    },
  ];

  return (
    <Grid container spacing={3}>
      {metricCards.map((metric, index) => (
        <Grid item xs={12} sm={6} md={4} lg={2} key={index}>
          <MetricCard>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    {metric.title}
                  </Typography>
                  <Typography variant="h5" component="div">
                    {metric.value}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {metric.trend}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: `${metric.color}.main` }}>
                  {metric.icon}
                </Avatar>
              </Box>
            </CardContent>
          </MetricCard>
        </Grid>
      ))}
    </Grid>
  );
};

// System Health Component
const SystemHealthPanel: React.FC<{ health: SystemHealth }> = ({ health }) => {
  const healthItems = [
    { name: 'API Services', status: health.apiStatus },
    { name: 'Database', status: health.databaseStatus },
    { name: 'AI Services', status: health.aiServicesStatus },
    { name: 'Update Monitor', status: health.updateMonitorStatus },
  ];

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy': return 'Operational';
      case 'degraded': return 'Degraded Performance';
      case 'critical': return 'Service Disruption';
      default: return 'Unknown';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle color="success" />;
      case 'degraded': return <Warning color="warning" />;
      case 'critical': return <Error color="error" />;
      default: return <Schedule />;
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">System Health</Typography>
        <Tooltip title="Refresh Status">
          <IconButton size="small">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>
      
      <List dense>
        {healthItems.map((item, index) => (
          <ListItem key={index}>
            <ListItemIcon>
              {getStatusIcon(item.status)}
            </ListItemIcon>
            <ListItemText
              primary={item.name}
              secondary={getStatusText(item.status)}
            />
            <StatusIndicator status={item.status} />
          </ListItem>
        ))}
      </List>
      
      <Typography variant="caption" color="textSecondary">
        Last checked: {health.lastHealthCheck.toLocaleTimeString()}
      </Typography>
    </Paper>
  );
};

// Chapter Performance Chart
const ChapterPerformanceChart: React.FC = () => {
  const data = [
    { month: 'Jan', views: 4000, updates: 24, quality: 85 },
    { month: 'Feb', views: 3000, updates: 18, quality: 87 },
    { month: 'Mar', views: 5000, updates: 32, quality: 89 },
    { month: 'Apr', views: 4500, updates: 28, quality: 88 },
    { month: 'May', views: 6000, updates: 35, quality: 90 },
    { month: 'Jun', views: 5500, updates: 30, quality: 91 },
  ];

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Chapter Performance Trends
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <RechartsTooltip />
          <Legend />
          <Line yAxisId="left" type="monotone" dataKey="views" stroke="#8884d8" name="Views" />
          <Line yAxisId="left" type="monotone" dataKey="updates" stroke="#82ca9d" name="Updates" />
          <Line yAxisId="right" type="monotone" dataKey="quality" stroke="#ffc658" name="Quality Score" />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
};

// Recent Activity Component
const RecentActivityPanel: React.FC<{ activities: RecentActivity[] }> = ({ activities }) => {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'chapter_updated': return <Update color="primary" />;
      case 'chapter_published': return <CheckCircle color="success" />;
      case 'update_approved': return <CheckCircle color="success" />;
      case 'user_joined': return <People color="info" />;
      default: return <NotificationsActive />;
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Recent Activity
      </Typography>
      
      <List>
        {activities.slice(0, 5).map((activity, index) => (
          <React.Fragment key={activity.id}>
            <ListItem alignItems="flex-start">
              <ListItemIcon>
                {getActivityIcon(activity.type)}
              </ListItemIcon>
              <ListItemText
                primary={activity.description}
                secondary={
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      by {activity.user}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {activity.timestamp.toLocaleString()}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
            {index < activities.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
      
      <Button fullWidth variant="outlined" sx={{ mt: 1 }}>
        View All Activity
      </Button>
    </Paper>
  );
};

// Top Chapters Table
const TopChaptersTable: React.FC<{ chapters: ChapterStats[] }> = ({ chapters }) => {
  const getStatusChip = (status: string) => {
    const statusConfig = {
      published: { color: 'success' as const, label: 'Published' },
      review: { color: 'warning' as const, label: 'In Review' },
      draft: { color: 'default' as const, label: 'Draft' },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig];
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Top Performing Chapters
      </Typography>
      
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Chapter</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Quality</TableCell>
              <TableCell align="right">Views</TableCell>
              <TableCell align="right">Updates</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {chapters.slice(0, 5).map((chapter) => (
              <TableRow key={chapter.id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {chapter.title}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Updated {chapter.lastUpdated.toLocaleDateString()}
                  </Typography>
                </TableCell>
                <TableCell>
                  {getStatusChip(chapter.status)}
                </TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                    <Typography variant="body2" sx={{ mr: 1 }}>
                      {chapter.qualityScore}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={chapter.qualityScore}
                      sx={{ width: 50, height: 4 }}
                      color={chapter.qualityScore >= 80 ? 'success' : 'warning'}
                    />
                  </Box>
                </TableCell>
                <TableCell align="right">
                  {chapter.views.toLocaleString()}
                </TableCell>
                <TableCell align="right">
                  {chapter.pendingUpdates > 0 && (
                    <Chip
                      label={chapter.pendingUpdates}
                      color="warning"
                      size="small"
                    />
                  )}
                </TableCell>
                <TableCell>
                  <Tooltip title="Edit Chapter">
                    <IconButton size="small">
                      <Edit />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="View Chapter">
                    <IconButton size="small">
                      <Visibility />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

// Main Dashboard Component
export const NeurosurgicalDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <DashboardContainer>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Neurosurgical Encyclopedia Dashboard
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Monitor content quality, system health, and user engagement
        </Typography>
      </Box>

      {/* Metrics Overview */}
      <Box sx={{ mb: 3 }}>
        <MetricsOverview metrics={mockMetrics} />
      </Box>

      {/* Main Content Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Overview" />
          <Tab label="Content Analytics" />
          <Tab label="System Health" />
          <Tab label="User Activity" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Box sx={{ mb: 3 }}>
              <ChapterPerformanceChart />
            </Box>
            <TopChaptersTable chapters={mockChapterStats} />
          </Grid>
          <Grid item xs={12} lg={4}>
            <Box sx={{ mb: 3 }}>
              <SystemHealthPanel health={mockSystemHealth} />
            </Box>
            <RecentActivityPanel activities={mockRecentActivity} />
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info">
              Content analytics dashboard coming soon...
            </Alert>
          </Grid>
        </Grid>
      )}

      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <SystemHealthPanel health={mockSystemHealth} />
          </Grid>
          <Grid item xs={12} md={6}>
            <Alert severity="info">
              Detailed system monitoring coming soon...
            </Alert>
          </Grid>
        </Grid>
      )}

      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <RecentActivityPanel activities={mockRecentActivity} />
          </Grid>
        </Grid>
      )}
    </DashboardContainer>
  );
};

export default NeurosurgicalDashboard;
