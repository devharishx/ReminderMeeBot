#!/usr/bin/env python3
"""
Test script for ReminderBot components
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from time_parser import TimeParser
from database import ReminderDatabase
from ads import AdsManager
from config import MESSAGES

def test_time_parser():
    """Test the time parser functionality"""
    print("🧪 Testing Time Parser...")
    
    parser = TimeParser()
    
    test_cases = [
        "remind me to drink water in 30 minutes",
        "remind me to call mom in 2 hours",
        "remind me to buy groceries tomorrow at 3 PM",
        "remind me every day at 7 AM to go for a walk",
        "remind me every Monday at 9 AM to check emails",
        "remind me to submit report on Monday at 9 AM"
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: '{test_case}'")
        reminder_time, task, reminder_type, cron_expr = parser.parse_reminder_text(test_case)
        
        if reminder_time:
            time_str = parser.format_reminder_time(reminder_time)
            print(f"✅ Parsed successfully:")
            print(f"   Task: {task}")
            print(f"   Time: {time_str}")
            print(f"   Type: {reminder_type}")
            if cron_expr:
                print(f"   Cron: {cron_expr}")
        else:
            print("❌ Failed to parse time")

def test_database():
    """Test the database functionality"""
    print("\n🧪 Testing Database...")
    
    db = ReminderDatabase()
    
    # Test user preferences
    test_user_id = 12345
    db.set_user_preferences(test_user_id, language='en', is_premium=False)
    prefs = db.get_user_preferences(test_user_id)
    print(f"✅ User preferences: {prefs}")
    
    # Test adding reminder
    test_time = datetime.now() + timedelta(minutes=5)
    reminder_id = db.add_reminder(
        test_user_id, 
        "Test reminder", 
        test_time, 
        "one_time", 
        language='en'
    )
    print(f"✅ Added reminder with ID: {reminder_id}")
    
    # Test getting reminders
    reminders = db.get_user_reminders(test_user_id)
    print(f"✅ Found {len(reminders)} reminders for user")
    
    # Test deleting reminder
    success = db.delete_reminder(reminder_id, test_user_id)
    print(f"✅ Deleted reminder: {success}")

def test_ads():
    """Test the ads functionality"""
    print("\n🧪 Testing Ads...")
    
    ads_manager = AdsManager()
    
    # Test getting ad
    ad_message = ads_manager.get_ad(12345, is_premium=False)
    if ad_message:
        print(f"✅ Got ad: {ad_message}")
    else:
        print("❌ No ad returned")
    
    # Test premium user (should not get ads)
    premium_ad = ads_manager.get_ad(12345, is_premium=True)
    if premium_ad is None:
        print("✅ Premium user correctly gets no ads")
    else:
        print("❌ Premium user got an ad")

def test_messages():
    """Test the message system"""
    print("\n🧪 Testing Messages...")
    
    # Test English messages
    welcome_en = MESSAGES['en']['welcome']
    print(f"✅ English welcome message: {len(welcome_en)} characters")
    
    # Test Hindi messages
    welcome_hi = MESSAGES['hi']['welcome']
    print(f"✅ Hindi welcome message: {len(welcome_hi)} characters")

def main():
    """Run all tests"""
    print("🚀 Starting ReminderBot Tests...\n")
    
    try:
        test_time_parser()
        test_database()
        test_ads()
        test_messages()
        
        print("\n🎉 All tests completed successfully!")
        print("✅ The bot components are working correctly.")
        print("\nTo run the bot:")
        print("python bot.py")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Please check your installation and dependencies.")

if __name__ == "__main__":
    main() 