import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from database import ReminderDatabase
from ads import AdsManager
from config import SCHEDULER_TIMEZONE

class ReminderScheduler:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.db = ReminderDatabase()
        self.ads_manager = AdsManager()
        self.scheduler = AsyncIOScheduler(timezone=SCHEDULER_TIMEZONE)
        self.scheduler.start()
        
        # Start the reminder checker
        self.scheduler.add_job(
            self.check_due_reminders,
            'interval',
            minutes=1,
            id='check_due_reminders'
        )
    
    async def add_reminder(self, user_id: int, task: str, reminder_time: datetime, 
                          reminder_type: str, cron_expression: str = None, language: str = 'en') -> int:
        """Add a new reminder to the scheduler"""
        try:
            # Add to database
            reminder_id = self.db.add_reminder(
                user_id, task, reminder_time, reminder_type, cron_expression, language
            )
            
            print(f"📅 Scheduling reminder {reminder_id} for user {user_id}")
            print(f"📅 Task: {task}")
            print(f"📅 Time: {reminder_time}")
            print(f"📅 Type: {reminder_type}")
            
            # Schedule the reminder
            if reminder_type == 'one_time':
                self.scheduler.add_job(
                    self.send_reminder,
                    DateTrigger(run_date=reminder_time),
                    args=[reminder_id, user_id, task, reminder_time],
                    id=f'reminder_{reminder_id}'
                )
                print(f"✅ Scheduled one-time reminder {reminder_id} for {reminder_time}")
                
            elif reminder_type == 'recurring' and cron_expression:
                self.scheduler.add_job(
                    self.send_recurring_reminder,
                    CronTrigger.from_crontab(cron_expression),
                    args=[reminder_id, user_id, task, reminder_time],
                    id=f'recurring_{reminder_id}'
                )
                print(f"✅ Scheduled recurring reminder {reminder_id} with cron: {cron_expression}")
            
            return reminder_id
            
        except Exception as e:
            print(f"❌ Error adding reminder: {e}")
            return None
    
    async def send_reminder(self, reminder_id: int, user_id: int, task: str, reminder_time):
        """Send reminder to user with enhanced notification"""
        try:
            # Format reminder message with better notification formatting
            message = f"""
🔔 *REMINDER!* 🔔

📝 **Task:** {task}
⏰ **Time:** {datetime.now().strftime("%I:%M %p")}
📱 **Type:** Push Notification

💡 *Don't forget to complete this task!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            # Send the reminder with notification enabled
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown',
                disable_notification=False,  # Enable push notification
                disable_web_page_preview=True
            )
            
            # Send simple notification message for immediate visibility
            simple_notification = f"🔔 REMINDER: {task}"
            await self.bot.send_message(
                chat_id=user_id,
                text=simple_notification,
                parse_mode='Markdown',
                disable_notification=False,  # Enable push notification
                disable_web_page_preview=True
            )
            
            self.db.mark_reminder_sent(reminder_id)
            
            print(f"📱 Sent push reminder {reminder_id} to user {user_id}")
            print(f"📱 Notification: {task}")
            
            # Show ad after reminder (if enabled)
            await self._show_ad_after_reminder(user_id)
            
            # Show "Set New Reminder" button as a separate message after everything
            await self._show_set_new_reminder_button(user_id)
            
        except Exception as e:
            print(f"Error sending reminder {reminder_id}: {e}")
    
    async def send_recurring_reminder(self, reminder_id: int, user_id: int, task: str, reminder_time):
        """Send recurring reminder to user with enhanced notification"""
        try:
            # Format reminder message with better notification formatting
            message = f"""
🔄 *RECURRING REMINDER!* 🔄

📝 **Task:** {task}
⏰ **Time:** {datetime.now().strftime("%I:%M %p")}
📅 **Type:** Recurring

💡 *Don't forget to complete this task!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            # Create keyboard with "Set New Reminder" button
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("📝 Set New Reminder", callback_data="new_reminder")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send the reminder with notification enabled and keyboard
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown',
                disable_notification=False,  # Enable push notification
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
            
            # Also send a simple notification message for better visibility
            notification_msg = f"🔄 RECURRING: {task}"
            await self.bot.send_message(
                chat_id=user_id,
                text=notification_msg,
                disable_notification=False,  # Enable push notification
                disable_web_page_preview=True
            )
            
            print(f"🔄 Sent recurring reminder {reminder_id} to user {user_id}")
            print(f"🔄 Notification: {task}")
            
            # Show ad after reminder (if enabled)
            await self._show_ad_after_reminder(user_id)
            
        except Exception as e:
            print(f"Error sending recurring reminder {reminder_id}: {e}")
    
    async def _show_ad_after_reminder(self, user_id: int):
        """Show ad after reminder is sent"""
        try:
            from ads import AdsManager
            ads_manager = AdsManager()
            
            if ads_manager.should_show_ad(user_id):
                ad_message = await ads_manager.get_ad(user_id, "en")
                if ad_message:
                    # Add a small delay before showing ad
                    await asyncio.sleep(2)
                    
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=ad_message,
                        parse_mode='Markdown',
                        disable_web_page_preview=False
                    )
                    print(f"💼 Sent ad to user {user_id}")
                    
        except Exception as e:
            print(f"Error showing ad to user {user_id}: {e}")
    
    async def check_due_reminders(self):
        """Check for due reminders and send them"""
        try:
            due_reminders = self.db.get_due_reminders()
            
            for reminder in due_reminders:
                print(f"🔍 Checking reminder {reminder['id']} for user {reminder['user_id']}")
                
                if reminder['reminder_type'] == 'one_time':
                    await self.send_reminder(
                        reminder['id'],
                        reminder['user_id'],
                        reminder['task'],
                        reminder['reminder_time']
                    )
                elif reminder['reminder_type'] == 'recurring':
                    await self.send_recurring_reminder(
                        reminder['id'],
                        reminder['user_id'],
                        reminder['task'],
                        reminder['reminder_time']
                    )
                    
        except Exception as e:
            print(f"Error checking due reminders: {e}")
    
    def delete_reminder(self, reminder_id: int, user_id: int) -> bool:
        """Delete a reminder from the scheduler"""
        try:
            # Remove from database
            success = self.db.delete_reminder(reminder_id, user_id)
            
            if success:
                # Remove from scheduler
                job_id = f'reminder_{reminder_id}'
                recurring_job_id = f'recurring_{reminder_id}'
                
                try:
                    self.scheduler.remove_job(job_id)
                except:
                    pass
                
                try:
                    self.scheduler.remove_job(recurring_job_id)
                except:
                    pass
            
            return success
            
        except Exception as e:
            print(f"Error deleting reminder {reminder_id}: {e}")
            return False
    
    def get_scheduler_status(self) -> Dict:
        """Get scheduler status for monitoring"""
        return {
            "running": self.scheduler.running,
            "job_count": len(self.scheduler.get_jobs()),
            "timezone": SCHEDULER_TIMEZONE
        }
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown() 

    async def _show_set_new_reminder_button(self, user_id: int):
        """Show 'Set New Reminder' button as a separate message"""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            # Create keyboard with "Set New Reminder" button
            keyboard = [
                [InlineKeyboardButton("📝 Set New Reminder", callback_data="new_reminder")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send the button as a separate message
            await self.bot.send_message(
                chat_id=user_id,
                text="💡 *Want to set another reminder?*",
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
            print(f"📝 Sent 'Set New Reminder' button to user {user_id}")
            
        except Exception as e:
            print(f"Error showing 'Set New Reminder' button to user {user_id}: {e}") 