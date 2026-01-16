"""Tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient

# Setup test environment
import os
os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"
os.environ["OPENROUTER_API_KEY"] = "test_api_key"
os.environ["SUPADATA_API_KEY"] = "test_supadata_key"
os.environ["DATABASE_URL"] = "sqlite:///./test_api.db"

from api import app
from database import Base, engine, SessionLocal, Video

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Setup test database before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def create_video():
    """Create a test video."""
    db = SessionLocal()
    video = Video(
        tiktok_url="https://tiktok.com/@test/video/123",
        title="Test Video",
        status="completed",
        hashtags=["test"],
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    video_id = video.id
    db.close()
    return video_id


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health(self):
        """Health endpoint should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestVideoEndpoints:
    """Test video API endpoints."""

    def test_list_videos_empty(self):
        """Should return empty list when no videos."""
        response = client.get("/api/videos")
        assert response.status_code == 200
        assert response.json()["videos"] == []
        assert response.json()["total"] == 0

    def test_list_videos(self, create_video):
        """Should return list of videos."""
        response = client.get("/api/videos")
        assert response.status_code == 200
        assert len(response.json()["videos"]) == 1
        assert response.json()["videos"][0]["title"] == "Test Video"

    def test_get_video(self, create_video):
        """Should return single video."""
        response = client.get(f"/api/videos/{create_video}")
        assert response.status_code == 200
        assert response.json()["id"] == create_video

    def test_get_video_not_found(self):
        """Should return 404 for missing video."""
        response = client.get("/api/videos/99999")
        assert response.status_code == 404

    def test_toggle_favorite(self, create_video):
        """Should toggle favorite status."""
        response = client.patch(
            f"/api/videos/{create_video}/favorite",
            json={"is_favorite": True}
        )
        assert response.status_code == 200
        assert response.json()["is_favorite"] is True

    def test_update_tags(self, create_video):
        """Should update manual tags."""
        response = client.patch(
            f"/api/videos/{create_video}/tags",
            json={"tags": ["new", "tags"]}
        )
        assert response.status_code == 200
        assert response.json()["manual_tags"] == ["new", "tags"]


class TestChatEndpoints:
    """Test chat API endpoints."""

    def test_get_empty_chat(self, create_video):
        """Should return empty chat history."""
        response = client.get(f"/api/videos/{create_video}/chat")
        assert response.status_code == 200
        assert response.json()["messages"] == []
