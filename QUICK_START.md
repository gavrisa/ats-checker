# 🚀 Quick Start - Deploy in 10 Minutes!

## **⚡ Super Fast Deployment**

### **1. Backend (Render) - 5 minutes**
1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub**
3. **Click "New +" → "Web Service"**
4. **Connect your repo**
5. **Configure:**
   - **Name**: `ats-checker-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
6. **Click "Create Web Service"**
7. **Copy the URL** (e.g., `https://ats-checker-backend.onrender.com`)

### **2. Frontend (Vercel) - 5 minutes**
1. **Go to [vercel.com](https://vercel.com)**
2. **Sign up with GitHub**
3. **Click "New Project"**
4. **Import your repo**
5. **Configure:**
   - **Framework**: `Next.js`
   - **Root Directory**: `web`
   - **Build Command**: `npm run build`
6. **Add Environment Variable:**
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `[Your Render URL from step 1]`
7. **Click "Deploy"**

## **🎯 What You Get**

- ✅ **Backend**: `https://ats-checker-backend.onrender.com`
- ✅ **Frontend**: `https://ats-checker-frontend.vercel.app`
- ✅ **24/7 availability**
- ✅ **No local setup needed**
- ✅ **Works from anywhere**

## **🔧 Test Your Deployment**

```bash
# Test backend
curl https://your-backend-url.onrender.com/health

# Test frontend
# Open your Vercel URL in browser
```

## **🎉 Done!**

Your ATS Resume Checker is now live and will work perfectly with all file types!

---

**Need the full guide?** See `DEPLOYMENT.md`
**Want to run the script?** Run `./deploy.sh`
