#!/usr/bin/env python3
"""
Daily Automotive News App

Fetches, deduplicates, and emails top auto news daily.
Tracks sent articles in SQLite to avoid duplicates.
"""
import sys
import os
from datetime import datetime
import db
import scraper
import emailer
from openai import OpenAI

def rank_articles_with_llm(articles, top_n=10):
    """
    Use OpenAI to rank articles by interestingness.
    Returns top N most interesting articles.
    """
    if len(articles) <= top_n:
        return articles  # No need to rank if we have fewer than top_n
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set - returning articles in order found")
        return articles[:top_n]
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Format articles for LLM
        article_list = ""
        for i, article in enumerate(articles, 1):
            article_list += f"{i}. [{article['source']}] {article['title']}\n"
        
        prompt = f"""You are an automotive news editor selecting the most interesting stories for an enthusiast reader.

From these {len(articles)} automotive news articles, choose the {top_n} MOST INTERESTING:

{article_list}

Prioritize:
- New product launches and unveilings
- EV technology breakthroughs (battery, range, charging innovations)
- Exclusive scoops and leaked information
- Major industry moves (mergers, partnerships, funding, strategy shifts)
- Performance car news and track tests
- Autonomous driving developments
- Source diversity (pick from different publications)

AVOID:
- Local charger installations
- Minor discounts or deals
- Routine software updates
- Generic tips articles

Return EXACTLY {top_n} items as a comma-separated list of numbers (e.g., "3,7,12,1,19,4,8,15,22,11").
Just the numbers, nothing else."""

        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the comma-separated numbers
        try:
            indices = [int(x.strip()) - 1 for x in result.split(',')]  # Convert to 0-indexed
            ranked_articles = [articles[i] for i in indices if 0 <= i < len(articles)]
            
            print(f"  🤖 LLM ranked {len(ranked_articles)} articles")
            return ranked_articles[:top_n]
            
        except (ValueError, IndexError) as e:
            print(f"  ⚠️  Failed to parse LLM response: {e}")
            print(f"     Raw response: {result[:100]}")
            return articles[:top_n]
            
    except Exception as e:
        print(f"  ⚠️  LLM ranking failed: {e}")
        return articles[:top_n]

def main():
    """Main app logic."""
    print("=" * 60)
    print("🚗 Daily Automotive News App")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize database
    db.init_db()
    
    # Cleanup old articles (keep last 1 day so we get fresh articles daily)
    db.cleanup_old_articles(days=1)
    
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
    
    # Rank articles with LLM to find most interesting
    print(f"\n🤖 Ranking articles with LLM...")
    top_articles = rank_articles_with_llm(new_articles, top_n=10)
    
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
