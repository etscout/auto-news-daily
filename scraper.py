#!/usr/bin/env python3
"""
Scrape automotive news from multiple sources.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# News sources to scrape
SOURCES = [
    {
        "name": "Autoblog",
        "url": "https://www.autoblog.com/",
        "selector": "article h2 a"
    },
    {
        "name": "The Drive",
        "url": "https://www.thedrive.com/news",
        "selector": "h3 a"
    },
    {
        "name": "Jalopnik",
        "url": "https://jalopnik.com/",
        "selector": "h1 a"
    },
    {
        "name": "Electrek",
        "url": "https://electrek.co/",
        "selector": "h2.article-title a"
    },
    {
        "name": "Car and Driver",
        "url": "https://www.caranddriver.com/news/",
        "selector": "h3.article-title a"
    }
]

def fetch_articles_from_source(source):
    """Fetch articles from a single source."""
    articles = []
    
    try:
        response = requests.get(source["url"], timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code != 200:
            print(f"  ❌ {source['name']}: HTTP {response.status_code}")
            return articles
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select(source["selector"])
        
        for link in links[:10]:  # Top 10 from each source
            title = link.get_text(strip=True)
            href = link.get('href')
            
            if not href or not title:
                continue
            
            # Make absolute URL
            if href.startswith('/'):
                from urllib.parse import urljoin
                href = urljoin(source["url"], href)
            
            articles.append({
                'title': title,
                'url': href,
                'source': source['name']
            })
        
        print(f"  ✅ {source['name']}: {len(articles)} articles")
        
    except Exception as e:
        print(f"  ❌ {source['name']}: {str(e)[:50]}")
    
    return articles

def fetch_all_articles():
    """Fetch articles from all sources."""
    print("🔍 Fetching automotive news...")
    
    all_articles = []
    
    for source in SOURCES:
        articles = fetch_articles_from_source(source)
        all_articles.extend(articles)
    
    print(f"\n📰 Total articles fetched: {len(all_articles)}")
    return all_articles

if __name__ == "__main__":
    articles = fetch_all_articles()
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article['title']} ({article['source']})")
