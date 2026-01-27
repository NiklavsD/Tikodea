"""TikTok video scraping - Phase 3 implementation."""
import re
from typing import Optional
import httpx
from config import get_settings
from quota_tracker import check_quota, increment_quota, get_quota_status

settings = get_settings()

# ScrapTik free tier limit
SCRAPTIK_MONTHLY_LIMIT = 50


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

    # 2. Try ScrapTik for metadata (most reliable)
    metadata = get_metadata_scraptik(url)

    # 3. If ScrapTik failed, try yt-dlp for metadata (with proxy if configured)
    if not metadata.get("title"):
        metadata = get_metadata_ytdlp(url)

    # 4. If yt-dlp failed, try oEmbed API
    if not metadata.get("title"):
        metadata = get_metadata_oembed(url) or metadata

    # 5. Always have fallback from URL parsing
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


def get_metadata_scraptik(url: str) -> dict:
    """Get video metadata from ScrapTik API via RapidAPI."""
    if not settings.rapidapi_key:
        print("ScrapTik: No RapidAPI key configured")
        return {}

    # Check quota before making request
    has_quota, used, limit = check_quota("scraptik", SCRAPTIK_MONTHLY_LIMIT)

    if not has_quota:
        print(f"ScrapTik: Monthly quota exceeded ({used}/{limit}) - using fallback")
        return {}

    # Warn when approaching limit
    if used >= limit * 0.8:  # 80% threshold
        print(f"⚠️  ScrapTik quota warning: {used}/{limit} used ({limit - used} remaining)")

    try:
        # Extract video ID from URL for ScrapTik
        video_id = None

        # Standard URL: https://www.tiktok.com/@username/video/1234567890
        match = re.search(r"tiktok\.com/@[^/]+/video/(\d+)", url)
        if match:
            video_id = match.group(1)

        if not video_id:
            print("ScrapTik: Could not extract video ID from URL")
            return {}

        # Try with URL parameter (some APIs prefer full URL over ID)
        response = httpx.get(
            "https://scraptik.p.rapidapi.com/video",
            headers={
                "x-rapidapi-host": "scraptik.p.rapidapi.com",
                "x-rapidapi-key": settings.rapidapi_key,
            },
            params={"url": url},
            timeout=30.0,
        )

        print(f"ScrapTik API response status: {response.status_code}")
        if response.status_code != 200:
            print(f"ScrapTik API response: {response.text[:500]}")
            if "does not exist" in response.text:
                print("\nℹ To find correct endpoint: visit https://rapidapi.com/scraptik-api-scraptik-api-default/api/scraptik/")
                print("  Click 'Endpoints' tab, find video endpoint, copy the path from code snippets\n")

        if response.status_code == 200:
            data = response.json()

            # Check for subscription error
            if "message" in data and "not subscribed" in data.get("message", "").lower():
                print("ScrapTik: Not subscribed to API - visit https://rapidapi.com/scraptik-api-scraptik-api-default/api/scraptik/pricing")
                return {}

            # Extract video data from ScrapTik response
            video = data.get("aweme_detail", {})
            author = video.get("author", {})
            stats = video.get("statistics", {})

            # Extract description and hashtags
            description = video.get("desc", "")
            hashtags = re.findall(r"#(\w+)", description)

            # Increment quota on successful call
            used, limit = increment_quota("scraptik", SCRAPTIK_MONTHLY_LIMIT)
            print(f"✓ ScrapTik: Success ({used}/{limit} used this month)")

            return {
                "title": description[:100] if description else f"TikTok by @{author.get('unique_id', 'unknown')}",
                "description": description,
                "creator": author.get("unique_id") or author.get("nickname"),
                "hashtags": hashtags,
                "view_count": stats.get("play_count"),
                "like_count": stats.get("digg_count"),
                "thumbnail_url": video.get("video", {}).get("cover", {}).get("url_list", [None])[0],
            }
        else:
            print(f"ScrapTik error: {response.status_code}")
            return {}
    except Exception as e:
        print(f"ScrapTik metadata error: {e}")
        return {}


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
            title = data.get("title", "")

            # Extract hashtags from title/description
            hashtags = re.findall(r"#(\w+)", title)

            print(f"✓ oEmbed: Success (title, creator, thumbnail)")

            return {
                "title": title,
                "description": title,  # oEmbed only has title
                "creator": data.get("author_name"),
                "hashtags": hashtags,
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
