import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  BugReport as BugIcon,
  Security as SecurityIcon,
  Code as CodeIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { apiService } from '../services/api';

interface DashboardStats {
  overview: {
    total_repositories: number;
    total_pull_requests: number;
    total_reviews: number;
    total_sessions: number;
  };
  recent_activity: {
    pull_requests_week: number;
    reviews_week: number;
    sessions_week: number;
  };
  issue_breakdown: {
    by_type: Record<string, number>;
    by_severity: Record<string, number>;
  };
  top_repositories: Array<{
    name: string;
    pr_count: number;
    review_count: number;
  }>;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, trendsData] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getTrendsData()
      ]);
      setStats(statsData);
      setTrends(trendsData);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return '#d32f2f';
      case 'high': return '#f57c00';
      case 'medium': return '#fbc02d';
      case 'low': return '#388e3c';
      default: return '#757575';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'bug': return <BugIcon />;
      case 'security': return <SecurityIcon />;
      case 'quality': return <CodeIcon />;
      default: return <AssessmentIcon />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!stats) {
    return <Alert severity="info">No data available</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <StorageIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Repositories
                  </Typography>
                  <Typography variant="h4">
                    {stats.overview.total_repositories}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CodeIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Pull Requests
                  </Typography>
                  <Typography variant="h4">
                    {stats.overview.total_pull_requests}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AssessmentIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Reviews
                  </Typography>
                  <Typography variant="h4">
                    {stats.overview.total_reviews}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <BugIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Sessions
                  </Typography>
                  <Typography variant="h4">
                    {stats.overview.total_sessions}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3}>
        {/* Trends Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Activity Trends (Last 30 Days)
              </Typography>
              {trends && (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trends.daily_reviews}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="count" stroke="#1976d2" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Issue Breakdown */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Issues by Type
              </Typography>
              {Object.entries(stats.issue_breakdown.by_type).map(([type, count]) => (
                <Box key={type} display="flex" alignItems="center" mb={1}>
                  {getTypeIcon(type)}
                  <Typography variant="body2" sx={{ ml: 1, mr: 2 }}>
                    {type}
                  </Typography>
                  <Chip label={count} size="small" />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Severity Breakdown */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Issues by Severity
              </Typography>
              {Object.entries(stats.issue_breakdown.by_severity).map(([severity, count]) => (
                <Box key={severity} display="flex" alignItems="center" mb={2}>
                  <Chip
                    label={severity}
                    size="small"
                    sx={{
                      backgroundColor: getSeverityColor(severity),
                      color: 'white',
                      mr: 2,
                    }}
                  />
                  <Typography variant="body2" sx={{ flexGrow: 1 }}>
                    {count} issues
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(count / Math.max(...Object.values(stats.issue_breakdown.by_severity))) * 100}
                    sx={{ width: 100 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Top Repositories */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Repositories
              </Typography>
              {stats.top_repositories.map((repo, index) => (
                <Box key={repo.name} display="flex" alignItems="center" mb={2}>
                  <Typography variant="body2" sx={{ mr: 2, minWidth: 30 }}>
                    {index + 1}.
                  </Typography>
                  <Typography variant="body2" sx={{ flexGrow: 1 }}>
                    {repo.name}
                  </Typography>
                  <Chip label={`${repo.pr_count} PRs`} size="small" sx={{ mr: 1 }} />
                  <Chip label={`${repo.review_count} reviews`} size="small" />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
