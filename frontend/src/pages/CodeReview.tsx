import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  BugReport as BugIcon,
  Security as SecurityIcon,
  Code as CodeIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api';

interface ReviewSession {
  session_id: string;
  status: string;
  total_files: number;
  processed_files: number;
  total_issues: number;
  started_at: string;
  completed_at?: string;
  error_message?: string;
}

interface CodeReviewItem {
  id: number;
  file_path: string;
  line_number?: number;
  review_type: string;
  severity: string;
  title: string;
  description: string;
  suggestion?: string;
  ai_confidence: number;
  status: string;
  created_at: string;
}

const CodeReview: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<ReviewSession | null>(null);
  const [reviews, setReviews] = useState<CodeReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      fetchReviewData();
      // Poll for updates if session is still running
      const interval = setInterval(() => {
        if (session?.status === 'running' || session?.status === 'pending') {
          fetchReviewData();
        }
      }, 2000);
      
      return () => clearInterval(interval);
    }
  }, [sessionId, session?.status]);

  const fetchReviewData = async () => {
    try {
      setLoading(true);
      const [sessionData, reviewsData] = await Promise.all([
        apiService.getReviewSession(sessionId!),
        apiService.getReviewResults(sessionId!)
      ]);
      setSession(sessionData);
      setReviews(reviewsData);
    } catch (err) {
      setError('Failed to load review data');
      console.error('Review error:', err);
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  if (loading && !session) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!session) {
    return <Alert severity="info">Review session not found</Alert>;
  }

  const progress = session.total_files > 0 ? (session.processed_files / session.total_files) * 100 : 0;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Code Review Results
      </Typography>

      {/* Session Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Session: {session.session_id}
            </Typography>
            <Chip
              label={session.status}
              color={getStatusColor(session.status) as any}
            />
          </Box>
          
          {session.status === 'running' && (
            <Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Processing files: {session.processed_files} / {session.total_files}
              </Typography>
              <LinearProgress variant="determinate" value={progress} />
            </Box>
          )}
          
          {session.status === 'completed' && (
            <Typography variant="body2" color="textSecondary">
              Completed: {new Date(session.completed_at!).toLocaleString()}
            </Typography>
          )}
          
          {session.error_message && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {session.error_message}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Review Results */}
      {session.status === 'completed' && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Found {session.total_issues} issues across {session.total_files} files
          </Typography>

          {reviews.length === 0 ? (
            <Alert severity="success">
              No issues found! Great job on the code quality.
            </Alert>
          ) : (
            <Box>
              {/* Group reviews by file */}
              {Object.entries(
                reviews.reduce((acc, review) => {
                  if (!acc[review.file_path]) {
                    acc[review.file_path] = [];
                  }
                  acc[review.file_path].push(review);
                  return acc;
                }, {} as Record<string, CodeReviewItem[]>)
              ).map(([filePath, fileReviews]) => (
                <Accordion key={filePath} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" width="100%">
                      <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                        {filePath}
                      </Typography>
                      <Chip label={`${fileReviews.length} issues`} size="small" />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {fileReviews.map((review) => (
                      <Card key={review.id} sx={{ mb: 2 }}>
                        <CardContent>
                          <Box display="flex" alignItems="center" mb={1}>
                            {getTypeIcon(review.review_type)}
                            <Chip
                              label={review.severity}
                              size="small"
                              sx={{
                                backgroundColor: getSeverityColor(review.severity),
                                color: 'white',
                                ml: 1,
                                mr: 1,
                              }}
                            />
                            <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                              Line {review.line_number || 'N/A'}
                            </Typography>
                            <Chip
                              label={`${review.ai_confidence}% confidence`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                          
                          <Typography variant="h6" gutterBottom>
                            {review.title}
                          </Typography>
                          
                          <Typography variant="body2" color="textSecondary" paragraph>
                            {review.description}
                          </Typography>
                          
                          {review.suggestion && (
                            <Box>
                              <Typography variant="subtitle2" gutterBottom>
                                Suggestion:
                              </Typography>
                              <Box
                                sx={{
                                  backgroundColor: '#f5f5f5',
                                  p: 1,
                                  borderRadius: 1,
                                  fontFamily: 'monospace',
                                }}
                              >
                                {review.suggestion}
                              </Box>
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default CodeReview;
