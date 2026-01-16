"""Telegram bot for receiving TikTok URLs."""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from config import get_settings
from database import SessionLocal, Video, init_db
from scraper import validate_tiktok_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    await message.answer(
        "👋 Welcome to Tikodea!\n\n"
        "I help you save and analyze TikTok videos.\n\n"
        "Commands:\n"
        "/save <url> [context] - Save a TikTok video\n"
        "/status - Check processing status\n"
        "/help - Show this help message"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(
        "📚 Tikodea Commands:\n\n"
        "/save <url> [context]\n"
        "  Save a TikTok video for analysis.\n"
        "  Example: /save https://tiktok.com/@user/video/123 investment opportunity\n\n"
        "/status\n"
        "  Check how many videos are processing.\n\n"
        "Just paste a TikTok URL and I'll save it automatically!"
    )


@dp.message(Command("save"))
async def cmd_save(message: Message):
    """Handle /save command."""
    # Parse command arguments
    args = message.text.split(maxsplit=2)

    if len(args) < 2:
        await message.answer("❌ Please provide a TikTok URL.\nExample: /save https://tiktok.com/@user/video/123")
        return

    url = args[1]
    context = args[2] if len(args) > 2 else None

    await save_video(message, url, context)


@dp.message()
async def handle_message(message: Message):
    """Handle regular messages - detect TikTok URLs."""
    if not message.text:
        return

    # Check if message contains a TikTok URL
    text = message.text.strip()

    # Split to separate URL from potential context
    parts = text.split(maxsplit=1)
    potential_url = parts[0]

    if validate_tiktok_url(potential_url):
        context = parts[1] if len(parts) > 1 else None
        await save_video(message, potential_url, context)


async def save_video(message: Message, url: str, context: str = None):
    """Save a TikTok video to the database and queue for processing."""
    if not validate_tiktok_url(url):
        await message.answer(
            "❌ Invalid TikTok URL.\n\n"
            "Supported formats:\n"
            "• https://tiktok.com/@user/video/123\n"
            "• https://vm.tiktok.com/abc123\n"
            "• https://vt.tiktok.com/abc123"
        )
        return

    db = SessionLocal()
    try:
        # Create video record
        video = Video(
            tiktok_url=url,
            context=context,
            status="pending",
            telegram_chat_id=str(message.chat.id),
            telegram_message_id=message.message_id,
        )
        db.add(video)
        db.commit()
        db.refresh(video)

        # Queue for processing
        try:
            from queue_manager import enqueue_video_processing
            job_id = enqueue_video_processing(video.id)
            logger.info(f"Queued video {video.id} as job {job_id}")
        except Exception as e:
            logger.warning(f"Queue not available, will process synchronously: {e}")

        # Confirm to user
        response = f"✅ Video saved! (ID: {video.id})\n"
        if context:
            response += f"📝 Context: {context}\n"
        response += "\n🔄 Processing will start shortly..."

        await message.answer(response)

    except Exception as e:
        logger.error(f"Error saving video: {e}")
        await message.answer(f"❌ Error saving video: {e}")
    finally:
        db.close()


@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Handle /status command."""
    db = SessionLocal()
    try:
        pending = db.query(Video).filter(Video.status == "pending").count()
        processing = db.query(Video).filter(Video.status == "processing").count()
        completed = db.query(Video).filter(Video.status == "completed").count()
        failed = db.query(Video).filter(Video.status == "failed").count()

        await message.answer(
            f"📊 Video Status:\n\n"
            f"⏳ Pending: {pending}\n"
            f"🔄 Processing: {processing}\n"
            f"✅ Completed: {completed}\n"
            f"❌ Failed: {failed}"
        )
    finally:
        db.close()


async def main():
    """Start the bot."""
    init_db()
    logger.info("Starting Tikodea Telegram bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
