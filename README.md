# 🎥 YouTube Video Summarizer with Search & Timestamped AI Notes

A complete, production-ready application for extracting YouTube video transcripts, generating AI-powered summaries with Google Gemini, and enabling semantic search through video content using FAISS vector search.

## 🚨 SECURITY NOTICE

**⚠️ API Key Security**: If you cloned this repo before the security fix (commit 36810c7), your API key may have been exposed. Please:

1. **Immediately regenerate your Gemini API key** at https://aistudio.google.com/app/apikey
2. Delete the old exposed key
3. Update your local `.env` file with the new key
4. **NEVER** commit `.env` files or real API keys to GitHub

The `.env.example` file now contains only placeholders. Your actual `.env` file is protected by `.gitignore`.

## ✨ Features

### 🎯 Core Capabilities

- **📝 Transcript Extraction**
  - Primary: `youtube-transcript-api` for fast, reliable extraction
  - Fallback: `yt-dlp` for auto-captions when primary fails
  - Multi-language support with auto-detection
  - Optional translation to English using Gemini

- **🤖 AI Summarization (Gemini)**
  - Executive Summary: 5-10 key bullet points
  - Section-wise summaries with timestamps
  - 10 quotable highlights from the video
  - All summaries reference specific timestamps

- **🔍 Semantic Search**
  - Ask questions about video content
  - FAISS-powered vector search
  - Returns relevant segments with timestamps
  - Confidence scoring for results

- **📥 Export Features**
  - Export summaries as Markdown
  - Export summaries as PDF (professional formatting)
  - Includes video metadata, summaries, highlights

- **📊 Quality Metrics**
  - Coverage percentage
  - Confidence score
  - Chunk statistics
  - Word count analysis

## 🏗 Architecture

### Tech Stack

- **Backend**: Flask (REST API)
- **Frontend**: Streamlit (Interactive UI)
- **LLM**: Google Gemini API
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Search**: FAISS (local)
- **Transcript**: youtube-transcript-api + yt-dlp

### Project Structure

```
youtube_summarizer/
│
├── app.py                          # Flask backend server
├── streamlit_app.py                # Streamlit frontend
├── config.py                       # Configuration & API keys
├── requirements.txt                # Python dependencies
│
├── services/
│   ├── transcript_service.py      # Transcript extraction
│   ├── segmentation_service.py    # Text chunking
│   ├── summarization_service.py   # Gemini AI summaries
│   ├── embedding_service.py       # Generate embeddings
│   ├── search_service.py          # FAISS search
│   └── export_service.py          # Markdown/PDF export
│
├── utils/
│   ├── youtube_utils.py           # YouTube helpers
│   ├── text_utils.py              # Text processing
│   └── timestamp_utils.py         # Timestamp formatting
│
└── data/
    ├── transcripts/               # Saved transcripts
    ├── embeddings/                # Vector embeddings
    └── summaries/                 # Generated summaries
```

## 🚀 Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection for API calls

### 2. Clone/Download Project

```bash
cd "Youtube Video Summarizer"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Gemini API Key

**IMPORTANT**: You need a Gemini API key for summarization features.

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 5. Configure API Key

**Option A: Environment Variable (Recommended)**

Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

Windows (Command Prompt):
```cmd
set GEMINI_API_KEY=your_api_key_here
```

Linux/Mac:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Option B: Create .env file**

Create a file named `.env` in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

Then install python-dotenv (already in requirements.txt) and add to config.py:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 6. Run the Application

**Step 1: Start Flask Backend**

Open a terminal and run:

```bash
python app.py
```

You should see:
```
Starting YouTube Video Summarizer Backend...
Gemini API Key configured: True
Server starting at http://127.0.0.1:5000
```

**Step 2: Start Streamlit Frontend**

Open a **NEW** terminal and run:

```bash
streamlit run streamlit_app.py
```

The browser will automatically open to `http://localhost:8501`

### 7. Using the Application

1. **Enter YouTube URL**: Paste any YouTube video URL
2. **Configure Options**: 
   - Select transcript language
   - Enable translation if needed
3. **Click Process**: Wait for the video to be processed (1-3 minutes)
4. **View Results**:
   - Executive summary
   - Section summaries with timestamps
   - Key highlights
   - Quality metrics
5. **Search**: Switch to Search tab to ask questions
6. **Export**: Download as Markdown or PDF

