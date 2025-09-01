# ATS Checker Debug Guide

## Issue: "Failed to fetch" Error

The backend API is working correctly (confirmed by our tests), but the frontend is experiencing "Failed to fetch" errors. This guide will help you identify and fix the issue.

## ✅ What We Know Works

1. **Backend API**: The API at `https://ats-checker-cz1i.onrender.com` is working correctly
2. **Health Endpoint**: Returns 200 OK with proper JSON response
3. **Analyze Endpoint**: Accepts file uploads and returns analysis results
4. **CORS**: Backend has CORS properly configured

## 🔍 Debugging Steps

### Step 1: Check Browser Console

1. Open your browser's Developer Tools (F12)
2. Go to the Console tab
3. Refresh the page
4. Look for any error messages, especially:
   - CORS errors
   - Network errors
   - JavaScript errors

### Step 2: Check Network Tab

1. In Developer Tools, go to the Network tab
2. Try to upload a file and analyze
3. Look for failed requests to the API
4. Check the request/response details

### Step 3: Test with the HTML Test File

1. Open `test_api.html` in your browser
2. This will test the API directly from the browser
3. Check if it works in the same browser where the main app fails

### Step 4: Check Environment Variables

The frontend might need environment variables set. Check if you need to create a `.env.local` file in the `web` directory:

```bash
# web/.env.local
NEXT_PUBLIC_API_URL=https://ats-checker-cz1i.onrender.com
```

### Step 5: Common Issues and Solutions

#### Issue 1: CORS Errors
**Symptoms**: Console shows CORS errors
**Solution**: The backend already has CORS configured, but you might need to add specific origins

#### Issue 2: Mixed Content
**Symptoms**: Frontend on HTTPS trying to access HTTP API
**Solution**: Ensure both frontend and backend use HTTPS

#### Issue 3: Network Blocking
**Symptoms**: "Failed to fetch" with no specific error
**Solution**: Check firewall, antivirus, or corporate network settings

#### Issue 4: Browser Security
**Symptoms**: Works in some browsers but not others
**Solution**: Check browser security settings, try incognito mode

## 🛠️ Quick Fixes to Try

### Fix 1: Add Environment Variable
```bash
cd web
echo "NEXT_PUBLIC_API_URL=https://ats-checker-cz1i.onrender.com" > .env.local
npm run dev
```

### Fix 2: Update CORS in Backend
If you have access to the backend, you can make CORS more permissive:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Fix 3: Try Different Browser
Test in different browsers to see if it's browser-specific

### Fix 4: Check Network
- Try on different network (mobile hotspot)
- Disable VPN if using one
- Check corporate firewall settings

## 📊 Debug Information

The updated frontend code now includes:
- Automatic connection testing on page load
- Detailed console logging
- Better error messages
- Timeout handling
- Multiple fetch attempts

## 🎯 Next Steps

1. **Run the frontend**: `cd web && npm run dev`
2. **Open browser console** and check for errors
3. **Try the test HTML file** to isolate the issue
4. **Check network tab** for failed requests
5. **Report specific error messages** you see

## 📞 Getting Help

If you're still having issues, please provide:
1. Browser console error messages
2. Network tab failed request details
3. Browser and version
4. Operating system
5. Whether it works in the test HTML file

The API is definitely working, so the issue is in the frontend environment or browser configuration.
