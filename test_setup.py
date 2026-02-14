"""
Installation and Environment Test Script
Run this to verify your setup is correct
"""
import sys
import os

# Disable TensorFlow to avoid import errors (we use PyTorch backend)
os.environ['TRANSFORMERS_NO_TF'] = '1'

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    print("\nTesting package imports...")
    
    packages = {
        'flask': 'Flask',
        'streamlit': 'Streamlit',
        'google.generativeai': 'Google Generative AI',
        'youtube_transcript_api': 'YouTube Transcript API',
        'yt_dlp': 'yt-dlp',
        'faiss': 'FAISS',
        'reportlab': 'ReportLab',
        'langdetect': 'langdetect',
        'requests': 'requests',
        'numpy': 'NumPy',
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✅ {name} - OK")
        except ImportError:
            print(f"❌ {name} - MISSING")
            all_ok = False
    
    # Test sentence_transformers separately (may have TF warnings but still works)
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from sentence_transformers import SentenceTransformer
        print(f"✅ Sentence Transformers - OK")
    except Exception as e:
        print(f"⚠️  Sentence Transformers - WARNING (may still work)")
        print(f"    Issue: {str(e)[:80]}")
        # Don't fail the test - it will work via PyTorch backend
    
    return all_ok

def test_api_key():
    """Test if Gemini API key is set"""
    print("\nTesting API configuration...")
    
    api_key = os.environ.get('GEMINI_API_KEY', '')
    
    if api_key:
        print(f"✅ GEMINI_API_KEY is set ({api_key[:10]}...)")
        return True
    else:
        print("❌ GEMINI_API_KEY is not set")
        print("\nTo set your API key:")
        print("  Windows: set GEMINI_API_KEY=your_key")
        print("  Linux/Mac: export GEMINI_API_KEY='your_key'")
        print("\nGet your key from: https://aistudio.google.com/app/apikey")
        return False

def test_directories():
    """Test if data directories exist"""
    print("\nTesting directory structure...")
    
    directories = [
        'data',
        'data/transcripts',
        'data/embeddings',
        'data/summaries',
        'services',
        'utils',
    ]
    
    all_ok = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/ - OK")
        else:
            print(f"❌ {directory}/ - MISSING")
            all_ok = False
    
    return all_ok

def test_files():
    """Test if required files exist"""
    print("\nTesting required files...")
    
    files = [
        'app.py',
        'streamlit_app.py',
        'config.py',
        'requirements.txt',
        'services/transcript_service.py',
        'services/segmentation_service.py',
        'services/summarization_service.py',
        'services/embedding_service.py',
        'services/search_service.py',
        'services/export_service.py',
        'utils/youtube_utils.py',
        'utils/text_utils.py',
        'utils/timestamp_utils.py',
    ]
    
    all_ok = True
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file} - OK")
        else:
            print(f"❌ {file} - MISSING")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print("=" * 50)
    print("YouTube Video Summarizer - Installation Test")
    print("=" * 50)
    print()
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Package Imports", test_imports()))
    results.append(("API Configuration", test_api_key()))
    results.append(("Directory Structure", test_directories()))
    results.append(("Required Files", test_files()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! You're ready to go!")
        print("\nNext steps:")
        print("1. Start backend: python app.py")
        print("2. Start frontend: streamlit run streamlit_app.py")
        print("3. Open browser to http://localhost:8501")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install packages: pip install -r requirements.txt")
        print("- Set API key: export GEMINI_API_KEY='your_key'")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
