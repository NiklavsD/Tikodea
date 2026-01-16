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
    Scrape TikTok video data using multiple fallback methods.

    Returns dict with:
    - title, description, creator
    - hashtags (list)
    - view_count, like_count
    - thumbnail_url
    - transcript
    """
    if not validate_tiktok_url(url):
        raise ValueError(f"Invalid TikTok URL: {url}")

    # Try methods in order of reliability
    transcript = None
    metadata = {}

    # 1. Try Supadata for transcript
    transcript = get_transcript_supadata(url)

    # 2. Try yt-dlp for metadata (with proxy if configured)
    metadata = get_metadata_ytdlp(url)

    # 3. If yt-dlp failed, try oEmbed API
    if not metadata.get("title"):
        metadata = get_metadata_oembed(url) or metadata

    # 4. Always have fallback from URL parsing
    if not metadata.get("creator"):
        url_data = extract_from_url(url)
        metadata = {**url_data, **{k: v for k, v in metadata.items() if v}}

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
    if not settings.supadata_api_key:
        return None

    try:
        response = httpx.get(
            "https://api.supadata.ai/v1/transcript",
            headers={"x-api-key": settings.supadata_api_key},
            params={"url": url, "text": "true"},
            timeout=60.0,
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("content", "")
        elif response.status_code == 404:
            print(f"Supadata: Video not found or no transcript available")
        else:
            print(f"Supadata error: {response.status_code}")
        return None
    except Exception as e:
        print(f"Supadata transcript error: {e}")
        return None


def get_metadata_oembed(url: str) -> Optional[dict]:
    """Get metadata from TikTok oEmbed API."""
    try:
        import urllib.parse
        encoded_url = urllib.parse.quote(url, safe='')
        oembed_url = f'https://www.tiktok.com/oembed?url={encoded_url}'

        # Use proxy if configured
        proxy = settings.proxy_url if settings.proxy_url else None

        response = httpx.get(oembed_url, proxy=proxy, timeout=30, follow_redirects=True)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "description": data.get("title"),  # oEmbed only has title
                "creator": data.get("author_name"),
                "hashtags": [],
                "view_count": None,
                "like_count": None,
                "thumbnail_url": data.get("thumbnail_url"),
            }
        return None
    except Exception as e:
        print(f"oEmbed error: {e}")
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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
        }

        # Add proxy if configured
        if settings.proxy_url:
            ydl_opts["proxy"] = settings.proxy_url

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
            print(f"yt-dlp: TikTok blocked access - using fallback methods")
        else:
            print(f"yt-dlp error: {e}")
        return {}


def extract_from_url(url: str) -> dict:
    """Extract minimal metadata from URL when APIs fail."""
    video_id = None
    username = None

    # Standard URL: https://www.tiktok.com/@username/video/1234567890
    match = re.search(r"tiktok\.com/@([^/]+)/video/(\d+)", url)
    if match:
        username = match.group(1)
        video_id = match.group(2)

    return {
        "title": f"TikTok by @{username}" if username else "TikTok video",
        "description": None,
        "creator": username,
        "hashtags": [],
        "view_count": None,
        "like_count": None,
        "thumbnail_url": None,
    }