## 📖 API Documentation

### Flask Endpoints

#### POST `/process_video`

Process a YouTube video.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language": "en",
  "translate": false
}
```

**Response:**
```json
{
  "video_id": "VIDEO_ID",
  "metadata": {
    "title": "Video Title",
    "channel": "Channel Name"
  },
  "executive_summary": ["bullet 1", "bullet 2", ...],
  "section_summaries": [...],
  "highlights": [...],
  "metrics": {...}
}
```

#### POST `/search`

Search video transcript.

**Request:**
```json
{
  "video_id": "VIDEO_ID",
  "query": "What does the video say about...",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Relevant text segment...",
      "timestamp": "01:23",
      "start_time": 83,
      "score": 0.89,
      "relevance": "High"
    }
  ]
}
```

#### GET `/export_markdown/<video_id>`

Download summary as Markdown file.

#### GET `/export_pdf/<video_id>`

Download summary as PDF file.

## 🔧 Configuration

Edit `config.py` to customize:

- `CHUNK_SIZE`: Target words per segment (default: 700)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 100)
- `TOP_K_RESULTS`: Number of search results (default: 5)
- `EMBEDDING_MODEL`: Embedding model to use
- `GEMINI_MODEL`: Gemini model version

## 🐛 Troubleshooting

### Backend Not Starting

**Error**: `GEMINI_API_KEY not set`

**Solution**: Set the environment variable as shown in Setup step 5.

### Transcript Extraction Fails

**Error**: `Unable to fetch transcript`

**Possible causes**:
- Video has no captions/subtitles
- Video is age-restricted or private
- Network connectivity issues

**Solution**: Try a different video with captions enabled.

### Module Not Found Errors

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Ensure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**: Change port in `config.py`:
```python
FLASK_PORT = 5001  # Change to different port
```

## 🎓 How It Works

### 1. Transcript Extraction

```python
# Primary method: youtube-transcript-api
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# Fallback: yt-dlp for auto-captions
# Automatically tries when primary fails
```

### 2. Segmentation

- Splits transcript into ~700-word chunks
- Maintains 100-word overlap for context
- Preserves timestamps for each chunk

### 3. AI Summarization

Gemini prompts are designed to:
- Only use information from transcript
- Reference timestamps in summaries
- Avoid hallucinations
- Generate structured outputs

### 4. Semantic Search

- Converts chunks to embeddings (384-dim vectors)
- Stores in FAISS index for fast similarity search
- Computes cosine similarity for queries
- Returns top-K most relevant segments

## 📊 Example Output

**Executive Summary:**
1. The video discusses best practices for Python development
2. Key topics include virtual environments and dependency management
3. Demonstrates how to structure large Python projects
...

**Section Summary [02:15]:**
"This section covers setting up virtual environments using venv and virtualenv. The speaker recommends using venv for most projects..."

**Highlight [05:43]:**
"Always use virtual environments. This is the number one thing that will save you from dependency hell."

## 🚀 Deployment Options

**Streamlit Cloud** (Easiest):
1. Go to https://share.streamlit.io
2. Connect GitHub repository
3. Deploy with `streamlit_app.py`
4. Add API key in Settings → Secrets

**Other Platforms**: Render.com, Railway.app, Heroku, Docker - all supported!

## �🔒 Privacy & Data

- All processing happens locally (except Gemini API calls)
- No data is stored permanently by default
- Transcripts/embeddings saved in `data/` folder
- Delete `data/` folder contents to clear cache

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

This is a complete, standalone project. Feel free to:
- Fork and modify
- Add new features
- Improve existing functionality
- Share improvements

## 💡 Tips for Best Results

1. **Choose Videos with Good Captions**: Manual captions work better than auto-generated
2. **Longer Videos = Better Summaries**: 10-60 minute videos work best
3. **Structured Content**: Educational/tutorial videos produce better results
4. **Clear Audio**: Better transcripts lead to better summaries
5. **Use Specific Queries**: For search, be specific about what you're looking for

## 🎉 Acknowledgments

- **Google Gemini**: AI summarization
- **Sentence Transformers**: Embedding models
- **FAISS**: Efficient vector search
- **youtube-transcript-api**: Transcript extraction
- **Streamlit**: Beautiful UI framework

---

**Built with ❤️ for the AI & Python community**

For issues or questions, check the Troubleshooting section above.
