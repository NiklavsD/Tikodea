"""FastAPI backend for dashboard API."""
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import SessionLocal, Video, ChatMessage, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(title="Tikodea API", version="1.0.0", lifespan=lifespan)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "tikodea-api"}


# Video endpoints
@app.get("/api/videos")
async def list_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    favorites_only: bool = False,
    search: Optional[str] = None,
    tag: Optional[str] = None,
):
    """List videos with optional filtering."""
    db = SessionLocal()
    try:
        query = db.query(Video)

        if favorites_only:
            query = query.filter(Video.is_favorite == True)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Video.title.ilike(search_term))
                | (Video.description.ilike(search_term))
                | (Video.transcript.ilike(search_term))
            )

        if tag:
            # Search in hashtags JSON array
            query = query.filter(Video.hashtags.contains([tag]))

        videos = query.order_by(Video.created_at.desc()).offset(skip).limit(limit).all()
        total = query.count()

        return {
            "videos": [v.to_dict() for v in videos],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    finally:
        db.close()


@app.get("/api/videos/{video_id}")
async def get_video(video_id: int):
    """Get single video by ID."""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return video.to_dict()
    finally:
        db.close()


class FavoriteUpdate(BaseModel):
    is_favorite: bool


@app.patch("/api/videos/{video_id}/favorite")
async def toggle_favorite(video_id: int, update: FavoriteUpdate):
    """Toggle video favorite status."""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        video.is_favorite = update.is_favorite
        db.commit()
        return {"id": video_id, "is_favorite": video.is_favorite}
    finally:
        db.close()


class TagUpdate(BaseModel):
    tags: List[str]


@app.patch("/api/videos/{video_id}/tags")
async def update_tags(video_id: int, update: TagUpdate):
    """Update manual tags for a video."""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        video.manual_tags = update.tags
        db.commit()
        return {"id": video_id, "manual_tags": video.manual_tags}
    finally:
        db.close()


# Chat endpoints
class ChatRequest(BaseModel):
    message: str


@app.get("/api/videos/{video_id}/chat")
async def get_chat_history(video_id: int):
    """Get chat history for a video."""
    db = SessionLocal()
    try:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.video_id == video_id)
            .order_by(ChatMessage.created_at)
            .all()
        )
        return {
            "messages": [
                {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
                for m in messages
            ]
        }
    finally:
        db.close()


@app.post("/api/videos/{video_id}/chat")
async def send_chat_message(video_id: int, request: ChatRequest):
    """Send a chat message and get AI response."""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        # Save user message
        user_msg = ChatMessage(video_id=video_id, role="user", content=request.message)
        db.add(user_msg)
        db.commit()

        # Get AI response
        from llm_analyzer import chat_with_video
        response = chat_with_video(video, request.message)

        # Save assistant message
        assistant_msg = ChatMessage(video_id=video_id, role="assistant", content=response)
        db.add(assistant_msg)
        db.commit()

        return {"role": "assistant", "content": response}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
