# MentorEdge Deployment Guide

This guide covers deploying MentorEdge to various cloud platforms.

## 🚀 Quick Deploy Options

### Option 1: Streamlit Cloud (Recommended - FREE)

Streamlit Cloud is the easiest way to deploy Streamlit apps. It's free and takes just minutes.

#### Steps:

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - MentorEdge"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/mentoredge.git
   git push -u origin main
   ```

2. **Sign up for Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"

3. **Deploy the app**
   - Select your repository: `YOUR_USERNAME/mentoredge`
   - Select branch: `main`
   - Main file path: `frontend.py`
   - Click "Deploy!"

4. **Configure environment variables (Optional)**
   - In your app settings, go to "Secrets"
   - Add your Semantic Scholar API key:
     ```
     SEMANTIC_SCHOLAR_API_KEY=your-api-key-here
     ```

5. **Your app is live!**
   - Your app will be available at: `https://YOUR_APP_NAME.streamlit.app`

#### Advantages:
- ✅ Free tier available
- ✅ No credit card required
- ✅ Automatic deployments on git push
- ✅ Built-in CI/CD
- ✅ Easy environment variable management
- ✅ HTTPS by default

---

### Option 2: Render (FREE)

Render offers free hosting for web services.

#### Steps:

1. **Create a Render account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create a new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure the service**
   - **Name**: `mentoredge` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run frontend.py --server.port=$PORT --server.address=0.0.0.0`
   - **Plan**: Free

4. **Add environment variables (Optional)**
   - Go to "Environment" tab
   - Add: `SEMANTIC_SCHOLAR_API_KEY` = `your-api-key`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

#### Advantages:
- ✅ Free tier available
- ✅ Automatic SSL
- ✅ Custom domains
- ⚠️ Free tier spins down after inactivity (wake up takes ~30 seconds)

---

### Option 3: Railway (Easy & Fast)

Railway is great for quick deployments with good performance.

#### Steps:

1. **Sign up for Railway**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Create a new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure deployment**
   - Railway will auto-detect Python
   - Add start command in Railway dashboard:
     ```
     streamlit run frontend.py --server.port=$PORT
     ```

4. **Set environment variables**
   - Go to "Variables" tab
   - Add: `SEMANTIC_SCHOLAR_API_KEY` = `your-api-key`

5. **Deploy**
   - Railway will auto-deploy on push

#### Advantages:
- ✅ $5 free credit monthly
- ✅ Fast deployments
- ✅ Good performance
- ✅ Easy database integration

---

### Option 4: Docker Deployment (Any Platform)

Deploy using Docker for maximum portability.

#### Create Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Deploy to platforms supporting Docker:
- **Fly.io**: `fly launch` (has free tier)
- **DigitalOcean App Platform**: Connect GitHub repo
- **AWS Elastic Beanstalk**: Upload Dockerfile
- **Google Cloud Run**: `gcloud run deploy`
- **Azure Container Instances**: Deploy from Dockerfile

---

### Option 5: Heroku (Legacy - Not Recommended)

Heroku removed free tier, but still works if you have credits.

#### Steps:

1. **Create a `Procfile`**:
   ```
   web: streamlit run frontend.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create `runtime.txt`**:
   ```
   python-3.11.0
   ```

3. **Deploy via Heroku CLI**:
   ```bash
   heroku create mentoredge-app
   heroku config:set SEMANTIC_SCHOLAR_API_KEY=your-key
   git push heroku main
   ```

---

## 🔐 Environment Variables

For all platforms, you can optionally set:

- `SEMANTIC_SCHOLAR_API_KEY`: Your Semantic Scholar API key for higher rate limits

**Note**: The app works without an API key using public rate limits (5 req/sec).

---

## 📋 Pre-Deployment Checklist

- [ ] Code is pushed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] `.gitignore` excludes sensitive files
- [ ] `frontend.py` is the main entry point
- [ ] Environment variables are set (if using API key)
- [ ] Tested locally with `streamlit run frontend.py`

---

## 🐳 Docker Deployment (Advanced)

If you want to use Docker, I've included a Dockerfile below. Save it as `Dockerfile` in the root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

Then deploy to any Docker-compatible platform.

---

## 🌐 Recommended Deployment Platform

**For beginners**: Use **Streamlit Cloud** - it's free, easy, and perfect for Streamlit apps.

**For production**: Use **Railway** or **Render** for better performance and reliability.

---

## 🔧 Troubleshooting

### Issue: App fails to start
- Check that `frontend.py` is in the root directory
- Verify `requirements.txt` includes all dependencies
- Check logs for error messages

### Issue: API rate limits
- Add `SEMANTIC_SCHOLAR_API_KEY` environment variable
- Reduce "Papers per Keyword" in the app settings

### Issue: App times out
- Check if platform has timeout limits (Render free tier: 30s)
- Consider upgrading to paid tier or using Railway/Fly.io

---

## 📝 Notes

- All platforms support environment variables for API keys
- HTTPS is enabled by default on most platforms
- Auto-deployment on git push is standard
- Check platform documentation for specific limits

---

## 🆘 Need Help?

- Streamlit Cloud: [docs.streamlit.io/streamlit-cloud](https://docs.streamlit.io/streamlit-cloud)
- Render: [render.com/docs](https://render.com/docs)
- Railway: [docs.railway.app](https://docs.railway.app)

