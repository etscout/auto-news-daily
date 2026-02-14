# 🚗 Daily Auto News

Automated daily automotive news aggregator and emailer.

## Features

- 📰 Scrapes 5+ automotive news sources (Autoblog, The Drive, Jalopnik, Electrek, Car and Driver)
- 🗄️ SQLite database tracks sent articles to prevent duplicates
- 📧 Sends top 5 new articles daily via AgentMail
- 🧹 Auto-cleanup of old articles (30-day retention)
- 🎨 Beautiful HTML email formatting with source-specific emojis

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AgentMail:**
   - Ensure API key exists at: `~/.openclaw/workspace/agentmail_api_key`

3. **Run manually:**
   ```bash
   python main.py
   ```

4. **Schedule with cron:**
   ```bash
   # Add to OpenClaw cron (8 AM daily):
   # Run: cd /home/ck/.openclaw/workspace/auto-news-daily && python3 main.py
   ```

## Files

- `main.py` - Entry point, orchestrates fetch → filter → send
- `scraper.py` - Fetches articles from news sources
- `emailer.py` - Sends formatted email via AgentMail
- `db.py` - SQLite database for tracking sent articles
- `auto_news.db` - SQLite database (auto-created)

## Email Config

Edit `emailer.py` to change:
- `TO_EMAIL` - Recipient
- `BCC_EMAIL` - BCC recipient
- `FROM_EMAIL` - Sender (AgentMail inbox)

## Database

```bash
# View sent articles:
sqlite3 auto_news.db "SELECT * FROM sent_articles ORDER BY sent_at DESC LIMIT 10;"

# Reset database:
rm auto_news.db
```

## Maintenance

- Database auto-cleans articles older than 30 days
- No manual maintenance required
- All state is local (no external dependencies beyond AgentMail)

---

**Built with ❤️ by ET Scout 👽**
