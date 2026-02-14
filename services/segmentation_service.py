"""
Transcript segmentation service
"""
from typing import List, Dict
from utils.text_utils import count_words, split_into_sentences
from utils.timestamp_utils import seconds_to_timestamp


class SegmentationService:
    """Service for segmenting transcripts into semantic chunks"""
    
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        """
        Initialize segmentation service
        
        Args:
            chunk_size: Target words per chunk
            chunk_overlap: Word overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def segment_transcript(self, transcript: List[Dict]) -> List[Dict]:
        """
        Segment transcript into semantic chunks
        
        Args:
            transcript: List of transcript entries with text, start, duration
        
        Returns:
            List of chunks with metadata
        """
        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_start_time = 0
        chunk_id = 0
        
        for i, entry in enumerate(transcript):
            text = entry['text']
            words = count_words(text)
            
            # Start new chunk if needed
            if not current_chunk:
                chunk_start_time = entry['start']
            
            current_chunk.append(entry)
            current_word_count += words
            
            # Check if we've reached target chunk size
            if current_word_count >= self.chunk_size:
                # Create chunk
                chunk_text = ' '.join([e['text'] for e in current_chunk])
                chunk_end_time = current_chunk[-1]['start'] + current_chunk[-1]['duration']
                
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'start_time': chunk_start_time,
                    'end_time': chunk_end_time,
                    'timestamp': seconds_to_timestamp(chunk_start_time),
                    'word_count': current_word_count,
                    'entries': len(current_chunk),
                })
                
                chunk_id += 1
                
                # Calculate overlap for next chunk
                overlap_entries = self._get_overlap_entries(current_chunk, self.chunk_overlap)
                current_chunk = overlap_entries
                current_word_count = sum([count_words(e['text']) for e in overlap_entries])
                
                if overlap_entries:
                    chunk_start_time = overlap_entries[0]['start']
        
        # Add remaining entries as final chunk
        if current_chunk:
            chunk_text = ' '.join([e['text'] for e in current_chunk])
            chunk_end_time = current_chunk[-1]['start'] + current_chunk[-1]['duration']
            
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'start_time': chunk_start_time,
                'end_time': chunk_end_time,
                'timestamp': seconds_to_timestamp(chunk_start_time),
                'word_count': current_word_count,
                'entries': len(current_chunk),
            })
        
        return chunks
    
    def _get_overlap_entries(self, entries: List[Dict], target_words: int) -> List[Dict]:
        """
        Get entries from end to create overlap
        
        Args:
            entries: List of transcript entries
            target_words: Target word count for overlap
        
        Returns:
            List of entries for overlap
        """
        overlap = []
        word_count = 0
        
        for entry in reversed(entries):
            overlap.insert(0, entry)
            word_count += count_words(entry['text'])
            
            if word_count >= target_words:
                break
        
        return overlap
    
    def get_chunk_by_timestamp(self, chunks: List[Dict], timestamp: float) -> Dict:
        """
        Find chunk containing a specific timestamp
        
        Args:
            chunks: List of chunks
            timestamp: Time in seconds
        
        Returns:
            Matching chunk or None
        """
        for chunk in chunks:
            if chunk['start_time'] <= timestamp <= chunk['end_time']:
                return chunk
        
        return None
    
    def get_segments_summary(self, chunks: List[Dict]) -> Dict:
        """
        Get summary statistics for segments
        
        Args:
            chunks: List of chunks
        
        Returns:
            Summary statistics
        """
        total_words = sum([chunk['word_count'] for chunk in chunks])
        avg_words = total_words / len(chunks) if chunks else 0
        
        return {
            'total_chunks': len(chunks),
            'total_words': total_words,
            'avg_words_per_chunk': round(avg_words, 2),
            'total_duration': chunks[-1]['end_time'] if chunks else 0,
        }
