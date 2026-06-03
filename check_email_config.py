#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
django.setup()

from django.conf import settings

print("\n" + "="*70)
print("📧 EMAIL CONFIGURATION STATUS")
print("="*70)

print(f"\nEMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Check if credentials are set
email_user = os.environ.get('EMAIL_HOST_USER')
email_pass = os.environ.get('EMAIL_HOST_PASSWORD')

print(f"\n📍 Environment Variables:")
print(f"EMAIL_HOST_USER: {email_user if email_user else '❌ NOT SET'}")
print(f"EMAIL_HOST_PASSWORD: {'✅ SET' if email_pass else '❌ NOT SET'}")

if not email_user or not email_pass:
    print(f"""
⚠️  Gmail credentials not set in environment!

To enable real email sending, run:
    export EMAIL_HOST_USER="your-email@gmail.com"
    export EMAIL_HOST_PASSWORD="your-16-char-app-password"

Then the app password from yesterday will work!

📝 About Gmail App Passwords:
   ✅ Never expire automatically
   ✅ Valid indefinitely until you manually delete them
   ✅ Safe to create yesterday and use today
   ⚠️  Must use with 2FA enabled on Google Account
   ⚠️  Different from your regular Gmail password

📝 How to generate a Gmail App Password:
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Linux"
3. Google generates a 16-character password
4. Use: export EMAIL_HOST_PASSWORD="that-16-char-password"

""")
else:
    print(f"\n✅ Email credentials are configured!")
    print(f"   EMAIL_HOST_USER: {email_user}")
    print(f"   Ready to send real emails via Gmail!")

print("="*70 + "\n")
