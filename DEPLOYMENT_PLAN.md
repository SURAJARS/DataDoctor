# Data Doctor - Deployment Plan & Strategy

## Render + Vercel Deployment Guide

---

## 📋 PHASE 0: CHECKPOINT & ROLLBACK STRATEGY

### 1.1 Create Git Checkpoint (Current Working State)

**Status:** About to deploy to Render (Backend) and Vercel (Frontend)

**Current Build State:**

- ✅ Backend: Running on port 8001 (FastAPI + Uvicorn)
- ✅ Frontend: Running on port 3000 (React + Vite)
- ✅ 21 Major Features Implemented
- ✅ Email service works on localhost with Gmail app passwords
- ✅ All analysis engines functional
- ✅ PDF report generation working
- ✅ AutoML baseline + model suggestions implemented

**Creating Checkpoint:**

```bash
# Step 1: Create a feature branch for pre-deployment
git checkout -b pre-render-vercel-deployment

# Step 2: Add all changes
git add .

# Step 3: Create detailed checkpoint commit
git commit -m "CHECKPOINT: Pre-Render/Vercel deployment - Full feature set working on localhost

Features at this checkpoint:
- 45+ quality checks implemented
- 12+ analysis engines (Dataset, Scoring, ML Readiness, Bias, Drift, etc.)
- 21 major features including AutoML baseline & model suggestions
- Interactive 8-tab dashboard with 7D health radar chart
- Email delivery with Gmail SMTP (app passwords)
- PDF report generation + cleaned CSV export
- Large dataset support (Dask integration)
- FastAPI backend + React frontend locally working

Backend Stack: FastAPI, Uvicorn, Pandas, Dask, Scikit-learn, LightGBM
Frontend Stack: React 18, TypeScript, Vite, Recharts, Tailwind CSS

Status: Ready for Render (backend) + Vercel (frontend) deployment
Email Auth: Gmail app passwords (localhost working, strategy needed for production)"

# Step 4: Tag this checkpoint
git tag -a "v1.0.0-pre-production" -m "Complete feature set - Pre-Render/Vercel deployment"

# Step 5: Switch to main for deployment
git checkout main
git merge pre-render-vercel-deployment --no-ff -m "Merge: Pre-production checkpoint to main"

# Step 6: Push tags and branches
git push origin main --tags
```

**Rollback Plan (if deployment fails):**

```bash
# Option 1: Rollback to checkpoint tag
git reset --hard v1.0.0-pre-production

# Option 2: Rollback specific commits
git revert <commit-hash>

# Option 3: Reset to specific branch
git reset --hard origin/pre-render-vercel-deployment
```

**Checkpoint Documentation:**

- Save all environment variables
- Document current node/python versions
- Take screenshots of working dashboard
- Keep .env files (not in git for security)

---

## 📧 PHASE 1: EMAIL AUTHENTICATION STRATEGY

### Current Situation:

- ✅ Works on localhost with Gmail app passwords
- ❌ Doesn't work on Render/Vercel (environment variable issues)
- 🚨 Gmail app passwords are less secure for production

### 1.2 Production Email Solutions (Best to Worst)

#### **OPTION 1: SendGrid (⭐ RECOMMENDED for production)**

**Why SendGrid?**

- ✅ Enterprise-grade reliability (99.9% uptime)
- ✅ Dedicated IP option for high volume
- ✅ Full render/Vercel support
- ✅ Better deliverability rates
- ✅ Easy integration with Python
- ✅ Free tier: 100 emails/day

**Setup Steps:**

