import asyncio
from typing import List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class BotAnimations:
    """Animation utilities for better UI experience"""
    
    @staticmethod
    async def typing_animation(bot, chat_id: int, duration: float = 1.0):
        """Show typing animation"""
        try:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(duration)
        except Exception as e:
            print(f"Error in typing animation: {e}")
    
    @staticmethod
    async def loading_animation(bot, chat_id: int, message: str = "Processing..."):
        """Show loading animation"""
        try:
            loading_msg = await bot.send_message(
                chat_id=chat_id,
                text=f"⏳ {message}",
                parse_mode='Markdown'
            )
            await asyncio.sleep(1.5)
            await bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        except Exception as e:
            print(f"Error in loading animation: {e}")
    
    @staticmethod
    def create_progress_bar(progress: float, width: int = 10) -> str:
        """Create a visual progress bar"""
        filled = int(width * progress)
        empty = width - filled
        return "█" * filled + "░" * empty
    
    @staticmethod
    def create_animated_text(text: str, animation_type: str = "typing") -> List[str]:
        """Create animated text frames"""
        if animation_type == "typing":
            frames = []
            for i in range(1, len(text) + 1):
                frames.append(text[:i] + "▋")
            return frames
        elif animation_type == "dots":
            frames = []
            for i in range(4):
                dots = "." * i
                frames.append(f"{text}{dots}")
            return frames
        return [text]
    
    @staticmethod
    def create_success_animation(task: str = "", time: str = "") -> str:
        """Create success animation text"""
        if task and time:
            return f"""
✅ *Success!* ✅

🎉 Your reminder has been set successfully!
📝 **Task:** {task}
⏰ **Time:** {time}
📱 You'll receive a push notification when it's time.
"""
        else:
            return """
✅ *Success!* ✅

🎉 Your reminder has been set successfully!
📱 You'll receive a push notification when it's time.
"""
    
    @staticmethod
    def create_error_animation() -> str:
        """Create error animation text"""
        return """
❌ *Oops!* ❌

Something went wrong. Please try again.
"""
    
    @staticmethod
    def create_splash_screen_animation() -> str:
        """Create beautiful splash screen for first-time users"""
        return """
🎉 *Welcome to ReminderBot!* 🎉

I'm your personal productivity assistant that helps you stay organized with smart reminders.

✨ *What I can do:*
• Set reminders with natural language
• Recurring reminders \\(daily, weekly, etc\\)
• Smart time parsing
• Push notifications
• Multi\\-language support

🚀 *Let's create your first reminder!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    @staticmethod
    def create_welcome_animation() -> str:
        """Create welcome animation text"""
        return """
🎉 *Welcome to ReminderBot!* 🎉

I'm your personal productivity assistant that helps you stay organized with smart reminders.

✨ *What I can do:*
• Set reminders with natural language
• Recurring reminders \\(daily, weekly, etc\\)
• Smart time parsing
• Push notifications
• Multi\\-language support

🚀 *Let's get started!*
"""
    
    @staticmethod
    def create_reminder_confirmation_animation(task: str, time: str) -> str:
        """Create reminder confirmation animation"""
        return f"""
🎯 *Reminder Confirmation* 🎯

📝 **Task:** {task}
⏰ **Time:** {time}
📱 **Type:** Push Notification

🎯 This reminder will be sent as a push notification to your phone!

Would you like to set this reminder?
"""
    
    @staticmethod
    def create_time_selection_animation() -> str:
        """Create time selection animation"""
        return """
⏰ *Choose Your Reminder Time* ⏰

Select when you want to be reminded:

Quick Options:
• 5 minutes
• 15 minutes  
• 30 minutes
• 1 hour
• 2 hours
• 4 hours

Or choose:
• Tomorrow
• Next week
• Daily
• Weekly
"""
    
    @staticmethod
    def create_task_input_animation() -> str:
        """Create task input animation"""
        return """
