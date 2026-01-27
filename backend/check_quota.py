#!/usr/bin/env python3
"""Check API quota status."""
from quota_tracker import get_quota_status

# ScrapTik free tier limit
SCRAPTIK_MONTHLY_LIMIT = 50


def main():
    """Display quota status."""
    status = get_quota_status("scraptik", SCRAPTIK_MONTHLY_LIMIT)

    print("\n" + "="*50)
    print("ScrapTik API Quota Status")
    print("="*50)
    print(f"Used:      {status['used']}/{status['limit']} requests")
    print(f"Remaining: {status['remaining']} requests")
    print(f"Progress:  {status['percent_used']}%")

    # Visual progress bar
    bar_length = 40
    filled = int(bar_length * status['percent_used'] / 100)
    bar = "#" * filled + "-" * (bar_length - filled)
    print(f"\n[{bar}] {status['percent_used']}%")

    # Status indicator
    if status['percent_used'] >= 100:
        print("\n[!] Quota exhausted - using fallback methods")
    elif status['percent_used'] >= 80:
        print(f"\n[!] Warning: Only {status['remaining']} requests remaining")
    elif status['percent_used'] >= 50:
        print(f"\n[*] Half used: {status['remaining']} requests left")
    else:
        print(f"\n[OK] Healthy: {status['remaining']} requests available")

    print("="*50 + "\n")


if __name__ == "__main__":
    main()
