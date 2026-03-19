# 🚀 DEPLOYMENT WITH YOUR SENDGRID API KEY

## Complete Step-by-Step Guide

---

## ✅ WHAT'S BEEN DONE

✅ Backend code updated with SendGrid integration
✅ SendGrid package added to requirements.txt
✅ Changes committed to git
✅ Ready to deploy!

---

## 📋 NEXT 4 STEPS TO LIVE (70 minutes remaining)

### **STEP 1: Deploy Backend to Render (20 min)**

**Go to:** https://render.com

**Steps:**

1. Click: **New Web Service**
2. Connect GitHub (if not already connected)
3. Select: **DataDoctor** repository
4. Configure:

   ```
   Name: datadoctor-backend
   Environment: Python
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && python main.py
   Region: Ohio (closest to you)
   Instance: Free or Starter
   ```

5. **Environment Variables** (CRITICAL):

   ```
   SENDGRID_API_KEY
   Value: [YOUR_SENDGRID_API_KEY_FROM_EARLIER]
   👉 MARK AS SECRET (toggle the lock icon)

   SENDGRID_SENDER_EMAIL
   Value: noreply@datadoctor.app

   ENVIRONMENT
   Value: production
   ```

6. Click: **Create Web Service**

7. **Wait 2-3 minutes** for deployment
   - Watch the logs (should see: "Application startup complete")
8. **Copy your Render URL** (looks like):

   ```
   https://datadoctor-backend.onrender.com
   ```

9. **Test it works:**
   ```
   Visit: https://datadoctor-backend.onrender.com/docs
   Should see: Swagger API documentation ✓
   ```

---

### **STEP 2: Update Frontend URL (5 min)**

Edit: `frontend/src/utils/api.ts`

Find this line:

```typescript
const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  (process.env.NODE_ENV === "production"
    ? "http://localhost:8001" // ← CHANGE THIS
    : "http://localhost:8001");
```

Change to:

```typescript
const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  (process.env.NODE_ENV === "production"
    ? "https://datadoctor-backend.onrender.com" // ← YOUR RENDER URL
    : "http://localhost:8001");
```

Then:

```bash
git add frontend/src/utils/api.ts
git commit -m "Update: Frontend API URL for production"
git push origin main
```

---

### **STEP 3: Deploy Frontend to Vercel (15 min)**

**Go to:** https://vercel.com

**Steps:**

1. Click: **Add New Project**
2. Select: **DataDoctor** repository
3. Configure:

   ```
   Framework: Vite
   Build Command: cd frontend && npm run build
   Output Directory: frontend/dist
   Root Directory: ./
   ```

4. **Environment Variables**:

   ```
   REACT_APP_API_URL
   Value: https://datadoctor-backend.onrender.com

   REACT_APP_ENVIRONMENT
   Value: production
   ```

5. Click: **Deploy**

6. **Wait 1-2 minutes** for deployment

7. **Copy your Vercel URL** (Vercel shows it after deploy):

   ```
   https://your-app-name.vercel.app
   ```

8. **Test it loads:**
   ```
   Visit: https://your-vercel-url.vercel.app
   Should see: Data Doctor landing page ✓
   ```

---

### **STEP 4: Update CORS & Test Everything (10 min)**

**Update Backend CORS** for Vercel URL:

Edit: `backend/main.py`

