# Email Configuration Guide

## Overview

The Data Doctor application can send PDF reports via email. To enable this feature, you need to configure SMTP settings with environment variables or through the application.

## Gmail Configuration (Recommended)

### Step 1: Create a Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click "Security" in the left menu
3. Enable "2-Step Verification" (if not already enabled)
4. Scroll down and click "App passwords"
5. Select "Mail" and "Windows Computer" (or your device)
6. Google will generate a 16-character password - save this!

### Step 2: Set Environment Variables

#### On Windows (PowerShell):

```powershell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SENDER_EMAIL = "your-email@gmail.com"
$env:SENDER_PASSWORD = "your-16-char-app-password"
```

#### On Windows (Command Prompt):

```cmd
set SMTP_SERVER=smtp.gmail.com
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=your-16-char-app-password
```

#### On macOS/Linux:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-16-char-app-password"
```

### Step 3: Restart the Backend Server

After setting the environment variables, restart the backend:

```bash
python backend/main.py
```

## Other SMTP Providers

### Office 365 / Outlook

```
SMTP_SERVER: smtp.office365.com
Port: 587
```

### SendGrid

```
SMTP_SERVER: smtp.sendgrid.net
Port: 587
SENDER_EMAIL: apikey
SENDER_PASSWORD: SG.your-sendgrid-api-key
```

### AWS SES

```
SMTP_SERVER: email-smtp.[region].amazonaws.com
Port: 587
SENDER_EMAIL: your-verified-address@example.com
SENDER_PASSWORD: your-generated-smtp-password
```

## Testing Email Configuration

1. Upload a dataset in the Data Doctor application
2. Click the "📧 Email Report" button
3. Enter a test email address
4. Check your inbox for the report (may take a few minutes)

## Troubleshooting

### "Could not connect to backend"

- Ensure backend is running: `python backend/main.py`
- Check that port 8000 is not in use

### "SMTP Authentication Error"

- Verify SMTP_SERVER, SENDER_EMAIL, and SENDER_PASSWORD are correct
- For Gmail: Make sure you're using an App Password, not your regular password
- For Gmail: Ensure 2-Step Verification is enabled

### Email not received

- Check spam/junk folder
- Verify recipient email address is correct
- Check backend logs for error messages
- Try sending to the same email as SENDER_EMAIL first

### "Permission denied" on environment variables

- Ensure PowerShell/terminal is running with Administrator privileges
- On Unix systems, use: `sudo -i` before setting environment variables

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** instead of hardcoding passwords
3. **Use App Passwords** instead of your main Gmail password
4. **Regenerate credentials** if they are accidentally exposed
5. **Use HTTPS** in production deployments

## Environment Variable Persistence

### Windows (Permanent):

1. Right-click "This PC" → Properties
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Add new User or System variables for SMTP_SERVER, SENDER_EMAIL, SENDER_PASSWORD
5. Restart terminal/application

### macOS/Linux (Permanent):

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
```

Then run: `source ~/.bashrc`

## Docker Deployment

If using Docker, pass environment variables:

```bash
docker run -e SMTP_SERVER=smtp.gmail.com \
           -e SENDER_EMAIL=your@gmail.com \
           -e SENDER_PASSWORD=your-app-password \
           data-doctor-backend
```

Or in docker-compose.yml:

```yaml
environment:
  - SMTP_SERVER=smtp.gmail.com
  - SENDER_EMAIL=your@gmail.com
  - SENDER_PASSWORD=your-app-password
```
