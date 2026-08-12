import smtplib
import base64
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from auth.core.settings import settings
from langgraph.types import interrupt,Command
from langgraph.graph import END
from langchain_core.runnables import RunnableConfig


def get_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    """Exchanges a refresh token for a fresh access token."""
    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(url, data=payload)
    
    if not response.ok:
        raise Exception(f"Failed to refresh token: {response.text}")
        
    return response.json().get("access_token")

def generate_oauth2_string(email: str, access_token: str) -> str:
    """Encodes the email and access token into the XOAUTH2 format."""
    auth_string = f"user={email}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode("ascii")).decode("ascii")
def send_email_to_user(recipient_email: str , subject: str , body: str, config: RunnableConfig):
    """
    Sends an email to a user. Use this tool ONLY when explicitly asked to send an email.
    DO not use this tool for casual conversations greetings and conversations in which you are not explicitly told to send an Email it is strictly for sending emails when you are told to

    Args:
        recipient_email: The email address to send the message to.
        body: The main content of the email message. this should be in a HTML format to suit message tone and language. EXCLUDE the <html> and <body> tags, which should reflect the tone and language of the  excluding the <html> and </body> tags. use necessary html tags like <p> <h2> <br> <h1> <strong><b> <i> ,inline css and every other necessary HTML tag to ensure attractive, standard and professional formatting
        subject: The title of the email. IF THE USER DOES NOT PROVIDE ONE, YOU MUST GENERATE A HIGHLY RELEVANT SUBJECT LINE BASED ON THE BODY. NEVER LEAVE THIS BLANK.
    Example:
    body = '<h2>Hello World!</h2><p>This is an example email.</p>'
    """
    if recipient_email == '':
        return f'ERROR: You are NOT supposed to use this rule. analyse user message again and respond appropriately'
    if subject == '':
        return "you did not call this tool with a subject call this tool again with a subject"
    refresh_token = config.get("configurable", {}).get("refresh_token")
    sender_email = config.get("configurable", {}).get("email")
    print(f"this is the refresh token {refresh_token}, this is sender_email {sender_email}")
    print("calling email tool")
    print(f'\n body: {body} \n\n subject:  {subject}')
    message = MIMEMultipart()
  
    decision = interrupt({
        "recipient": recipient_email,
        "subject": subject,
        "body": body
    })
    if decision.get("decision")== 'yes':
        message["From"] = sender_email
        message["To"] = decision.get("recipient_email")
        message["Subject"] = decision.get("subject")
        body = f"""<html>
        <body> {decision.get("body")} </body>
        </html>
        """
        message.attach(MIMEText(body, "html"))
        print("i wanna see sucsess")
        try:
            if not refresh_token:
                raise Exception("Missing refresh token. User must log in again.")
                
            access_token = get_access_token(
                settings.GOOGLE_CLIENT_ID, 
                settings.GOOGLE_CLIENT_SECRET, 
                refresh_token
            )
            auth_string = generate_oauth2_string(sender_email, access_token)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            auth_code,auth_response = server.docmd("AUTH", f"XOAUTH2 {auth_string}")
            if auth_code != 235:
                raise Exception(f"OAuth2 Auth Failed! Code: {auth_code}. Reason: {auth_response}")
            print(f'sending')
            server.sendmail(sender_email, decision.get("recipient_email"), message.as_string())
            print(f'success')
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            
        finally:
            if 'server' in locals():
                server.quit()
        return "successful"
    elif decision.get("decision") == 'no':
        return Command(
                    goto=END
                )
