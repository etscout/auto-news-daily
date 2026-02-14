#!/usr/bin/env python3
"""
Send automotive news emails via AgentMail.
"""
from pathlib import Path
from datetime import datetime
from agentmail import AgentMail

# Email config
AGENTMAIL_KEY_FILE = Path.home() / ".openclaw/workspace/agentmail_api_key"
FROM_EMAIL = "et_scout@agentmail.to"
TO_EMAIL = "calebkaay@gmail.com"
BCC_EMAIL = "et-scout-bcc@kaay.me"

def format_email_html(articles):
    """Format articles as HTML email."""
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">🚗 Daily Auto News - {date_str}</h2>
        <p style="color: #7f8c8d;">Your curated automotive headlines for today</p>
        <hr style="border: none; border-top: 2px solid #3498db; margin: 20px 0;">
    """
    
    for i, article in enumerate(articles, 1):
        # Emoji based on source
        emoji = {
            "Autoblog": "🏎️",
            "The Drive": "🚙",
            "Jalopnik": "🔧",
            "Electrek": "⚡",
            "Car and Driver": "🏁"
        }.get(article['source'], "📰")
        
        html += f"""
        <div style="margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background-color: #f8f9fa;">
            <h3 style="margin: 0 0 10px 0; color: #2c3e50;">
                {emoji} {i}. {article['title']}
            </h3>
            <p style="margin: 5px 0; color: #7f8c8d; font-size: 14px;">
                <strong>Source:</strong> {article['source']}
            </p>
            <p style="margin: 10px 0 0 0;">
                <a href="{article['url']}" style="color: #3498db; text-decoration: none; font-weight: bold;">
                    Read Article →
                </a>
            </p>
        </div>
        """
    
    html += """
        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
        <p style="color: #95a5a6; font-size: 12px; text-align: center;">
            Daily Auto News • Delivered by ET Scout 👽<br>
            Tomorrow's headlines at 8 AM
        </p>
    </div>
    """
    
    return html

def format_email_text(articles):
    """Format articles as plain text email."""
    date_str = datetime.now().strftime("%B %d, %Y")
    
    text = f"🚗 Daily Auto News - {date_str}\n"
    text += "=" * 50 + "\n\n"
    
    for i, article in enumerate(articles, 1):
        text += f"{i}. {article['title']}\n"
        text += f"   Source: {article['source']}\n"
        text += f"   {article['url']}\n\n"
    
    text += "=" * 50 + "\n"
    text += "Daily Auto News • Delivered by ET Scout 👽\n"
    text += "Tomorrow's headlines at 8 AM\n"
    
    return text

def send_email(articles):
    """Send email with articles."""
    if not articles:
        print("⚠️  No articles to send")
        return False
    
    # Read API key
    with open(AGENTMAIL_KEY_FILE, 'r') as f:
        api_key = f.read().strip()
    
    # Initialize client
    client = AgentMail(api_key=api_key)
    
    # Format email
    date_str = datetime.now().strftime("%b %d")
    subject = f"🚗 Daily Auto News - {date_str} - Top {len(articles)} Stories"
    
    html = format_email_html(articles)
    text = format_email_text(articles)
    
    try:
        print(f"📧 Sending to {TO_EMAIL} (BCC: {BCC_EMAIL})...")
        client.inboxes.messages.send(
            inbox_id=FROM_EMAIL,
            to=TO_EMAIL,
            bcc=BCC_EMAIL,
            subject=subject,
            text=text,
            html=html
        )
        print(f"✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    # Test with dummy articles
    test_articles = [
        {
            'title': 'Test Article 1',
            'url': 'https://example.com/1',
            'source': 'Autoblog'
        },
        {
            'title': 'Test Article 2',
            'url': 'https://example.com/2',
            'source': 'Electrek'
        }
    ]
    send_email(test_articles)
