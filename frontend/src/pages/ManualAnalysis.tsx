import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  BugReport as BugIcon,
  Security as SecurityIcon,
  Code as CodeIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiService } from '../services/api';

interface AnalysisResult {
  file_path: string;
  language: string;
  ai_analysis: {
    bugs: Array<{
      line: number;
      type: string;
      severity: string;
      title: string;
      description: string;
      suggestion: string;
    }>;
    security_issues: Array<{
      line: number;
      type: string;
      severity: string;
      title: string;
      description: string;
      suggestion: string;
    }>;
    quality_issues: Array<{
      line: number;
      type: string;
      severity: string;
      title: string;
      description: string;
      suggestion: string;
    }>;
  };
  static_analysis: {
    security_issues: Array<{
      line: number;
      type: string;
      severity: string;
      title: string;
      description: string;
      tool: string;
    }>;
    quality_issues: Array<{
      line: number;
      type: string;
      severity: string;
      title: string;
      description: string;
      tool: string;
    }>;
  };
  timestamp: string;
}

const ManualAnalysis: React.FC = () => {
  const [code, setCode] = useState('');
  const [filePath, setFilePath] = useState('');
  const [language, setLanguage] = useState('python');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some code to analyze');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await apiService.analyzeCodeManually(code, filePath || 'example.py', language);
      setAnalysisResult(result);
    } catch (err) {
      setError('Failed to analyze code');
      console.error('Analysis error:', err);
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

  const renderIssues = (issues: any[], title: string) => {
    if (!issues || issues.length === 0) return null;

    return (
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center">
            {getTypeIcon(title.toLowerCase())}
            <Typography variant="h6" sx={{ ml: 1 }}>
              {title} ({issues.length})
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {issues.map((issue, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Chip
                    label={issue.severity}
                    size="small"
                    sx={{
                      backgroundColor: getSeverityColor(issue.severity),
                      color: 'white',
                      mr: 1,
                    }}
                  />
                  <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                    Line {issue.line}
                  </Typography>
                  {issue.tool && (
                    <Chip label={issue.tool} size="small" variant="outlined" />
                  )}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {issue.title}
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {issue.description}
                </Typography>
                {issue.suggestion && (
                  <>
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
                      {issue.suggestion}
                    </Box>
                  </>
                )}
              </CardContent>
            </Card>
          ))}
        </AccordionDetails>
      </Accordion>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Manual Code Analysis
      </Typography>

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Code Input
              </Typography>
              
              <TextField
                fullWidth
                label="File Path"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="example.py"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                select
                label="Language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                SelectProps={{ native: true }}
                sx={{ mb: 2 }}
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="go">Go</option>
                <option value="rust">Rust</option>
              </TextField>
              
              <TextField
                fullWidth
                multiline
                rows={15}
                label="Code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Enter your code here..."
                sx={{ mb: 2 }}
              />
              
              <Button
                variant="contained"
                onClick={handleAnalyze}
                disabled={loading || !code.trim()}
                fullWidth
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze Code'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analysis Results
              </Typography>
              
              {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
              
              {analysisResult ? (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    File: {analysisResult.file_path}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Language: {analysisResult.language}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Analyzed: {new Date(analysisResult.timestamp).toLocaleString()}
                  </Typography>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  {renderIssues(analysisResult.ai_analysis.bugs, 'Bugs')}
                  {renderIssues(analysisResult.ai_analysis.security_issues, 'Security Issues')}
                  {renderIssues(analysisResult.ai_analysis.quality_issues, 'Quality Issues')}
                  {renderIssues(analysisResult.static_analysis.security_issues, 'Static Security Issues')}
                  {renderIssues(analysisResult.static_analysis.quality_issues, 'Static Quality Issues')}
                  
                  {(!analysisResult.ai_analysis.bugs?.length &&
                    !analysisResult.ai_analysis.security_issues?.length &&
                    !analysisResult.ai_analysis.quality_issues?.length &&
                    !analysisResult.static_analysis.security_issues?.length &&
                    !analysisResult.static_analysis.quality_issues?.length) && (
                    <Alert severity="success">
                      No issues found! Your code looks good.
                    </Alert>
                  )}
                </Box>
              ) : (
                <Alert severity="info">
                  Enter code above and click "Analyze Code" to see results.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ManualAnalysis;
