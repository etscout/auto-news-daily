#!/usr/bin/env python3
"""
Web UI for Daily Auto News app.
Manage sources, view history, check stats.
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import json
from pathlib import Path
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Simple auth (change this!)
USERNAME = "caleb"
PASSWORD = "autonews2026"

DB_PATH = Path(__file__).parent / "auto_news.db"
SOURCES_FILE = Path(__file__).parent / "sources.json"

# Load sources from file
def load_sources():
    """Load sources from JSON file."""
    if SOURCES_FILE.exists():
        with open(SOURCES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_sources(sources):
    """Save sources to JSON file."""
    with open(SOURCES_FILE, 'w') as f:
        json.dump(sources, f, indent=2)

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Auth decorator
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout."""
    session.pop('logged_in', None)
    flash('Logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Dashboard."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get stats
    cursor.execute("SELECT COUNT(*) FROM sent_articles")
    total_sent = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM sent_articles
        GROUP BY source
        ORDER BY count DESC
    """)
    source_stats = cursor.fetchall()
    
    cursor.execute("""
        SELECT * FROM sent_articles
        ORDER BY sent_at DESC
        LIMIT 10
    """)
    recent_articles = cursor.fetchall()
    
    conn.close()
    
    sources = load_sources()
    
    return render_template('index.html',
                         total_sent=total_sent,
                         source_stats=source_stats,
                         recent_articles=recent_articles,
                         total_sources=len(sources))

@app.route('/sources')
@login_required
def sources():
    """Manage sources."""
    sources = load_sources()
    return render_template('sources.html', sources=sources)

@app.route('/sources/add', methods=['POST'])
@login_required
def add_source():
    """Add new source."""
    name = request.form.get('name')
    url = request.form.get('url')
    selector = request.form.get('selector')
    
    if not all([name, url, selector]):
        flash('All fields required', 'error')
        return redirect(url_for('sources'))
    
    sources = load_sources()
    sources.append({
        'name': name,
        'url': url,
        'selector': selector
    })
    save_sources(sources)
    
    flash(f'Added source: {name}', 'success')
    return redirect(url_for('sources'))

@app.route('/sources/delete/<int:index>')
@login_required
def delete_source(index):
    """Delete source."""
    sources = load_sources()
    if 0 <= index < len(sources):
        deleted = sources.pop(index)
        save_sources(sources)
        flash(f'Deleted source: {deleted["name"]}', 'success')
    else:
        flash('Invalid source index', 'error')
    
    return redirect(url_for('sources'))

@app.route('/history')
@login_required
def history():
    """View sent articles history."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM sent_articles")
    total = cursor.fetchone()[0]
    
    # Get paginated articles
    cursor.execute("""
        SELECT * FROM sent_articles
        ORDER BY sent_at DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    articles = cursor.fetchall()
    
    conn.close()
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('history.html',
                         articles=articles,
                         page=page,
                         total_pages=total_pages,
                         total=total)

@app.route('/stats')
@login_required
def stats():
    """View detailed stats."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Articles by source
    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM sent_articles
        GROUP BY source
        ORDER BY count DESC
    """)
    by_source = cursor.fetchall()
    
    # Articles by date
    cursor.execute("""
        SELECT DATE(sent_at) as date, COUNT(*) as count
        FROM sent_articles
        GROUP BY DATE(sent_at)
        ORDER BY date DESC
        LIMIT 30
    """)
    by_date = cursor.fetchall()
    
    conn.close()
    
    return render_template('stats.html',
                         by_source=by_source,
                         by_date=by_date)

if __name__ == '__main__':
    # Initialize DB if needed
    import db
    db.init_db()
    
    # Initialize sources.json if doesn't exist
    if not SOURCES_FILE.exists():
        default_sources = [
            {"name": "Autoblog", "url": "https://www.autoblog.com/", "selector": "article h2 a"},
            {"name": "The Drive", "url": "https://www.thedrive.com/news", "selector": "h3 a"},
            {"name": "Jalopnik", "url": "https://jalopnik.com/", "selector": "h1 a"},
            {"name": "Electrek", "url": "https://electrek.co/", "selector": "h2.article-title a"},
            {"name": "Car and Driver", "url": "https://www.caranddriver.com/news/", "selector": "h3.article-title a"}
        ]
        save_sources(default_sources)
    
    print("🌐 Starting web UI at http://localhost:5000")
    print(f"📝 Login: {USERNAME} / {PASSWORD}")
    app.run(host='0.0.0.0', port=5000, debug=True)
