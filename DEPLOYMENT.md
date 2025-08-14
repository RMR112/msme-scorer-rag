# 🚀 Railway Deployment Guide

## Overview

This guide explains how to deploy both frontend and backend to Railway as separate services.

## Prerequisites

- Railway account (free tier available)
- GitHub repository with your code
- OpenAI API key

## 🏗️ Deployment Steps

### 1. Prepare Your Repository

Ensure your repository structure is clean:

```
Scorer-MSME-RAG/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── railway.json
│   └── ...
├── frontend/
│   ├── package.json
│   ├── railway.json
│   └── ...
└── README.md
```

### 2. Deploy Backend Service

1. **Go to Railway Dashboard**

   - Visit [railway.app](https://railway.app)
   - Click "New Project"

2. **Connect Repository**

   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Choose the `backend` directory as the source

3. **Configure Environment Variables**

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Deploy**
   - Railway will automatically detect `requirements.txt`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Deploy Frontend Service

1. **Add Another Service**

   - In the same Railway project
   - Click "New Service" → "GitHub Repo"
   - Select the same repository
   - Choose the `frontend` directory as the source

2. **Configure Environment Variables**

   ```
   NEXT_PUBLIC_API_URL=https://your-backend-service-url.railway.app
   ```

3. **Deploy**
   - Railway will automatically detect `package.json`
   - Build command: `npm install && npm run build`
   - Start command: `npm start`

## 🔧 Configuration Files

### Backend (`backend/railway.json`)

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/docs"
  }
}
```

### Frontend (`frontend/railway.json`)

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm start",
    "healthcheckPath": "/"
  }
}
```

## 🌐 Service URLs

After deployment, you'll get:

- **Backend URL**: `https://your-backend-service.railway.app`
- **Frontend URL**: `https://your-frontend-service.railway.app`

## 🔄 Environment Variables

### Backend Service

- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: Automatically set by Railway

### Frontend Service

- `NEXT_PUBLIC_API_URL`: Your backend service URL
- `PORT`: Automatically set by Railway

## 📊 Monitoring

- **Health Checks**: Both services have health check endpoints
- **Logs**: View real-time logs in Railway dashboard
- **Metrics**: Monitor CPU, memory, and network usage

## 🚨 Troubleshooting

### Common Issues:

1. **Build Failures**

   - Check logs for missing dependencies
   - Ensure all files are committed to GitHub

2. **Environment Variables**

   - Verify `OPENAI_API_KEY` is set correctly
   - Check `NEXT_PUBLIC_API_URL` points to backend

3. **Port Issues**

   - Railway automatically sets `$PORT` environment variable
   - Ensure your app uses `$PORT` instead of hardcoded port

4. **CORS Issues**
   - Backend is configured to allow all origins in production
   - Frontend should work without CORS issues

## 💰 Cost Optimization

- **Free Tier**: 500 hours/month per service
- **Scaling**: Automatically scales based on traffic
- **Sleep Mode**: Services sleep after inactivity (free tier)

## 🔒 Security

- Environment variables are encrypted
- HTTPS enabled by default
- No sensitive data in code repository

## 📝 Next Steps

1. Test both services after deployment
2. Update domain names if needed
3. Set up custom domains (optional)
4. Configure monitoring and alerts
