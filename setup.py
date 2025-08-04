#!/usr/bin/env python3
"""
Setup script for ReminderBot
"""

import os
import sys
import subprocess
import sqlite3
from datetime import datetime

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_database():
    """Create and initialize the database"""
    print("🗄️ Creating database...")
    try:
        from database import ReminderDatabase
        db = ReminderDatabase()
        print("✅ Database created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def test_components():
    """Test all bot components"""
    print("🧪 Testing components...")
    try:
        subprocess.check_call([sys.executable, "test_bot.py"])
        print("✅ All components working correctly")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Component test failed: {e}")
        return False

def check_config():
    """Check if configuration is valid"""
    print("⚙️ Checking configuration...")
    try:
        from config import BOT_TOKEN, ADS_API_URL, ADS_ENABLED
        if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN":
            print("✅ Bot token configured")
        else:
            print("⚠️ Please update BOT_TOKEN in config.py")
        
        print(f"✅ Ads API URL: {ADS_API_URL}")
        print(f"✅ Ads enabled: {ADS_ENABLED}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def create_env_file():
    """Create .env file for environment variables"""
    env_content = """# ReminderBot Environment Variables
# Add your bot token here
BOT_TOKEN=8290575138:AAEdhmLvFkoG4l-RwnH3FbjV2nwaudJtHWk

# Database settings
DATABASE_PATH=reminders.db

# Ads configuration
ADS_API_URL=https://adsgram.io/api/bot_ad
ADS_ENABLED=True

# Scheduler settings
SCHEDULER_TIMEZONE=UTC
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 ReminderBot Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create database
    if not create_database():
        return False
    
    # Check configuration
    if not check_config():
        print("⚠️ Please update your configuration before running the bot")
    
    # Test components
    if not test_components():
        print("⚠️ Some components failed tests, but you can still try running the bot")
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Update BOT_TOKEN in config.py with your bot token")
    print("2. Run the bot: python bot.py")
    print("3. Test the bot: python test_bot.py")
    print("\n📚 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 