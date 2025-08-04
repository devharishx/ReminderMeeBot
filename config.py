import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = "7181313693:AAHOuIsik3hgFStg1e3Vfc_jrUSYcNsNCrc"

# Database
DATABASE_PATH = "reminders.db"

# AdsGram Configuration
ADSGRAM_API_URL = "https://adsgram.io/api/bot_ad"
ADSGRAM_BOT_USERNAME = "@Remindermeebot"
ADSGRAM_BOT_ID = "7181313693"
ADSGRAM_BOT_TOKEN = "7181313693:AAHOuIsik3hgFStg1e3Vfc_jrUSYcNsNCrc"
ADS_ENABLED = True
ADS_FREQUENCY = 1  # Show ad after every reminder
ADS_PLACEMENT = "after_reminder"  # After reminder is sent
ADS_TYPE = "any"  # Any type of ad

# Scheduler
SCHEDULER_TIMEZONE = "UTC"

# Limits
MAX_REMINDERS_PER_USER = 50
REMINDER_MESSAGE_LENGTH = 500

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "hi"]

# Messages
MESSAGES = {
    "en": {
        "welcome": "🎉 Welcome to ReminderBot!",
        "help": "📚 How to use ReminderBot",
        "reminder_sent": "✅ Reminder set successfully!",
        "no_reminders": "📝 You have no active reminders.",
        "reminder_deleted": "🗑️ Reminder deleted successfully!",
        "error": "❌ An error occurred. Please try again.",
        "ad_sponsored": "💼 Sponsored Message",
        "ad_premium": "⭐ Upgrade to Premium for ad-free experience!"
    },
    "hi": {
        "welcome": "🎉 रिमाइंडरबॉट में आपका स्वागत है!",
        "help": "📚 रिमाइंडरबॉट का उपयोग कैसे करें",
        "reminder_sent": "✅ रिमाइंडर सफलतापूर्वक सेट किया गया!",
        "no_reminders": "📝 आपके पास कोई सक्रिय रिमाइंडर नहीं है।",
        "reminder_deleted": "🗑️ रिमाइंडर सफलतापूर्वक हटा दिया गया!",
        "error": "❌ एक त्रुटि हुई। कृपया पुनः प्रयास करें।",
        "ad_sponsored": "💼 प्रायोजित संदेश",
        "ad_premium": "⭐ विज्ञापन-मुक्त अनुभव के लिए प्रीमियम में अपग्रेड करें!"
    }
} 