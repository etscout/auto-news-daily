#!/usr/bin/env python3
"""
Database layer for tracking sent articles.
Uses SQLite to prevent duplicate sends.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "auto_news.db"

def init_db():
    """Initialize database with articles table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on URL for fast lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_url ON sent_articles(url)
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")

def has_been_sent(url):
    """Check if article URL has already been sent."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM sent_articles WHERE url = ?", (url,))
    count = cursor.fetchone()[0]
    
    conn.close()
    return count > 0

def mark_as_sent(url, title, source):
    """Mark article as sent."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO sent_articles (url, title, source)
            VALUES (?, ?, ?)
        """, (url, title, source))
        conn.commit()
    except sqlite3.IntegrityError:
        # Already exists, ignore
        pass
    
    conn.close()

def get_sent_count():
    """Get total number of sent articles."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM sent_articles")
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def cleanup_old_articles(days=30):
    """Remove articles older than N days to keep DB lean."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM sent_articles
        WHERE sent_at < datetime('now', '-' || ? || ' days')
    """, (days,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        print(f"🧹 Cleaned up {deleted} old articles (>{days} days)")
    
    return deleted

if __name__ == "__main__":
    # Initialize DB when run directly
    init_db()
    print(f"📊 Total sent articles: {get_sent_count()}")
