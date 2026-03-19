"""
Gmail App Password Setup Helper
Guides you through generating and configuring a fresh app password
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║         📧 GMAIL APP PASSWORD SETUP WIZARD                   ║
╚══════════════════════════════════════════════════════════════╝
""")

print("""
STEP 1: Generate a Fresh App Password
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open: https://myaccount.google.com/apppasswords

2. If you don't see "App passwords":
   • Go to: https://myaccount.google.com/security
   • Make sure 2-Step Verification is ON ✓
   • Then go back to app passwords

3. Select:
   • Select app: Mail
   • Select device: Other (Windows)

4. Click "Generate"

5. Google will show a 16-character password like:
   abcd efgh ijkl mnop
   
   ⚠️ IMPORTANT: Copy the password WITHOUT spaces
   ✓ Use: abcdefghijklmnop
   ✗ Don't use: abcd efgh ijkl mnop

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

input("Press Enter when you have copied your app password...")

print("""
STEP 2: Configure Environment Variables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Choose one method:

METHOD A: Temporary (Current Terminal Session)
──────────────────────────────────────────────

Run these commands in PowerShell:

$env:SMTP_SERVER = "smtp.gmail.com"
$env:SENDER_EMAIL = "surajars24@gmail.com"
$env:SENDER_PASSWORD = "YOUR_16_CHAR_PASSWORD"

Then in the SAME terminal, start backend:
cd "c:\\Users\\SURAJ ARS\\Documents\\innovations\\DataDoctor"
python backend/main.py

✓ Works immediately
✗ Lost when terminal closes


METHOD B: Permanent (All Future Sessions)
──────────────────────────────────────────

Run PowerShell as ADMINISTRATOR and execute:

[Environment]::SetEnvironmentVariable("SMTP_SERVER", "smtp.gmail.com", "User")
[Environment]::SetEnvironmentVariable("SENDER_EMAIL", "surajars24@gmail.com", "User")
[Environment]::SetEnvironmentVariable("SENDER_PASSWORD", "YOUR_16_CHAR_PASSWORD", "User")

Then RESTART your computer.

✓ Works permanently
✓ Survives terminal/computer restarts
✗ Requires restart


METHOD C: .env File (Development)
─────────────────────────────────

Create or edit: .env in project root

SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=surajars24@gmail.com
SENDER_PASSWORD=YOUR_16_CHAR_PASSWORD

Then add to backend/main.py (after imports):

from dotenv import load_dotenv
load_dotenv()

✓ Easy to manage
✓ Don't commit to git
✗ Requires code change

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("""
STEP 3: Test Your Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After setting environment variables, run:

cd "c:\\Users\\SURAJ ARS\\Documents\\innovations\\DataDoctor"
python test_email.py

This will test:
✓ SMTP connection
✓ TLS encryption
✓ Authentication
✓ Email sending

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("""
TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Error: "Authentication failed"
→ Password is wrong or not copied correctly
→ Solution: Generate a NEW app password again

Error: "Connection refused"
→ Gmail is blocking your IP (security check)
→ Solution: Click "Allow" in Gmail Security alert

Error: "SMTPServerDisconnected"
→ Firewall blocking port 587
→ Solution: Check Windows Firewall settings

Error: "Still not working after setup"
→ environment variables not being read
→ Solution: Run as Administrator and restart computer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("""
QUICK SETUP (RECOMMENDED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open https://myaccount.google.com/apppasswords
2. Generate: Mail → Other (Windows)
3. Copy the 16-character password WITHOUT spaces
4. Paste below:
""")

new_password = input("\nEnter your new app password: ").strip().replace(" ", "")

if len(new_password) == 16:
    print(f"\n✓ Password length valid: {len(new_password)} characters")
    
    print(f"""
5. Run this in PowerShell (as ADMIN for permanent setup):

$env:SMTP_SERVER = "smtp.gmail.com"
$env:SENDER_EMAIL = "surajars24@gmail.com"
$env:SENDER_PASSWORD = "{new_password}"

6. Then start backend in same terminal:

cd "c:\\Users\\SURAJ ARS\\Documents\\innovations\\DataDoctor"
python backend/main.py

7. Test in another terminal:

cd "c:\\Users\\SURAJ ARS\\Documents\\innovations\\DataDoctor"
python test_email.py
""")
else:
    print(f"\n⚠️ Password should be 16 characters, got {len(new_password)}")
    print("Make sure to copy WITHOUT spaces.")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Now you can proceed with backend setup!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
