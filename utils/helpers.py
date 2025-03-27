"""Helper functions for Groot CLI."""

import datetime
from typing import Any, Dict, List, Optional

def format_age(timestamp: datetime.datetime) -> str:
    """Format a timestamp as a human-readable age string."""
    if not timestamp:
        return "Unknown"

    now = datetime.datetime.now(timestamp.tzinfo)
    delta = now - timestamp
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"

def format_resource_name(resource_type: str, name: str) -> str:
    """Format a resource name for display."""
    if not name:
        return f"<{resource_type}-name>"
    return name

def parse_key_value_string(s: str) -> Dict[str, str]:
    """Parse a string of key=value pairs into a dictionary."""
    if not s:
        return {}

    result = {}
    pairs = s.split(',')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            result[key.strip()] = value.strip()

    return result

def format_dict_as_yaml(d: Dict[str, Any], indent: int = 0) -> str:
    """Format a dictionary as YAML-like string."""
    if not d:
        return ""

    result = []
    for key, value in d.items():
        if isinstance(value, dict):
            result.append(f"{' ' * indent}{key}:")
            result.append(format_dict_as_yaml(value, indent + 2))
        elif isinstance(value, list):
            result.append(f"{' ' * indent}{key}:")
            for item in value:
                if isinstance(item, dict):
                    result.append(f"{' ' * (indent + 2)}- {format_dict_as_yaml(item, indent + 4)}")
                else:
                    result.append(f"{' ' * (indent + 2)}- {item}")
        else:
            result.append(f"{' ' * indent}{key}: {value}")

    return "\n".join(result)

def truncate_string(s: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length."""
    if not s:
        return ""

    if len(s) <= max_length:
        return s

    return s[:max_length - 3] + "..."

def parse_duration(duration_str: str) -> Optional[datetime.timedelta]:
    """Parse a duration string (e.g., '1h', '30m', '1d') into a timedelta."""
    if not duration_str:
        return None

    unit = duration_str[-1]
    try:
        value = int(duration_str[:-1])
    except ValueError:
        return None

    if unit == 's':
        return datetime.timedelta(seconds=value)
    elif unit == 'm':
        return datetime.timedelta(minutes=value)
    elif unit == 'h':
        return datetime.timedelta(hours=value)
    elif unit == 'd':
        return datetime.timedelta(days=value)
    else:
        return None