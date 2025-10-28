"""
Webhook schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any

class WebhookPayload(BaseModel):
    """GitHub webhook payload model"""
    action: str
    pull_request: Optional[Dict[str, Any]] = None
    repository: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None
