# 🚀 Quick Deployment Guide

## Deploy to Streamlit Cloud in 5 Minutes (FREE)

### Step 1: Push to GitHub

If you haven't already:

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "MentorEdge - Academic Paper Recommendation Engine"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/mentoredge.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to**: [share.streamlit.io](https://share.streamlit.io)

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Fill in the details**:
   - **Repository**: Select `YOUR_USERNAME/mentoredge`
   - **Branch**: `main`
   - **Main file path**: `frontend.py`
   - **App URL** (optional): Choose a custom name

5. **Click "Deploy!"**

6. **Wait ~2 minutes** for deployment

### Step 3: Add API Key (Optional)

For better performance:

1. In Streamlit Cloud dashboard, click on your app
2. Go to "Settings" → "Secrets"
3. Add:
   ```
   SEMANTIC_SCHOLAR_API_KEY = "your-api-key-here"
   ```
4. Save and redeploy

### ✅ Done!

Your app is live at: `https://YOUR_APP_NAME.streamlit.app`

---

## Alternative: Deploy to Render (FREE)

1. **Go to**: [render.com](https://render.com)
2. **Sign up** with GitHub
3. **New +** → **Web Service**
4. **Connect** your GitHub repo
5. **Settings**:
   - Name: `mentoredge`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run frontend.py --server.port=$PORT --server.address=0.0.0.0`
6. **Add Environment Variable** (Optional):
   - `SEMANTIC_SCHOLAR_API_KEY` = `your-key`
7. **Create Web Service**

---

## Alternative: Deploy to Railway (FREE $5/month credit)

1. **Go to**: [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select** your repository
5. **Add Variable** (Optional):
   - `SEMANTIC_SCHOLAR_API_KEY` = `your-key`
6. **Railway auto-deploys!**

---

## 🔑 Get Semantic Scholar API Key (Optional)

1. Go to: [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api)
2. Sign up for free API access
3. Copy your API key
4. Add it as an environment variable in your deployment platform

**Note**: The app works without an API key, but you'll have slower rate limits (5 requests/second).

---

## 📋 Files Needed for Deployment

✅ `frontend.py` - Main Streamlit app  
✅ `requirements.txt` - Python dependencies  
✅ `.streamlit/config.toml` - Streamlit configuration  
✅ `.gitignore` - Git ignore file  
✅ `DEPLOYMENT.md` - Full deployment guide  

All files are ready! Just push to GitHub and deploy. 🎉

