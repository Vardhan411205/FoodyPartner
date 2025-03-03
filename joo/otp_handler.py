from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import OTPVerification
import random

def generate_otp():
    """Generate a 4-digit OTP"""
    return str(random.randint(1000, 9999))

def send_otp(email, purpose):
    try:
        # Generate 4-digit OTP
        otp = generate_otp()
        
        # Set expiry time (15 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=15)
        
        # Save OTP
        OTPVerification.objects.create(
            email=email,
            otp=otp,
            purpose=purpose,
            expires_at=expires_at
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

def verify_otp(email, otp, purpose):
    try:
        verification = OTPVerification.objects.filter(
            email=email,
            otp=otp,
            purpose=purpose,
            is_verified=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if verification:
            verification.is_verified = True
            verification.save()
            return True
            
        return False
        
    except Exception:
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