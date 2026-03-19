# Email Configuration Fix Guide

## Problem Summary

1. ❌ Emails not being sent
2. ✅ AUTO-FIX: Now downloads full 200-row dataset (was truncated to 100)
3. ✅ BACKEND: Successfully running on port 8000
4. ✅ FRONTEND: Successfully running on port 3003

---

## Email Issue Analysis

### Why Emails Aren't Working

**Root Cause:** Environment variables for email credentials are not set in the Python process.

Environment variables need:

```
SMTP_SERVER = smtp.gmail.com
SENDER_EMAIL = surajars24@gmail.com
SENDER_PASSWORD = [APP-SPECIFIC PASSWORD]
```

### Gmail App Password Requirements

⚠️ **Important:** Gmail has security restrictions:

1. **2-Factor Authentication (2FA) Required**
   - Must be enabled on your Gmail account
   - Go to: https://myaccount.google.com/security

2. **App Passwords Are Time-Sensitive**
   - App passwords don't have expiration dates
   - BUT the password you're using (`zjdhepclgcgleybs`) may not work in all scenarios
   - Gmail might revoke access after security checks

3. **Common Issues:**
   - Using regular password instead of app password ❌
   - 2FA not enabled ❌
   - Password changed on gmail.com (sync issue) ❌
   - Password explicitly revoked in Gmail settings ❌
   - Session tokens cleared ❌

---

## Solution: Set Up Fresh App Password

### Step 1: Generate New App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select: Mail → Other (Windows)
3. Google will generate a 16-character password
4. Copy the full password (including spaces)

### Step 2: Set Environment Variables (Choose One Method)

#### Method A: Permanent (Windows Registry) - RECOMMENDED

```powershell
# Run PowerShell as Administrator
[Environment]::SetEnvironmentVariable("SMTP_SERVER", "smtp.gmail.com", "User")
[Environment]::SetEnvironmentVariable("SENDER_EMAIL", "surajars24@gmail.com", "User")
[Environment]::SetEnvironmentVariable("SENDER_PASSWORD", "[NEW_APP_PASSWORD]", "User")

# Restart terminal/computer for changes to take effect
```

#### Method B: Temporary (Current Session Only)

```powershell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SENDER_EMAIL = "surajars24@gmail.com"
$env:SENDER_PASSWORD = "[NEW_APP_PASSWORD]"

# Then start backend in same terminal:
cd "c:\Users\SURAJ ARS\Documents\innovations\DataDoctor"
python backend/main.py
```

#### Method C: .env File (Best for Development)

Create `.env` file in project root:

```
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=surajars24@gmail.com
SENDER_PASSWORD=[NEW_APP_PASSWORD]
```

Then use python-dotenv to load it in main.py

---

## Testing Email After Setup

1. **Upload a dataset** to the app
2. **Run analysis**
3. **Click "📧 Email Report"**
4. **Enter recipient email** (can be your own)
5. **Wait for response**

### Expected Success Response:

```json
{
  "status": "success",
  "message": "Report sent successfully to user@example.com",
  "timestamp": "2026-03-15T..."
}
```

### Common Error Messages:

**"Email authentication failed"**

- Password incorrect or app password never generated
- Solution: Get new app password from Gmail

**"Email sending failed: SMTPServerDisconnected"**

- Firewall blocking port 587
- Solution: Check firewall/antivirus settings

**"Unexpected error: [SMTP error message]"**

- Something went wrong with email setup
- Solution: Check Gmail Settings > Security > App passwords is not revoked

---

## Verification Steps

```powershell
# 1. Check if variables are set
echo $env:SMTP_SERVER
echo $env:SENDER_EMAIL
echo $env:SENDER_PASSWORD  # Should show masked characters

# 2. Check backend is reading them
$response = Invoke-WebRequest -Uri "http://localhost:8000/mail-config" -UseBasicParsing
$response.Content | ConvertFrom-Json

# 3. Test email endpoint
$body = @{
    recipient_email = "your-email@gmail.com"
    subject = "Test"
    body = "Test email"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/test-email" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -UseBasicParsing
```

---

## Fixed Issues Summary

### ✅ Issue 1: Auto-Fix Downloads Only 100 Rows

**Fixed:** Removed 100-row limit in `/api/download-cleaned/{analysis_id}`

- Now downloads full dataset (200+ rows supported)
- File: `backend/main.py` line 547

### ✅ Issue 2: 404 Errors

**Root Cause:** Backend wasn't running (port 8000 in use)
**Fixed:**

- Killed process using port 8000 (PID 22444)
- Backend now running successfully on port 8000
- Frontend now running successfully on port 3003

### ⚠️ Issue 3: Email Not Working

**Root Cause:** SMTP environment variables not set
**Solution:** Follow the configuration steps above

---

## Quick Start After Email Setup

```powershell
# Windows PowerShell as Administrator:
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SENDER_EMAIL = "surajars24@gmail.com"
$env:SENDER_PASSWORD = "YOUR_NEW_APP_PASSWORD_HERE"

cd "c:\Users\SURAJ ARS\Documents\innovations\DataDoctor"
python backend/main.py

# In another terminal:
cd "c:\Users\SURAJ ARS\Documents\innovations\DataDoctor\frontend"
npm run dev
```

Then open: **http://localhost:3003**

---

## Still Having Issues?

### Check These:

1. ✓ Gmail 2FA is enabled
2. ✓ Fresh app password generated (not old one)
3. ✓ Environment variables set correctly
4. ✓ Backend shows no errors on startup
5. ✓ Port 8000 is listening (netstat -ano | findstr :8000)

### Debug Email Service:

```python
# Run this in Python to test directly
import sys
sys.path.insert(0, 'backend')
from email_service import EmailService

email = EmailService()
result = email.send_report(
    recipient_email="test@gmail.com",
    subject="Test",
    body="Test email"
)
print(result)
```

If it returns `'status': 'error'`, the message will show the specific problem.
