"""Discord bot for receiving TikTok URLs."""
import asyncio
import logging
import discord
from discord import app_commands

from config import get_settings
from database import SessionLocal, Video, init_db
from scraper import validate_tiktok_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


class TikodeaBot(discord.Client):
    """Discord bot client for Tikodea."""

    def __init__(self):
        intents = discord.Intents.default()
        # Note: Enable MESSAGE_CONTENT intent in Discord Developer Portal for auto-detection
        # intents.message_content = True
        intents.dm_messages = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        """Set up slash commands."""
        await self.tree.sync()
        logger.info("Slash commands synced")


bot = TikodeaBot()


@bot.event
async def on_ready():
    """Called when the bot is ready."""
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="for TikTok URLs")
    )
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.tree.command(name="save", description="Save a TikTok video for analysis")
@app_commands.describe(
    url="The TikTok video URL",
    context="Optional context about the video"
)
async def cmd_save(interaction: discord.Interaction, url: str, context: str = None):
    """Handle /save slash command."""
    await save_video(interaction, url, context)


@bot.tree.command(name="status", description="Check video processing statistics")
async def cmd_status(interaction: discord.Interaction):
    """Handle /status slash command."""
    db = SessionLocal()
    try:
        pending = db.query(Video).filter(Video.status == "pending").count()
        processing = db.query(Video).filter(Video.status == "processing").count()
        completed = db.query(Video).filter(Video.status == "completed").count()
        failed = db.query(Video).filter(Video.status == "failed").count()

        await interaction.response.send_message(
            f"📊 **Video Status:**\n\n"
            f"⏳ Pending: {pending}\n"
            f"🔄 Processing: {processing}\n"
            f"✅ Completed: {completed}\n"
            f"❌ Failed: {failed}"
        )
    finally:
        db.close()


@bot.tree.command(name="help", description="Show usage instructions")
async def cmd_help(interaction: discord.Interaction):
    """Handle /help slash command."""
    await interaction.response.send_message(
        "📚 **Tikodea Commands:**\n\n"
        "**/save** `<url>` `[context]`\n"
        "  Save a TikTok video for analysis.\n"
        "  Example: `/save https://tiktok.com/@user/video/123 investment opportunity`\n\n"
        "**/status**\n"
        "  Check how many videos are processing.\n\n"
        "Just paste a TikTok URL and I'll save it automatically!"
    )


@bot.event
async def on_message(message: discord.Message):
    """Handle regular messages - detect TikTok URLs.

    Note: Requires MESSAGE_CONTENT privileged intent to be enabled in Discord Developer Portal.
    Without it, message.content will be empty and auto-detection won't work.
    Use /save command instead.
    """
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    if not message.content:
        return

    # Split to separate URL from potential context
    text = message.content.strip()
    parts = text.split(maxsplit=1)
    potential_url = parts[0]

    if validate_tiktok_url(potential_url):
        context = parts[1] if len(parts) > 1 else None
        await save_video_from_message(message, potential_url, context)


async def save_video(interaction: discord.Interaction, url: str, context: str = None):
    """Save a TikTok video from a slash command."""
    if not validate_tiktok_url(url):
        await interaction.response.send_message(
            "❌ Invalid TikTok URL.\n\n"
            "Supported formats:\n"
            "• https://tiktok.com/@user/video/123\n"
            "• https://vm.tiktok.com/abc123\n"
            "• https://vt.tiktok.com/abc123",
            ephemeral=True
        )
        return

    db = SessionLocal()
    try:
        # Create video record
        video = Video(
            tiktok_url=url,
            context=context,
            status="pending",
            discord_channel_id=str(interaction.channel_id),
            discord_message_id=str(interaction.id),
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

        await interaction.response.send_message(response)

    except Exception as e:
        logger.error(f"Error saving video: {e}")
        await interaction.response.send_message(f"❌ Error saving video: {e}", ephemeral=True)
    finally:
        db.close()


async def save_video_from_message(message: discord.Message, url: str, context: str = None):
    """Save a TikTok video from a regular message (auto-detection)."""
    if not validate_tiktok_url(url):
        await message.reply(
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
            discord_channel_id=str(message.channel.id),
            discord_message_id=str(message.id),
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

        await message.reply(response)

    except Exception as e:
        logger.error(f"Error saving video: {e}")
        await message.reply(f"❌ Error saving video: {e}")
    finally:
        db.close()


def main():
    """Start the bot."""
    if not settings.discord_bot_token:
        logger.error("DISCORD_BOT_TOKEN not set in environment")
        return

    init_db()
    logger.info("Starting Tikodea Discord bot...")
    bot.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
