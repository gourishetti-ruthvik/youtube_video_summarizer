"""
Timestamp formatting utilities
"""
from typing import Union


def seconds_to_timestamp(seconds: Union[int, float]) -> str:
    """
    Convert seconds to HH:MM:SS format
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted timestamp string
    """
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def timestamp_to_seconds(timestamp: str) -> int:
    """
    Convert HH:MM:SS or MM:SS timestamp to seconds
    
    Args:
        timestamp: Formatted timestamp
    
    Returns:
        Time in seconds
    """
    parts = timestamp.split(':')
    
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    else:
        return 0


def format_timestamp_range(start: Union[int, float], end: Union[int, float]) -> str:
    """
    Format a time range
    
    Args:
        start: Start time in seconds
        end: End time in seconds
    
    Returns:
        Formatted range (e.g., "01:30 - 02:45")
    """
    return f"{seconds_to_timestamp(start)} - {seconds_to_timestamp(end)}"


def create_youtube_timestamp_link(video_id: str, seconds: Union[int, float]) -> str:
    """
    Create a YouTube link with timestamp
    
    Args:
        video_id: YouTube video ID
        seconds: Time in seconds
    
    Returns:
        YouTube URL with timestamp
    """
    return f"https://www.youtube.com/watch?v={video_id}&t={int(seconds)}s"
