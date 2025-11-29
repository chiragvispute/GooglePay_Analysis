# 🚀 Deploy Google Pay CrewAI Analyzer to Render

## 🛠️ Latest Fixes Applied

### ✅ Build Issues Resolved
- **Fixed**: `lxml` compilation errors on Render (removed dependency)
- **Fixed**: Python 3.13 compatibility issues (using Python 3.11)
- **Fixed**: `python-dotenv` version conflict (CrewAI needs 1.1.1+)
- **Added**: `runtime.txt` specifying Python 3.11.11
- **Updated**: BeautifulSoup to use built-in `html.parser` instead of lxml

## Quick Deployment Steps

### 1. Render Setup
1. **Push to GitHub**: Make sure your code is pushed to GitHub
2. **Create Render Account**: Go to [render.com](https://render.com) and sign up
3. **Connect GitHub**: Link your GitHub account to Render

### 2. Deploy as Web Service
1. Click **"New"** → **"Web Service"**
2. Connect your `GooglePay_Analysis` repository
3. Configure settings:
   - **Name**: `google-pay-analyzer` 
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python crewai_app.py`
   - **Instance Type**: Free tier is fine for testing

### 3. Environment Variables
Add these in Render's Environment tab:
```
GEMINI_API_KEY=AIzaSyDpqMG3eOjEM7OKO4_KTynmfaF-J4YJpLc
```

### 4. Deploy
- Click **"Create Web Service"**
- Wait for build to complete (5-10 minutes)
- Your API will be live at: `https://your-app-name.onrender.com`

## ✅ Compatibility Fixed
- ✅ All dependency conflicts resolved
- ✅ Compatible package versions in requirements.txt
- ✅ Procfile configured for web service
- ✅ Environment variables set up

## API Endpoints
Once deployed, your API will have:
- `POST /analyze` - Full AI analysis of Google Pay HTML
- `POST /upload` - Upload HTML file directly
- `POST /quick-insights` - Custom query analysis
- `GET /health` - Health check

## Example Usage After Deployment
```bash
curl -X GET "https://your-app-name.onrender.com/health"

curl -X POST "https://your-app-name.onrender.com/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "html_content": "<your_google_pay_html>",
    "timeframe": "1month"
  }'
```

## Troubleshooting
- If build fails, check the build logs in Render dashboard
- Free tier sleeps after 15 minutes of inactivity (first request may be slow)
- For production use, consider upgrading to paid tier