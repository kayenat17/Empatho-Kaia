import sqlite3
from datetime import datetime, timedelta
from collections import Counter
import json

def init_db():
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='journal'")
    table_exists = c.fetchone() is not None
    
    if not table_exists:
        # Create new table with all columns
        c.execute('''
            CREATE TABLE journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry TEXT NOT NULL,
                emotion TEXT,
                full_analysis TEXT,
                sentiment TEXT,
                timestamp TEXT
            )
        ''')
    else:
        # Check if new columns exist, add them if they don't
        c.execute("PRAGMA table_info(journal)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'full_analysis' not in columns:
            c.execute('ALTER TABLE journal ADD COLUMN full_analysis TEXT')
        
        if 'sentiment' not in columns:
            c.execute('ALTER TABLE journal ADD COLUMN sentiment TEXT')
    
    conn.commit()
    conn.close()

def save_entry(entry, emotion, full_analysis, sentiment):
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    
    # Check if new columns exist
    c.execute("PRAGMA table_info(journal)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'full_analysis' in columns and 'sentiment' in columns:
        # Use new schema
        c.execute('''
            INSERT INTO journal (entry, emotion, full_analysis, sentiment, timestamp) 
            VALUES (?, ?, ?, ?, ?)
        ''', (entry, emotion, full_analysis, sentiment, timestamp))
    else:
        # Use old schema
        c.execute('''
            INSERT INTO journal (entry, emotion, timestamp) 
            VALUES (?, ?, ?)
        ''', (entry, emotion, timestamp))
    
    conn.commit()
    conn.close()

def get_all_entries():
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, entry, emotion, full_analysis, sentiment, timestamp 
        FROM journal ORDER BY id DESC
    ''')
    entries = []
    for row in c.fetchall():
        entry_data = {
            'id': row[0], 
            'entry': row[1], 
            'emotion': row[2], 
            'sentiment': row[4],
            'timestamp': row[5]
        }
        
        # Parse full analysis if available
        if row[3]:
            try:
                entry_data['full_analysis'] = json.loads(row[3])
            except:
                entry_data['full_analysis'] = None
                
        entries.append(entry_data)
    conn.close()
    return entries

def get_emotion_stats():
    """Get emotion statistics and trends"""
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    
    # Check if sentiment column exists
    c.execute("PRAGMA table_info(journal)")
    columns = [column[1] for column in c.fetchall()]
    
    # Get all entries from last 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    
    if 'sentiment' in columns:
        c.execute('''
            SELECT emotion, sentiment, timestamp 
            FROM journal 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC
        ''', (thirty_days_ago,))
    else:
        c.execute('''
            SELECT emotion, timestamp 
            FROM journal 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC
        ''', (thirty_days_ago,))
    
    recent_entries = c.fetchall()
    
    # Calculate statistics
    emotion_counts = Counter([entry[0] for entry in recent_entries])
    
    if 'sentiment' in columns:
        sentiment_counts = Counter([entry[1] for entry in recent_entries])
    else:
        # If no sentiment column, create empty counter
        sentiment_counts = Counter()
    
    # Calculate daily averages
    daily_emotions = {}
    for entry in recent_entries:
        if 'sentiment' in columns:
            date = entry[2][:10]  # Get just the date part
        else:
            date = entry[1][:10]  # Get just the date part
        if date not in daily_emotions:
            daily_emotions[date] = []
        daily_emotions[date].append(entry[0])
    
    # Get streak information
    c.execute('''
        SELECT COUNT(*) as streak 
        FROM (
            SELECT DISTINCT DATE(timestamp) as entry_date 
            FROM journal 
            ORDER BY entry_date DESC
        )
    ''')
    total_days = c.fetchone()[0]
    
    # Get recent activity
    c.execute('''
        SELECT COUNT(*) 
        FROM journal 
        WHERE timestamp > ?
    ''', ((datetime.now() - timedelta(days=7)).isoformat(),))
    weekly_entries = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_entries': len(recent_entries),
        'emotion_distribution': dict(emotion_counts),
        'sentiment_distribution': dict(sentiment_counts),
        'daily_averages': {date: Counter(emotions).most_common(1)[0][0] 
                          for date, emotions in daily_emotions.items()},
        'streak_days': total_days,
        'weekly_entries': weekly_entries,
        'most_common_emotion': emotion_counts.most_common(1)[0][0] if emotion_counts else 'neutral',
        'overall_sentiment': sentiment_counts.most_common(1)[0][0] if sentiment_counts else 'neutral'
    }

def get_entries_by_date_range(start_date, end_date):
    """Get entries within a specific date range"""
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, entry, emotion, full_analysis, sentiment, timestamp 
        FROM journal 
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
    ''', (start_date, end_date))
    
    entries = []
    for row in c.fetchall():
        entry_data = {
            'id': row[0], 
            'entry': row[1], 
            'emotion': row[2], 
            'sentiment': row[4],
            'timestamp': row[5]
        }
        
        if row[3]:
            try:
                entry_data['full_analysis'] = json.loads(row[3])
            except:
                entry_data['full_analysis'] = None
                
        entries.append(entry_data)
    
    conn.close()
    return entries


