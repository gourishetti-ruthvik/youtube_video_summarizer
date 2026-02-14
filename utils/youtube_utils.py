"""
YouTube utility functions
"""
import re
from typing import Optional
import requests


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats
    
    Args:
        url: YouTube URL
    
    Returns:
        video_id or None
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Check if it's already a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    return None


def get_video_metadata(video_id: str) -> dict:
    """
    Fetch video metadata from YouTube
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Dictionary with title, channel, publish_date
    """
    try:
        # Using oembed API (no API key required)
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", "Unknown Title"),
                "channel": data.get("author_name", "Unknown Channel"),
                "thumbnail": data.get("thumbnail_url", ""),
            }
    except Exception as e:
        print(f"Error fetching metadata: {e}")
    
    return {
        "title": "Unknown Title",
        "channel": "Unknown Channel",
        "thumbnail": "",
    }


def format_video_url(video_id: str) -> str:
    """
    Create standard YouTube URL from video ID
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Standard YouTube URL
    """
    return f"https://www.youtube.com/watch?v={video_id}"
