# 🚀 Quick Setup Guide - ReminderBot

## ⚡ Fast Start (5 minutes)

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Bot
```bash
python bot.py
```

**OR use the startup script:**
```bash
./start_bot.sh
```

## 📋 What You Get

✅ **Complete Telegram Bot** with your token: `8290575138:AAEdhmLvFkoG4l-RwnH3FbjV2nwaudJtHWk`

✅ **Natural Language Processing** - Users can say:
- "Remind me to drink water in 30 minutes"
- "Remind me every day at 7 AM to go for a walk"
- "Remind me to submit report on Monday at 9 AM"

✅ **Ad Monetization** - Built-in ad system with:
- External API support (AdsGram-style)
- Fallback ads for reliability
- Premium user system (ad-free)

✅ **Multi-language Support** - English and Hindi

✅ **Database** - SQLite with automatic setup

✅ **Scheduler** - APScheduler for reliable reminders

## 🎯 Bot Commands

- `/start` - Welcome message
- `/remind` - Set new reminder
- `/list` - Show all reminders
- `/delete` - Delete reminders
- `/help` - Help and examples

## 🔧 Files Created

```
remider/
├── bot.py              # Main bot (ready to run)
├── config.py           # Configuration (token included)
├── database.py         # Database operations
├── time_parser.py      # Natural language parsing
├── scheduler.py        # Reminder scheduling
├── ads.py             # Ad management
├── requirements.txt    # Dependencies
├── test_bot.py        # Test script
├── admin.py           # Admin console
├── setup.py           # Setup script
├── start_bot.sh       # Startup script
├── README.md          # Full documentation
└── SETUP_GUIDE.md    # This file
```

## 🧪 Test Everything

```bash
python test_bot.py
```

## 🔧 Admin Tools

```bash
python admin.py
```

Admin commands:
- `stats` - Show bot statistics
- `users` - List all users
- `reminders` - List all reminders
- `premium <user_id>` - Make user premium
- `free <user_id>` - Remove premium

## 🌐 Hosting Options

### Local Development
```bash
python bot.py
```

### Railway (Recommended)
1. Push to GitHub
2. Connect to Railway
3. Add environment variable: `BOT_TOKEN`
4. Deploy

### Replit
1. Create Python repl
2. Upload files
3. Add bot token to secrets
4. Run `python bot.py`

## 💰 Monetization

The bot includes:
- **Ad System**: Shows ads after each reminder
- **Premium Users**: Ad-free experience
- **External API**: Connect to real ad providers
- **Fallback Ads**: Always shows ads even if API fails

## 🎉 Ready to Use!

Your bot is fully functional with:
- ✅ Natural language processing
- ✅ Ad monetization
- ✅ Multi-language support
- ✅ Database storage
- ✅ Reliable scheduling
- ✅ Admin tools

**Just run `python bot.py` and start earning!** 