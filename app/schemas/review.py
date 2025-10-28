"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ReviewType(str, Enum):
    """Review type enumeration"""
    BUG = "bug"
    SECURITY = "security"
    QUALITY = "quality"
    SUGGESTION = "suggestion"
    SUMMARY = "summary"

class Severity(str, Enum):
    """Severity level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    INFO = "info"

class FileInfo(BaseModel):
    """File information for analysis"""
    path: str = Field(..., description="File path")
    language: Optional[str] = Field(None, description="Programming language")
    changed_lines: Optional[List[int]] = Field(None, description="Changed line numbers")

class ReviewRequest(BaseModel):
    """Request model for code review"""
    repository_id: int = Field(..., description="Repository ID")
    pull_request_id: int = Field(..., description="Pull request ID")
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    pr_number: int = Field(..., description="Pull request number")
    pr_title: str = Field(..., description="Pull request title")
    head_sha: str = Field(..., description="Head commit SHA")
    base_sha: str = Field(..., description="Base commit SHA")
    files: List[FileInfo] = Field(..., description="Files to analyze")

class CodeReviewItem(BaseModel):
    """Individual code review item"""
    id: int
    file_path: str
    line_number: Optional[int]
    review_type: ReviewType
    severity: Severity
    title: str
    description: str
    suggestion: Optional[str]
    ai_confidence: int = Field(..., ge=0, le=100)
    status: str = "open"
    created_at: datetime

class ReviewSessionResponse(BaseModel):
    """Response model for review session"""
    session_id: str
    status: str
    total_files: Optional[int] = None
    processed_files: Optional[int] = None
    total_issues: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    message: Optional[str] = None

class AnalysisResult(BaseModel):
    """Analysis result model"""
    file_path: str
    language: str
    ai_analysis: Dict[str, Any]
    static_analysis: Dict[str, Any]
    timestamp: str

class WebhookPayload(BaseModel):
    """GitHub webhook payload model"""
    action: str
    pull_request: Optional[Dict[str, Any]] = None
    repository: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None

class RepositoryInfo(BaseModel):
    """Repository information model"""
    id: int
    github_id: int
    name: str
    full_name: str
    owner: str
    url: str
    created_at: datetime

class PullRequestInfo(BaseModel):
    """Pull request information model"""
    id: int
    github_id: int
    number: int
    title: str
    state: str
    author: str
    created_at: datetime
    updated_at: datetime

class DashboardStats(BaseModel):
    """Dashboard statistics model"""
    overview: Dict[str, int]
    recent_activity: Dict[str, int]
    issue_breakdown: Dict[str, Dict[str, int]]
    top_repositories: List[Dict[str, Any]]

class TrendsData(BaseModel):
    """Trends data model"""
    daily_prs: List[Dict[str, Any]]
    daily_reviews: List[Dict[str, Any]]
    issue_trends: List[Dict[str, Any]]

class RepositoryAnalytics(BaseModel):
    """Repository analytics model"""
    repository: Dict[str, Any]
    stats: Dict[str, Any]
    recent_pull_requests: List[Dict[str, Any]]
    top_files_with_issues: List[Dict[str, Any]]

class ReviewSessionInfo(BaseModel):
    """Review session information model"""
    id: int
    session_id: str
    repository_id: int
    pull_request_id: int
    status: str
    total_files: int
    processed_files: int
    total_issues: int
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
