"""
Direct Email Testing Script
Tests Gmail SMTP connection and email sending
"""

import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("=" * 60)
print("📧 EMAIL CONFIGURATION TESTER")
print("=" * 60)

# Get credentials from environment or input
smtp_server = os.getenv('SMTP_SERVER') or 'smtp.gmail.com'
sender_email = os.getenv('SENDER_EMAIL') or input("Enter sender email: ")
sender_password = os.getenv('SENDER_PASSWORD') or input("Enter app password: ")

print(f"\n✓ Configuration:")
print(f"  SMTP Server: {smtp_server}")
print(f"  Email: {sender_email}")
print(f"  Password: {'*' * len(sender_password)}")

# Step 1: Test SMTP Connection
print(f"\n[Step 1/4] Testing SMTP connection...")
try:
    server = smtplib.SMTP(smtp_server, 587)
    print("✓ Connected to SMTP server")
except Exception as e:
    print(f"✗ Failed to connect: {e}")
    sys.exit(1)

# Step 2: Test TLS
print(f"\n[Step 2/4] Testing TLS encryption...")
try:
    server.starttls()
    print("✓ TLS enabled")
except Exception as e:
    print(f"✗ TLS failed: {e}")
    server.quit()
    sys.exit(1)

# Step 3: Test Login
print(f"\n[Step 3/4] Testing authentication...")
try:
    server.login(sender_email, sender_password)
    print("✓ Authentication SUCCESS")
except smtplib.SMTPAuthenticationError as e:
    print(f"✗ Authentication FAILED: {e}")
    print("\n❌ ISSUE: Email/Password incorrect")
    print("\nSolutions:")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Generate a NEW app password (don't use old one)")
    print("3. Copy the 16-character password WITHOUT spaces")
    print("4. Set: $env:SENDER_PASSWORD = 'new_password'")
    server.quit()
    sys.exit(1)
except smtplib.SMTPException as e:
    print(f"✗ SMTP Error: {e}")
    server.quit()
    sys.exit(1)

# Step 4: Test Sending Email
print(f"\n[Step 4/4] Testing email send...")
try:
    recipient = input("Enter recipient email (or press Enter to use your own): ").strip()
    if not recipient:
        recipient = sender_email
    
    # Create test email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = "🧪 DataDoctor - Email Test"
    
    body = """
Hello,

This is a test email from DataDoctor to verify email functionality is working.

If you received this, congratulations! 🎉

✓ SMTP Connection: OK
✓ TLS Encryption: OK
✓ Authentication: OK
✓ Email Sent: OK

Your email configuration is ready for DataDoctor reports.

Best regards,
DataDoctor Team
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send
    server.send_message(msg)
    print(f"✓ Email sent successfully to: {recipient}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour email is configured correctly!")
    print("You can now use email features in DataDoctor.")
    
except Exception as e:
    print(f"✗ Failed to send email: {e}")
    sys.exit(1)
finally:
    server.quit()
