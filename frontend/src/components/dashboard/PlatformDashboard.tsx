import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Alert,
  Avatar,
  IconButton,
  Tooltip,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Api as ApiIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Cloud as CloudIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Launch as LaunchIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Update as UpdateIcon
} from '@mui/icons-material';

interface PlatformMetrics {
  systemHealth: 'healthy' | 'degraded' | 'unhealthy';
  apiResponseTime: number;
  uptime: string;
  totalRequests: number;
  activeUsers: number;
  errorRate: number;
  databaseStatus: boolean;
  redisStatus: boolean;
  aiProvidersStatus: { [key: string]: boolean };
  memoryUsage: number;
  diskUsage: number;
}

interface ServiceEndpoint {
  name: string;
  path: string;
  method: string;
  status: 'active' | 'inactive' | 'maintenance';
  responseTime: number;
  description: string;
}

const PlatformDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<PlatformMetrics | null>(null);
  const [services, setServices] = useState<ServiceEndpoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedPanel, setExpandedPanel] = useState<string | false>('overview');

  useEffect(() => {
    fetchPlatformData();
    const interval = setInterval(fetchPlatformData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchPlatformData = async () => {
    try {
      setRefreshing(true);

      // Fetch platform health and metrics from real monitoring APIs
      const [healthRes, keysRes, systemRes, apiRes, statusRes] = await Promise.all([
        fetch('/api/monitoring/health/detailed'),
        fetch('/api/keys/services/health'),
        fetch('/api/monitoring/metrics/system'),
        fetch('/api/monitoring/metrics/api-endpoints'),
        fetch('/api/monitoring/status/summary')
      ]);

      if (healthRes.ok) {
        const healthData = await healthRes.json();
        const keysData = keysRes.ok ? await keysRes.json() : null;
        const systemData = systemRes.ok ? await systemRes.json() : null;
        const apiData = apiRes.ok ? await apiRes.json() : null;
        const statusData = statusRes.ok ? await statusRes.json() : null;

        // Calculate real metrics from API responses
        const systemMetrics = systemData?.metrics || {};
        const apiMetrics = apiData?.api_endpoints || {};
        const statusSummary = statusData?.summary || {};

        // Create AI providers status object
        const aiProvidersStatus = {
          openai: keysData?.services?.openai?.health === 'healthy',
          gemini: keysData?.services?.gemini?.health === 'healthy',
          claude: keysData?.services?.claude?.health === 'healthy',
          perplexity: keysData?.services?.perplexity?.health === 'healthy'
        };

        setMetrics({
          systemHealth: healthData.status === 'healthy' ? 'healthy' : 'degraded',
          apiResponseTime: apiMetrics.average_response_time || 0,
          uptime: statusSummary.uptime_percentage || '0%',
          totalRequests: apiMetrics.total_requests || 0,
          activeUsers: statusSummary.active_sessions || 0,
          errorRate: apiMetrics.error_rate || 0,
          databaseStatus: healthData.details?.database || false,
          redisStatus: healthData.details?.redis || false,
          aiProvidersStatus,
          memoryUsage: systemMetrics.memory_usage_percent || 0,
          diskUsage: systemMetrics.disk_usage_percent || 0
        });

        // Set available services with real endpoint data
        const endpointMetrics = apiMetrics.endpoints || {};
        const hasActiveAiProviders = Object.values(aiProvidersStatus).some(Boolean);

        setServices([
          {
            name: 'Health Check',
            path: '/api/health',
            method: 'GET',
            status: healthData.status === 'healthy' ? 'active' : 'degraded',
            responseTime: endpointMetrics['/api/health']?.avg_response_time || 0,
            description: 'Basic health endpoint'
          },
          {
            name: 'Search API',
            path: '/api/search',
            method: 'POST',
            status: healthData.details?.semantic_search ? 'active' : 'inactive',
            responseTime: endpointMetrics['/api/search']?.avg_response_time || 0,
            description: 'Advanced semantic search'
          },
          {
            name: 'AI Generation',
            path: '/api/ai/generate',
            method: 'POST',
            status: hasActiveAiProviders ? 'active' : 'inactive',
            responseTime: endpointMetrics['/api/ai/generate']?.avg_response_time || 0,
            description: 'Multi-provider AI content generation'
          },
          {
            name: 'Literature Analysis',
            path: '/api/literature/analyze',
            method: 'POST',
            status: healthData.details?.literature_engine ? 'active' : 'inactive',
            responseTime: endpointMetrics['/api/literature/analyze']?.avg_response_time || 0,
            description: 'AI-powered literature analysis'
          },
          {
            name: 'Monitoring',
            path: '/api/monitoring',
            method: 'GET',
            status: 'active',
            responseTime: endpointMetrics['/api/monitoring']?.avg_response_time || 0,
            description: 'System monitoring and metrics'
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch platform data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleAccordionChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedPanel(isExpanded ? panel : false);
  };

  const getStatusIcon = (status: boolean | string) => {
    if (status === true || status === 'active') return <CheckIcon color="success" />;
    if (status === 'degraded' || status === 'maintenance') return <WarningIcon color="warning" />;
    return <ErrorIcon color="error" />;
  };

  const getStatusColor = (status: boolean | string) => {
    if (status === true || status === 'active') return 'success';
    if (status === 'degraded' || status === 'maintenance') return 'warning';
    return 'error';
  };

  const MetricCard = ({
    title,
    value,
    unit = '',
    icon,
    color = 'primary',
    trend
  }: {
    title: string;
    value: string | number;
    unit?: string;
    icon: React.ReactNode;
    color?: 'primary' | 'success' | 'warning' | 'error';
    trend?: 'up' | 'down' | 'stable';
  }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Avatar sx={{ bgcolor: `${color}.main` }}>
            {icon}
          </Avatar>
          {trend && (
            <Chip
              label={trend}
              size="small"
              color={trend === 'up' ? 'success' : trend === 'down' ? 'error' : 'default'}
            />
          )}
        </Box>
        <Typography variant="h4" component="div" color={`${color}.main`} fontWeight="bold">
          {value}{unit}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress size={60} />
        <Typography variant="h6" ml={2}>
          Loading Platform Dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3, backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      {/* Header */}
      <Box mb={4}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h3" component="h1" gutterBottom fontWeight="bold" color="primary.main">
              🏥 Medical Knowledge Platform
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Advanced AI-Powered Medical Intelligence System
            </Typography>
          </Box>
          <Box display="flex" alignItems="center">
            <Badge
              color={metrics?.systemHealth === 'healthy' ? 'success' : 'warning'}
              variant="dot"
              sx={{ mr: 2 }}
            >
              <Typography variant="body2" color="text.secondary">
                Status: {metrics?.systemHealth || 'Unknown'}
              </Typography>
            </Badge>
            <Tooltip title="Refresh Data">
              <IconButton
                onClick={fetchPlatformData}
                disabled={refreshing}
                color="primary"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* System Status Alert */}
        <Alert
          severity={metrics?.systemHealth === 'healthy' ? 'success' : 'warning'}
          sx={{ mb: 3 }}
        >
          <Typography variant="body1">
            <strong>Platform Status: </strong>
            {metrics?.systemHealth === 'healthy' ?
              '🟢 All systems operational - Platform ready for use' :
              '🟡 Some systems may be experiencing issues - Monitoring in progress'
            }
          </Typography>
        </Alert>
      </Box>

      {/* Key Metrics Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="API Response Time"
            value={metrics?.apiResponseTime || 0}
            unit="ms"
            icon={<SpeedIcon />}
            color="primary"
            trend="stable"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="System Uptime"
            value={metrics?.uptime || '0%'}
            icon={<CloudIcon />}
            color="success"
            trend="up"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Requests"
            value={(metrics?.totalRequests || 0).toLocaleString()}
            icon={<AnalyticsIcon />}
            color="primary"
            trend="up"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Error Rate"
            value={metrics?.errorRate || 0}
            unit="%"
            icon={<SecurityIcon />}
            color={metrics?.errorRate && metrics.errorRate > 1 ? 'warning' : 'success'}
            trend="stable"
          />
        </Grid>
      </Grid>

      {/* Detailed Information Panels */}
      <Grid container spacing={3}>
        {/* System Health Panel */}
        <Grid item xs={12} md={6}>
          <Accordion expanded={expandedPanel === 'overview'} onChange={handleAccordionChange('overview')}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center">
                <DashboardIcon sx={{ mr: 2 }} color="primary" />
                <Typography variant="h6">System Overview</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <List>
                <ListItem>
                  <ListItemIcon>{getStatusIcon(metrics?.databaseStatus)}</ListItemIcon>
                  <ListItemText
                    primary="Database Connection"
                    secondary={metrics?.databaseStatus ? 'Connected and responsive' : 'Connection issues detected'}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>{getStatusIcon(metrics?.redisStatus)}</ListItemIcon>
                  <ListItemText
                    primary="Redis Cache"
                    secondary={metrics?.redisStatus ? 'Cache operational' : 'Cache issues detected'}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon><MemoryIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary={`Memory Usage: ${metrics?.memoryUsage || 0}%`}
                    secondary={
                      <LinearProgress
                        variant="determinate"
                        value={metrics?.memoryUsage || 0}
                        color={metrics?.memoryUsage && metrics.memoryUsage > 80 ? 'warning' : 'primary'}
                        sx={{ mt: 1 }}
                      />
                    }
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon><StorageIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary={`Disk Usage: ${metrics?.diskUsage || 0}%`}
                    secondary={
                      <LinearProgress
                        variant="determinate"
                        value={metrics?.diskUsage || 0}
                        color={metrics?.diskUsage && metrics.diskUsage > 80 ? 'warning' : 'success'}
                        sx={{ mt: 1 }}
                      />
                    }
                  />
                </ListItem>
              </List>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* AI Providers Panel */}
        <Grid item xs={12} md={6}>
          <Accordion expanded={expandedPanel === 'ai'} onChange={handleAccordionChange('ai')}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center">
                <ApiIcon sx={{ mr: 2 }} color="primary" />
                <Typography variant="h6">AI Providers Status</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <List>
                {Object.entries(metrics?.aiProvidersStatus || {}).map(([provider, status]) => (
                  <React.Fragment key={provider}>
                    <ListItem>
                      <ListItemIcon>{getStatusIcon(status)}</ListItemIcon>
                      <ListItemText
                        primary={provider.charAt(0).toUpperCase() + provider.slice(1)}
                        secondary={status ? 'Service operational' : 'Service unavailable'}
                      />
                      <Chip
                        label={status ? 'Active' : 'Inactive'}
                        size="small"
                        color={getStatusColor(status) as any}
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* API Endpoints Panel */}
        <Grid item xs={12}>
          <Accordion expanded={expandedPanel === 'endpoints'} onChange={handleAccordionChange('endpoints')}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center">
                <NetworkIcon sx={{ mr: 2 }} color="primary" />
                <Typography variant="h6">API Endpoints</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {services.map((service, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                          <Typography variant="h6" component="div">
                            {service.name}
                          </Typography>
                          <Chip
                            label={service.status}
                            size="small"
                            color={getStatusColor(service.status) as any}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" mb={2}>
                          {service.description}
                        </Typography>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                          <Typography variant="caption" color="text.secondary">
                            {service.method} {service.path}
                          </Typography>
                          <Typography variant="caption" color="primary.main">
                            {service.responseTime}ms
                          </Typography>
                        </Box>
                        <Button
                          variant="outlined"
                          size="small"
                          fullWidth
                          endIcon={<LaunchIcon />}
                          onClick={() => window.open('/api/docs', '_blank')}
                        >
                          View in API Docs
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Quick Actions Panel */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              🚀 Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<ApiIcon />}
                  onClick={() => window.open('/api/docs', '_blank')}
                  sx={{ py: 2 }}
                >
                  API Documentation
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AnalyticsIcon />}
                  onClick={() => window.open('/api/monitoring/health/detailed', '_blank')}
                  sx={{ py: 2 }}
                >
                  Health Report
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<SettingsIcon />}
                  onClick={() => window.open('/api/keys/services/health', '_blank')}
                  sx={{ py: 2 }}
                >
                  API Key Status
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<UpdateIcon />}
                  onClick={fetchPlatformData}
                  disabled={refreshing}
                  sx={{ py: 2 }}
                >
                  Refresh Data
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PlatformDashboard;