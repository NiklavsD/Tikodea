"""Migration script to add Discord columns to the videos table.

Run this once to add the new Discord columns to an existing database.
Usage: python migrations/add_discord_columns.py
"""
import sqlite3
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_settings

settings = get_settings()


def get_db_path():
    """Get the SQLite database file path."""
    db_url = settings.database_url
    if db_url.startswith("file:"):
        return db_url[5:]
    elif db_url.startswith("sqlite:///"):
        return db_url[10:]
    else:
        return db_url


def migrate():
    """Add Discord columns to the videos table."""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. No migration needed.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(videos)")
        columns = [col[1] for col in cursor.fetchall()]

        migrations_applied = 0

        if "discord_channel_id" not in columns:
            cursor.execute("ALTER TABLE videos ADD COLUMN discord_channel_id VARCHAR(100)")
            print("Added discord_channel_id column")
            migrations_applied += 1
        else:
            print("discord_channel_id column already exists")

        if "discord_message_id" not in columns:
            cursor.execute("ALTER TABLE videos ADD COLUMN discord_message_id VARCHAR(100)")
            print("Added discord_message_id column")
            migrations_applied += 1
        else:
            print("discord_message_id column already exists")

        conn.commit()

        if migrations_applied > 0:
            print(f"Migration complete. {migrations_applied} column(s) added.")
        else:
            print("No migrations needed. All columns already exist.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
