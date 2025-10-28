"""
Code Review API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
import uuid
from datetime import datetime

from app.core.database import get_db, Repository, PullRequest, CodeReview, ReviewSession
from app.services.code_analysis import CodeAnalysisService
from app.services.github_service import GitHubService
from app.services.static_analysis import StaticAnalysisService
from app.schemas.review import (
    ReviewRequest, ReviewResponse, ReviewSessionResponse,
    CodeReviewItem, AnalysisResult
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
code_analysis_service = CodeAnalysisService()
github_service = GitHubService()
static_analysis_service = StaticAnalysisService()

@router.post("/analyze", response_model=ReviewSessionResponse)
async def analyze_pull_request(
    request: ReviewRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze a pull request for code issues"""
    
    try:
        # Create review session
        session_id = str(uuid.uuid4())
        review_session = ReviewSession(
            session_id=session_id,
            repository_id=request.repository_id,
            pull_request_id=request.pull_request_id,
            status="pending",
            total_files=len(request.files),
            metadata=request.dict()
        )
        db.add(review_session)
        db.commit()
        db.refresh(review_session)
        
        # Start background analysis
        background_tasks.add_task(
            _run_code_analysis,
            session_id,
            request,
            db
        )
        
        return ReviewSessionResponse(
            session_id=session_id,
            status="pending",
            message="Analysis started"
        )
        
    except Exception as e:
        logger.error(f"Error starting code analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}", response_model=ReviewSessionResponse)
