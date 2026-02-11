"""Analytics service - computes usage stats from chat session data."""
import datetime
from collections import defaultdict


def compute_analytics(chat_sessions: dict) -> dict:
    """
    Compute analytics from the user's chat_sessions dict.
    Returns a dict with all computed metrics.
    """
    if not chat_sessions:
        return _empty_analytics()

    now = datetime.datetime.now()
    today = now.date()

    total_chats = len(chat_sessions)
    total_user_msgs = 0
    total_assistant_msgs = 0
    total_user_chars = 0
    total_assistant_chars = 0
    total_user_words = 0
    msgs_per_chat = []
    chats_by_date = defaultdict(int)
    msgs_by_date = defaultdict(int)
    msgs_by_weekday = defaultdict(int)  # 0=Mon, 6=Sun
    msgs_by_hour = defaultdict(int)
    persona_usage = defaultdict(int)
    longest_chat_title = ""
    longest_chat_len = 0

    for session_id, session_data in chat_sessions.items():
        messages = session_data.get("messages", [])
        timestamp = _parse_timestamp(session_data.get("timestamp"))
        persona = session_data.get("persona", "Default")
        persona_usage[persona] += 1

        user_count = 0
        assistant_count = 0

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                user_count += 1
                total_user_chars += len(content)
                total_user_words += len(content.split())
            elif role == "assistant":
                assistant_count += 1
                total_assistant_chars += len(content)

        total_user_msgs += user_count
        total_assistant_msgs += assistant_count
        msgs_per_chat.append(user_count + assistant_count)

        if (user_count + assistant_count) > longest_chat_len:
            longest_chat_len = user_count + assistant_count
            longest_chat_title = session_data.get("title", "Untitled")

        # Group by date
        if timestamp:
            chat_date = timestamp.date()
            chats_by_date[chat_date] += 1
            msgs_by_date[chat_date] += user_count + assistant_count
            msgs_by_weekday[timestamp.weekday()] += user_count + assistant_count
            msgs_by_hour[timestamp.hour] += user_count + assistant_count

    # Build last 7 days activity
    last_7_days = {}
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        last_7_days[d.strftime("%a")] = chats_by_date.get(d, 0)

    # Messages last 7 days
    msgs_last_7 = {}
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        msgs_last_7[d.strftime("%a")] = msgs_by_date.get(d, 0)

    # Most active day of week
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    most_active_day = ""
    if msgs_by_weekday:
        best_day_idx = max(msgs_by_weekday, key=msgs_by_weekday.get)
        most_active_day = weekday_names[best_day_idx]

    # Most active hour
    most_active_hour = ""
    if msgs_by_hour:
        best_hour = max(msgs_by_hour, key=msgs_by_hour.get)
        most_active_hour = f"{best_hour:02d}:00"

    avg_msgs = round(sum(msgs_per_chat) / len(msgs_per_chat), 1) if msgs_per_chat else 0

    # Today's stats
    today_chats = chats_by_date.get(today, 0)
    today_msgs = msgs_by_date.get(today, 0)

    return {
        "total_chats": total_chats,
        "total_user_msgs": total_user_msgs,
        "total_assistant_msgs": total_assistant_msgs,
        "total_messages": total_user_msgs + total_assistant_msgs,
        "total_user_chars": total_user_chars,
        "total_assistant_chars": total_assistant_chars,
        "avg_msgs_per_chat": avg_msgs,
        "longest_chat_title": longest_chat_title,
        "longest_chat_len": longest_chat_len,
        "chats_last_7_days": last_7_days,
        "msgs_last_7_days": msgs_last_7,
        "most_active_day": most_active_day,
        "most_active_hour": most_active_hour,
        "persona_usage": dict(persona_usage),
        "today_chats": today_chats,
        "today_msgs": today_msgs,
        "total_user_words": total_user_words,
    }


def _parse_timestamp(ts):
    """Parse a timestamp from various formats."""
    if ts is None:
        return None
    if isinstance(ts, datetime.datetime):
        return ts
    if isinstance(ts, str):
        try:
            return datetime.datetime.fromisoformat(ts)
        except Exception:
            return None
    if hasattr(ts, 'timestamp'):
        try:
            return datetime.datetime.fromtimestamp(ts.timestamp())
        except Exception:
            return None
    return None


def _empty_analytics():
    """Return empty analytics dict."""
    return {
        "total_chats": 0,
        "total_user_msgs": 0,
        "total_assistant_msgs": 0,
        "total_messages": 0,
        "total_user_chars": 0,
        "total_assistant_chars": 0,
        "avg_msgs_per_chat": 0,
        "longest_chat_title": "",
        "longest_chat_len": 0,
        "chats_last_7_days": {},
        "msgs_last_7_days": {},
        "most_active_day": "-",
        "most_active_hour": "-",
        "persona_usage": {},
        "today_chats": 0,
        "today_msgs": 0,
        "total_user_words": 0,
    }
