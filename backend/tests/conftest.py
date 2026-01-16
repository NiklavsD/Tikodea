"""Pytest configuration and fixtures."""
import os
import sys
import pytest

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables before importing config
os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"
os.environ["GOOGLE_AI_API_KEY"] = "test_api_key"
os.environ["SUPADATA_API_KEY"] = "test_supadata_key"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["DATABASE_URL"] = "sqlite:///./test_tikodea.db"


@pytest.fixture
def test_db():
    """Create a test database."""
    from database import engine, Base, SessionLocal

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_video(test_db):
    """Create a sample video for testing."""
    from database import Video

    video = Video(
        tiktok_url="https://tiktok.com/@test/video/123456",
        context="Test context",
        title="Test Video",
        description="A test video #test #demo",
        creator="testuser",
        hashtags=["test", "demo"],
        view_count=1000,
        like_count=100,
        transcript="This is a test transcript.",
        status="completed",
    )
    test_db.add(video)
    test_db.commit()
    test_db.refresh(video)
    return video
