# 🚀 ATS Resume Checker - Deployment Guide

## **🎯 Overview**
This guide will help you deploy your ATS Resume Checker to:
- **Backend**: Render (FastAPI)
- **Frontend**: Vercel (Next.js)

## **🔧 Backend Deployment (Render)**

### **Step 1: Create Render Account**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Verify your email

### **Step 2: Deploy Backend**
1. **Click "New +" → "Web Service"**
2. **Connect your GitHub repository**
3. **Configure the service:**
   - **Name**: `ats-checker-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

4. **Click "Create Web Service"**

### **Step 3: Get Your Backend URL**
- Render will give you a URL like: `https://ats-checker-backend.onrender.com`
- **Save this URL** - you'll need it for the frontend

## **🌐 Frontend Deployment (Vercel)**

### **Step 1: Create Vercel Account**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub (recommended)
3. Verify your email

### **Step 2: Deploy Frontend**
1. **Click "New Project"**
2. **Import your GitHub repository**
3. **Configure the project:**
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

4. **Add Environment Variables:**
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-backend-url.onrender.com` (from Step 3)

5. **Click "Deploy"**

## **🔗 Connect Frontend to Backend**

### **Update API Configuration**
In your frontend code, update the API URL:

```typescript
// web/app/page.tsx
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### **Update CORS Settings**
In your backend, update CORS origins:

```python
# api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.vercel.app",
        "http://localhost:3000",  # for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## **✅ Test Your Deployment**

### **Backend Test**
```bash
curl https://your-backend-url.onrender.com/health
```

### **Frontend Test**
1. Open your Vercel URL
2. Upload a test file
3. Check if it connects to the backend

## **🔧 Troubleshooting**

### **Common Issues:**

1. **Backend not starting:**
   - Check Render logs
   - Verify requirements.txt
   - Check startup command

2. **Frontend can't connect to backend:**
   - Verify CORS settings
   - Check environment variables
   - Ensure backend URL is correct

3. **File upload issues:**
   - Check file size limits
   - Verify supported file types
   - Check backend logs

## **📱 Your Live URLs**

After deployment, you'll have:
- **Backend**: `https://ats-checker-backend.onrender.com`
- **Frontend**: `https://ats-checker-frontend.vercel.app`

## **🎉 Success!**

Your ATS Resume Checker is now:
- ✅ **Always available** (24/7)
- ✅ **No local setup needed**
- ✅ **Works from anywhere**
- ✅ **Scalable and reliable**

## **🔄 Updates**

To update your deployed app:
1. **Push changes to GitHub**
2. **Render/Vercel will auto-deploy**
3. **No manual intervention needed**

---

**Need help?** Check the logs in Render/Vercel dashboards!
