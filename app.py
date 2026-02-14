"""
Flask backend for YouTube Video Summarizer
"""
import os
# CRITICAL: Set this before any ML library imports to avoid TensorFlow issues
os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
from pathlib import Path

# Import services
from services.transcript_service import TranscriptService
from services.segmentation_service import SegmentationService
from services.summarization_service import SummarizationService
from services.embedding_service import EmbeddingService
from services.search_service import SearchService
from services.export_service import ExportService

# Import utilities
from utils.youtube_utils import extract_video_id, get_video_metadata
from utils.text_utils import count_words

# Import config
import config

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize services
transcript_service = TranscriptService()
segmentation_service = SegmentationService(
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP
)
embedding_service = EmbeddingService(model_name=config.EMBEDDING_MODEL)
search_service = SearchService()
export_service = ExportService()

# Check API key
if not config.GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not set in environment variables")
    summarization_service = None
else:
    summarization_service = SummarizationService(
        api_key=config.GEMINI_API_KEY,
        model_name=config.GEMINI_MODEL
    )

# Store processed videos in memory (in production, use database)
processed_videos = {}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gemini_configured': bool(config.GEMINI_API_KEY),
    })


@app.route('/process_video', methods=['POST'])
def process_video():
    """
    Process YouTube video: extract transcript, segment, summarize, create embeddings
    
    Request JSON:
    {
        "url": "YouTube URL",
        "language": "en" (optional),
        "translate": false (optional)
    }
    
    Returns:
    {
        "video_id": "...",
        "metadata": {...},
        "executive_summary": [...],
        "section_summaries": [...],
        "highlights": [...],
        "metrics": {...}
    }
    """
    try:
        data = request.json
        url = data.get('url')
        language = data.get('language', 'en')
        translate = data.get('translate', False)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Check if already processed
        if video_id in processed_videos:
            return jsonify(processed_videos[video_id])
        
        # Step 1: Get video metadata
        print(f"Fetching metadata for video {video_id}...")
        metadata = get_video_metadata(video_id)
        
        # Step 2: Extract transcript
        print(f"Extracting transcript...")
        transcript_data = transcript_service.get_transcript(video_id, language)
        
        # Save transcript
        transcript_service.save_transcript(
            video_id,
            transcript_data,
            str(config.TRANSCRIPTS_DIR)
        )
        
        # Step 3: Translation if needed
        full_text = transcript_data['full_text']
        if translate and transcript_data['language'] != 'en':
            if summarization_service:
                print("Translating to English...")
                full_text = summarization_service.translate_to_english(full_text)
        
        # Step 4: Segment transcript
        print("Segmenting transcript...")
        chunks = segmentation_service.segment_transcript(
            transcript_data['transcript']
        )
        
        # Step 5: Generate embeddings
        print("Generating embeddings...")
        embeddings = embedding_service.generate_embeddings(chunks)
        
        # Save embeddings
        embedding_service.save_embeddings(
            embeddings,
            chunks,
            video_id,
            str(config.EMBEDDINGS_DIR)
        )
        
        # Step 6: Create search index
        print("Creating search index...")
        search_service.create_index(embeddings, chunks, video_id)
        search_service.save_index(str(config.EMBEDDINGS_DIR))
        
        # Step 7: Generate summaries
        executive_summary = []
        section_summaries = []
        highlights = []
        
        if summarization_service:
            print("Generating executive summary...")
            executive_summary = summarization_service.generate_executive_summary(
                full_text,
                metadata['title']
            )
            
            print("Generating section summaries...")
            section_summaries = summarization_service.generate_section_summaries(
                chunks,
                metadata['title']
            )
            
            print("Generating highlights...")
            highlights = summarization_service.generate_highlights(full_text, chunks)
        
        # Step 8: Calculate quality metrics
        total_words = sum([chunk['word_count'] for chunk in chunks])
        avg_chunk_words = total_words / len(chunks) if chunks else 0
        
        # Calculate coverage (simplified)
        coverage_percent = min(100, (len(chunks) * avg_chunk_words / total_words * 100)) if total_words > 0 else 0
        
        # Calculate confidence score (based on embedding quality)
        confidence_score = 0.85  # Placeholder - could be calculated from embedding similarities
        
        metrics = {
            'coverage_percent': round(coverage_percent, 2),
            'confidence_score': round(confidence_score, 2),
            'total_chunks': len(chunks),
            'total_words': total_words,
            'avg_words_per_chunk': round(avg_chunk_words, 2),
            'duration': transcript_data.get('duration', 0),
        }
        
        # Step 9: Prepare response
        result = {
            'video_id': video_id,
            'metadata': metadata,
            'executive_summary': executive_summary,
            'section_summaries': section_summaries,
            'highlights': highlights,
            'metrics': metrics,
            'language': transcript_data['language'],
        }
        
        # Cache result
        processed_videos[video_id] = result
        
        # Save summary
        summary_data = {
            'title': metadata['title'],
            'channel': metadata['channel'],
            'video_id': video_id,
            'executive_summary': executive_summary,
            'section_summaries': section_summaries,
            'highlights': highlights,
            'metrics': metrics,
        }
        
        export_service.save_markdown(
            summary_data,
            video_id,
            str(config.SUMMARIES_DIR)
        )
        
        print(f"Video {video_id} processed successfully!")
        return jsonify(result)
    
    except Exception as e:
        print(f"Error processing video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/search', methods=['POST'])
def search():
    """
    Semantic search in video transcript with AI-powered answer
    
    Request JSON:
    {
        "video_id": "...",
        "query": "search query",
        "top_k": 5 (optional)
    }
    
    Returns:
    {
        "answer": {
            "text": "AI generated answer...",
            "confidence": "high/medium/low",
            "timestamps": ["00:10", "01:23"]
        },
        "results": [
            {
                "text": "...",
                "timestamp": "...",
                "score": 0.95,
                "relevance": "High"
            }
        ]
    }
    """
    try:
        data = request.json
        video_id = data.get('video_id')
        query = data.get('query')
        top_k = data.get('top_k', config.TOP_K_RESULTS)
        
        if not video_id or not query:
            return jsonify({'error': 'video_id and query are required'}), 400
        
        print(f"Processing search query: '{query}' for video {video_id}")
        
        # Load search index if not already loaded
        if search_service.video_id != video_id:
            search_service.load_index(video_id, str(config.EMBEDDINGS_DIR))
        
        # Generate query embedding
        query_embedding = embedding_service.generate_query_embedding(query)
        
        # Search for relevant chunks
        results = search_service.search(query_embedding, top_k)
        
        print(f"✓ Found {len(results)} relevant chunks")
        
        # Generate AI-powered answer if summarization service is available
        answer = None
        if summarization_service and results:
            # Get video metadata for context
            video_metadata = processed_videos.get(video_id, {}).get('metadata', {})
            video_title = video_metadata.get('title', 'this video')
            
            print(f"Generating AI answer using top {min(5, len(results))} results...")
            answer = summarization_service.answer_question(
                query,
                results,
                video_title
            )
            print(f"✓ Answer generated (confidence: {answer['confidence']})")
        
        response = {
            'results': results
        }
        
        if answer:
            response['answer'] = answer
        
        return jsonify(response)
    
    except Exception as e:
        print(f"✗ Error searching: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/export_markdown/<video_id>', methods=['GET'])
def export_markdown(video_id):
    """
    Export summary as Markdown file
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Markdown file download
    """
    try:
        markdown_path = config.SUMMARIES_DIR / f"{video_id}_summary.md"
        
        if not markdown_path.exists():
            return jsonify({'error': 'Summary not found'}), 404
        
        return send_file(
            markdown_path,
            as_attachment=True,
            download_name=f"{video_id}_summary.md",
            mimetype='text/markdown'
        )
    
    except Exception as e:
        print(f"Error exporting markdown: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/export_pdf/<video_id>', methods=['GET'])
def export_pdf(video_id):
    """
    Export summary as PDF file
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        PDF file download
    """
    try:
        # Check if we have the summary data
        if video_id not in processed_videos:
            return jsonify({'error': 'Video not processed yet'}), 404
        
        summary_data = processed_videos[video_id]
        
        print(f"Generating PDF for video {video_id}...")
        
        # Prepare data for PDF
        pdf_data = {
            'title': summary_data['metadata']['title'],
            'channel': summary_data['metadata']['channel'],
            'video_id': video_id,
            'executive_summary': summary_data['executive_summary'],
            'section_summaries': summary_data['section_summaries'],
            'highlights': summary_data['highlights'],
            'metrics': summary_data['metrics'],
        }
        
        # Generate PDF
        pdf_path = export_service.save_pdf(
            pdf_data,
            video_id,
            str(config.SUMMARIES_DIR)
        )
        
        print(f"✓ PDF generated successfully: {pdf_path}")
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"{video_id}_summary.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        print(f"✗ Error exporting PDF: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500


@app.route('/list_videos', methods=['GET'])
def list_videos():
    """
    List all processed videos
    
    Returns:
    {
        "videos": [
            {
                "video_id": "...",
                "title": "...",
                "channel": "..."
            }
        ]
    }
    """
    videos = []
    for video_id, data in processed_videos.items():
        videos.append({
            'video_id': video_id,
            'title': data['metadata']['title'],
            'channel': data['metadata']['channel'],
        })
    
    return jsonify({'videos': videos})


if __name__ == '__main__':
    print("Starting YouTube Video Summarizer Backend...")
    print(f"Gemini API Key configured: {bool(config.GEMINI_API_KEY)}")
    print(f"Server starting at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=True
    )
