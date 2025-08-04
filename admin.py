#!/usr/bin/env python3
"""
Admin script for ReminderBot management
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import ReminderDatabase
from ads import AdsManager
from config import MESSAGES

class BotAdmin:
    def __init__(self):
        self.db = ReminderDatabase()
        self.ads_manager = AdsManager()
    
    def show_statistics(self):
        """Show bot statistics"""
        print("📊 ReminderBot Statistics")
        print("=" * 40)
        
        # Get all reminders
        conn = self.db.db_path
        import sqlite3
        conn = sqlite3.connect(conn)
        cursor = conn.cursor()
        
        # Total reminders
        cursor.execute("SELECT COUNT(*) FROM reminders")
        total_reminders = cursor.fetchone()[0]
        
        # Active reminders
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE is_active = 1")
        active_reminders = cursor.fetchone()[0]
        
        # Total users
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM reminders")
        total_users = cursor.fetchone()[0]
        
        # Premium users
        cursor.execute("SELECT COUNT(*) FROM user_preferences WHERE is_premium = 1")
        premium_users = cursor.fetchone()[0]
        
        # Reminder types
        cursor.execute("SELECT reminder_type, COUNT(*) FROM reminders GROUP BY reminder_type")
        reminder_types = cursor.fetchall()
        
        conn.close()
        
        print(f"📈 Total Reminders: {total_reminders}")
        print(f"✅ Active Reminders: {active_reminders}")
        print(f"👥 Total Users: {total_users}")
        print(f"⭐ Premium Users: {premium_users}")
        print(f"📅 Reminder Types:")
        for reminder_type, count in reminder_types:
            print(f"   {reminder_type}: {count}")
        
        # Ad statistics
        ad_stats = self.ads_manager.get_ad_stats()
        print(f"\n📢 Ad Statistics:")
        print(f"   Ads Enabled: {ad_stats['ads_enabled']}")
        print(f"   API URL: {ad_stats['api_url']}")
        print(f"   Fallback Ads: {ad_stats['fallback_ads_count']}")
    
    def list_users(self):
        """List all users with their reminder counts"""
        print("👥 User List")
        print("=" * 40)
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.user_id, COUNT(r.id) as reminder_count, 
                   up.is_premium, up.language
            FROM reminders r
            LEFT JOIN user_preferences up ON r.user_id = up.user_id
            WHERE r.is_active = 1
            GROUP BY r.user_id
            ORDER BY reminder_count DESC
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            print("No users found")
            return
        
        for user_id, reminder_count, is_premium, language in users:
            premium_status = "⭐ Premium" if is_premium else "👤 Free"
            lang = language or "en"
            print(f"User {user_id}: {reminder_count} reminders ({premium_status}) [{lang}]")
    
    def list_reminders(self, user_id=None):
        """List all reminders"""
        print("📋 Reminder List")
        print("=" * 40)
        
        if user_id:
            reminders = self.db.get_user_reminders(user_id)
            print(f"Reminders for user {user_id}:")
        else:
            # Get all reminders
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, task, reminder_time, reminder_type, is_active
                FROM reminders
                ORDER BY reminder_time DESC
                LIMIT 20
            """)
            rows = cursor.fetchall()
            conn.close()
            
            reminders = []
            for row in rows:
                reminders.append({
                    'id': row[0],
                    'user_id': row[1],
                    'task': row[2],
                    'reminder_time': datetime.fromisoformat(row[3]),
                    'reminder_type': row[4],
                    'is_active': bool(row[5])
                })
        
        if not reminders:
            print("No reminders found")
            return
        
        for reminder in reminders:
            status = "✅ Active" if reminder['is_active'] else "❌ Inactive"
            time_str = reminder['reminder_time'].strftime("%Y-%m-%d %H:%M")
            print(f"ID {reminder['id']} (User {reminder['user_id']}): {reminder['task']}")
            print(f"   Time: {time_str} | Type: {reminder['reminder_type']} | {status}")
            print()
    
    def delete_user_reminders(self, user_id):
        """Delete all reminders for a user"""
        print(f"🗑️ Deleting all reminders for user {user_id}...")
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE reminders SET is_active = 0 WHERE user_id = ?", (user_id,))
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ Deleted {affected_rows} reminders for user {user_id}")
    
    def set_premium_user(self, user_id, is_premium=True):
        """Set user premium status"""
        print(f"⭐ Setting premium status for user {user_id}: {is_premium}")
        
        self.db.set_user_preferences(user_id, is_premium=is_premium)
        print(f"✅ User {user_id} premium status updated")
    
    def show_help(self):
        """Show admin help"""
        print("🔧 ReminderBot Admin Commands")
        print("=" * 40)
        print("stats                    - Show bot statistics")
        print("users                    - List all users")
        print("reminders [user_id]      - List reminders (optional user_id)")
        print("delete-user <user_id>    - Delete all reminders for user")
        print("premium <user_id>        - Make user premium")
        print("free <user_id>           - Remove premium from user")
        print("help                     - Show this help")
        print("quit                     - Exit admin")

def main():
    """Main admin function"""
    admin = BotAdmin()
    
    print("🔧 ReminderBot Admin Console")
    print("Type 'help' for commands")
    print()
    
    while True:
        try:
            command = input("admin> ").strip().lower()
            
            if command == "quit" or command == "exit":
                print("👋 Goodbye!")
                break
            elif command == "help":
                admin.show_help()
            elif command == "stats":
                admin.show_statistics()
            elif command == "users":
                admin.list_users()
            elif command.startswith("reminders"):
                parts = command.split()
                user_id = int(parts[1]) if len(parts) > 1 else None
                admin.list_reminders(user_id)
            elif command.startswith("delete-user"):
                parts = command.split()
                if len(parts) > 1:
                    user_id = int(parts[1])
                    admin.delete_user_reminders(user_id)
                else:
                    print("❌ Please provide user ID")
            elif command.startswith("premium"):
                parts = command.split()
                if len(parts) > 1:
                    user_id = int(parts[1])
                    admin.set_premium_user(user_id, True)
                else:
                    print("❌ Please provide user ID")
            elif command.startswith("free"):
                parts = command.split()
                if len(parts) > 1:
                    user_id = int(parts[1])
                    admin.set_premium_user(user_id, False)
                else:
                    print("❌ Please provide user ID")
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 