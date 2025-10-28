"""
GitHub Webhook API Routes
"""

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import json
import logging
from typing import Dict, Any

from app.core.database import get_db, Repository, PullRequest
from app.services.github_service import GitHubService
from app.schemas.webhook import WebhookPayload

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize GitHub service
github_service = GitHubService()

@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle GitHub webhook events"""
    
    try:
        # Get request body and signature
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        event_type = request.headers.get("X-GitHub-Event", "")
        
        # Verify webhook signature
        if not github_service.verify_webhook_signature(body, signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        payload = json.loads(body.decode('utf-8'))
        
        logger.info(f"Received GitHub webhook: {event_type}")
        
        # Handle different event types
        if event_type == "pull_request":
            await _handle_pull_request_event(payload, background_tasks, db)
        elif event_type == "push":
            await _handle_push_event(payload, background_tasks, db)
        elif event_type == "repository":
            await _handle_repository_event(payload, background_tasks, db)
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return {"status": "success", "event": event_type}
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _handle_pull_request_event(payload: Dict[str, Any], background_tasks: BackgroundTasks, db: Session):
    """Handle pull request webhook events"""
    
    try:
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        repo_data = payload.get("repository", {})
        
        # Extract repository info
        owner = repo_data.get("owner", {}).get("login")
        repo_name = repo_data.get("name")
        repo_full_name = repo_data.get("full_name")
        
        if not all([owner, repo_name, repo_full_name]):
            logger.error("Missing repository information in webhook")
            return
        
        # Get or create repository record
        repository = db.query(Repository).filter(
            Repository.full_name == repo_full_name
        ).first()
        
        if not repository:
            repository = Repository(
                github_id=repo_data.get("id"),
                name=repo_name,
                full_name=repo_full_name,
                owner=owner,
                url=repo_data.get("html_url")
            )
            db.add(repository)
            db.commit()
            db.refresh(repository)
        
        # Handle different PR actions
        if action in ["opened", "synchronize"]:
            # Get or create pull request record
            pr_number = pr_data.get("number")
            pr = db.query(PullRequest).filter(
                PullRequest.github_id == pr_data.get("id")
            ).first()
            
            if not pr:
                pr = PullRequest(
                    github_id=pr_data.get("id"),
                    repository_id=repository.id,
                    number=pr_number,
                    title=pr_data.get("title"),
                    body=pr_data.get("body"),
                    state=pr_data.get("state"),
                    author=pr_data.get("user", {}).get("login"),
                    head_sha=pr_data.get("head", {}).get("sha"),
                    base_sha=pr_data.get("base", {}).get("sha")
                )
                db.add(pr)
                db.commit()
                db.refresh(pr)
            else:
                # Update existing PR
                pr.title = pr_data.get("title")
                pr.body = pr_data.get("body")
                pr.state = pr_data.get("state")
                pr.head_sha = pr_data.get("head", {}).get("sha")
                pr.base_sha = pr_data.get("base", {}).get("sha")
                db.commit()
            
            # Trigger code analysis for new/updated PRs
            if action == "opened" or (action == "synchronize" and pr_data.get("draft") == False):
                background_tasks.add_task(
                    _trigger_code_analysis,
                    repository.id,
                    pr.id,
                    owner,
                    repo_name,
                    pr_number,
                    pr_data.get("title", ""),
                    pr_data.get("head", {}).get("sha"),
                    pr_data.get("base", {}).get("sha")
                )
        
        elif action == "closed":
            # Update PR state
            pr = db.query(PullRequest).filter(
                PullRequest.github_id == pr_data.get("id")
            ).first()
            
            if pr:
                pr.state = "closed"
                db.commit()
        
        logger.info(f"Processed PR {action} event for {repo_full_name}#{pr_data.get('number')}")
        
    except Exception as e:
        logger.error(f"Error handling PR event: {str(e)}")

async def _handle_push_event(payload: Dict[str, Any], background_tasks: BackgroundTasks, db: Session):
    """Handle push webhook events"""
    
    try:
        repo_data = payload.get("repository", {})
        commits = payload.get("commits", [])
        
        logger.info(f"Received push event for {repo_data.get('full_name')} with {len(commits)} commits")
        
        # Could trigger analysis for specific branches or commits
        # For now, just log the event
        
    except Exception as e:
        logger.error(f"Error handling push event: {str(e)}")

async def _handle_repository_event(payload: Dict[str, Any], background_tasks: BackgroundTasks, db: Session):
    """Handle repository webhook events"""
    
    try:
        action = payload.get("action")
        repo_data = payload.get("repository", {})
        
        if action == "created":
            # New repository added
            repository = Repository(
                github_id=repo_data.get("id"),
                name=repo_data.get("name"),
                full_name=repo_data.get("full_name"),
                owner=repo_data.get("owner", {}).get("login"),
                url=repo_data.get("html_url")
            )
            db.add(repository)
            db.commit()
            
            logger.info(f"Added new repository: {repo_data.get('full_name')}")
        
        elif action == "deleted":
            # Repository deleted
            repository = db.query(Repository).filter(
                Repository.full_name == repo_data.get("full_name")
            ).first()
            
            if repository:
                repository.is_active = False
                db.commit()
                
                logger.info(f"Deactivated repository: {repo_data.get('full_name')}")
        
    except Exception as e:
        logger.error(f"Error handling repository event: {str(e)}")

async def _trigger_code_analysis(
    repository_id: int,
    pr_id: int,
    owner: str,
    repo_name: str,
    pr_number: int,
    pr_title: str,
    head_sha: str,
    base_sha: str
):
    """Trigger code analysis for a pull request"""
    
    try:
        # Get PR files from GitHub
        files = await github_service.get_pull_request_files(owner, repo_name, pr_number)
        
        if not files:
            logger.warning(f"No files found for PR {owner}/{repo_name}#{pr_number}")
            return
        
        # Prepare file information
        file_info = []
        for file in files:
            if file["status"] in ["added", "modified"]:
                file_info.append({
                    "path": file["filename"],
                    "language": _detect_language(file["filename"]),
                    "changed_lines": _extract_changed_lines(file.get("patch", ""))
                })
        
        if not file_info:
            logger.info(f"No relevant files to analyze for PR {owner}/{repo_name}#{pr_number}")
            return
        
        # Import here to avoid circular imports
        from app.api.routes.reviews import _run_code_analysis
        from app.schemas.review import ReviewRequest
        
        # Create review request
        review_request = ReviewRequest(
            repository_id=repository_id,
            pull_request_id=pr_id,
            owner=owner,
            repo=repo_name,
            pr_number=pr_number,
            pr_title=pr_title,
            head_sha=head_sha,
            base_sha=base_sha,
            files=file_info
        )
        
        # Start analysis (this would normally be done through the API)
        logger.info(f"Starting code analysis for PR {owner}/{repo_name}#{pr_number}")
        
    except Exception as e:
        logger.error(f"Error triggering code analysis: {str(e)}")

def _detect_language(filename: str) -> str:
    """Detect programming language from filename"""
    
    extensions = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sh': 'shell',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.md': 'markdown',
        '.txt': 'text'
    }
    
    for ext, lang in extensions.items():
        if filename.lower().endswith(ext):
            return lang
    
    return 'unknown'

def _extract_changed_lines(patch: str) -> list:
    """Extract changed line numbers from git patch"""
    
    changed_lines = []
    
    if not patch:
        return changed_lines
    
    lines = patch.split('\n')
    for line in lines:
        if line.startswith('@@'):
            # Parse hunk header
            parts = line.split(' ')
            if len(parts) >= 3:
                line_info = parts[2]
                if line_info.startswith('+'):
                    try:
                        start_line = int(line_info.split(',')[0][1:])
                        changed_lines.append(start_line)
                    except (ValueError, IndexError):
                        continue
    
    return changed_lines