Find the CORS middleware (around line 20-30):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://datadoctor.vercel.app",  # ← ADD YOUR VERCEL URL HERE
    ],
    ...
)
```

Replace `datadoctor` with your actual Vercel subdomain from Step 3.

Then:

```bash
git add backend/main.py
git commit -m "Update: CORS for production Vercel URL"
git push origin main
# Render auto-redeploys in 2-3 minutes
```

---

## ✅ FINAL VERIFICATION

Once all deployed, test these:

```
1. ✓ Frontend loads: https://your-vercel.vercel.app
2. ✓ Upload test CSV file
3. ✓ Click "Analyze" button
4. ✓ Wait 2-5 minutes for analysis
5. ✓ See analysis results on dashboard
6. ✓ Click "Download PDF Report" → File downloads
7. ✓ Click "Download Cleaned CSV" → File downloads
8. ✓ Enter email & click "Send Email Report"
9. ✓ Check your inbox → Email received!
10. ✓ Open email attachment → PDF opens correctly
11. ✓ All dashboard tabs working
12. ✓ Health radar chart displays
```

If all ✓ → **YOU'RE LIVE!** 🎉

---

## 🔐 IMPORTANT: API KEY SAFETY

**⚠️ DO NOT:**

- ❌ Commit to git
- ❌ Put in `.env` file (unless local only)
- ❌ Share with anyone
- ❌ Post on GitHub

**✓ DO:**

- ✅ Use Render "Secret" environment variable
- ✅ Treat like a password
- ✅ Rotate it monthly (SendGrid dashboard)
- ✅ Delete if accidentally exposed

---

## ⏱️ TIMELINE

| Step       | Action          | Time   | Total  |
| ---------- | --------------- | ------ | ------ |
| 1          | Deploy Render   | 20 min | 20 min |
| 2          | Update frontend | 5 min  | 25 min |
| 3          | Deploy Vercel   | 15 min | 40 min |
| 4          | CORS + Test     | 10 min | 50 min |
| **Buffer** | Troubleshooting | 20 min | 70 min |

**TOTAL: 70 minutes from now!** ⏱️

---

## 🆘 TROUBLESHOOTING

### Email Not Sending?

**Check 1:** API key correct in Render dashboard

```
Render → datadoctor-backend → Environment
Should see: SENDGRID_API_KEY = SG.W1bEwlWt... (masked)
```

**Check 2:** Render logs

```
Render → datadoctor-backend → Logs
Look for: "Email sent successfully" ✓
Or errors: "SendGrid error: ..."
```

**Check 3:** Test API directly

```bash
curl -X POST https://datadoctor-backend.onrender.com/api/email-report \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@gmail.com", "analysis_id": "test123"}'
```

### Frontend Can't Reach Backend?

**Check:** API URL is correct

```typescript
// frontend/src/utils/api.ts should have:
"https://datadoctor-backend.onrender.com";
```

**Check:** CORS is updated

```python
# backend/main.py should have your Vercel URL:
allow_origins=[..., "https://your-vercel.vercel.app"]
```

### Build Fails?

**Render Backend Fails:**

- Check: Python version (3.9+)
- Check: requirements.txt has all packages
- Check: backend/main.py has no syntax errors

**Vercel Frontend Fails:**

- Check: Node version (16+)
- Check: package.json exists
- Check: npm run build works locally

---

## 🎯 YOUR URLS (After Deployment)

```
Frontend: https://your-vercel-url.vercel.app
Backend:  https://datadoctor-backend.onrender.com
API Docs: https://datadoctor-backend.onrender.com/docs
Email:    SendGrid (you have the API key! ✓)
```

---

## 📊 WHAT HAPPENS WHEN YOU DEPLOY

```
1. User visits frontend on Vercel
2. User uploads CSV file
3. Frontend sends to backend on Render
4. Backend analyzes with 45+ checks
5. Backend returns results to frontend
6. User sees dashboard with analysis
7. User clicks "Send Email"
8. Backend calls SendGrid API
9. SendGrid sends email with PDF + CSV
10. Email arrives in user's inbox
✅ Complete workflow!
```

---

## 🚀 YOU'RE READY!

**Start from STEP 1 above and you'll be live in 70 minutes.**

Everything is coded, documented, and ready.

Good luck! Let me know if you hit any issues. 🎉

---

**Summary:**

- ✅ SendGrid integrated in backend
- ✅ API key generated
- ✅ Requirements updated
- ✅ Code committed
- ✅ Ready to deploy

**Next:** Follow STEP 1 (Render deployment) → You'll be live! 🚀
