"""
Text processing utilities
"""
import re
from typing import List
from langdetect import detect, LangDetectException


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text
    
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()


def count_words(text: str) -> int:
    """
    Count words in text
    
    Args:
        text: Text to count
    
    Returns:
        Word count
    """
    return len(text.split())


def detect_language(text: str) -> str:
    """
    Detect the language of text
    
    Args:
        text: Text to analyze
    
    Returns:
        Language code (e.g., 'en', 'es', 'fr')
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum character length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences
    
    Args:
        text: Text to split
    
    Returns:
        List of sentences
    """
    # Simple sentence splitter
    sentences = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sentences if s.strip()]