async def get_review_session(session_id: str, db: Session = Depends(get_db)):
    """Get review session status and results"""
    
    session = db.query(ReviewSession).filter(ReviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Review session not found")
    
    return ReviewSessionResponse(
        session_id=session.session_id,
        status=session.status,
        total_files=session.total_files,
        processed_files=session.processed_files,
        total_issues=session.total_issues,
        started_at=session.started_at,
        completed_at=session.completed_at,
        error_message=session.error_message
    )

@router.get("/session/{session_id}/results", response_model=List[CodeReviewItem])
async def get_review_results(session_id: str, db: Session = Depends(get_db)):
    """Get detailed review results for a session"""
    
    session = db.query(ReviewSession).filter(ReviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Review session not found")
    
    # Get all reviews for this session
    reviews = db.query(CodeReview).filter(
        CodeReview.repository_id == session.repository_id,
        CodeReview.pull_request_id == session.pull_request_id
    ).all()
    
    return [
        CodeReviewItem(
            id=review.id,
            file_path=review.file_path,
            line_number=review.line_number,
            review_type=review.review_type,
            severity=review.severity,
            title=review.title,
            description=review.description,
            suggestion=review.suggestion,
            ai_confidence=review.ai_confidence,
            status=review.status,
            created_at=review.created_at
        )
        for review in reviews
    ]

@router.post("/manual", response_model=AnalysisResult)
async def analyze_code_manually(
    code: str,
    file_path: str,
    language: str,
    repository_name: str = "manual-analysis"
):
    """Manually analyze code without GitHub integration"""
    
    try:
        # Run AI analysis
        ai_result = await code_analysis_service.analyze_code(
            code=code,
            file_path=file_path,
            language=language,
            repository_name=repository_name,
            pr_title="Manual Analysis",
            changed_lines=[]
        )
        
        # Run static analysis
        static_result = await static_analysis_service.analyze_code(
            code=code,
            language=language,
            file_path=file_path
        )
        
        # Combine results
        combined_result = {
            "file_path": file_path,
            "language": language,
            "ai_analysis": ai_result,
            "static_analysis": static_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return AnalysisResult(**combined_result)
        
    except Exception as e:
        logger.error(f"Error in manual analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/repositories", response_model=List[Dict[str, Any]])
async def get_repositories(db: Session = Depends(get_db)):
    """Get all tracked repositories"""
    
    repositories = db.query(Repository).filter(Repository.is_active == True).all()
    
    return [
        {
            "id": repo.id,
            "github_id": repo.github_id,
            "name": repo.name,
            "full_name": repo.full_name,
            "owner": repo.owner,
            "url": repo.url,
            "created_at": repo.created_at.isoformat()
        }
        for repo in repositories
    ]

@router.get("/repositories/{repo_id}/pull-requests", response_model=List[Dict[str, Any]])
async def get_pull_requests(repo_id: int, db: Session = Depends(get_db)):
    """Get pull requests for a repository"""
    
    pull_requests = db.query(PullRequest).filter(
        PullRequest.repository_id == repo_id
    ).order_by(PullRequest.created_at.desc()).limit(50).all()
    
    return [
        {
            "id": pr.id,
            "github_id": pr.github_id,
            "number": pr.number,
            "title": pr.title,
            "state": pr.state,
            "author": pr.author,
            "created_at": pr.created_at.isoformat(),
            "updated_at": pr.updated_at.isoformat()
        }
        for pr in pull_requests
    ]

async def _run_code_analysis(session_id: str, request: ReviewRequest, db: Session):
    """Background task to run code analysis"""
    
    try:
        # Update session status
        session = db.query(ReviewSession).filter(ReviewSession.session_id == session_id).first()
        session.status = "running"
        db.commit()
        
        total_issues = 0
        
        # Analyze each file
        for i, file_info in enumerate(request.files):
            try:
                # Get file content from GitHub
                file_content = await github_service.get_file_content(
                    owner=request.owner,
                    repo=request.repo,
                    file_path=file_info["path"],
                    ref=request.head_sha
                )
                
                if not file_content:
                    logger.warning(f"Could not get content for {file_info['path']}")
                    continue
                
                # Run AI analysis
                ai_result = await code_analysis_service.analyze_code(
                    code=file_content,
                    file_path=file_info["path"],
                    language=file_info.get("language", "unknown"),
                    repository_name=f"{request.owner}/{request.repo}",
                    pr_title=request.pr_title,
                    changed_lines=file_info.get("changed_lines", [])
                )
                
                # Run static analysis
                static_result = await static_analysis_service.analyze_code(
                    code=file_content,
                    language=file_info.get("language", "unknown"),
                    file_path=file_info["path"]
                )
                
                # Save AI analysis results
                for bug in ai_result.get("bugs", []):
                    review = CodeReview(
                        repository_id=request.repository_id,
                        pull_request_id=request.pull_request_id,
                        file_path=file_info["path"],
                        line_number=bug.get("line"),
                        review_type="bug",
                        severity=bug.get("severity", "medium"),
                        title=bug.get("title", "Bug detected"),
                        description=bug.get("description", ""),
                        suggestion=bug.get("suggestion", ""),
                        ai_confidence=bug.get("confidence", 75),
                        metadata={"source": "ai", "analysis_type": "bug"}
                    )
                    db.add(review)
                    total_issues += 1
                
                # Save security issues
                for security_issue in ai_result.get("security_issues", []):
                    review = CodeReview(
                        repository_id=request.repository_id,
                        pull_request_id=request.pull_request_id,
                        file_path=file_info["path"],
                        line_number=security_issue.get("line"),
                        review_type="security",
                        severity=security_issue.get("severity", "high"),
                        title=security_issue.get("title", "Security issue"),
                        description=security_issue.get("description", ""),
                        suggestion=security_issue.get("suggestion", ""),
                        ai_confidence=security_issue.get("confidence", 85),
                        metadata={"source": "ai", "analysis_type": "security"}
                    )
                    db.add(review)
                    total_issues += 1
                
                # Save static analysis results
                for security_issue in static_result.get("security_issues", []):
                    review = CodeReview(
                        repository_id=request.repository_id,
                        pull_request_id=request.pull_request_id,
                        file_path=file_info["path"],
                        line_number=security_issue.get("line"),
                        review_type="security",
                        severity=security_issue.get("severity", "medium"),
                        title=security_issue.get("title", "Static analysis issue"),
                        description=security_issue.get("description", ""),
                        suggestion=security_issue.get("suggestion", ""),
                        ai_confidence=security_issue.get("confidence", 80),
                        metadata={"source": "static", "tool": security_issue.get("tool")}
                    )
                    db.add(review)
                    total_issues += 1
                
                # Update progress
                session.processed_files = i + 1
                session.total_issues = total_issues
                db.commit()
                
            except Exception as e:
                logger.error(f"Error analyzing file {file_info['path']}: {str(e)}")
                continue
        
        # Generate summary
        try:
            summary = await code_analysis_service.generate_review_summary(
                repository_name=f"{request.owner}/{request.repo}",
                pr_title=request.pr_title,
                analysis_results=[ai_result]  # Simplified for now
            )
            
            # Create summary review
            summary_review = CodeReview(
                repository_id=request.repository_id,
                pull_request_id=request.pull_request_id,
                file_path="SUMMARY",
                line_number=0,
                review_type="summary",
                severity="info",
                title="AI Code Review Summary",
                description=summary,
                suggestion="",
                ai_confidence=90,
                metadata={"source": "ai", "analysis_type": "summary"}
            )
            db.add(summary_review)
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
        
        # Complete session
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Code analysis completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error in background analysis: {str(e)}")
        session.status = "failed"
        session.error_message = str(e)
        db.commit()