```python
# backend/email_service.py (Updated for SendGrid)

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, MIMEType, Attachment, FileContent, FileName, Disposition
import base64
import os
from email.mime.base import MIMEBase
from email.encoders import encode_base64
import io

class EmailService:
    def __init__(self):
        # Get from environment variable (set in Render/Vercel dashboard)
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.sender_email = os.getenv("SENDGRID_SENDER_EMAIL", "noreply@datadoctor.app")
        self.from_email = Email(self.sender_email)
        self.sg = sendgrid.SendGridAPIClient(self.sendgrid_api_key)

    def send_analysis_report_email(self, recipient_email: str, analysis_id: str,
                                  pdf_path: str = None, csv_path: str = None):
        """Send analysis report via SendGrid"""
        try:
            # Create email
            to_email = To(recipient_email)
            subject = f"Data Doctor Analysis Report - {analysis_id}"

            html_content = f"""
            <h2>Data Doctor Analysis Report</h2>
            <p>Your dataset analysis for <strong>{analysis_id}</strong> is complete!</p>

            <h3>What's Included:</h3>
            <ul>
                <li>📊 Comprehensive health score and quality assessment</li>
                <li>🤖 ML readiness evaluation</li>
                <li>🔍 Data quality issues and anomalies</li>
                <li>📈 Feature importance ranking</li>
                <li>🧠 Model suggestions and recommendations</li>
                <li>📄 Professional PDF report (attached)</li>
                <li>📥 Cleaned CSV dataset (attached)</li>
            </ul>

            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Review the PDF report for detailed insights</li>
                <li>Check the cleaned CSV for data improvements</li>
                <li>Use recommendations to improve your ML model</li>
            </ol>

            <p>Questions? Visit https://datadoctor.app or reply to this email.</p>
            """

            mail = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )

            # Add PDF attachment if exists
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as attachment:
                    pdf_data = base64.b64encode(attachment.read()).decode()
                    mail.attachment = Attachment(
                        FileContent(pdf_data),
                        FileName(f"report_{analysis_id}.pdf"),
                        MIMEType("application", "pdf"),
                        Disposition("attachment")
                    )

            # Add CSV attachment if exists
            if csv_path and os.path.exists(csv_path):
                with open(csv_path, 'rb') as attachment:
                    csv_data = base64.b64encode(attachment.read()).decode()
                    mail.attachment = Attachment(
                        FileContent(csv_data),
                        FileName(f"cleaned_{analysis_id}.csv"),
                        MIMEType("text", "csv"),
                        Disposition("attachment")
                    )

            # Send via SendGrid
            response = self.sg.send(mail)

            print(f"Email sent successfully: {response.status_code}")
            return {
                'status': 'success',
                'message': f'Report sent to {recipient_email}',
                'delivery_status': response.status_code
            }

        except Exception as e:
            print(f"SendGrid email error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to send email: {str(e)}'
            }
```

**Environment Variables Needed:**

```bash
# .env file (NOT in git)
SENDGRID_API_KEY=sg_live_xxxxxxxxxxxxxxxxxxxx
SENDGRID_SENDER_EMAIL=noreply@yourdomain.com
```

**Install SendGrid:**

```bash
pip install sendgrid
```

**Cost:** Free tier + $0.10 per 1000 emails after free tier

---

#### **OPTION 2: Mailgun (Alternative, also good)**

**Why Mailgun?**

- ✅ Developer-friendly API
- ✅ Good free tier (14 days trial)
- ✅ Routing and tracking features
- ✅ Full render/Vercel support
- ✅ $0.50 per 1000 emails (after free tier)

**Setup:**

```python
# backend/email_service.py (Mailgun version)

import requests
import base64
import os

class EmailService:
    def __init__(self):
        self.mailgun_domain = os.getenv("MAILGUN_DOMAIN")
        self.mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        self.sender_email = os.getenv("MAILGUN_SENDER_EMAIL", f"noreply@{self.mailgun_domain}")

    def send_analysis_report_email(self, recipient_email: str, analysis_id: str,
                                  pdf_path: str = None, csv_path: str = None):
        """Send via Mailgun API"""
        try:
            url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"

            files = []
            if pdf_path and os.path.exists(pdf_path):
                files.append(("attachment", open(pdf_path, 'rb')))
            if csv_path and os.path.exists(csv_path):
                files.append(("attachment", open(csv_path, 'rb')))

            data = {
                "from": self.sender_email,
                "to": [recipient_email],
                "subject": f"Data Doctor Analysis Report - {analysis_id}",
                "html": "<h2>Your Data Doctor analysis is ready!</h2>..."
            }

            response = requests.post(
                url,
                auth=("api", self.mailgun_api_key),
                data=data,
                files=files if files else None
            )

            return {
                'status': 'success' if response.status_code == 200 else 'error',
                'message': response.json().get('message', '')
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}
```

**Environment Variables:**

```bash
MAILGUN_DOMAIN=mg.yourdomain.com
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxx
MAILGUN_SENDER_EMAIL=noreply@yourdomain.com
```

---

#### **OPTION 3: AWS SES (For high volume)**

**Why AWS SES?**

