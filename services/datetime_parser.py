from datetime import datetime, timedelta
import re

def parse_natural_datetime(command: str):

    command = command.lower()
    now = datetime.now()

    date = None
    time = None

    # ------------------------
    # TIME PARSING
    # ------------------------

    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', command)

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridian = time_match.group(3)

        if meridian == "pm" and hour != 12:
            hour += 12
        if meridian == "am" and hour == 12:
            hour = 0

        time = f"{hour:02d}:{minute:02d}"

    # ------------------------
    # DATE PARSING
    # ------------------------

    if "tomorrow" in command:
        date_obj = now + timedelta(days=1)

    elif "today" in command:
        date_obj = now

    elif "next monday" in command:
        days_ahead = (0 - now.weekday() + 7) % 7
        days_ahead = 7 if days_ahead == 0 else days_ahead
        date_obj = now + timedelta(days=days_ahead)

    elif "in" in command and "hour" in command:
        hours = int(re.search(r'in (\d+) hour', command).group(1))
        future = now + timedelta(hours=hours)
        date_obj = future
        time = future.strftime("%H:%M")

    else:
        date_obj = None

    if date_obj:
        date = date_obj.strftime("%d/%m/%Y")

    return {
        "reminder_date": date or "",
        "reminder_time": time or ""
    }