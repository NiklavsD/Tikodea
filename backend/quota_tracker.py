"""Track API quota usage for rate-limited services."""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


QUOTA_FILE = Path(__file__).parent / "api_quota.json"


def get_current_month() -> str:
    """Get current month as YYYY-MM string."""
    return datetime.now().strftime("%Y-%m")


def load_quota() -> dict:
    """Load quota data from file."""
    if not QUOTA_FILE.exists():
        return {}

    try:
        with open(QUOTA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_quota(data: dict) -> None:
    """Save quota data to file."""
    with open(QUOTA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check_quota(service: str, limit: int) -> tuple[bool, int, int]:
    """
    Check if service has quota remaining.

    Returns:
        (has_quota, used, limit)
    """
    data = load_quota()
    current_month = get_current_month()

    # Reset if new month
    if service not in data or data[service].get("month") != current_month:
        data[service] = {
            "month": current_month,
            "used": 0,
            "limit": limit
        }
        save_quota(data)

    used = data[service]["used"]
    has_quota = used < limit

    return has_quota, used, limit


def increment_quota(service: str, limit: int) -> tuple[int, int]:
    """
    Increment quota usage for service.

    Returns:
        (used, limit)
    """
    data = load_quota()
    current_month = get_current_month()

    # Initialize if needed
    if service not in data or data[service].get("month") != current_month:
        data[service] = {
            "month": current_month,
            "used": 0,
            "limit": limit
        }

    # Increment
    data[service]["used"] += 1
    save_quota(data)

    return data[service]["used"], data[service]["limit"]


def get_quota_status(service: str, limit: int) -> dict:
    """Get quota status for service."""
    has_quota, used, limit = check_quota(service, limit)
    remaining = limit - used
    percent_used = (used / limit * 100) if limit > 0 else 0

    return {
        "service": service,
        "used": used,
        "limit": limit,
        "remaining": remaining,
        "percent_used": round(percent_used, 1),
        "has_quota": has_quota,
    }
