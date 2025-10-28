import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

interface Repository {
  id: number;
  github_id: number;
  name: string;
  full_name: string;
  owner: string;
  url: string;
  created_at: string;
}

interface PullRequest {
  id: number;
  github_id: number;
  number: number;
  title: string;
  state: string;
  author: string;
  created_at: string;
  updated_at: string;
}

const Repositories: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRepositories();
  }, []);

  const fetchRepositories = async () => {
    try {
      setLoading(true);
      const data = await apiService.getRepositories();
      setRepositories(data);
    } catch (err) {
      setError('Failed to load repositories');
      console.error('Repositories error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStateColor = (state: string) => {
    switch (state.toLowerCase()) {
      case 'open': return 'success';
      case 'closed': return 'default';
      case 'merged': return 'primary';
      default: return 'default';
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

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Repositories
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate('/manual')}
        >
          Manual Analysis
        </Button>
      </Box>

      <Grid container spacing={3}>
        {repositories.map((repo) => (
          <Grid item xs={12} md={6} lg={4} key={repo.id}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {repo.name}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {repo.owner}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Created: {new Date(repo.created_at).toLocaleDateString()}
                </Typography>
                <Box display="flex" gap={1} flexWrap="wrap">
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => window.open(repo.url, '_blank')}
                  >
                    View on GitHub
                  </Button>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => navigate(`/repository/${repo.id}`)}
                  >
                    View Analytics
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {repositories.length === 0 && (
        <Alert severity="info">
          No repositories found. Make sure you have connected your GitHub account and repositories are being tracked.
        </Alert>
      )}
    </Box>
  );
};

export default Repositories;
