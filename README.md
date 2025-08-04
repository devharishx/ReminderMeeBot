# 🤖 ReminderBot - Telegram Reminder Bot with Ads

A powerful Telegram bot that allows users to set natural-language reminders with built-in ad monetization.

## ✨ Features

- **Natural Language Processing**: Set reminders using natural language like "remind me to drink water in 30 minutes"
- **Multiple Reminder Types**: One-time and recurring reminders
- **Smart Time Parsing**: Understands various time formats (in X minutes, tomorrow at 5pm, every Monday, etc.)
- **Ad Monetization**: Built-in ad system with external API support
- **Multi-language Support**: English and Hindi
- **Premium System**: Ad-free experience for premium users
- **Easy Management**: List, delete, and manage all reminders

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Telegram bot token (get from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**:
   - Open `config.py`
   - Update `BOT_TOKEN` with your bot token
   - Customize other settings as needed

4. **Run the bot**:
   ```bash
   python bot.py
   ```

## 📋 Bot Commands

- `/start` - Welcome message and instructions
- `/remind` - Set a new reminder
- `/list` - Show all your reminders
- `/delete` - Delete a specific reminder
- `/help` - Show help and examples

## 💬 Usage Examples

### One-time Reminders
- "Remind me to call mom in 2 hours"
- "Remind me to buy groceries tomorrow at 3 PM"
- "Remind me to submit report on Monday at 9 AM"

### Recurring Reminders
- "Remind me every day at 7 AM to go for a walk"
- "Remind me every Monday at 9 AM to check emails"
- "Remind me every 2 hours to drink water"

## 🏗️ Project Structure

```
reminder-bot/
├── bot.py              # Main bot file
├── config.py           # Configuration settings
├── database.py         # Database operations
├── time_parser.py      # Natural language time parsing
├── scheduler.py        # Reminder scheduling
├── ads.py             # Ad management
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── reminders.db       # SQLite database (created automatically)
```

## 🔧 Configuration

### Bot Settings (`config.py`)

```python
# Bot Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Database Configuration
DATABASE_PATH = "reminders.db"

# Ads Configuration
ADS_API_URL = "https://adsgram.io/api/bot_ad"
ADS_ENABLED = True

# Bot Settings
MAX_REMINDERS_PER_USER = 50
```

### Ad System

The bot includes a built-in ad system that:
- Fetches ads from external APIs (like AdsGram)
- Shows fallback ads if external API is unavailable
- Skips ads for premium users
- Can be easily customized or disabled

## 🌐 Hosting Options

### Local Development
```bash
python bot.py
```

### Railway (Recommended)
1. Create account on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables:
   - `BOT_TOKEN`: Your bot token
4. Deploy

### Replit
1. Create new Python repl
2. Upload all files
3. Add bot token to secrets
4. Run `python bot.py`

### Heroku
1. Create `Procfile`:
   ```
   worker: python bot.py
   ```
2. Deploy using Heroku CLI or GitHub integration

## 🎯 Advanced Features

### Premium System
- Premium users get ad-free experience
- Set `is_premium = True` in database for specific users
- Easy to extend with payment integration

### Multi-language Support
- English and Hindi support
- Easy to add more languages
- Language detection based on user preferences

### Custom Ad Integration
- Replace `ADS_API_URL` with your ad provider
- Modify `ads.py` for custom ad logic
- Add ad frequency controls

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check if bot token is correct
   - Ensure bot is not blocked by user
   - Check console for error messages

2. **Reminders not sending**:
   - Verify scheduler is running
   - Check database connectivity
   - Ensure bot has permission to send messages

3. **Time parsing issues**:
   - Check time format in user input
   - Verify timezone settings
   - Test with simple time formats first

### Debug Mode

Enable debug logging by modifying `bot.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Monetization

### Ad Revenue
- Built-in ad system with external API support
- Fallback ads for reliability
- Premium user system for ad-free experience

### Premium Features (Future)
- Unlimited reminders
- Advanced scheduling
- Custom themes
- Priority support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For support or questions:
- Create an issue on GitHub
- Contact the bot developer
- Check the documentation

## 🔄 Updates

### Version 1.0.0
- Initial release
- Natural language processing
- Basic ad system
- Multi-language support
- SQLite database

### Planned Features
- Web dashboard for management
- Advanced recurring patterns
- Integration with calendar apps
- Voice reminder support
- Group reminder support

---

**Made with ❤️ for productivity and monetization** 