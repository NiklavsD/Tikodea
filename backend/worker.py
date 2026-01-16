"""Background worker for video processing jobs."""
from datetime import datetime
from database import SessionLocal, Video


def process_video(video_id: int) -> dict:
    """
    Process a TikTok video through the full pipeline.

    Steps:
    1. Scrape video metadata and transcript
    2. Run 4-lens LLM analysis
    3. Update database with results
    """
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {"error": f"Video {video_id} not found"}

        video.status = "processing"
        db.commit()

        try:
            # Step 1: Scrape TikTok data
            from scraper import scrape_tiktok
            scrape_result = scrape_tiktok(video.tiktok_url)

            video.title = scrape_result.get("title")
            video.description = scrape_result.get("description")
            video.creator = scrape_result.get("creator")
            video.hashtags = scrape_result.get("hashtags", [])
            video.view_count = scrape_result.get("view_count")
            video.like_count = scrape_result.get("like_count")
            video.thumbnail_url = scrape_result.get("thumbnail_url")
            video.transcript = scrape_result.get("transcript")
            db.commit()

            # Step 2: Run LLM analysis
            from llm_analyzer import analyze_video
            analysis = analyze_video(
                transcript=video.transcript,
                title=video.title,
                description=video.description,
                hashtags=video.hashtags,
                context=video.context,
            )

            video.investment_analysis = analysis.get("investment")
            video.product_analysis = analysis.get("product")
            video.content_analysis = analysis.get("content")
            video.knowledge_analysis = analysis.get("knowledge")

            video.status = "completed"
            video.processed_at = datetime.utcnow()
            db.commit()

            return {"status": "completed", "video_id": video_id}

        except Exception as e:
            video.status = "failed"
            video.error_message = str(e)
            db.commit()
            return {"error": str(e), "video_id": video_id}

    finally:
        db.close()
