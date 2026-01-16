"""Tests for TikTok URL validation."""
import pytest
from scraper import validate_tiktok_url


class TestUrlValidation:
    """Test TikTok URL validation."""

    def test_valid_standard_url(self):
        """Standard TikTok video URL should be valid."""
        assert validate_tiktok_url("https://www.tiktok.com/@user/video/123456789")
        assert validate_tiktok_url("https://tiktok.com/@user/video/123456789")

    def test_valid_short_url(self):
        """Short TikTok URLs should be valid."""
        assert validate_tiktok_url("https://vm.tiktok.com/ZMxxxxxx")
        assert validate_tiktok_url("https://vt.tiktok.com/ZMxxxxxx")

    def test_valid_t_url(self):
        """TikTok /t/ format URLs should be valid."""
        assert validate_tiktok_url("https://www.tiktok.com/t/ZTxxxxxx")
        assert validate_tiktok_url("https://tiktok.com/t/ZTxxxxxx")

    def test_invalid_urls(self):
        """Non-TikTok URLs should be invalid."""
        assert not validate_tiktok_url("https://youtube.com/watch?v=123")
        assert not validate_tiktok_url("https://instagram.com/reel/123")
        assert not validate_tiktok_url("not a url")
        assert not validate_tiktok_url("")

    def test_invalid_tiktok_pages(self):
        """TikTok non-video pages should be invalid."""
        assert not validate_tiktok_url("https://tiktok.com/@user")
        assert not validate_tiktok_url("https://tiktok.com/explore")
