# Google Pay Smart Analyzer API

🚀 **Deploy-ready API for Google Pay transaction analysis with AI insights**

## 🔧 Quick Setup

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set Gemini API key in .env
echo "GEMINI_API_KEY=your_key_here" > .env

# Run the API
python app.py
```

### Deploy on Render
1. Connect your GitHub repo to Render
2. Set environment variable: `GEMINI_API_KEY=your_key`
3. Deploy as Web Service
4. Use the provided URL

## 🌐 API Endpoints

### 1. Health Check
```bash
GET /health
```

### 2. Quick Insights (No AI needed)
```bash
POST /quick-insights
Content-Type: multipart/form-data
Body: file=your_gpay_file.html
```

### 3. AI Analysis
```bash
POST /analyze
Content-Type: multipart/form-data
Body: 
  file=your_gpay_file.html
  query="Give me my one month report and identify key insights"
  timeframe=one month
```

### 4. Upload & Parse
```bash
POST /upload
Content-Type: multipart/form-data
Body: file=your_gpay_file.html
```

## 🧪 Testing

### Test Locally
```bash
# Start API
python app.py

# Run tests (in another terminal)
python test_api.py
```

### Test with cURL
```bash
# Quick insights
curl -X POST "http://localhost:8000/quick-insights" \
  -F "file=@My Activity.html"

# AI Analysis
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@My Activity.html" \
  -F "query=Give me my spending summary" \
  -F "timeframe=one month"
```

## 📱 Frontend Integration

```javascript
// Upload file and get AI insights
const formData = new FormData();
formData.append('file', htmlFile);
formData.append('query', 'Give me my one month report');
formData.append('timeframe', 'one month');

fetch('/analyze', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('AI Insights:', data.insights);
});
```

## 🚀 Deploy Commands

### For Render.com:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`
- **Environment:** `GEMINI_API_KEY=your_key`

The API automatically detects the PORT from environment variables for deployment platforms.