- ✅ Very cheap ($0.10 per 1000 emails)
- ✅ Scalable to millions
- ✅ Good for production at scale
- ⚙️ More complex setup
- ✅ Full Render/Vercel support

**Setup:**

```python
# backend/email_service.py (AWS SES version)

import boto3
import os

class EmailService:
    def __init__(self):
        self.ses_client = boto3.client(
            'ses',
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.sender_email = os.getenv("SES_SENDER_EMAIL")

    def send_analysis_report_email(self, recipient_email: str, analysis_id: str,
                                  pdf_path: str = None, csv_path: str = None):
        """Send via AWS SES"""
        try:
            self.ses_client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [recipient_email]},
                Message={
                    'Subject': {'Data': f'Data Doctor Analysis Report - {analysis_id}'},
                    'Body': {'Html': {'Data': '<h2>Your analysis is ready!</h2>'}}
                }
            )
            return {'status': 'success', 'message': 'Email sent'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
```

---

#### **OPTION 4: Keep Gmail App Passwords (Not Recommended for Production)**

**Issues:**

- Less secure (not proper OAuth2)
- Account lockouts on Render/Vercel
- IP whitelisting complications
- Google rate limiting

**If you must use it:**

```python
# backend/email_service.py (Gmail with proper error handling)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.encoders import encode_base64
import os

class EmailService:
    def __init__(self):
        self.sender_email = os.getenv("GMAIL_SENDER_EMAIL")
        self.app_password = os.getenv("GMAIL_APP_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_analysis_report_email(self, recipient_email: str, analysis_id: str,
                                  pdf_path: str = None, csv_path: str = None):
        """Send via Gmail SMTP with retries"""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = f"Data Doctor Analysis Report - {analysis_id}"

            # Add body
            body = """<h2>Your Data Doctor analysis is complete!</h2>..."""
            message.attach(MIMEText(body, "html"))

            # Add attachments
            if pdf_path and os.path.exists(pdf_path):
                self._add_attachment(message, pdf_path, f"report_{analysis_id}.pdf")
            if csv_path and os.path.exists(csv_path):
                self._add_attachment(message, csv_path, f"cleaned_{analysis_id}.csv")

            # Send with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                        server.starttls()
                        server.login(self.sender_email, self.app_password)
                        server.send_message(message)
                    return {'status': 'success', 'message': f'Email sent to {recipient_email}'}
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    # Retry after exponential backoff
                    import time
                    time.sleep(2 ** attempt)

        except Exception as e:
            return {'status': 'error', 'message': f'Email failed: {str(e)}'}
```

**For Render/Vercel with Gmail:**

- Enable "Less secure app access" (Not recommended!)
- Use app-specific passwords (recommended over full password)
- Set IP whitelist if possible
- Consider Render's SMTP relay as alternative

---

## 🎯 RECOMMENDATION STRATEGY

| Scenario                     | Best Option                       |
| ---------------------------- | --------------------------------- |
| **Startup/MVP**              | SendGrid (free tier, easy setup)  |
| **High volume (>10K/month)** | AWS SES (cheapest at scale)       |
| **European users (GDPR)**    | Mailgun (better compliance)       |
| **Simple setup**             | Mailgun or SendGrid               |
| **Not recommended**          | Gmail app passwords on production |

---

## 🚀 PHASE 2: RENDER DEPLOYMENT (Backend)

### 2.1 Prepare Backend for Render

**Step 1: Update main.py for Render**

```python
# backend/main.py (Update entry point)

if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment (Render sets PORT env var)
    port = int(os.getenv("PORT", 8000))

    # Get host (0.0.0.0 for Render)
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        app,
        host=host,
        port=port,
        # Disable reload in production
        reload=os.getenv("ENVIRONMENT") != "production"
    )
```

**Step 2: Create requirements.txt (Already exists, verify)**

```bash
cat backend/requirements.txt
```

**Step 3: Create Render-specific files**

**backend/render.yaml** (Render deployment config):

```yaml
services:
  - type: web
    name: datadoctor-backend
    runtime: python
    pythonVersion: 3.9
    startCommand: "cd backend && python main.py"
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: PYTHON_VERSION
        value: 3.9
      - key: PORT
        scope: runtime
      # Add other env vars below
      - key: SENDGRID_API_KEY
        scope: secret
      - key: DATABASE_URL
        scope: secret
```

**Step 4: Create .renderignore**

```
# .renderignore
__pycache__/
*.pyc
.git
.gitignore
.env
.venv
node_modules/
.vscode
.idea
*.log
```

