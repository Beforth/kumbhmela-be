#!/usr/bin/env python
"""
Standalone test email sending script for SMTP settings
Usage: python test-email.py
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import socket
import sys
import getpass


def send_test_email(host, port, use_tls, username, password, from_email, from_name, to_email, test_message="This is a test email from Kumbh Suraksha."):
    """Send a test email using SMTP settings"""
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Kumbh Suraksha - Test Email'
    msg['From'] = formataddr((from_name or 'Kumbh Suraksha', from_email))
    msg['To'] = to_email
    
    # Create email body
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #f97316;">Kumbh Suraksha</h2>
          <h3>Test Email</h3>
          <p>{test_message}</p>
          <p style="color: #666; font-size: 12px; margin-top: 30px;">
            This is a test email to verify SMTP settings configuration.
          </p>
        </div>
      </body>
    </html>
    """
    
    text_body = f"""
    Kumbh Suraksha - Test Email
    
    {test_message}
    
    This is a test email to verify SMTP settings configuration.
    """
    
    # Attach parts
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    # Send email with proper error handling and timeout
    server = None
    try:
        # Set socket timeout
        socket.setdefaulttimeout(30)  # 30 seconds timeout
        
        print(f"Connecting to SMTP server: {host}:{port}")
        print(f"Using TLS: {use_tls}")
        
        # Connect to SMTP server
        if use_tls:
            server = smtplib.SMTP(host, port, timeout=30)
            server.set_debuglevel(1)  # Enable debug output
            print("Starting TLS...")
            server.starttls()
            print("TLS started successfully")
        else:
            server = smtplib.SMTP_SSL(host, port, timeout=30)
            server.set_debuglevel(1)
            print("Connected via SSL")
        
        # Login
        print(f"Logging in as: {username}")
        server.login(username, password)
        print("Login successful")
        
        # Send email
        print(f"Sending email to: {to_email}")
        server.send_message(msg)
        print("Email sent successfully!")
        
        return True
        
    except socket.gaierror as e:
        print(f"ERROR: DNS resolution failed for SMTP host '{host}': {str(e)}")
        print("Please check the SMTP host address.")
        return False
    except socket.timeout:
        print(f"ERROR: Connection timeout while connecting to SMTP server '{host}:{port}'")
        print("Please check your network connection and SMTP settings.")
        return False
    except ConnectionRefusedError:
        print(f"ERROR: Connection refused by SMTP server '{host}:{port}'")
        print("Please check the SMTP host and port settings.")
        return False
    except OSError as e:
        if "Network is unreachable" in str(e) or "errno 101" in str(e):
            print(f"ERROR: Network is unreachable. Cannot connect to SMTP server '{host}:{port}'")
            print("Please check your network connection and firewall settings.")
        else:
            print(f"ERROR: Network error: {str(e)}")
        return False
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: SMTP authentication failed: {str(e)}")
        print("Please check your username and password in SMTP settings.")
        return False
    except smtplib.SMTPException as e:
        print(f"ERROR: SMTP error: {str(e)}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to send email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if server:
            try:
                server.quit()
                print("Disconnected from SMTP server")
            except:
                pass


def main():
    """Main function to test email sending"""
    print("=" * 60)
    print("Kumbh Suraksha - SMTP Email Test")
    print("=" * 60)
    print()
    
    # Get SMTP settings from user
    print("Enter SMTP Settings:")
    print("-" * 60)
    
    host = input("SMTP Host (e.g., smtp.gmail.com): ").strip()
    if not host:
        print("ERROR: SMTP host is required")
        return
    
    port_str = input("SMTP Port (e.g., 587 for TLS, 465 for SSL): ").strip()
    try:
        port = int(port_str) if port_str else 587
    except ValueError:
        print("ERROR: Invalid port number")
        return
    
    use_tls_str = input("Use TLS? (y/n, default: y): ").strip().lower()
    use_tls = use_tls_str != 'n'
    
    username = input("SMTP Username/Email: ").strip()
    if not username:
        print("ERROR: Username is required")
        return
    
    password = getpass.getpass("SMTP Password: ").strip()
    if not password:
        print("ERROR: Password is required")
        return
    
    from_email = input(f"From Email (default: {username}): ").strip() or username
    from_name = input("From Name (optional): ").strip() or None
    
    print()
    to_email = input("Recipient Email: ").strip()
    if not to_email:
        print("ERROR: Recipient email is required")
        return
    
    print()
    print("SMTP Configuration:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Use TLS: {use_tls}")
    print(f"  Username: {username}")
    print(f"  From Email: {from_email}")
    print(f"  From Name: {from_name or 'N/A'}")
    print(f"  To Email: {to_email}")
    print()
    
    confirm = input("Send test email? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    print()
    print("Sending test email...")
    print("-" * 60)
    
    success = send_test_email(
        host=host,
        port=port,
        use_tls=use_tls,
        username=username,
        password=password,
        from_email=from_email,
        from_name=from_name,
        to_email=to_email
    )
    
    print("-" * 60)
    if success:
        print("✓ Test email sent successfully!")
        print(f"  Please check the inbox of: {to_email}")
    else:
        print("✗ Failed to send test email")
        print("  Please check the error messages above and verify your SMTP settings.")


if __name__ == '__main__':
    main()

