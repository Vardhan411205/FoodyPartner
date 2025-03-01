from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import OTPVerification
import random

def generate_otp():
    """Generate a 4-digit OTP"""
    return str(random.randint(1000, 9999))

def send_otp(email, purpose='signup'):
    """Send OTP to email"""
    try:
        # Generate OTP
        otp = generate_otp()
        
        # Save OTP to database
        OTPVerification.objects.create(
            email=email,
            otp=otp,
            purpose=purpose
        )
        
        # Send email
        subject = 'Your OTP for Mr.Foody & Ms.Foody'
        message = f'Your OTP is: {otp}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list)
        
        return {
            'status': 'success',
            'message': 'OTP sent successfully'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def verify_otp(email, otp, purpose='signup'):
    """Verify OTP"""
    try:
        verification = OTPVerification.objects.filter(
            email=email,
            purpose=purpose,
            is_verified=False
        ).latest('created_at')
        
        if verification.otp == otp:
            verification.is_verified = True
            verification.save()
            return True
    except OTPVerification.DoesNotExist:
        return False
    return False

def is_email_verified(email, purpose='signup'):
    """Check if email is verified"""
    try:
        # Check if there's a verified OTP for this email
        verified = OTPVerification.objects.filter(
            email=email,
            purpose=purpose,
            is_verified=True,
            created_at__gte=timezone.now() - timedelta(minutes=30)
        ).exists()
        
        return verified
        
    except Exception:
        return False

# Keep these for backward compatibility
def send_signup_otp(email):
    return send_otp(email, 'signup')

def verify_signup_otp(email, otp):
    return verify_otp(email, otp, 'signup')