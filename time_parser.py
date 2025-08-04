import re
import parsedatetime
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
from typing import Tuple, Optional, Dict
import calendar

class TimeParser:
    def __init__(self):
        self.cal = parsedatetime.Calendar()
        
        # Common time patterns
        self.time_patterns = {
            'in_x_minutes': r'in (\d+) minutes?',
            'in_x_hours': r'in (\d+) hours?',
            'in_x_days': r'in (\d+) days?',
            'in_x_weeks': r'in (\d+) weeks?',
            'in_x_months': r'in (\d+) months?',
            'in_x_years': r'in (\d+) years?',
            'at_time': r'at (\d{1,2}):?(\d{2})? ?(am|pm)?',
            'tomorrow_at': r'tomorrow at (\d{1,2}):?(\d{2})? ?(am|pm)?',
            'next_day_at': r'next (\w+) at (\d{1,2}):?(\d{2})? ?(am|pm)?',
            'every_day_at': r'every day at (\d{1,2}):?(\d{2})? ?(am|pm)?',
            'every_weekday_at': r'every (\w+) at (\d{1,2}):?(\d{2})? ?(am|pm)?',
            'every_x_days': r'every (\d+) days? at (\d{1,2}):?(\d{2})? ?(am|pm)?',
            'every_x_hours': r'every (\d+) hours?',
            'every_x_minutes': r'every (\d+) minutes?',
        }
        
        self.days_of_week = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
    
    def parse_reminder_text(self, text: str) -> Tuple[Optional[datetime], str, str, Optional[str]]:
        """
        Parse reminder text and extract time, task, reminder type, and cron expression
        
        Returns:
            Tuple of (reminder_time, task, reminder_type, cron_expression)
        """
        text = text.lower().strip()
        
        # Remove common prefixes
        prefixes = ['remind me to', 'remind me', 'reminder to', 'reminder']
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        
        # Try to parse different time patterns
        reminder_time, reminder_type, cron_expr = self._parse_time_patterns(text)
        
        if reminder_time:
            # Extract task by removing time-related words
            task = self._extract_task(text, reminder_time)
            return reminder_time, task, reminder_type, cron_expr
        
        # Try parsedatetime as fallback
        try:
            parsed_time, _ = self.cal.parseDT(text)
            if parsed_time:
                task = self._extract_task_from_datetime(text, parsed_time)
                return parsed_time, task, 'one_time', None
        except:
            pass
        
        return None, text, 'one_time', None
    
    def _parse_time_patterns(self, text: str) -> Tuple[Optional[datetime], str, Optional[str]]:
        """Parse various time patterns in the text"""
        now = datetime.now()
        
        # Check for "in X minutes/hours/days"
        for pattern_name, pattern in self.time_patterns.items():
            match = re.search(pattern, text)
            if match:
                if pattern_name == 'in_x_minutes':
                    minutes = int(match.group(1))
                    return now + timedelta(minutes=minutes), 'one_time', None
                
                elif pattern_name == 'in_x_hours':
                    hours = int(match.group(1))
                    return now + timedelta(hours=hours), 'one_time', None
                
                elif pattern_name == 'in_x_days':
                    days = int(match.group(1))
                    return now + timedelta(days=days), 'one_time', None
                
                elif pattern_name == 'in_x_weeks':
                    weeks = int(match.group(1))
                    return now + timedelta(weeks=weeks), 'one_time', None
                
                elif pattern_name == 'in_x_months':
                    months = int(match.group(1))
                    return now + relativedelta(months=months), 'one_time', None
                
                elif pattern_name == 'in_x_years':
                    years = int(match.group(1))
                    return now + relativedelta(years=years), 'one_time', None
                
                elif pattern_name == 'at_time':
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                    ampm = match.group(3) if match.group(3) else ''
                    
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    
                    reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if reminder_time <= now:
                        reminder_time += timedelta(days=1)
                    
                    return reminder_time, 'one_time', None
                
                elif pattern_name == 'tomorrow_at':
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                    ampm = match.group(3) if match.group(3) else ''
                    
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    
                    tomorrow = now + timedelta(days=1)
                    reminder_time = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    return reminder_time, 'one_time', None
                
                elif pattern_name == 'next_day_at':
                    day_name = match.group(1).lower()
                    hour = int(match.group(2))
                    minute = int(match.group(3)) if match.group(3) else 0
                    ampm = match.group(4) if match.group(4) else ''
                    
                    if day_name in self.days_of_week:
                        target_day = self.days_of_week[day_name]
                        current_day = now.weekday()
                        days_ahead = target_day - current_day
                        
                        if days_ahead <= 0:
                            days_ahead += 7
                        
                        reminder_time = now + timedelta(days=days_ahead)
                        
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                        
                        reminder_time = reminder_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        return reminder_time, 'one_time', None
                
                elif pattern_name == 'every_day_at':
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                    ampm = match.group(3) if match.group(3) else ''
                    
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    
                    reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if reminder_time <= now:
                        reminder_time += timedelta(days=1)
                    
                    cron_expr = f"{minute} {hour} * * *"
                    return reminder_time, 'recurring', cron_expr
                
                elif pattern_name == 'every_weekday_at':
                    day_name = match.group(1).lower()
                    hour = int(match.group(2))
                    minute = int(match.group(3)) if match.group(3) else 0
                    ampm = match.group(4) if match.group(4) else ''
                    
                    if day_name in self.days_of_week:
                        target_day = self.days_of_week[day_name]
                        
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                        
                        reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        if reminder_time <= now:
                            reminder_time += timedelta(days=1)
                        
                        cron_expr = f"{minute} {hour} * * {target_day}"
                        return reminder_time, 'recurring', cron_expr
                
                elif pattern_name == 'every_x_days':
                    days = int(match.group(1))
                    hour = int(match.group(2))
                    minute = int(match.group(3)) if match.group(3) else 0
                    ampm = match.group(4) if match.group(4) else ''
                    
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    
                    reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if reminder_time <= now:
                        reminder_time += timedelta(days=1)
                    
                    cron_expr = f"{minute} {hour} */{days} * *"
                    return reminder_time, 'recurring', cron_expr
                
                elif pattern_name == 'every_x_hours':
                    hours = int(match.group(1))
                    reminder_time = now + timedelta(hours=hours)
                    cron_expr = f"0 */{hours} * * *"
                    return reminder_time, 'recurring', cron_expr
                
                elif pattern_name == 'every_x_minutes':
                    minutes = int(match.group(1))
                    reminder_time = now + timedelta(minutes=minutes)
                    cron_expr = f"*/{minutes} * * * *"
                    return reminder_time, 'recurring', cron_expr
        
        return None, 'one_time', None
    
    def _extract_task(self, text: str, reminder_time: datetime) -> str:
        """Extract the task description from the text"""
        # Remove time-related patterns from the text
        task = text
        
        # Remove common time patterns
        time_patterns_to_remove = [
            r'in \d+ minutes?',
            r'in \d+ hours?',
            r'in \d+ days?',
            r'in \d+ weeks?',
            r'in \d+ months?',
            r'in \d+ years?',
            r'at \d{1,2}:?\d{0,2} ?(am|pm)?',
            r'tomorrow at \d{1,2}:?\d{0,2} ?(am|pm)?',
            r'next \w+ at \d{1,2}:?\d{0,2} ?(am|pm)?',
            r'every day at \d{1,2}:?\d{0,2} ?(am|pm)?',
            r'every \w+ at \d{1,2}:?\d{0,2} ?(am|pm)?',
            r'every \d+ days? at \d{1,2}:?\d{0,2} ?(am|pm)?',
            r'every \d+ hours?',
            r'every \d+ minutes?',
        ]
        
        for pattern in time_patterns_to_remove:
            task = re.sub(pattern, '', task, flags=re.IGNORECASE)
        
        # Clean up the task
        task = re.sub(r'\s+', ' ', task).strip()
        task = task.strip('.,!?')
        
        return task if task else "Reminder"
    
    def _extract_task_from_datetime(self, text: str, reminder_time: datetime) -> str:
        """Extract task when using parsedatetime fallback"""
        # This is a simplified version - in practice, you might want more sophisticated parsing
        return text.strip() or "Reminder"
    
    def format_reminder_time(self, reminder_time: datetime, language: str = 'en') -> str:
        """Format reminder time for display"""
        if language == 'hi':
            # Hindi formatting
            return reminder_time.strftime("%d/%m/%Y %I:%M %p")
        else:
            # English formatting
            return reminder_time.strftime("%B %d, %Y at %I:%M %p")
    
    def get_next_occurrence(self, cron_expression: str, from_time: datetime = None) -> datetime:
        """Get the next occurrence for a cron expression"""
        if not from_time:
            from_time = datetime.now()
        
        # Simple cron parser for basic expressions
        parts = cron_expression.split()
        if len(parts) != 5:
            return from_time
        
        minute, hour, day, month, weekday = parts
        
        # For now, return a simple calculation
        # In a production system, you'd want a proper cron parser
        return from_time + timedelta(days=1) 