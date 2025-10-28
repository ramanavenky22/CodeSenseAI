"""
Database configuration and models
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./codesense_ai.db")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Database dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class Repository(Base):
    """Repository model"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    full_name = Column(String, unique=True, index=True)
    owner = Column(String, index=True)
    url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    pull_requests = relationship("PullRequest", back_populates="repository")
    reviews = relationship("CodeReview", back_populates="repository")

class PullRequest(Base):
    """Pull Request model"""
    __tablename__ = "pull_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    number = Column(Integer, index=True)
    title = Column(String)
    body = Column(Text)
    state = Column(String)
    author = Column(String)
    head_sha = Column(String)
    base_sha = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    reviews = relationship("CodeReview", back_populates="pull_request")

class CodeReview(Base):
    """Code Review model"""
    __tablename__ = "code_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"))
    file_path = Column(String, index=True)
    line_number = Column(Integer)
    review_type = Column(String)  # bug, security, quality, suggestion
    severity = Column(String)  # low, medium, high, critical
    title = Column(String)
    description = Column(Text)
    suggestion = Column(Text)
    ai_confidence = Column(Integer)  # 0-100
    status = Column(String, default="open")  # open, resolved, dismissed
    metadata = Column(JSON)  # Additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="reviews")
    pull_request = relationship("PullRequest", back_populates="reviews")

class ReviewSession(Base):
    """Review Session model for tracking analysis runs"""
    __tablename__ = "review_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"))
    session_id = Column(String, unique=True, index=True)
    status = Column(String)  # pending, running, completed, failed
    total_files = Column(Integer)
    processed_files = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    metadata = Column(JSON)
    
    # Relationships
    repository = relationship("Repository")
    pull_request = relationship("PullRequest")