📝 *What do you want to be reminded about?* 📝

Please type your reminder task:

Examples:
• Call mom
• Buy groceries
• Submit report
• Drink water
• Take medicine
• Go for a walk
"""
    
    @staticmethod
    def create_clean_task_input_animation() -> str:
        """Create clean task input animation (no examples)"""
        return """
📝 *What do you want to be reminded about?*

Please type your reminder task:
"""
    
    @staticmethod
    def create_quick_task_input_animation() -> str:
        """Create quick task input animation"""
        return """
📝 *Quick Reminder Setup*

What do you want to be reminded about?

Please type your reminder task:
"""
    
    @staticmethod
    def create_reminders_list_animation(count: int) -> str:
        """Create reminders list animation"""
        if count == 0:
            return """
📭 *No Reminders Found* 📭

You don't have any reminders set yet.

Create your first reminder to get started!
"""
        else:
            return f"""
📋 *Your Reminders* 📋

You have {count} active reminder(s).
"""
    
    @staticmethod
    def create_delete_confirmation_animation() -> str:
        """Create delete confirmation animation"""
        return """
🗑️ *Delete Reminder* 🗑️

Select a reminder to delete from the list below.
"""
    
    @staticmethod
    def create_settings_animation() -> str:
        """Create settings animation"""
        return """
⚙️ *Settings* ⚙️

Customize your ReminderBot experience:

• Language settings
• Premium features
• Notification preferences
• Account management
"""
    
    @staticmethod
    def create_help_animation() -> str:
        """Create help animation"""
        return """
🤖 *ReminderBot Help* 🤖

Quick Examples:
• "Call mom in 2 hours"
• "Buy groceries tomorrow at 3 PM"
• "Submit report on Monday at 9 AM"
• "Drink water every 2 hours"
• "Go for a walk every day at 7 AM"

Features:
• Natural language processing
• Push notifications
• Recurring reminders
• Multi-language support
• Ad-free premium option
"""
    
    @staticmethod
    def create_keyboard_with_animation(keyboard_type: str = "main") -> InlineKeyboardMarkup:
        """Create animated keyboards"""
        if keyboard_type == "main":
            keyboard = [
                [InlineKeyboardButton("📝 Set New Reminder", callback_data="new_reminder")],
                [InlineKeyboardButton("📋 My Reminders", callback_data="list_reminders")],
                [InlineKeyboardButton("🗑️ Delete Reminder", callback_data="delete_reminder")],
                [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
                [InlineKeyboardButton("❓ Help", callback_data="help")]
            ]
        elif keyboard_type == "time":
            keyboard = [
                [
                    InlineKeyboardButton("⏰ 5 minutes", callback_data="time_5min"),
                    InlineKeyboardButton("⏰ 15 minutes", callback_data="time_15min"),
                    InlineKeyboardButton("⏰ 30 minutes", callback_data="time_30min")
                ],
                [
                    InlineKeyboardButton("⏰ 1 hour", callback_data="time_1hour"),
                    InlineKeyboardButton("⏰ 2 hours", callback_data="time_2hours"),
                    InlineKeyboardButton("⏰ 4 hours", callback_data="time_4hours")
                ],
                [
                    InlineKeyboardButton("📅 Tomorrow", callback_data="time_tomorrow"),
                    InlineKeyboardButton("📅 Next week", callback_data="time_nextweek")
                ],
                [
                    InlineKeyboardButton("🔄 Daily", callback_data="time_daily"),
                    InlineKeyboardButton("🔄 Weekly", callback_data="time_weekly")
                ],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_reminder")]
            ]
        elif keyboard_type == "confirm":
            keyboard = [
                [
                    InlineKeyboardButton("✅ Confirm", callback_data="confirm_reminder"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_reminder")
                ]
            ]
        else:
            keyboard = [[InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")]]
        
        return InlineKeyboardMarkup(keyboard) 