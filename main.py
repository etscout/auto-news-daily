#!/usr/bin/env python3
"""
Daily Automotive News App

Fetches, deduplicates, and emails top auto news daily.
Tracks sent articles in SQLite to avoid duplicates.
"""
import sys
from datetime import datetime
import db
import scraper
import emailer

def main():
    """Main app logic."""
    print("=" * 60)
    print("🚗 Daily Automotive News App")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize database
    db.init_db()
    
    # Cleanup old articles (keep last 30 days)
    db.cleanup_old_articles(days=30)
    
    # Fetch articles from all sources
    all_articles = scraper.fetch_all_articles()
    
    if not all_articles:
        print("\n⚠️  No articles found!")
        return 1
    
    # Filter out already-sent articles
    print(f"\n🔍 Filtering duplicates...")
    new_articles = []
    
    for article in all_articles:
        if db.has_been_sent(article['url']):
            continue
        new_articles.append(article)
    
    print(f"  ✅ New articles: {len(new_articles)}")
    print(f"  ⏭️  Already sent: {len(all_articles) - len(new_articles)}")
    
    if not new_articles:
        print("\n⚠️  No new articles to send!")
        print(f"📊 Total articles in DB: {db.get_sent_count()}")
        return 0
    
    # Take top 5 new articles
    top_articles = new_articles[:5]
    
    print(f"\n📰 Top {len(top_articles)} articles to send:")
    for i, article in enumerate(top_articles, 1):
        print(f"  {i}. {article['title'][:60]}... ({article['source']})")
    
    # Send email
    print()
    success = emailer.send_email(top_articles)
    
    if not success:
        print("\n❌ Email send failed!")
        return 1
    
    # Mark articles as sent
    print(f"\n💾 Marking {len(top_articles)} articles as sent...")
    for article in top_articles:
        db.mark_as_sent(article['url'], article['title'], article['source'])
    
    print(f"✅ Done! Total articles in DB: {db.get_sent_count()}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
