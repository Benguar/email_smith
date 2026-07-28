import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings import settings


def send_email_to_user(recipient_email: str, subject: str , body: str):
    """
    Sends an email to a user. Use this tool ONLY when explicitly asked to send an email.
    DO not use this tool for casual conversations greetings and conversations in which you are not explicitly told to send an Email it is strictly for sending emails when you are told to

    Args:
        recipient_email: The email address to send the message to.
        body: The main content of the email message.
        subject: The title of the email. IF THE USER DOES NOT PROVIDE ONE, YOU MUST GENERATE A HIGHLY RELEVANT SUBJECT LINE BASED ON THE BODY. NEVER LEAVE THIS BLANK.
    """
    print(f'THe send email tool has been called')
    sender_email = "iqmbenzy@gmail.com"
    app_password = settings.GMAIL_APP_PASSWORD

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    

    body = f"""
    <html>
        <body>
            <p>{body}></p>
        </body>
    </html>
    """
  
    message.attach(MIMEText(body, "html"))

    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        print(f'sending')
        server.sendmail(sender_email, recipient_email, message.as_string())
        print(f'success')
    except Exception as e:
        print(f"Failed to send email: {e}")
        
    finally:
        server.quit()
    return "Email sent successfully"