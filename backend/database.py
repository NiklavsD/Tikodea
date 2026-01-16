"""Database models and connection management."""
from datetime import datetime, timezone
from typing import Optional
import json

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

from config import get_settings

settings = get_settings()

# Create engine - handle SQLite URL format
db_url = settings.database_url
if db_url.startswith("file:"):
    db_url = f"sqlite:///{db_url[5:]}"
elif not db_url.startswith("sqlite"):
    db_url = f"sqlite:///{db_url}"

engine = create_engine(db_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Video(Base):
    """Processed TikTok video with analysis."""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    tiktok_url = Column(String(500), nullable=False, index=True)
    context = Column(Text, nullable=True)  # User-provided context

    # Metadata from TikTok
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    creator = Column(String(200), nullable=True)
    hashtags = Column(JSON, default=list)  # List of hashtags
    view_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)

    # Extracted content
    transcript = Column(Text, nullable=True)

    # Analysis results (JSON for flexibility)
    investment_analysis = Column(JSON, nullable=True)
    product_analysis = Column(JSON, nullable=True)
    content_analysis = Column(JSON, nullable=True)
    knowledge_analysis = Column(JSON, nullable=True)

    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)

    # User interaction
    is_favorite = Column(Boolean, default=False)
    manual_tags = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)

    # Telegram info
    telegram_chat_id = Column(String(100), nullable=True)
    telegram_message_id = Column(Integer, nullable=True)

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "tiktok_url": self.tiktok_url,
            "context": self.context,
            "title": self.title,
            "description": self.description,
            "creator": self.creator,
            "hashtags": self.hashtags or [],
            "view_count": self.view_count,
            "like_count": self.like_count,
            "thumbnail_url": self.thumbnail_url,
            "transcript": self.transcript,
            "investment_analysis": self.investment_analysis,
            "product_analysis": self.product_analysis,
            "content_analysis": self.content_analysis,
            "knowledge_analysis": self.knowledge_analysis,
            "status": self.status,
            "error_message": self.error_message,
            "is_favorite": self.is_favorite,
            "manual_tags": self.manual_tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }


class ChatMessage(Base):
    """Chat messages for per-video research conversations."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, index=True, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
