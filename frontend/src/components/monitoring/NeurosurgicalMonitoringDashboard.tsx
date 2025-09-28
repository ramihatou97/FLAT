/**
 * Neurosurgical Monitoring Dashboard
 * Real-time system health monitoring with neurosurgical platform focus
 */

import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Database,
  Brain,
  Zap,
  TrendingUp,
  TrendingDown,
  Shield,
  Server,
  BarChart3,
  RefreshCw,
  AlertCircle,
  Settings,
  Eye,
  DollarSign,
  Cpu,
  HardDrive,
  Wifi
} from 'lucide-react';

interface SystemHealth {
  overall_healthy: boolean;
  checks: Record<string, any>;
  uptime_seconds: number;
  timestamp: string;
}

interface SystemMetrics {
  cpu: { percent: number; count: number };
  memory: { total_mb: number; used_mb: number; percent: number };
  disk: { total_gb: number; used_gb: number; percent: number };
  process: { cpu_percent: number; memory_mb: number; threads: number };
}

interface AIServiceMetrics {
  [key: string]: {
    status: string;
    circuit_breaker: { state: string; failure_count: number; can_call: boolean };
    performance: { avg_response_time_ms: number; success_rate: number; calls_today: number };
    cost: { estimated_daily_cost: number; budget_remaining: number };
  };
}

interface Alert {
  id: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: string;
  acknowledged?: boolean;
}

