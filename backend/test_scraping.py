#!/usr/bin/env python3
"""Test TikTok scraping with a real URL."""
import json
from scraper import scrape_tiktok

# Test URL - you can replace this with any TikTok video URL
TEST_URL = "https://www.tiktok.com/@zachking/video/7445916814181780769"


def main():
    """Test scraping a TikTok video."""
    print(f"\nTesting scraper with URL:\n{TEST_URL}\n")
    print("="*60)

    try:
        result = scrape_tiktok(TEST_URL)

        print("\nScraping Result:")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*60)

        # Check what we got
        print("\nData Quality Check:")
        print(f"  Title:       {'✓' if result.get('title') else 'X'} {result.get('title', 'Missing')[:60]}")
        print(f"  Creator:     {'✓' if result.get('creator') else 'X'} {result.get('creator', 'Missing')}")
        print(f"  Description: {'✓' if result.get('description') else 'X'} {'Present' if result.get('description') else 'Missing'}")
        print(f"  Hashtags:    {'✓' if result.get('hashtags') else 'X'} {len(result.get('hashtags', []))} found")
        print(f"  View Count:  {'✓' if result.get('view_count') else 'X'} {result.get('view_count', 'Missing')}")
        print(f"  Like Count:  {'✓' if result.get('like_count') else 'X'} {result.get('like_count', 'Missing')}")
        print(f"  Thumbnail:   {'✓' if result.get('thumbnail_url') else 'X'} {'Present' if result.get('thumbnail_url') else 'Missing'}")
        print(f"  Transcript:  {'✓' if result.get('transcript') else 'X'} {'Present' if result.get('transcript') else 'Missing'}")

        print("\n" + "="*60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
