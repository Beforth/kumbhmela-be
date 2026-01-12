from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """User registration endpoint"""
    try:
        # Log incoming data for debugging
        print(f"Register request method: {request.method}")
        print(f"Register request content type: {request.content_type}")
        print(f"Register request data: {request.data}")
        print(f"Register request body (raw): {request.body[:200] if hasattr(request, 'body') else 'N/A'}")
        
        # Check if request.data is empty
        if not request.data:
            error_msg = {'error': 'Request body is empty. Please send JSON data with email, full_name, and password.'}
            print(f"Register error: {error_msg}")
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        # Log validation errors
        print(f"Register validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Register exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """User login endpoint"""
    try:
        # Log incoming data for debugging
        print(f"Login request method: {request.method}")
        print(f"Login request content type: {request.content_type}")
        print(f"Login request data: {request.data}")
        
        # Check if request.data is empty
        if not request.data:
            error_msg = {'error': 'Request body is empty. Please send JSON data with email and password.'}
            print(f"Login error: {error_msg}")
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        # Log validation errors
        print(f"Login validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Login exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint - Get and Update"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change password endpoint - requires authentication"""
    try:
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Both old_password and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 6:
            return Response(
                {'error': 'New password must be at least 6 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify old password
        user = request.user
        if not user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        print(f"Change password exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    """Forgot password endpoint - sends password reset email"""
    try:
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response(
                {'message': 'If an account exists with this email, a password reset link has been sent.'},
                status=status.HTTP_200_OK
            )
        
        # Generate a temporary password or reset token
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Set the temporary password
        user.set_password(temp_password)
        user.save()
        
        # Get SMTP settings
        from kumbh.models import SmtpSettings
        smtp_settings = SmtpSettings.objects.filter(is_default=True, is_active=True).first()
        
        if not smtp_settings:
            return Response(
                {'error': 'Email service is not configured. Please contact administrator.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Send email using SMTP settings
        try:
            _send_password_reset_email(user, temp_password, smtp_settings)
            return Response(
                {'message': 'Password reset email has been sent. Please check your inbox.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return Response(
                {'error': f'Failed to send email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        print(f"Forgot password exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _send_password_reset_email(user, temp_password, smtp_settings):
    """Send password reset email using SMTP settings"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.utils import formataddr
    import socket
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Kumbh Suraksha - Password Reset'
    msg['From'] = formataddr((smtp_settings.from_name or 'Kumbh Suraksha', smtp_settings.from_email))
    msg['To'] = user.email
    
    # Create email body
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #f97316;">Kumbh Suraksha</h2>
          <h3>Password Reset Request</h3>
          <p>Hello {user.full_name or user.email},</p>
          <p>You have requested to reset your password. Your temporary password is:</p>
          <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center;">
            <strong style="font-size: 18px; color: #f97316;">{temp_password}</strong>
          </div>
          <p>Please login with this temporary password and change it immediately for security.</p>
          <p style="color: #666; font-size: 12px; margin-top: 30px;">
            If you did not request this password reset, please ignore this email or contact support.
          </p>
        </div>
      </body>
    </html>
    """
    
    text_body = f"""
    Kumbh Suraksha - Password Reset
    
    Hello {user.full_name or user.email},
    
    You have requested to reset your password. Your temporary password is:
    
    {temp_password}
    
    Please login with this temporary password and change it immediately for security.
    
    If you did not request this password reset, please ignore this email or contact support.
    """
    
    # Attach parts
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    # Send email with proper error handling and timeout
    server = None
    try:
        # Set socket timeout
        socket.setdefaulttimeout(30)  # 30 seconds timeout
        
        # Connect to SMTP server
        if smtp_settings.use_tls:
            server = smtplib.SMTP(smtp_settings.host, smtp_settings.port, timeout=30)
            server.set_debuglevel(0)  # Set to 1 for debugging
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_settings.host, smtp_settings.port, timeout=30)
            server.set_debuglevel(0)
        
        # Login
        server.login(smtp_settings.username, smtp_settings.password)
        
        # Send email
        server.send_message(msg)
        
        print(f"Password reset email sent successfully to {user.email}")
        
    except socket.gaierror as e:
        raise Exception(f"DNS resolution failed for SMTP host '{smtp_settings.host}': {str(e)}. Please check the SMTP host address.")
    except socket.timeout:
        raise Exception(f"Connection timeout while connecting to SMTP server '{smtp_settings.host}:{smtp_settings.port}'. Please check your network connection and SMTP settings.")
    except ConnectionRefusedError:
        raise Exception(f"Connection refused by SMTP server '{smtp_settings.host}:{smtp_settings.port}'. Please check the SMTP host and port settings.")
    except OSError as e:
        if "Network is unreachable" in str(e) or "errno 101" in str(e):
            raise Exception(f"Network is unreachable. Cannot connect to SMTP server '{smtp_settings.host}:{smtp_settings.port}'. Please check your network connection and firewall settings.")
        else:
            raise Exception(f"Network error: {str(e)}")
    except smtplib.SMTPAuthenticationError as e:
        raise Exception(f"SMTP authentication failed. Please check your username and password in SMTP settings.")
    except smtplib.SMTPException as e:
        raise Exception(f"SMTP error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
    finally:
        if server:
            try:
                server.quit()
            except:
                pass
