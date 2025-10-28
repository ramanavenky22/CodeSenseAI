"""
Dashboard API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.database import get_db, Repository, PullRequest, CodeReview, ReviewSession

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    try:
        # Basic counts
        total_repos = db.query(Repository).filter(Repository.is_active == True).count()
        total_prs = db.query(PullRequest).count()
        total_reviews = db.query(CodeReview).count()
        total_sessions = db.query(ReviewSession).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_prs = db.query(PullRequest).filter(
            PullRequest.created_at >= week_ago
        ).count()
        
        recent_reviews = db.query(CodeReview).filter(
            CodeReview.created_at >= week_ago
        ).count()
        
        recent_sessions = db.query(ReviewSession).filter(
            ReviewSession.started_at >= week_ago
        ).count()
        
        # Issue breakdown by type
        issue_types = db.query(
            CodeReview.review_type,
            func.count(CodeReview.id).label('count')
        ).group_by(CodeReview.review_type).all()
        
        # Issue breakdown by severity
        issue_severities = db.query(
            CodeReview.severity,
            func.count(CodeReview.id).label('count')
        ).group_by(CodeReview.severity).all()
        
        # Repository activity
        repo_activity = db.query(
            Repository.name,
            func.count(PullRequest.id).label('pr_count'),
            func.count(CodeReview.id).label('review_count')
        ).join(PullRequest).join(CodeReview).group_by(
            Repository.id, Repository.name
        ).order_by(desc('pr_count')).limit(10).all()
        
        return {
            "overview": {
                "total_repositories": total_repos,
                "total_pull_requests": total_prs,
                "total_reviews": total_reviews,
                "total_sessions": total_sessions
            },
            "recent_activity": {
                "pull_requests_week": recent_prs,
                "reviews_week": recent_reviews,
                "sessions_week": recent_sessions
            },
            "issue_breakdown": {
                "by_type": {item.review_type: item.count for item in issue_types},
                "by_severity": {item.severity: item.count for item in issue_severities}
            },
            "top_repositories": [
                {
                    "name": repo.name,
                    "pr_count": repo.pr_count,
                    "review_count": repo.review_count
                }
                for repo in repo_activity
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_trends_data(days: int = 30, db: Session = Depends(get_db)):
    """Get trends data for charts"""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily PR trends
        daily_prs = db.query(
            func.date(PullRequest.created_at).label('date'),
            func.count(PullRequest.id).label('count')
        ).filter(
            PullRequest.created_at >= start_date
        ).group_by(
            func.date(PullRequest.created_at)
        ).order_by('date').all()
        
        # Daily review trends
        daily_reviews = db.query(
            func.date(CodeReview.created_at).label('date'),
            func.count(CodeReview.id).label('count')
        ).filter(
            CodeReview.created_at >= start_date
        ).group_by(
            func.date(CodeReview.created_at)
        ).order_by('date').all()
        
        # Issue trends by type
        issue_trends = db.query(
            func.date(CodeReview.created_at).label('date'),
            CodeReview.review_type,
            func.count(CodeReview.id).label('count')
        ).filter(
            CodeReview.created_at >= start_date
        ).group_by(
            func.date(CodeReview.created_at),
            CodeReview.review_type
        ).order_by('date').all()
        
        return {
            "daily_prs": [
                {"date": str(item.date), "count": item.count}
                for item in daily_prs
            ],
            "daily_reviews": [
                {"date": str(item.date), "count": item.count}
                for item in daily_reviews
            ],
            "issue_trends": [
                {
                    "date": str(item.date),
                    "type": item.review_type,
                    "count": item.count
                }
                for item in issue_trends
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting trends data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/repositories/{repo_id}/analytics")
async def get_repository_analytics(repo_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific repository"""
    
    try:
        repository = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Repository stats
        pr_count = db.query(PullRequest).filter(
            PullRequest.repository_id == repo_id
        ).count()
        
        review_count = db.query(CodeReview).filter(
            CodeReview.repository_id == repo_id
        ).count()
        
        # Issue breakdown
        issue_types = db.query(
            CodeReview.review_type,
            func.count(CodeReview.id).label('count')
        ).filter(
            CodeReview.repository_id == repo_id
        ).group_by(CodeReview.review_type).all()
        
        # Recent PRs
        recent_prs = db.query(PullRequest).filter(
            PullRequest.repository_id == repo_id
        ).order_by(desc(PullRequest.created_at)).limit(10).all()
        
        # Top files with issues
        file_issues = db.query(
            CodeReview.file_path,
            func.count(CodeReview.id).label('count')
        ).filter(
            CodeReview.repository_id == repo_id
        ).group_by(CodeReview.file_path).order_by(
            desc('count')
        ).limit(10).all()
        
        return {
            "repository": {
                "id": repository.id,
                "name": repository.name,
                "full_name": repository.full_name,
                "owner": repository.owner,
                "url": repository.url
            },
            "stats": {
                "pull_requests": pr_count,
                "reviews": review_count,
                "issue_types": {item.review_type: item.count for item in issue_types}
            },
            "recent_pull_requests": [
                {
                    "id": pr.id,
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "author": pr.author,
                    "created_at": pr.created_at.isoformat()
                }
                for pr in recent_prs
            ],
            "top_files_with_issues": [
                {
                    "file_path": file.file_path,
                    "issue_count": file.count
                }
                for file in file_issues
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting repository analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_recent_sessions(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent review sessions"""
    
    try:
        sessions = db.query(ReviewSession).order_by(
            desc(ReviewSession.started_at)
        ).limit(limit).all()
        
        return [
            {
                "id": session.id,
                "session_id": session.session_id,
                "repository_id": session.repository_id,
                "pull_request_id": session.pull_request_id,
                "status": session.status,
                "total_files": session.total_files,
                "processed_files": session.processed_files,
                "total_issues": session.total_issues,
                "started_at": session.started_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "error_message": session.error_message
            }
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error getting recent sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