**Step 5: Add startup script**

**backend/startup.sh:**

```bash
#!/bin/bash
set -e

echo "Starting Data Doctor Backend on Render..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations (if database exists)
# python manage.py migrate

# Start server
python main.py
```

### 2.2 Deploy to Render

1. **Create Render Account:** https://render.com
2. **Connect GitHub Repository**
3. **Create New Web Service:**
   - Name: `datadoctor-backend`
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && python main.py`
   - Instance Type: Free or Starter ($7/month)

4. **Set Environment Variables in Render Dashboard:**

   ```
   ENVIRONMENT=production
   FRONTEND_URL=https://datadoctor.vercel.app
   SENDGRID_API_KEY=sg_live_xxxxx
   SENDGRID_SENDER_EMAIL=noreply@datadoctor.app
   ```

5. **Deploy!** → Render automatically deploys on git push

**Your backend will be at:** `https://datadoctor-backend.onrender.com`

---

## 🎨 PHASE 3: VERCEL DEPLOYMENT (Frontend)

### 3.1 Prepare Frontend for Vercel

**Step 1: Update API URL for production**

**frontend/src/utils/api.ts** (Update):

```typescript
// frontend/src/utils/api.ts

const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  (process.env.NODE_ENV === "production"
    ? "https://datadoctor-backend.onrender.com" // Update with your Render URL
    : "http://localhost:8001");

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
```

**Step 2: Create vercel.json**

**vercel.json:**

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "devCommand": "cd frontend && npm run dev",
  "env": {
    "REACT_APP_API_URL": "@api_url",
    "REACT_APP_ENVIRONMENT": "production"
  },
  "regions": ["iad1"],
  "functions": {
    "api/**/*.ts": {
      "memory": 1024,
      "maxDuration": 60
    }
  }
}
```

**Step 3: Update frontend/.env.production**

```env
REACT_APP_API_URL=https://datadoctor-backend.onrender.com
REACT_APP_ENVIRONMENT=production
```

### 3.2 Deploy to Vercel

1. **Create Vercel Account:** https://vercel.com
2. **Connect GitHub Repository**
3. **Configure Project:**
   - Framework: Vite
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/dist`
   - Root Directory: `./`

4. **Set Environment Variables:**
   - `REACT_APP_API_URL=https://datadoctor-backend.onrender.com`
   - `REACT_APP_ENVIRONMENT=production`

5. **Deploy!**

**Your frontend will be at:** `https://datadoctor.vercel.app`

---

## 🔐 PHASE 4: CORS & Security Configuration

### 4.1 Update Backend CORS

**backend/main.py** (Update CORS middleware):

```python
from fastapi.middleware.cors import CORSMiddleware

# In main.py app configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://datadoctor.vercel.app",  # Vercel frontend
        "https://www.datadoctor.vercel.app"  # With www
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)
```

### 4.2 Backend Environment Variables (Render)

```
# Production
ENVIRONMENT=production
FRONTEND_URL=https://datadoctor.vercel.app
SENDGRID_API_KEY=sg_live_xxxxx
SENDGRID_SENDER_EMAIL=noreply@datadoctor.app

# Optional Database
DATABASE_URL=postgresql://user:pass@host:5432/datadoctor
REDIS_URL=redis://user:pass@host:6379

# API Keys (if needed for future features)
STRIPE_API_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

---

## 📊 PHASE 5: TESTING & VERIFICATION

### Pre-Deployment Checklist:

```markdown
## Pre-Deployment Checklist

### Backend (Render)

- [ ] Unit tests pass (`pytest backend/`)
- [ ] API endpoints respond correctly
- [ ] Email service working (test mode)
- [ ] Large file uploads work
- [ ] PDF generation works
- [ ] All analysis engines functional
- [ ] Error handling in place
- [ ] Logs properly configured

### Frontend (Vercel)

- [ ] Build succeeds without warnings
- [ ] All API calls point to production backend
- [ ] Dashboard loads correctly
- [ ] Charts render properly
- [ ] File upload form works
- [ ] Email report sending works
- [ ] Mobile responsive
- [ ] Browser console errors resolved

### Integration Tests

- [ ] Upload file → Get analysis → Download PDF
- [ ] Upload file → Email report
- [ ] All tabs load correctly
- [ ] Performance acceptable (< 5 second load)
- [ ] Error messages user-friendly

