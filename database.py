import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_PATH

class ReminderDatabase:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                reminder_time DATETIME NOT NULL,
                reminder_type TEXT NOT NULL,
                cron_expression TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                language TEXT DEFAULT 'en'
            )
        ''')
        
        # Create user preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'en',
                is_premium BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_reminder(self, user_id: int, task: str, reminder_time: datetime, 
                    reminder_type: str, cron_expression: str = None, language: str = 'en') -> int:
        """Add a new reminder to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reminders (user_id, task, reminder_time, reminder_type, cron_expression, language)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, task, reminder_time, reminder_type, cron_expression, language))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reminder_id
    
    def get_user_reminders(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all reminders for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, task, reminder_time, reminder_type, cron_expression, language
            FROM reminders 
            WHERE user_id = ?
        '''
        
        if active_only:
            query += ' AND is_active = 1'
        
        query += ' ORDER BY reminder_time ASC'
        
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        reminders = []
        for row in rows:
            reminders.append({
                'id': row[0],
                'task': row[1],
                'reminder_time': datetime.fromisoformat(row[2]),
                'reminder_type': row[3],
                'cron_expression': row[4],
                'language': row[5]
            })
        
        conn.close()
        return reminders
    
    def get_reminder_by_id(self, reminder_id: int) -> Optional[Dict]:
        """Get a specific reminder by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, task, reminder_time, reminder_type, cron_expression, language
            FROM reminders 
            WHERE id = ? AND is_active = 1
        ''', (reminder_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'task': row[2],
                'reminder_time': datetime.fromisoformat(row[3]),
                'reminder_type': row[4],
                'cron_expression': row[5],
                'language': row[6]
            }
        return None
    
    def delete_reminder(self, reminder_id: int, user_id: int) -> bool:
        """Delete a reminder (mark as inactive)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reminders 
            SET is_active = 0 
            WHERE id = ? AND user_id = ?
        ''', (reminder_id, user_id))
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    def get_due_reminders(self) -> List[Dict]:
        """Get all reminders that are due to be sent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, task, reminder_time, reminder_type, cron_expression, language
            FROM reminders 
            WHERE reminder_time <= datetime('now') AND is_active = 1
            ORDER BY reminder_time ASC
        ''')
        
        rows = cursor.fetchall()
        
        reminders = []
        for row in rows:
            reminders.append({
                'id': row[0],
                'user_id': row[1],
                'task': row[2],
                'reminder_time': datetime.fromisoformat(row[3]),
                'reminder_type': row[4],
                'cron_expression': row[5],
                'language': row[6]
            })
        
        conn.close()
        return reminders
    
    def mark_reminder_sent(self, reminder_id: int):
        """Mark a one-time reminder as sent (delete it)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reminders 
            SET is_active = 0 
            WHERE id = ? AND reminder_type = 'one_time'
        ''', (reminder_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT language, is_premium 
            FROM user_preferences 
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'language': row[0],
                'is_premium': bool(row[1])
            }
        return {'language': 'en', 'is_premium': False}
    
    def set_user_preferences(self, user_id: int, language: str = 'en', is_premium: bool = False):
        """Set user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, language, is_premium)
            VALUES (?, ?, ?)
        ''', (user_id, language, is_premium))
        
        conn.commit()
        conn.close()
    
    def get_reminder_count(self, user_id: int) -> int:
        """Get the number of active reminders for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) 
            FROM reminders 
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count 