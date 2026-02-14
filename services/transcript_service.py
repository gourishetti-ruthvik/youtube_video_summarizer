"""
Transcript extraction service
"""
import json
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound,
    VideoUnavailable
)
import yt_dlp
from utils.text_utils import clean_text, detect_language
from utils.timestamp_utils import seconds_to_timestamp


class TranscriptService:
    """Service for extracting transcripts from YouTube videos"""
    
    def __init__(self):
        self.ydl_opts = {
            'writeautomaticsub': True,
            'writesubtitles': True,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
    
    def get_transcript(self, video_id: str, language: str = 'en') -> Dict:
        """
        Get transcript for a YouTube video
        
        Args:
            video_id: YouTube video ID
            language: Preferred language code
        
        Returns:
            Dictionary with transcript data and metadata
        """
        # Try primary method: youtube-transcript-api
        transcript_data = self._get_transcript_primary(video_id, language)
        
        if not transcript_data:
            # Fallback: yt-dlp
            transcript_data = self._get_transcript_fallback(video_id, language)
        
        if not transcript_data:
            raise Exception("Unable to fetch transcript from any source")
        
        # Process transcript
        full_text = self._combine_transcript_text(transcript_data['transcript'])
        detected_language = detect_language(full_text[:1000])
        
        return {
            'video_id': video_id,
            'transcript': transcript_data['transcript'],
            'full_text': full_text,
            'language': detected_language,
            'source': transcript_data['source'],
            'duration': transcript_data.get('duration', 0),
        }
    
    def _get_transcript_primary(self, video_id: str, language: str) -> Optional[Dict]:
        """
        Get transcript using youtube-transcript-api
        
        Args:
            video_id: YouTube video ID
            language: Preferred language
        
        Returns:
            Transcript data or None
        """
        try:
            # Try to get transcript directly (works with newer API versions)
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            except Exception:
                # Try English as fallback
                try:
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                except Exception:
                    # Get any available transcript
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Format transcript
            formatted_transcript = []
            for entry in transcript_data:
                formatted_transcript.append({
                    'text': clean_text(entry['text']),
                    'start': entry['start'],
                    'duration': entry['duration'],
                })
            
            duration = max([e['start'] + e['duration'] for e in formatted_transcript]) if formatted_transcript else 0
            
            return {
                'transcript': formatted_transcript,
                'source': 'youtube-transcript-api',
                'duration': duration,
            }
        
        except Exception as e:
            print(f"Primary transcript fetch failed: {e}")
            return None
    
    def _get_transcript_fallback(self, video_id: str, language: str) -> Optional[Dict]:
        """
        Get transcript using yt-dlp (fallback method)
        
        Args:
            video_id: YouTube video ID
            language: Preferred language
        
        Returns:
            Transcript data or None
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Get subtitles
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # Prefer manual subtitles, fall back to auto-generated
                captions = subtitles.get(language, automatic_captions.get(language, []))
                
                if not captions:
                    # Try English as fallback
                    captions = subtitles.get('en', automatic_captions.get('en', []))
                
                if not captions:
                    return None
                
                # Find JSON3 format (best for parsing)
                caption_url = None
                for caption in captions:
                    if caption.get('ext') == 'json3':
                        caption_url = caption.get('url')
                        break
                
                if not caption_url:
                    return None
                
                # Download and parse captions
                import requests
                response = requests.get(caption_url, timeout=10)
                caption_data = response.json()
                
                # Parse JSON3 format
                formatted_transcript = []
                events = caption_data.get('events', [])
                
                for event in events:
                    if 'segs' in event:
                        text = ''.join([seg.get('utf8', '') for seg in event['segs']])
                        if text.strip():
                            formatted_transcript.append({
                                'text': clean_text(text),
                                'start': event.get('tStartMs', 0) / 1000,
                                'duration': event.get('dDurationMs', 0) / 1000,
                            })
                
                duration = info.get('duration', 0)
                
                return {
                    'transcript': formatted_transcript,
                    'source': 'yt-dlp',
                    'duration': duration,
                }
        
        except Exception as e:
            print(f"Fallback transcript fetch failed: {e}")
            return None
    
    def _combine_transcript_text(self, transcript: List[Dict]) -> str:
        """
        Combine transcript entries into full text
        
        Args:
            transcript: List of transcript entries
        
        Returns:
            Combined text
        """
        return ' '.join([entry['text'] for entry in transcript])
    
    def save_transcript(self, video_id: str, transcript_data: Dict, directory: str) -> str:
        """
        Save transcript to file
        
        Args:
            video_id: YouTube video ID
            transcript_data: Transcript data
            directory: Directory to save to
        
        Returns:
            File path
        """
        from pathlib import Path
        
        file_path = Path(directory) / f"{video_id}_transcript.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
