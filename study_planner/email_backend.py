"""
Custom email backend that sends emails via Gmail SMTP AND prints to console.
Perfect for development - you see the emails both sent AND logged.
"""
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend


class DualEmailBackend:
    """
    Email backend that sends via both SMTP (Gmail) and Console.
    Emails are actually sent to Gmail AND printed in console for debugging.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        # Pass through all kwargs to SMTPEmailBackend (e.g., username, password, etc.)
        self.smtp_backend = SMTPEmailBackend(fail_silently=fail_silently, **kwargs)
        self.console_backend = ConsoleEmailBackend(fail_silently=fail_silently)
    
    def open(self):
        self.smtp_backend.open()
        self.console_backend.open()
    
    def close(self):
        self.smtp_backend.close()
        self.console_backend.close()
    
    def send_messages(self, email_messages):
        """Send messages to both SMTP and console"""
        # Send to console first (for debugging)
        self.console_backend.send_messages(email_messages)
        
        # Send to Gmail
        try:
            return self.smtp_backend.send_messages(email_messages)
        except Exception as e:
            print(f"\n❌ Gmail SMTP Error: {str(e)}")
            print("Make sure you have:")
            print("  1. Gmail App Password (16-char password from https://myaccount.google.com/apppasswords)")
            print("  2. Set environment variables:")
            print("     export EMAIL_HOST_USER='wainainaalvin76@gmail.com'")
            print("     export EMAIL_HOST_PASSWORD='your-16-char-app-password'")
            print("\nEmails are still printed above in console.\n")
            return 0
