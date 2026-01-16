"""Tests for database models."""
import pytest
from database import Video, ChatMessage


class TestVideoModel:
    """Test Video model."""

    def test_create_video(self, test_db):
        """Should create a video record."""
        video = Video(
            tiktok_url="https://tiktok.com/@test/video/999",
            context="Investment research",
            status="pending",
        )
        test_db.add(video)
        test_db.commit()

        assert video.id is not None
        assert video.status == "pending"
        assert video.is_favorite is False

    def test_video_to_dict(self, sample_video):
        """Should convert video to dictionary."""
        data = sample_video.to_dict()

        assert data["id"] == sample_video.id
        assert data["tiktok_url"] == "https://tiktok.com/@test/video/123456"
        assert data["title"] == "Test Video"
        assert data["hashtags"] == ["test", "demo"]
        assert data["is_favorite"] is False

    def test_video_favorite_toggle(self, sample_video, test_db):
        """Should toggle favorite status."""
        assert sample_video.is_favorite is False

        sample_video.is_favorite = True
        test_db.commit()
        test_db.refresh(sample_video)

        assert sample_video.is_favorite is True


class TestChatMessage:
    """Test ChatMessage model."""

    def test_create_message(self, sample_video, test_db):
        """Should create a chat message."""
        msg = ChatMessage(
            video_id=sample_video.id,
            role="user",
            content="What is this video about?",
        )
        test_db.add(msg)
        test_db.commit()

        assert msg.id is not None
        assert msg.video_id == sample_video.id
        assert msg.role == "user"
