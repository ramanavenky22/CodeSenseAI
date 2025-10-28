"""
GitHub Integration Service
"""

import hmac
import hashlib
import json
import logging
from typing import Dict, List, Any, Optional
from github import Github, GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository
from github.Commit import Commit
from app.core.config import settings

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for GitHub API integration"""
    
    def __init__(self):
        """Initialize GitHub service"""
        self.github = Github(settings.GITHUB_TOKEN)
        self.webhook_secret = settings.GITHUB_WEBHOOK_SECRET
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        try:
            expected_signature = 'sha256=' + hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
    
    async def get_repository(self, owner: str, repo: str) -> Optional[Repository]:
        """Get repository by owner and name"""
        try:
            return self.github.get_repo(f"{owner}/{repo}")
        except GithubException as e:
            logger.error(f"Error getting repository {owner}/{repo}: {str(e)}")
            return None
    
    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Optional[PullRequest]:
        """Get pull request by number"""
        try:
            repository = await self.get_repository(owner, repo)
            if repository:
                return repository.get_pull(pr_number)
            return None
        except GithubException as e:
            logger.error(f"Error getting PR {pr_number} from {owner}/{repo}: {str(e)}")
            return None
    
    async def get_pull_request_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get files changed in a pull request"""
        try:
            pr = await self.get_pull_request(owner, repo, pr_number)
            if not pr:
                return []
            
            files = []
            for file in pr.get_files():
                files.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch,
                    "raw_url": file.raw_url,
                    "blob_url": file.blob_url,
                    "sha": file.sha
                })
            
            return files
        except GithubException as e:
            logger.error(f"Error getting PR files for {owner}/{repo}#{pr_number}: {str(e)}")
            return []
    
    async def get_file_content(self, owner: str, repo: str, file_path: str, ref: str = "main") -> Optional[str]:
        """Get file content from repository"""
        try:
            repository = await self.get_repository(owner, repo)
            if repository:
                content = repository.get_contents(file_path, ref=ref)
                if content:
                    return content.decoded_content.decode('utf-8')
            return None
        except GithubException as e:
            logger.error(f"Error getting file content for {owner}/{repo}/{file_path}: {str(e)}")
            return None
    
    async def create_review_comment(self, 
                                  owner: str, 
                                  repo: str, 
                                  pr_number: int,
                                  file_path: str,
                                  line_number: int,
                                  body: str,
                                  commit_sha: str) -> bool:
        """Create a review comment on a pull request"""
        try:
            pr = await self.get_pull_request(owner, repo, pr_number)
            if not pr:
                return False
            
            pr.create_review_comment(
                body=body,
                commit=pr.get_commits().reversed[0],  # Latest commit
                path=file_path,
                line=line_number
            )
            
            logger.info(f"Created review comment on {owner}/{repo}#{pr_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Error creating review comment: {str(e)}")
            return False
    
    async def create_review(self, 
                          owner: str, 
                          repo: str, 
                          pr_number: int,
                          body: str,
                          event: str = "COMMENT") -> bool:
        """Create a review on a pull request"""
        try:
            pr = await self.get_pull_request(owner, repo, pr_number)
            if not pr:
                return False
            
            pr.create_review(
                body=body,
                event=event  # APPROVE, REQUEST_CHANGES, COMMENT
            )
            
            logger.info(f"Created review on {owner}/{repo}#{pr_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Error creating review: {str(e)}")
            return False
    
    async def get_commit_details(self, owner: str, repo: str, sha: str) -> Optional[Dict[str, Any]]:
        """Get commit details"""
        try:
            repository = await self.get_repository(owner, repo)
            if repository:
                commit = repository.get_commit(sha)
                return {
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date.isoformat(),
                    "files": [file.filename for file in commit.files]
                }
            return None
        except GithubException as e:
            logger.error(f"Error getting commit details for {owner}/{repo}@{sha}: {str(e)}")
            return None
    
    async def get_repository_info(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get repository information"""
        try:
            repository = await self.get_repository(owner, repo)
            if repository:
                return {
                    "id": repository.id,
                    "name": repository.name,
                    "full_name": repository.full_name,
                    "owner": repository.owner.login,
                    "description": repository.description,
                    "language": repository.language,
                    "stars": repository.stargazers_count,
                    "forks": repository.forks_count,
                    "url": repository.html_url,
                    "created_at": repository.created_at.isoformat(),
                    "updated_at": repository.updated_at.isoformat()
                }
            return None
        except GithubException as e:
            logger.error(f"Error getting repository info for {owner}/{repo}: {str(e)}")
            return None
