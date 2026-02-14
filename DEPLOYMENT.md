# Deployment Guide

## 🔒 Important Security Notice

**Your API key was exposed in the previous commit!** Please follow these steps immediately:

1. **Regenerate your Gemini API Key**:
   - Go to https://aistudio.google.com/app/apikey
   - Delete the old key: `AIzaSyD7AZTsGbYwlmFmRimGpv__ijlYZI8Lx5w`
   - Generate a new API key
   - Update your local `.env` file with the new key

2. **Never commit `.env` file** - It's already in `.gitignore`, keep it that way!

---

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free & Easy)

**Best for**: Quick deployment, no backend management needed

#### Steps:
1. **Prepare Your App**:
   - Ensure all code is pushed to GitHub (✅ Already done!)
   
2. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `gourishetti-ruthvik/youtube_video_summarizer`
   - Main file: `streamlit_app.py`
   - Click "Deploy"

3. **Add Secret Environment Variables**:
   - In Streamlit Cloud dashboard, go to App Settings → Secrets
   - Add your new API key:
   ```toml
   GEMINI_API_KEY = "your_new_api_key_here"
   ```

4. **Note**: For Streamlit Cloud, you need to modify the app to run without Flask backend. See "Streamlit-Only Mode" below.

---

### Option 2: Render.com (Flask + Streamlit)

**Best for**: Full-stack deployment with both backend and frontend

#### Deploy Flask Backend:
1. Go to https://render.com
2. Sign up and connect GitHub
3. Click "New" → "Web Service"
4. Select your repository
5. Configure:
   - **Name**: `youtube-summarizer-api`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Add Environment Variable**: 
     - Key: `GEMINI_API_KEY`
     - Value: `your_new_api_key_here`
6. Click "Create Web Service"

#### Deploy Streamlit Frontend:
1. Create a new Web Service for Streamlit
2. Configure:
   - **Name**: `youtube-summarizer-frontend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Add Environment Variables**:
     - `GEMINI_API_KEY`: your new key
     - `BACKEND_URL`: URL of your Flask backend (from step 1)
3. Update `streamlit_app.py` to use `BACKEND_URL` environment variable

---

### Option 3: Railway.app

**Best for**: Simple deployment with automatic scaling

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in Settings
6. Railway will auto-detect Python and deploy both services

---

### Option 4: Heroku

**Best for**: Traditional PaaS deployment

1. Install Heroku CLI
2. Create `Procfile`:
```
web: python app.py
worker: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```
3. Deploy:
```bash
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_new_api_key_here
git push heroku main
```

---

### Option 5: Docker Deployment

**Best for**: Containerized deployment, maximum control

1. **Create `Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000 8501

CMD ["sh", "-c", "python app.py & streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]
```

2. **Create `docker-compose.yml`**:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
      - "8501:8501"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./data:/app/data
```

3. **Build and Run**:
```bash
docker-compose up --build
```

---

## 🎯 Streamlit-Only Mode (No Flask Backend)

For simpler deployment on Streamlit Cloud, you can merge backend logic into the frontend:

### Modifications Needed:

1. **Update `streamlit_app.py`**:
   - Import services directly instead of making HTTP requests
   - Replace `requests.post()` calls with direct function calls
   - Example:
   ```python
   # Instead of:
   response = requests.post(f"{BACKEND_URL}/process", json=data)
   
   # Use:
   from services.transcript_service import TranscriptService
   from services.summarization_service import SummarizationService
   # ... initialize and use services directly
   ```

2. **Benefits**:
   - Single deployment target
   - No backend server to manage
   - Lower costs
   - Simpler architecture

---

## 📝 Pre-Deployment Checklist

- [ ] Regenerated API key after exposure
- [ ] Updated `.env` with new key (locally only)
- [ ] Verified `.env` is in `.gitignore`
- [ ] All code pushed to GitHub
- [ ] Removed test/debug files
- [ ] Tested application locally
- [ ] Set environment variables in deployment platform
- [ ] Configured proper ports for cloud deployment

---

## 🔧 Production Optimizations

### 1. Add Rate Limiting:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/process', methods=['POST'])
@limiter.limit("10 per hour")
def process_video():
    # ... existing code
```

### 2. Add Caching:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_summary(video_id):
    # Cache video summaries
```

### 3. Add Error Tracking (Sentry):
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### 4. Add Analytics:
- Google Analytics for frontend
- Custom logging for API usage

---

## 🆘 Troubleshooting

### "Module not found" errors:
```bash
pip install -r requirements.txt --upgrade
```

### Port already in use:
```bash
# Change ports in config.py or use environment variables
export FLASK_PORT=5001
export STREAMLIT_PORT=8502
```

### Memory issues on free tier:
- Reduce `CHUNK_SIZE` in config
- Use smaller models
- Implement video duration limits

---

## 📊 Monitoring

After deployment, monitor:
- API usage and rate limits
- Error rates
- Response times
- Memory/CPU usage
- API key usage on Google Cloud Console

---

## 💰 Cost Estimates

| Platform | Cost | Best For |
|----------|------|----------|
| Streamlit Cloud | Free (Public repos) | Simple demos |
| Render.com | $7/month (Starter) | Small projects |
| Railway.app | $5/month usage-based | Moderate traffic |
| Heroku | $7/month (Basic) | Traditional apps |
| AWS/GCP/Azure | Variable (pay-as-go) | Enterprise |

---

## 🔗 Useful Resources

- [Streamlit Deployment Docs](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Render Deployment Guide](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Google Cloud Run](https://cloud.google.com/run/docs)

---

**Ready to deploy? Choose your platform and follow the steps above!**
