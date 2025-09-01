# 🚀 Quick Start Guide

## ✅ **Your ATS Checker is Now Running!**

From your terminal output, I can see:
- ✅ **Frontend**: Running on `http://localhost:3000`
- ✅ **Backend**: Should be running on `http://localhost:8000`

## 🌐 **Access Your Application**

**Open your browser and go to:** `http://localhost:3000`

## 🔄 **How to Restart (if needed)**

### **Option 1: Use the Script (Recommended)**
```bash
./start_app.sh
```

### **Option 2: Manual Start**
```bash
# Terminal 1 - Backend
cd api
python3 main.py

# Terminal 2 - Frontend  
cd web
npm run dev
```

## 🎯 **What You'll See**

1. **Upload your resume** (PDF, DOCX, or TXT)
2. **Paste a job description**
3. **Click "Get My Score"**
4. **Get professional analysis** with:
   - ✅ Relevant technical keywords only
   - ✅ Smart matching and missing detection
   - ✅ Professional bullet suggestions for improvement

## 🛠️ **Troubleshooting**

**If frontend won't start:**
- Make sure you're in the `/web` directory: `cd web`
- Run: `npm run dev`

**If backend won't start:**
- Make sure you're in the `/api` directory: `cd api`
- Run: `python3 main.py`

## 💡 **Pro Tip**
Keep the terminal open while using the app. The servers need to stay running!
