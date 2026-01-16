"""TikTok video scraping - Phase 3 implementation."""
import re
from typing import Optional
import httpx
from config import get_settings

settings = get_settings()


def validate_tiktok_url(url: str) -> bool:
    """Validate that URL is a TikTok video URL."""
    patterns = [
        r"https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+",
        r"https?://(?:vm|vt)\.tiktok\.com/[\w]+",
        r"https?://(?:www\.)?tiktok\.com/t/[\w]+",
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def scrape_tiktok(url: str) -> dict:
    """
    Scrape TikTok video data.

    Returns dict with:
    - title, description, creator
    - hashtags (list)
    - view_count, like_count
    - thumbnail_url
    - transcript (from Supadata or speech-to-text)
    """
    if not validate_tiktok_url(url):
        raise ValueError(f"Invalid TikTok URL: {url}")

    # Get transcript from Supadata
    transcript = get_transcript_supadata(url)

    # Get metadata using yt-dlp
    metadata = get_metadata_ytdlp(url)

    return {
        "title": metadata.get("title"),
        "description": metadata.get("description"),
        "creator": metadata.get("creator"),
        "hashtags": metadata.get("hashtags", []),
        "view_count": metadata.get("view_count"),
        "like_count": metadata.get("like_count"),
        "thumbnail_url": metadata.get("thumbnail_url"),
        "transcript": transcript,
    }


def get_transcript_supadata(url: str) -> Optional[str]:
    """Get transcript from Supadata API."""
    try:
        response = httpx.get(
            "https://api.supadata.ai/v1/transcript",
            headers={"x-api-key": settings.supadata_api_key},
            params={"url": url, "text": "true"},
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("content", "")
    except Exception as e:
        print(f"Supadata transcript error: {e}")
        return None


def get_metadata_ytdlp(url: str) -> dict:
    """Get video metadata using yt-dlp."""
    try:
        import yt_dlp

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Extract hashtags from description
            description = info.get("description", "") or ""
            hashtags = re.findall(r"#(\w+)", description)

            return {
                "title": info.get("title"),
                "description": description,
                "creator": info.get("uploader") or info.get("channel"),
                "hashtags": hashtags,
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "thumbnail_url": info.get("thumbnail"),
            }
    except Exception as e:
        error_msg = str(e)
        if "blocked" in error_msg.lower():
            print(f"yt-dlp blocked by TikTok - try using a VPN or proxy")
        else:
            print(f"yt-dlp metadata error: {e}")
        # Return minimal data extracted from URL
        return extract_from_url(url)


def extract_from_url(url: str) -> dict:
    """Extract minimal metadata from URL when APIs fail."""
    # Try to extract video ID and username from URL
    import re

    video_id = None
    username = None

    # Standard URL: https://www.tiktok.com/@username/video/1234567890
    match = re.search(r"tiktok\.com/@([^/]+)/video/(\d+)", url)
    if match:
        username = match.group(1)
        video_id = match.group(2)

    return {
        "title": f"TikTok video {video_id}" if video_id else "TikTok video",
        "description": None,
        "creator": username,
        "hashtags": [],
        "view_count": None,
        "like_count": None,
        "thumbnail_url": None,
    }