const NeurosurgicalMonitoringDashboard: React.FC = () => {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [aiMetrics, setAIMetrics] = useState<AIServiceMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds

  useEffect(() => {
    fetchDashboardData();

    if (autoRefresh) {
      const interval = setInterval(fetchDashboardData, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch all monitoring data concurrently
      const [healthRes, metricsRes, aiRes, alertsRes] = await Promise.all([
        fetch('/api/monitoring/health/detailed'),
        fetch('/api/monitoring/metrics/system'),
        fetch('/api/monitoring/metrics/ai-services'),
        fetch('/api/monitoring/alerts')
      ]);

      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setSystemHealth(healthData.details);
      }

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setSystemMetrics(metricsData.metrics);
      }

      if (aiRes.ok) {
        const aiData = await aiRes.json();
        setAIMetrics(aiData.ai_services);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.alerts);
      }

    } catch (error) {
      console.error('Failed to fetch monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await fetch(`/api/monitoring/alerts/acknowledge/${alertId}`, { method: 'POST' });
      setAlerts(prev => prev.map(alert =>
        alert.id === alertId ? { ...alert, acknowledged: true } : alert
      ));
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'available':
        return 'text-green-600 bg-green-100';
      case 'warning':
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy':
      case 'error':
      case 'circuit_open':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'available':
        return <CheckCircle className="w-4 h-4" />;
      case 'warning':
      case 'degraded':
        return <AlertTriangle className="w-4 h-4" />;
      case 'unhealthy':
      case 'error':
      case 'circuit_open':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const renderSystemOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-full ${systemHealth?.overall_healthy ? 'bg-green-100' : 'bg-red-100'}`}>
            <Activity className={`w-5 h-5 ${systemHealth?.overall_healthy ? 'text-green-600' : 'text-red-600'}`} />
          </div>
          <div>
            <h3 className="font-semibold">System Status</h3>
            <p className={`text-sm ${systemHealth?.overall_healthy ? 'text-green-600' : 'text-red-600'}`}>
              {systemHealth?.overall_healthy ? 'Healthy' : 'Issues Detected'}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-full bg-blue-100">
            <Clock className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold">Uptime</h3>
            <p className="text-sm text-gray-600">
              {systemHealth ? formatUptime(systemHealth.uptime_seconds) : '--'}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-full bg-purple-100">
            <Brain className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="font-semibold">AI Services</h3>
            <p className="text-sm text-gray-600">
              {aiMetrics ? Object.values(aiMetrics).filter(s => s.status === 'healthy').length : 0}/
              {aiMetrics ? Object.keys(aiMetrics).length : 0} Active
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-full ${alerts.filter(a => !a.acknowledged).length > 0 ? 'bg-red-100' : 'bg-green-100'}`}>
            <AlertTriangle className={`w-5 h-5 ${alerts.filter(a => !a.acknowledged).length > 0 ? 'text-red-600' : 'text-green-600'}`} />
          </div>
          <div>
            <h3 className="font-semibold">Active Alerts</h3>
            <p className="text-sm text-gray-600">
              {alerts.filter(a => !a.acknowledged).length} Unacknowledged
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSystemMetrics = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-blue-600" />
            <span>CPU Usage</span>
          </h3>
          <span className="text-sm text-gray-500">
            {systemMetrics?.cpu.count} cores
          </span>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm">Usage</span>
            <span className="text-sm font-medium">{systemMetrics?.cpu.percent.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                (systemMetrics?.cpu.percent || 0) > 80 ? 'bg-red-500' :
                (systemMetrics?.cpu.percent || 0) > 60 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${systemMetrics?.cpu.percent || 0}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold flex items-center space-x-2">
            <Database className="w-4 h-4 text-green-600" />
            <span>Memory</span>
          </h3>
          <span className="text-sm text-gray-500">
            {systemMetrics?.memory.total_mb.toFixed(0)} MB
          </span>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm">Used</span>
            <span className="text-sm font-medium">
              {systemMetrics?.memory.used_mb.toFixed(0)} MB ({systemMetrics?.memory.percent.toFixed(1)}%)
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                (systemMetrics?.memory.percent || 0) > 85 ? 'bg-red-500' :
                (systemMetrics?.memory.percent || 0) > 70 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${systemMetrics?.memory.percent || 0}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold flex items-center space-x-2">
            <HardDrive className="w-4 h-4 text-purple-600" />
            <span>Disk Storage</span>
          </h3>
          <span className="text-sm text-gray-500">
            {systemMetrics?.disk.total_gb.toFixed(0)} GB
          </span>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm">Used</span>
            <span className="text-sm font-medium">
              {systemMetrics?.disk.used_gb.toFixed(1)} GB ({systemMetrics?.disk.percent.toFixed(1)}%)
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                (systemMetrics?.disk.percent || 0) > 90 ? 'bg-red-500' :
                (systemMetrics?.disk.percent || 0) > 75 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${systemMetrics?.disk.percent || 0}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAIServices = () => (
    <div className="bg-white p-6 rounded-lg border mb-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <Brain className="w-5 h-5 text-purple-600" />
        <span>Neurosurgical AI Services</span>
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {aiMetrics && Object.entries(aiMetrics).map(([service, metrics]) => (
          <div key={service} className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium capitalize">{service}</h4>
              <div className={`px-2 py-1 rounded-full text-xs ${getStatusColor(metrics.status)}`}>
                <div className="flex items-center space-x-1">
                  {getStatusIcon(metrics.status)}
                  <span>{metrics.status}</span>
                </div>
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Response Time</span>
                <span className="font-medium">{metrics.performance.avg_response_time_ms.toFixed(0)}ms</span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-600">Success Rate</span>
                <span className="font-medium">{metrics.performance.success_rate.toFixed(1)}%</span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-600">Calls Today</span>
                <span className="font-medium">{metrics.performance.calls_today}</span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-600">Circuit State</span>
                <span className={`font-medium ${
                  metrics.circuit_breaker.state === 'CLOSED' ? 'text-green-600' :
                  metrics.circuit_breaker.state === 'HALF_OPEN' ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {metrics.circuit_breaker.state}
                </span>
              </div>

              <div className="pt-2 border-t">
                <div className="flex justify-between">
                  <span className="text-gray-600">Daily Cost</span>
                  <span className="font-medium">${metrics.cost.estimated_daily_cost.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Budget Left</span>
                  <span className="font-medium">${metrics.cost.budget_remaining.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAlerts = () => (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <AlertTriangle className="w-5 h-5 text-orange-600" />
        <span>System Alerts</span>
      </h3>

      {alerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
          <p>No active alerts. System running normally.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map(alert => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border-l-4 ${
                alert.level === 'critical' ? 'border-red-500 bg-red-50' :
                alert.level === 'error' ? 'border-red-400 bg-red-50' :
                alert.level === 'warning' ? 'border-yellow-500 bg-yellow-50' :
                'border-blue-500 bg-blue-50'
              } ${alert.acknowledged ? 'opacity-60' : ''}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      alert.level === 'critical' ? 'bg-red-100 text-red-800' :
                      alert.level === 'error' ? 'bg-red-100 text-red-800' :
                      alert.level === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alert.level.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm">{alert.message}</p>
                </div>

                {!alert.acknowledged && (
                  <button
                    onClick={() => acknowledgeAlert(alert.id)}
                    className="ml-4 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Neurosurgical Platform Monitoring</h2>
          <p className="text-gray-600">Real-time system health and performance monitoring</p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">Auto-refresh</label>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-1 text-xs rounded ${
                autoRefresh ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
              }`}
            >
              {autoRefresh ? 'ON' : 'OFF'}
            </button>
          </div>

          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
            className="px-3 py-1 text-sm border border-gray-300 rounded"
          >
            <option value={10}>10s</option>
            <option value={30}>30s</option>
            <option value={60}>1m</option>
            <option value={300}>5m</option>
          </select>

          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* System Overview */}
      {renderSystemOverview()}

      {/* System Metrics */}
      {renderSystemMetrics()}

      {/* AI Services */}
      {renderAIServices()}

      {/* Alerts */}
      {renderAlerts()}

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg flex items-center space-x-3">
            <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
            <span>Loading monitoring data...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default NeurosurgicalMonitoringDashboard;