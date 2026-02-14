"""
Configuration file for YouTube Video Summarizer
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# CRITICAL: Set environment variables to avoid TensorFlow/Keras issues
# Must be done before any ML libraries are imported
os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Base directory
BASE_DIR = Path(__file__).parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Data directories
DATA_DIR = BASE_DIR / "data"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
SUMMARIES_DIR = DATA_DIR / "summaries"

# Create directories if they don't exist
for directory in [DATA_DIR, TRANSCRIPTS_DIR, EMBEDDINGS_DIR, SUMMARIES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Model configurations
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-2.5-flash"

# Segmentation settings
CHUNK_SIZE = 700  # Target words per chunk
CHUNK_OVERLAP = 100  # Overlap between chunks to preserve context

# Search settings
TOP_K_RESULTS = 5  # Number of search results to return

# Flask settings
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000

# Streamlit settings
STREAMLIT_PORT = 8501
