"""Redis queue management for async job processing."""
from redis import Redis
from rq import Queue
from config import get_settings

settings = get_settings()


def get_redis_connection() -> Redis:
    """Get Redis connection from URL."""
    # Parse Redis URL - handle Redis Cloud format
    url = settings.redis_url

    # Basic URL parsing for Redis Cloud
    if "@" in url:
        # Format: redis://user:password@host:port
        # or just: host:port (our case)
        pass

    return Redis.from_url(f"redis://{url}" if not url.startswith("redis://") else url)


def get_queue(name: str = "default") -> Queue:
    """Get RQ queue instance."""
    return Queue(name, connection=get_redis_connection())


def enqueue_video_processing(video_id: int) -> str:
    """Queue a video for processing."""
    from worker import process_video  # Import here to avoid circular imports

    queue = get_queue("video_processing")
    job = queue.enqueue(process_video, video_id, job_timeout="10m")
    return job.id
