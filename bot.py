import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
from telegram.error import TelegramError
from telegram.constants import ParseMode

from config import BOT_TOKEN, MESSAGES, MAX_REMINDERS_PER_USER
from database import ReminderDatabase
from time_parser import TimeParser
from scheduler import ReminderScheduler
from ads import AdsManager
from animations import BotAnimations

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CHOOSING_ACTION, ENTERING_TASK, CHOOSING_TIME, CONFIRMING_REMINDER = range(4)

class ReminderBot:
    def __init__(self):
        self.db = ReminderDatabase()
        self.time_parser = TimeParser()
        self.ads_manager = AdsManager()
        self.scheduler = None  # Will be initialized after bot creation
        
        # User states for conversation flow
        self.user_states = {}
        self.user_data = {}  # Store temporary user data
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with beautiful welcome"""
        user_id = update.effective_user.id
        user_prefs = self.db.get_user_preferences(user_id)
        language = user_prefs.get('language', 'en')
        
        # Check if this is first time user
        reminders = self.db.get_user_reminders(user_id)
        is_first_time = len(reminders) == 0
        
        if is_first_time:
            # Show splash screen animation for first-time users
            await self.show_splash_screen(update)
        else:
            # Show regular welcome for returning users
            await self.show_main_menu_from_message(update)
    
    async def show_splash_screen(self, update: Update):
        """Show beautiful splash screen for first-time users"""
        user_id = update.effective_user.id
        
        # Show typing animation
        await BotAnimations.typing_animation(self.scheduler.bot, user_id, 2.0)
        
        splash_text = BotAnimations.create_splash_screen_animation()
        
        # Create main menu keyboard
        reply_markup = BotAnimations.create_keyboard_with_animation("main")
        
        await update.message.reply_text(
            splash_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def test_notification_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test notification command"""
        user_id = update.effective_user.id
        
        try:
            # Send a test notification
            test_message = "🔔 TEST NOTIFICATION 🔔\n\nThis is a test push notification to verify your notification settings."
            
            await self.scheduler.bot.send_message(
                chat_id=user_id,
                text=test_message,
                parse_mode='Markdown',
                disable_notification=False,  # Enable push notification
                disable_web_page_preview=True
            )
            
            # Send simple test notification
            simple_test = "🔔 TEST: Notification check"
            await self.scheduler.bot.send_message(
                chat_id=user_id,
                text=simple_test,
                parse_mode='Markdown',
                disable_notification=False,  # Enable push notification
                disable_web_page_preview=True
            )
            
            # Show "Set New Reminder" button as a separate message
            keyboard = [
                [InlineKeyboardButton("📝 Set New Reminder", callback_data="new_reminder")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.scheduler.bot.send_message(
                chat_id=user_id,
                text="💡 *Want to set a reminder?*",
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
            await update.message.reply_text("✅ Test notification sent! Check your phone for the push notification.")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending test notification: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command with examples"""
        user_id = update.effective_user.id
        user_prefs = self.db.get_user_preferences(user_id)
        language = user_prefs.get('language', 'en')
        
        help_text = """
🤖 *ReminderBot Help*

*Quick Examples:*
• "Call mom in 2 hours"
• "Buy groceries tomorrow at 3 PM"
• "Submit report on Monday at 9 AM"
• "Drink water every 2 hours"
• "Go for a walk every day at 7 AM"

*Commands:*
• `/start` - Main menu
• `/remind` - Quick reminder setup
• `/list` - View all reminders
• `/delete` - Remove reminders
• `/help` - This help

*Features:*
• Natural language processing
• Push notifications
• Recurring reminders
• Multi-language support
• Ad-free premium option
"""
        
        # Create help keyboard
        keyboard = [
            [InlineKeyboardButton("📝 Try Quick Reminder", callback_data="quick_reminder")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "new_reminder":
            await self.start_reminder_setup(query)
        elif query.data == "quick_reminder":
            await self.start_quick_reminder(query)
        elif query.data == "list_reminders":
            await self.show_reminders_list(query)
        elif query.data == "delete_reminder":
            await self.show_delete_menu(query)
        elif query.data == "settings":
            await self.show_settings(query)
        elif query.data == "help":
            await self.show_help(query)
        elif query.data == "main_menu":
            await self.show_main_menu(query)
        elif query.data.startswith("delete_"):
            await self.delete_reminder_callback(query)
        elif query.data.startswith("time_"):
            await self.handle_time_selection(query)
        elif query.data == "confirm_reminder":
            await self.confirm_reminder(update, context)
        elif query.data == "cancel_reminder":
            await self.cancel_reminder_setup(query)
    
    async def start_reminder_setup(self, query):
        """Start the reminder setup process - ask for task first"""
        user_id = query.from_user.id
        
        # Show loading animation
        await BotAnimations.loading_animation(self.scheduler.bot, user_id, "Setting up reminder...")
        
        # Check if user has too many reminders
        reminder_count = self.db.get_reminder_count(user_id)
        if reminder_count >= MAX_REMINDERS_PER_USER:
            await query.edit_message_text(
                "❌ You have reached the maximum number of reminders.\n\nPlease delete some reminders before adding new ones.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📋 View My Reminders", callback_data="list_reminders")
                ]])
            )
            return
        
        # Initialize user data
        self.user_data[user_id] = {
            'task': None,
            'time': None,
            'reminder_type': 'one_time'
        }
        
        # Ask for the task first (clean input)
        task_text = BotAnimations.create_clean_task_input_animation()
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_reminder")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            task_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
        # Set conversation state
        self.user_states[user_id] = ENTERING_TASK
    
    async def start_quick_reminder(self, query):
        """Start quick reminder - ask for task first, then time"""
        user_id = query.from_user.id
        
        # Show loading animation
        await BotAnimations.loading_animation(self.scheduler.bot, user_id, "Preparing quick reminder...")
        
        # Initialize user data
        self.user_data[user_id] = {
            'task': None,
            'time': None,
            'reminder_type': 'one_time'
        }
        
        # Ask for task first (clean input)
        task_text = BotAnimations.create_quick_task_input_animation()
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_reminder")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            task_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
        # Set conversation state
        self.user_states[user_id] = ENTERING_TASK
    
    async def handle_time_selection(self, query):
        """Handle time selection from buttons"""
        user_id = query.from_user.id
        time_choice = query.data.split("_")[1]
        
        # Map time choices to actual times
        time_mapping = {
            "5min": "in 5 minutes",
            "15min": "in 15 minutes", 
            "30min": "in 30 minutes",
            "1hour": "in 1 hour",
            "2hours": "in 2 hours",
            "4hours": "in 4 hours",
            "tomorrow": "tomorrow at 9 AM",
            "nextweek": "next Monday at 9 AM",
            "daily": "every day at 9 AM",
            "weekly": "every Monday at 9 AM"
        }
        
        if time_choice in time_mapping:
            time_text = time_mapping[time_choice]
            
            # Process the reminder with the stored task
            if 'task' in self.user_data[user_id]:
                task = self.user_data[user_id]['task']
                await self.process_reminder_with_time_from_callback(query, task, time_text)
            else:
                # Store the time choice and ask for task
                self.user_data[user_id]['time_text'] = time_text
                
                # Ask for the task (clean input)
                task_text = BotAnimations.create_clean_task_input_animation()
                
                keyboard = [
                    [InlineKeyboardButton("❌ Cancel", callback_data="cancel_reminder")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    task_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
                
                # Set conversation state
                self.user_states[user_id] = ENTERING_TASK
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages during conversation"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states:
            # If not in conversation, show main menu
            await self.show_main_menu_from_message(update)
            return
        
        state = self.user_states[user_id]
        
        if state == ENTERING_TASK:
            await self.handle_task_input(update)
        elif state == CHOOSING_TIME:
            await self.handle_time_input(update)
    
    async def handle_task_input(self, update: Update):
        """Handle task input from user"""
        user_id = update.effective_user.id
        task = update.message.text
        
        # Store the task
        self.user_data[user_id]['task'] = task
        
        # Check if we have a pre-selected time
        if 'time_text' in self.user_data[user_id]:
            time_text = self.user_data[user_id]['time_text']
            await self.process_reminder_with_time(update, task, time_text)
        else:
            # Ask for time
            await self.ask_for_time(update)
    
    async def handle_time_input(self, update: Update):
        """Handle time input from user"""
        user_id = update.effective_user.id
        time_text = update.message.text
        
        # Process the reminder with the stored task
        if 'task' in self.user_data[user_id]:
            task = self.user_data[user_id]['task']
            await self.process_reminder_with_time(update, task, time_text)
        else:
            # If no task stored, ask for task first
            await self.start_reminder_setup_from_message(update)
    
    async def start_reminder_setup_from_message(self, update: Update):
        """Start reminder setup from text message"""
        user_id = update.effective_user.id
        
        # Check if user has too many reminders
        reminder_count = self.db.get_reminder_count(user_id)
        if reminder_count >= MAX_REMINDERS_PER_USER:
            await update.message.reply_text(
                "❌ You have reached the maximum number of reminders.\n\nPlease delete some reminders before adding new ones.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📋 View My Reminders", callback_data="list_reminders")
                ]])
            )
            return
        
        # Initialize user data
        self.user_data[user_id] = {
            'task': None,
            'time': None,
            'reminder_type': 'one_time'
        }
        
        # Ask for the task first (clean input)
        task_text = BotAnimations.create_clean_task_input_animation()
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_reminder")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            task_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
        # Set conversation state
        self.user_states[user_id] = ENTERING_TASK
    
    async def ask_for_time(self, update: Update):
        """Ask user to select time after they enter task"""
        # Create time selection keyboard with animation
        time_text = BotAnimations.create_time_selection_animation()
        reply_markup = BotAnimations.create_keyboard_with_animation("time")
        
        await update.message.reply_text(
            time_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def process_reminder_with_time_from_callback(self, query, task: str, time_text: str):
        """Process reminder with given task and time from callback"""
        user_id = query.from_user.id
        
        # Parse the time
        reminder_time, parsed_task, reminder_type, cron_expression = self.time_parser.parse_reminder_text(f"remind me to {task} {time_text}")
        
        if not reminder_time:
            await query.edit_message_text(
                "❌ I couldn't understand the time format. Please try again with a clearer time specification.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Try Again", callback_data="new_reminder")
                ]])
            )
            return
        
        # Store the parsed data
        self.user_data[user_id].update({
            'reminder_time': reminder_time,
            'parsed_task': parsed_task,
            'reminder_type': reminder_type,
            'cron_expression': cron_expression
        })
        
        # Show confirmation
        await self.show_reminder_confirmation_from_callback(query)
    
    async def show_reminder_confirmation_from_callback(self, query):
        """Show reminder confirmation with details from callback"""
        user_id = query.from_user.id
        user_data = self.user_data[user_id]
        
        task = user_data['parsed_task']
        reminder_time = user_data['reminder_time']
        
        time_str = self.time_parser.format_reminder_time(reminder_time)
        
        # Show typing animation
        await BotAnimations.typing_animation(self.scheduler.bot, user_id, 1.0)
        
        # Create confirmation with animation
        confirmation_text = BotAnimations.create_reminder_confirmation_animation(task, time_str)
        reply_markup = BotAnimations.create_keyboard_with_animation("confirm")
        
        await query.edit_message_text(
            confirmation_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def process_reminder_with_time(self, update: Update, task: str, time_text: str):
        """Process reminder with given task and time"""
        user_id = update.effective_user.id
        
        # Parse the time
        reminder_time, parsed_task, reminder_type, cron_expression = self.time_parser.parse_reminder_text(f"remind me to {task} {time_text}")
        
        if not reminder_time:
            await update.message.reply_text(
                "❌ I couldn't understand the time format. Please try again with a clearer time specification.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Try Again", callback_data="new_reminder")
                ]])
            )
            return
        
        # Store the parsed data
        self.user_data[user_id].update({
            'reminder_time': reminder_time,
            'parsed_task': parsed_task,
            'reminder_type': reminder_type,
            'cron_expression': cron_expression
        })
        
        # Show confirmation
        await self.show_reminder_confirmation(update)
    
    async def show_reminder_confirmation(self, update: Update):
        """Show reminder confirmation with details"""
        user_id = update.effective_user.id
        user_data = self.user_data[user_id]
        
        task = user_data['parsed_task']
        reminder_time = user_data['reminder_time']
        reminder_type = user_data['reminder_type']
        
        time_str = self.time_parser.format_reminder_time(reminder_time)
        reminder_type_str = "🔄 Recurring" if reminder_type == 'recurring' else "⏰ One-time"
        
        # Show typing animation
        await BotAnimations.typing_animation(self.scheduler.bot, user_id, 1.0)
        
        # Create confirmation with animation
        confirmation_text = BotAnimations.create_reminder_confirmation_animation(task, time_str)
        reply_markup = BotAnimations.create_keyboard_with_animation("confirm")
        
        await update.message.reply_text(
            confirmation_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def confirm_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm and save the reminder"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if user_id not in self.user_data:
            await query.answer("❌ Session expired. Please start over.")
            return
        
        user_data = self.user_data[user_id]
        
        try:
            # Add reminder to database and scheduler
            reminder_id = await self.scheduler.add_reminder(
                user_id=user_id,
                task=user_data['parsed_task'],
                reminder_time=user_data['reminder_time'],
                reminder_type=user_data['reminder_type'],
                cron_expression=user_data.get('cron_expression')
            )
            
            if reminder_id:
                # Show success animation
                await BotAnimations.loading_animation(self.scheduler.bot, user_id, 2.0)
                success_text = BotAnimations.create_success_animation(
                    user_data['parsed_task'],
                    self.time_parser.format_reminder_time(user_data['reminder_time'])
                )
                
                await query.edit_message_text(
                    success_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Clear user data
                del self.user_data[user_id]
                if user_id in self.user_states:
                    del self.user_states[user_id]
                
                # Show ad after successful reminder creation
                await self._show_ad_after_reminder_creation(user_id)
                
            else:
                await query.edit_message_text(
                    "❌ Failed to create reminder. Please try again.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄 Try Again", callback_data="new_reminder")
                    ]])
                )
                
        except Exception as e:
            print(f"Error confirming reminder: {e}")
            await query.edit_message_text(
                "❌ An error occurred. Please try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Try Again", callback_data="new_reminder")
                ]])
            )
    
    async def _show_ad_after_reminder_creation(self, user_id: int):
        """Show ad after reminder is created"""
        try:
            from ads import AdsManager
            ads_manager = AdsManager()
            
            if ads_manager.should_show_ad(user_id):
                # Add a small delay before showing ad
                await asyncio.sleep(3)
                
                # Get user preferences for language
                user_prefs = self.db.get_user_preferences(user_id)
                language = user_prefs.get('language', 'en')
                
                ad_data = await ads_manager.get_ad(user_id, language)
                if ad_data:
                    # Create inline keyboard buttons
                    buttons = []
                    if ad_data.get("button_name") and ad_data.get("click_url"):
                        buttons.append([InlineKeyboardButton(ad_data["button_name"], url=ad_data["click_url"])])
                    if ad_data.get("button_reward_name") and ad_data.get("reward_url"):
                        buttons.append([InlineKeyboardButton(ad_data["button_reward_name"], url=ad_data["reward_url"])])
                    
                    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
                    
                    # Send ad with image if available, otherwise as text
                    try:
                        if ad_data.get("image_url"):
                            await self.scheduler.bot.send_photo(
                                chat_id=user_id,
                                photo=ad_data["image_url"],
                                caption=ad_data.get("text_html", ""),
                                parse_mode=ParseMode.HTML,
                                reply_markup=reply_markup,
                                protect_content=True
                            )
                        else:
                            await self.scheduler.bot.send_message(
                                chat_id=user_id,
                                text=ad_data.get("text_html", ""),
                                parse_mode=ParseMode.HTML,
                                reply_markup=reply_markup,
                                protect_content=True
                            )
                        print(f"💼 Sent AdsGram ad after reminder creation to user {user_id}")
                    except Exception as send_error:
                        print(f"Error sending ad to user {user_id}: {send_error}")
                        # Try sending without HTML parsing as fallback
                        try:
                            plain_text = ad_data.get("text_html", "").replace("<b>", "").replace("</b>", "").replace("<br>", "\n").replace("<br/>", "\n")
                            await self.scheduler.bot.send_message(
                                chat_id=user_id,
                                text=plain_text,
                                reply_markup=reply_markup,
                                protect_content=True
                            )
                            print(f"💼 Sent plain text ad to user {user_id}")
                        except Exception as fallback_error:
                            print(f"Error sending fallback ad to user {user_id}: {fallback_error}")
                else:
                    print(f"💼 No AdsGram ads available for user {user_id} - skipping ad display")
                    
        except Exception as e:
            print(f"Error showing ad after reminder creation: {e}")
    
    async def cancel_reminder_setup(self, query):
        """Cancel reminder setup"""
        user_id = query.from_user.id
        
        # Clear user data
        if user_id in self.user_data:
            del self.user_data[user_id]
        if user_id in self.user_states:
            del self.user_states[user_id]
        
        await query.edit_message_text(
            "❌ Reminder setup cancelled.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")
            ]])
        )
    
    async def show_reminders_list(self, query):
        """Show list of user's reminders"""
        user_id = query.from_user.id
        reminders = self.db.get_user_reminders(user_id)
        
        if not reminders:
            await query.edit_message_text(
                "📭 You don't have any reminders set.\n\n"
                "Create your first reminder!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📝 Set Reminder", callback_data="new_reminder")
                ]])
            )
            return
        
        reminders_text = "📋 *Your Reminders:*\n\n"
        for i, reminder in enumerate(reminders, 1):
            time_str = self.time_parser.format_reminder_time(reminder['reminder_time'])
            reminder_type = "🔄 Recurring" if reminder['reminder_type'] == 'recurring' else "⏰ One-time"
            reminders_text += f"{i}. **{reminder['task']}**\n"
            reminders_text += f"   📅 {time_str}\n"
            reminders_text += f"   {reminder_type}\n"
            reminders_text += f"   🆔 `{reminder['id']}`\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Delete Reminder", callback_data="delete_reminder")],
            [InlineKeyboardButton("📝 Add New", callback_data="new_reminder")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            reminders_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def show_delete_menu(self, query):
        """Show delete reminder menu"""
        user_id = query.from_user.id
        reminders = self.db.get_user_reminders(user_id)
        
        if not reminders:
            await query.edit_message_text(
                "📭 No reminders to delete.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")
                ]])
            )
            return
        
        # Create delete buttons
        keyboard = []
        for reminder in reminders[:10]:  # Limit to 10 buttons
            time_str = self.time_parser.format_reminder_time(reminder['reminder_time'])
            button_text = f"🗑️ {reminder['task'][:20]}... ({time_str})" if len(reminder['task']) > 20 else f"🗑️ {reminder['task']} ({time_str})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"delete_{reminder['id']}")])
        
        keyboard.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🗑️ *Select a reminder to delete:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def delete_reminder_callback(self, query):
        """Delete reminder from callback"""
        reminder_id = int(query.data.split('_')[1])
        user_id = query.from_user.id
        
        success = self.scheduler.delete_reminder(reminder_id, user_id)
        
        if success:
            await query.edit_message_text(
                "✅ Reminder deleted successfully!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")
                ]])
            )
        else:
            await query.edit_message_text(
                "❌ Failed to delete reminder. Please try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")
                ]])
            )
    
    async def show_settings(self, query):
        """Show settings menu"""
        user_id = query.from_user.id
        user_prefs = self.db.get_user_preferences(user_id)
        
        settings_text = f"""
⚙️ *Settings*

🌐 **Language:** {user_prefs.get('language', 'en').upper()}
⭐ **Premium:** {"Yes" if user_prefs.get('is_premium', False) else "No"}
📊 **Reminders:** {self.db.get_reminder_count(user_id)}/{MAX_REMINDERS_PER_USER}
"""
        
        keyboard = [
            [InlineKeyboardButton("🌐 Change Language", callback_data="change_language")],
            [InlineKeyboardButton("⭐ Upgrade to Premium", callback_data="upgrade_premium")],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def show_help(self, query):
        """Show help menu"""
        help_text = """
🤖 *ReminderBot Help*

*Quick Examples:*
• "Call mom in 2 hours"
• "Buy groceries tomorrow at 3 PM"
• "Submit report on Monday at 9 AM"
• "Drink water every 2 hours"
• "Go for a walk every day at 7 AM"

*Features:*
• Natural language processing
• Push notifications
• Recurring reminders
• Multi-language support
• Ad-free premium option

*Need help?* Contact support!
"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Try Quick Reminder", callback_data="quick_reminder")],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def show_main_menu(self, query):
        """Show main menu"""
        user_id = query.from_user.id
        user_prefs = self.db.get_user_preferences(user_id)
        
        welcome_text = f"""
🎉 *Welcome back!* 🎉

What would you like to do today?
"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Set New Reminder", callback_data="new_reminder")],
            [InlineKeyboardButton("📋 My Reminders", callback_data="list_reminders")],
            [InlineKeyboardButton("🗑️ Delete Reminder", callback_data="delete_reminder")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def show_main_menu_from_message(self, update: Update):
        """Show main menu from text message"""
        user_id = update.effective_user.id
        user_prefs = self.db.get_user_preferences(user_id)
        
        welcome_text = f"""
🎉 *Welcome to ReminderBot!* 🎉

I'm your personal productivity assistant that helps you stay organized with smart reminders.

✨ *What I can do:*
• Set reminders with natural language
• Recurring reminders (daily, weekly, etc.)
• Smart time parsing
• Push notifications
• Multi-language support

🚀 *Let's get started!*
"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Set New Reminder", callback_data="new_reminder")],
            [InlineKeyboardButton("📋 My Reminders", callback_data="list_reminders")],
            [InlineKeyboardButton("🗑️ Delete Reminder", callback_data="delete_reminder")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again later.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
                ]])
            )
    
    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Initialize scheduler with bot instance
        self.scheduler = ReminderScheduler(application.bot)
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("test", self.test_notification_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_chat_members))
        
        # Add handler for first time users
        application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, self.handle_first_time_user))
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        print("🤖 ReminderBot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def setup_bot_info(self, bot):
        """Setup bot description and commands"""
        try:
            # Set bot description
            await bot.set_my_description(
                "🤖 Your Personal Productivity Assistant\n\n"
                "Set reminders with natural language:\n"
                "• 'Remind me to call mom in 2 hours'\n"
                "• 'Remind me every day at 7 AM to exercise'\n"
                "• 'Remind me to buy groceries tomorrow'\n\n"
                "Features:\n"
                "✅ Natural language processing\n"
                "✅ Push notifications\n"
                "✅ Recurring reminders\n"
                "✅ Multi-language support\n"
                "✅ Ad-free premium option\n\n"
                "Click /start to begin!"
            )
            
            # Set bot short description
            await bot.set_my_short_description(
                "🤖 Smart reminder bot with natural language processing and push notifications!"
            )
            
            # Set bot commands
            await bot.set_my_commands([
                ("start", "🚀 Start the bot and see main menu"),
                ("remind", "📝 Quick reminder setup"),
                ("list", "📋 View all your reminders"),
                ("delete", "🗑️ Delete a reminder"),
                ("help", "❓ Get help and examples")
            ])
            
            print("✅ Bot info configured successfully")
            
        except Exception as e:
            print(f"⚠️ Could not set bot info: {e}")
    
    async def send_welcome_message(self, update: Update):
        """Send welcome message when bot is added to chat"""
        try:
            welcome_text = """
🎉 *Welcome to ReminderBot!* 🎉

I'm your personal productivity assistant that helps you stay organized with smart reminders.

✨ *What I can do:*
• Set reminders with natural language
• Recurring reminders (daily, weekly, etc.)
• Smart time parsing
• Push notifications
• Multi-language support

🚀 *Quick Start:*
Send /start to begin setting reminders!

📝 *Examples:*
• "Remind me to call mom in 2 hours"
• "Remind me every day at 7 AM to exercise"
• "Remind me to buy groceries tomorrow"
"""
            
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            print(f"Error sending welcome message: {e}")
    
    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when bot is added to a chat"""
        for new_member in update.message.new_chat_members:
            if new_member.id == context.bot.id:
                await self.send_welcome_message(update)
                break
    
    async def handle_empty_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when user opens chat for first time"""
        try:
            # Check if this is a new user or first time opening chat
            user_id = update.effective_user.id
            
            # Send immediate welcome message
            welcome_text = """
🎉 *Welcome to ReminderBot!* 🎉

I'm your personal productivity assistant that helps you stay organized with smart reminders.

✨ *What I can do:*
• Set reminders with natural language
• Recurring reminders (daily, weekly, etc.)
• Smart time parsing
• Push notifications
• Multi-language support

🚀 *Quick Start:*
Click the START button below to begin!

📝 *Examples:*
• "Remind me to call mom in 2 hours"
• "Remind me every day at 7 AM to exercise"
• "Remind me to buy groceries tomorrow"

Click START to get started! 🚀
"""
            
            await context.bot.send_message(
                chat_id=user_id,
                text=welcome_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            print(f"Error sending empty chat welcome: {e}")
    
    async def handle_first_time_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle first time users"""
        user_id = update.effective_user.id
        
        # Check if this is a command (start, help, etc.)
        if update.message.text.startswith('/'):
            return
        
        # Check if user has any reminders (to determine if first time)
        reminders = self.db.get_user_reminders(user_id)
        is_first_time = len(reminders) == 0
        
        if is_first_time:
            # Send welcome message for first time users
            welcome_text = """
🎉 *Welcome to ReminderBot!* 🎉

I'm your personal productivity assistant that helps you stay organized with smart reminders.

✨ *What I can do:*
• Set reminders with natural language
• Recurring reminders (daily, weekly, etc.)
• Smart time parsing
• Push notifications
• Multi-language support

🚀 *Quick Start:*
Send /start to begin setting reminders!

📝 *Examples:*
• "Remind me to call mom in 2 hours"
• "Remind me every day at 7 AM to exercise"
• "Remind me to buy groceries tomorrow"

Click START to get started! 🚀
"""
            
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # For returning users, show main menu
            await self.show_main_menu_from_message(update) 

if __name__ == "__main__":
    bot = ReminderBot()
    bot.run() 