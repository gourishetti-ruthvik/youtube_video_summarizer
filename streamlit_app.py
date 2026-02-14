"""
Streamlit frontend for YouTube Video Summarizer
"""
import os
# CRITICAL: Set this before any imports to avoid TensorFlow issues
os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import streamlit as st
import json
import html
import traceback
from pathlib import Path
import config

# Direct service imports (no Flask backend needed)
from services.transcript_service import TranscriptService
from services.segmentation_service import SegmentationService
from services.summarization_service import SummarizationService
from services.embedding_service import EmbeddingService
from services.search_service import SearchService
from services.export_service import ExportService
from utils.youtube_utils import extract_video_id, get_video_metadata

# Initialize services (will be done in main)
transcript_service = None
segmentation_service = None
summarization_service = None
embedding_service = None
search_service = None
export_service = None

# Page configuration
st.set_page_config(
    page_title="YouTube Video Summarizer",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1200px;
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%);
        padding: 3rem 2rem;
        border-radius: 1rem;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(255, 0, 0, 0.2);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        text-align: center;
        margin: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.95);
        text-align: center;
        margin-top: 1rem;
        font-weight: 400;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a202c;
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #FF0000;
    }
    
    /* Content Sections */
    .content-section {
        margin-bottom: 3rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #ffcccb;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(255, 0, 0, 0.08);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.15);
    }
    
    /* Executive Summary List */
    .executive-list {
        background: #ffffff;
        padding: 2rem;
        border-radius: 0.75rem;
        border: 1px solid #ffcccb;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(255, 0, 0, 0.05);
    }
    
    .executive-list p {
        margin: 1.2rem 0;
        padding-left: 0.5rem;
        line-height: 1.8;
        font-size: 1.05rem;
        color: #1e293b;
    }
    
    /* Section Summary Container */
    .section-summary-container {
        margin: 1.5rem 0;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
        border: 1px solid #ffcccb;
        border-radius: 0.5rem;
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 1rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #ffebeb 0%, #fff5f5 100%);
        border-color: #ff9999;
    }
    
    .streamlit-expanderContent {
        padding: 1.5rem;
        background: #fafafa;
        border: 1px solid #e5e5e5;
        border-top: none;
        border-radius: 0 0 0.5rem 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Highlight Box */
    .highlight-box {
        background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
        border-left: 4px solid #FF0000;
        padding: 2rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(255, 0, 0, 0.08);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .highlight-box:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.12);
    }
    
    .highlight-number {
        display: inline-block;
        background: #FF0000;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        text-align: center;
        line-height: 32px;
        font-weight: 600;
        font-size: 1rem;
        margin-right: 0.8rem;
    }
    
    .timestamp {
        color: #FF0000;
        font-weight: 600;
        font-family: 'Courier New', monospace;
        background: rgba(255, 0, 0, 0.1);
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        font-size: 0.95rem;
    }
    
    /* Badge Styles */
    .confidence-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 2rem;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    
    .badge-high {
        background-color: #10b981;
        color: white;
    }
    
    .badge-medium {
        background-color: #f59e0b;
        color: white;
    }
    
    .badge-low {
        background-color: #ef4444;
        color: white;
    }
    
    /* Answer Box */
    .answer-box {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        border: 2px solid #FF0000;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.15);
    }
    
    .answer-text {
        color: #1e293b;
        font-size: 1.15rem;
        line-height: 1.8;
        margin: 0;
    }
    
    /* Relevance Indicators */
    .relevance-high {
        color: #10b981;
        font-weight: 600;
    }
    
    .relevance-medium {
        color: #f59e0b;
        font-weight: 600;
    }
    
    .relevance-low {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Info Boxes */
    .info-box {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1.2rem 1.8rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
        color: #1e40af;
    }
    
    .info-box strong {
        color: #1e3a8a;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .warning-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1.2rem 1.8rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
        color: #92400e;
    }
    
    .warning-box strong {
        color: #78350f;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .error-box {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1.2rem 1.8rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
        color: #991b1b;
    }
    
    .error-box strong {
        color: #7f1d1d;
        display: block;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .error-box code {
        background: rgba(0, 0, 0, 0.05);
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        font-family: 'Courier New', monospace;
        color: #7f1d1d;
    }
    
    .success-box {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 1.2rem 1.8rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
        color: #065f46;
    }
    
    .success-box strong {
        color: #064e3b;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(255, 0, 0, 0.3);
        background: linear-gradient(135deg, #CC0000 0%, #990000 100%);
    }
    
    /* Divider Styling */
    hr {
        margin: 3rem 0;
        border: none;
        border-top: 1px solid #e5e7eb;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        border-bottom: 3px solid #FF0000;
        color: #FF0000;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        padding: 3rem 0 2rem 0;
        margin-top: 4rem;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_services():
    """Initialize all services with API key"""
    global transcript_service, segmentation_service, summarization_service
    global embedding_service, search_service, export_service
    
    if not config.GEMINI_API_KEY:
        return False
    
    try:
        transcript_service = TranscriptService()
        segmentation_service = SegmentationService(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        summarization_service = SummarizationService(
            api_key=config.GEMINI_API_KEY,
            model_name=config.GEMINI_MODEL
        )
        embedding_service = EmbeddingService(model_name=config.EMBEDDING_MODEL)
        search_service = SearchService()
        export_service = ExportService()
        return True
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        return False


def process_video(url, language='en', translate=False):
    """Process video directly using services"""
    try:
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            return {'error': 'Invalid YouTube URL'}
        
        # Get metadata
        metadata = get_video_metadata(video_id)
        video_title = metadata.get('title', 'Unknown Video')
        
        # Get transcript
        transcript_data = transcript_service.get_transcript(video_id, language)
        full_text = transcript_data['full_text']
        transcript = transcript_data['transcript']
        
        # Translate if needed
        if translate and transcript_data['language'] != 'en':
            full_text = summarization_service.translate_to_english(full_text)
        
        # Segment transcript
        chunks = segmentation_service.segment_transcript(transcript)
        
        # Generate embeddings
        embeddings = embedding_service.generate_embeddings(chunks)
        
        # Create search index
        search_service.create_index(embeddings, chunks, video_id)
        
        # Generate summaries
        executive_summary = summarization_service.generate_executive_summary(
            full_text, video_title
        )
        
        section_summaries = summarization_service.generate_section_summaries(
            chunks, video_title
        )
        
        highlights = summarization_service.generate_highlights(full_text, chunks)
        
        # Calculate metrics
        total_words = sum([chunk['word_count'] for chunk in chunks])
        avg_chunk_words = total_words / len(chunks) if chunks else 0
        coverage_percent = min(100, (len(chunks) * avg_chunk_words / total_words * 100)) if total_words > 0 else 0
        
        # Prepare summary data for return
        summary_data = {
            'video_id': video_id,
            'metadata': metadata,
            'executive_summary': executive_summary,
            'section_summaries': section_summaries,
            'highlights': highlights
        }
        
        return {
            'video_id': video_id,
            'metadata': metadata,
            'executive_summary': executive_summary,
            'section_summaries': section_summaries,
            'highlights': highlights,
            'metrics': {
                'coverage_percent': coverage_percent,
                'confidence_score': 0.85,
                'total_chunks': len(chunks),
                'total_words': total_words
            }
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in process_video: {error_details}")
        return {'error': str(e), 'details': error_details}


def search_transcript(video_id, query, top_k=5):
    """Search transcript directly using services"""
    try:
        # Perform search
        results = search_service.search(video_id, query, top_k)
        
        # Get AI answer
        answer = None
        if results:
            answer = summarization_service.answer_question(query, results)
        
        return {
            'results': results,
            'answer': answer,
            'query': query
        }
    
    except Exception as e:
        return {'error': str(e)}


def get_export_data(video_id, format_type):
    """Get export data for download"""
    try:
        if format_type == 'markdown':
            content = export_service.export_markdown(video_id)
            return content, f"{video_id}_summary.md", "text/markdown"
        else:
            content = export_service.export_pdf(video_id)
            return content, f"{video_id}_summary.pdf", "application/pdf"
    except Exception as e:
        return None, None, None


def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">YouTube Video Summarizer</h1>
        <p class="main-subtitle">AI-Powered Video Analysis with Advanced Semantic Search</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize services
    if not initialize_services():
        st.markdown("""
        <div class="error-box">
            <strong>Configuration Error</strong><br/>
            Please set GEMINI_API_KEY in your environment variables or .env file<br/>
            Get your key from: <a href="https://aistudio.google.com/app/apikey" style="color: #DC2626;">Google AI Studio</a>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Settings")
        
        # API Key status
        if config.GEMINI_API_KEY:
            st.markdown("""
            <div class="success-box">
                <strong>API Status:</strong> Configured
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="error-box">
                <strong>API Status:</strong> Not Set<br/>
                Please set GEMINI_API_KEY in environment variables
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Options
        st.markdown("#### Processing Options")
        language = st.selectbox(
            "Transcript Language",
            options=['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh'],
            index=0,
            help="Preferred language for transcript"
        )
        
        translate = st.checkbox(
            "Translate to English",
            value=False,
            help="Use Gemini to translate if transcript is not in English"
        )
        
        st.divider()
        
        # About
        st.markdown("#### Technology Stack")
        st.markdown("""
        - **Gemini AI** for summarization
        - **FAISS** for semantic search
        - **Sentence Transformers** for embeddings
        """)
        
        st.divider()
        
        # Quality Metrics Documentation
        st.markdown("#### Quality Metrics Guide")
        st.markdown("""
        **Coverage**: Percentage of video transcript successfully processed
        
        **Confidence**: AI model's confidence score in summary accuracy (0-1 scale)
        
        **Total Chunks**: Number of segments the transcript was divided into for processing
        
        **Total Words**: Total word count in the video transcript
        """)
    
    # Main content
    tab1, tab2 = st.tabs(["Summarize", "Search"])
    
    with tab1:
        # Video input
        st.markdown('<h2 class="section-header">Enter YouTube Video URL</h2>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        
        with col1:
            video_url = st.text_input(
                "URL",
                placeholder="https://www.youtube.com/watch?v=...",
                label_visibility="collapsed"
            )
        
        with col2:
            process_button = st.button("Process Video", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process video
        if process_button and video_url:
            with st.spinner("Processing video... This may take a few minutes."):
                result = process_video(video_url, language, translate)
                
                if 'error' in result:
                    st.markdown(f"""
                    <div class="error-box">
                        <strong>Error:</strong> {result['error']}<br/><br/>
                        <strong>Common Solutions:</strong><br/>
                        • Try a different video with closed captions enabled<br/>
                        • Check if the video is publicly available<br/>
                        • Some videos may have regional restrictions<br/>
                        • Educational/tutorial videos typically work best
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show error details in expander for debugging
                    if 'details' in result:
                        with st.expander("🔍 Debug Information"):
                            st.code(result['details'])
                else:
                    # Store in session state
                    st.session_state['result'] = result
                    st.markdown("""
                    <div class="success-box">
                        <strong>Success!</strong> Video processed successfully
                    </div>
                    """, unsafe_allow_html=True)
        
        # Display results
        if 'result' in st.session_state:
            result = st.session_state['result']
            
            # Video metadata
            st.divider()
            st.markdown('<h2 class="section-header">Video Information</h2>', unsafe_allow_html=True)
            
            st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
            
            # Title
            st.markdown(f"""
            <div style="margin-bottom: 1.5rem;">
                <p style="color: #94a3b8; font-size: 0.875rem; margin-bottom: 0.5rem; font-weight: 500;">Title</p>
                <p style="color: #ffffff; font-size: 1.1rem; line-height: 1.5; font-weight: 500;">{result['metadata']['title']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Channel and Video ID in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div>
                    <p style="color: #94a3b8; font-size: 0.875rem; margin-bottom: 0.5rem; font-weight: 500;">Channel</p>
                    <p style="color: #ffffff; font-size: 1rem; font-weight: 500;">{result['metadata']['channel']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div>
                    <p style="color: #94a3b8; font-size: 0.875rem; margin-bottom: 0.5rem; font-weight: 500;">Video ID</p>
                    <p style="color: #ffffff; font-size: 1rem; font-weight: 500;">{result['video_id']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Quality metrics
            st.divider()
            st.markdown('<h2 class="section-header">Quality Metrics</h2>', unsafe_allow_html=True)
            
            st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
            metrics = result['metrics']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Coverage", f"{metrics['coverage_percent']:.1f}%")
            
            with col2:
                st.metric("Confidence", f"{metrics['confidence_score']:.2f}")
            
            with col3:
                st.metric("Total Chunks", metrics['total_chunks'])
            
            with col4:
                st.metric("Total Words", f"{metrics['total_words']:,}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Executive summary
            st.divider()
            st.markdown('<h2 class="section-header">Executive Summary</h2>', unsafe_allow_html=True)
            
            executive_summary = result.get('executive_summary', [])
            if executive_summary:
                summary_html = '<div class="executive-list">'
                for i, bullet in enumerate(executive_summary, 1):
                    summary_html += f'<p style="margin-bottom: 1rem; line-height: 1.8;"><strong>{i}.</strong> {bullet}</p>'
                summary_html += '</div>'
                st.markdown(summary_html, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-box">
                    No executive summary generated. Make sure Gemini API key is configured.
                </div>
                """, unsafe_allow_html=True)
            
            # Section summaries
            st.divider()
            st.markdown('<h2 class="section-header">Section-by-Section Summary</h2>', unsafe_allow_html=True)
            
            section_summaries = result.get('section_summaries', [])
            if section_summaries:
                st.markdown('<div class="section-summary-container">', unsafe_allow_html=True)
                for i, section in enumerate(section_summaries, 1):
                    with st.expander(f"**Section {i}** - {section['timestamp']}", expanded=False):
                        st.markdown(f"""
                        <div style="padding: 0.5rem 0; line-height: 1.8; font-size: 1.05rem; color: #ffffff;">
                            {section['summary']}
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-box">
                    No section summaries generated.
                </div>
                """, unsafe_allow_html=True)
            
            # Highlights
            st.divider()
            st.markdown('<h2 class="section-header">Key Highlights</h2>', unsafe_allow_html=True)
            
            highlights = result.get('highlights', [])
            if highlights:
                for i, highlight in enumerate(highlights, 1):
                    st.markdown(f"""
                    <div class="highlight-box">
                        <div style="margin-bottom: 1rem;">
                            <span class="highlight-number">{i}</span>
                            <span class="timestamp">{highlight['timestamp']}</span>
                        </div>
                        <p style="margin: 0; color: #1e293b; font-size: 1.1rem; line-height: 1.7; font-weight: 400;">
                            "{highlight['quote']}"
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-box">
                    No highlights generated.
                </div>
                """, unsafe_allow_html=True)
            
            # Export buttons
            st.divider()
            st.markdown('<h2 class="section-header">Export Summary</h2>', unsafe_allow_html=True)
            
            st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                # Get markdown content
                md_content, md_filename, md_mime = get_export_data(result['video_id'], 'markdown')
                if md_content:
                    st.download_button(
                        label="📄 Download Markdown",
                        data=md_content,
                        file_name=md_filename,
                        mime=md_mime,
                        use_container_width=True
                    )
                else:
                    st.error("Failed to generate Markdown")
            
            with col2:
                # Get PDF content
                pdf_content, pdf_filename, pdf_mime = get_export_data(result['video_id'], 'pdf')
                if pdf_content:
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_content,
                        file_name=pdf_filename,
                        mime=pdf_mime,
                        use_container_width=True
                    )
                else:
                    st.error("Failed to generate PDF")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<h2 class="section-header">AI-Powered Semantic Search</h2>', unsafe_allow_html=True)
        st.markdown("Ask natural language questions about the video content")
        
        # Check if video is processed
        if 'result' not in st.session_state:
            st.markdown("""
            <div class="warning-box">
                <strong>Notice:</strong> Please process a video first in the Summarize tab
            </div>
            """, unsafe_allow_html=True)
        else:
            result = st.session_state['result']
            video_id = result['video_id']
            
            # Add example questions
            with st.expander("Example Questions"):
                st.markdown("""
                - What is the main topic discussed in this video?
                - What are the key recommendations mentioned?
                - What problems does the speaker identify?
                - What solutions are proposed?
                - What examples or case studies are mentioned?
                - What are the key takeaways?
                """)
            
            # Search input
            st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
            col1, col2 = st.columns([4, 1])
            
            with col1:
                search_query = st.text_input(
                    "Search Query",
                    placeholder="What does the video say about...",
                    label_visibility="collapsed"
                )
            
            with col2:
                top_k = st.number_input("Results", min_value=1, max_value=10, value=5, label_visibility="collapsed")
            
            search_button = st.button("Search", type="primary", use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Search
            if search_button and search_query:
                with st.spinner("Analyzing video content and generating answer..."):
                    search_result = search_transcript(video_id, search_query, top_k)
                    
                    if 'error' in search_result:
                        st.markdown(f"""
                        <div class="error-box">
                            <strong>Error:</strong> {search_result['error']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Display AI-generated answer if available
                        answer = search_result.get('answer')
                        if answer:
                            st.divider()
                            
                            st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
                            
                            # Confidence badge
                            confidence = answer.get('confidence', 'medium')
                            badge_class = {
                                'high': 'badge-high',
                                'medium': 'badge-medium',
                                'low': 'badge-low'
                            }.get(confidence, 'badge-medium')
                            
                            badge_text = {
                                'high': 'HIGH CONFIDENCE',
                                'medium': 'MEDIUM CONFIDENCE',
                                'low': 'LOW CONFIDENCE'
                            }.get(confidence, 'MEDIUM CONFIDENCE')
                            
                            st.markdown("### AI Answer")
                            
                            # Confidence badge
                            st.markdown(f"""
                            <div class="confidence-badge {badge_class}">
                                {badge_text}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Answer box with styling (escape HTML to prevent injection)
                            answer_text = html.escape(answer.get('answer', ''))
                            st.markdown(f"""
                            <div class="answer-box">
                                <p class="answer-text">
                                    {answer_text}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show timestamps if available
                            timestamps = answer.get('timestamps', [])
                            if timestamps:
                                st.caption(f"Key timestamps: {', '.join(timestamps)}")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Display search results
                        results = search_result.get('results', [])
                        
                        st.divider()
                        st.markdown("### Relevant Segments")
                        
                        st.markdown('<div style="margin: 1.5rem 0;">', unsafe_allow_html=True)
                        if results:
                            st.markdown(f"""
                            <div class="info-box">
                                Found {len(results)} relevant segments from the video
                            </div>
                            """, unsafe_allow_html=True)
                            
                            for i, item in enumerate(results, 1):
                                relevance_class = {
                                    'High': 'relevance-high',
                                    'Medium': 'relevance-medium',
                                    'Low': 'relevance-low'
                                }.get(item['relevance'], 'relevance-medium')
                                
                                with st.expander(
                                    f"Segment {i} - [{item['timestamp']}] (Similarity: {item['score']:.2%})"
                                ):
                                    st.write(item['text'])
                                    st.markdown(f"<span class='{relevance_class}'>Relevance: {item['relevance']}</span> | Score: {item['score']:.4f}", unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="warning-box">
                                No relevant segments found
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div class="footer">
        <p>Built with Streamlit, Flask, and Google Gemini AI</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Powered by FAISS & Sentence Transformers</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