### Security Tests

- [ ] CORS properly configured
- [ ] No sensitive data in frontend
- [ ] Environment variables not exposed
- [ ] API keys properly secured
- [ ] Input validation working
```

### Testing Commands:

```bash
# Test backend
cd backend
pytest

# Test frontend build
cd ../frontend
npm run build
npm run preview

# Test API connectivity
curl https://datadoctor-backend.onrender.com/docs
```

---

## ⚠️ PHASE 6: TROUBLESHOOTING EMAIL AUTH

### If Email Still Fails on Render/Vercel:

**1. Check Environment Variables**

```bash
# In Render dashboard, verify vars are set
# Should see masked values like: sg_live_***
```

**2. Logs Analysis**

```bash
# Check Render logs
# Look for: "Email sent successfully" or error messages
```

**3. Test Email Endpoint**

```bash
curl -X POST https://datadoctor-backend.onrender.com/api/email-report \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "analysis_id": "test123"}'
```

**4. Common Issues:**

| Error                               | Solution                                   |
| ----------------------------------- | ------------------------------------------ |
| `SENDGRID_API_KEY not found`        | Add to Render env vars as SECRET           |
| `Connection timeout`                | Check SendGrid domain whitelist            |
| `451 Temporary service unavailable` | SendGrid account warming up                |
| `Invalid email address`             | Verify sender email configured in SendGrid |
| `500 Internal Server Error`         | Check backend logs, add try-catch          |

---

## 🔄 PHASE 7: ROLLBACK PROCEDURE

### If Production Deployment Fails:

**Immediate Rollback:**

```bash
# 1. Git rollback to checkpoint
git reset --hard v1.0.0-pre-production

# 2. Push to revert Render
git push origin main --force

# 3. Render auto-redeploys from git

# 4. Frontend already deployed?
# - Go to Vercel dashboard
# - Find last working deployment
# - Click "Promote to Production"
```

**Emergency Disable:**

- Render: Click "Pause" button on web service
- Vercel: Click "Stop deployments"

**Contact Support:**

- Render: Leave message in dashboard
- Vercel: Support chat in dashboard

---

## 📈 PHASE 8: POST-DEPLOYMENT MONITORING

### Monitor Production:

```bash
# Backend (Render)
- Check logs: https://dashboard.render.com
- Monitor CPU/Memory usage
- Track error rates
- Monitor email delivery rate

# Frontend (Vercel)
- Check deployment status: https://vercel.com
- Monitor performance metrics
- Track error reporting
- Check API latency

# Analytics
- Google Analytics setup
- Performance monitoring (Sentry)
- Error tracking (Bugsnag)
```

### Vercel Analytics Setup:

```typescript
// frontend/src/main.tsx
import { inject } from "@vercel/analytics";

inject();
```

### Render Error Logging:

```python
# backend/main.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## 💾 QUICK REFERENCE URLS

After deployment:

| Service                 | URL                                          |
| ----------------------- | -------------------------------------------- |
| **Production Frontend** | https://datadoctor.vercel.app                |
| **Production Backend**  | https://datadoctor-backend.onrender.com      |
| **API Docs**            | https://datadoctor-backend.onrender.com/docs |
| **Render Dashboard**    | https://dashboard.render.com                 |
| **Vercel Dashboard**    | https://vercel.com/dashboard                 |

---

## 🎯 DEPLOYMENT COMMAND SUMMARY

```bash
# 1. Create checkpoint
git checkout -b pre-render-vercel-deployment
git add .
git commit -m "CHECKPOINT: Pre-production state"
git tag v1.0.0-pre-production

# 2. Push to GitHub
git push origin main --tags

# 3. Vercel auto-deploys on push
# 4. Render auto-deploys on push
# 5. Monitor both dashboards

# Rollback if needed
git reset --hard v1.0.0-pre-production
git push origin main --force
```

---

## 📝 NEXT STEPS (In Order)

1. ✅ Create git checkpoint (above)
2. ✅ Choose email service (SendGrid recommended)
3. ✅ Update backend code for SendGrid/chosen service
4. ✅ Create Render account
5. ✅ Deploy backend to Render
6. ✅ Create Vercel account
7. ✅ Deploy frontend to Vercel
8. ✅ Test all features in production
9. ✅ Configure monitoring
10. ✅ Setup email verification
11. ✅ Launch!

---
