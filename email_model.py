import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

smtp_port = os.getenv("SMTP_PORT")
smtp_server = os.getenv("GSERVER")
sender_email = os.environ.get("GUSERNAME")
sender_password = os.environ.get("GPASSWORD")

def send_email(to: str, subject: str, message: str, cc: str=None) -> None:
    msg = MIMEMultipart()
    msg['From'] = "Teddox"
    msg['To'] = to
    if cc:
        msg['Cc'] = cc
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, [to, "udemezue@outlook.com"], text)        
        successful = True
    except Exception as e:
        print(f'Email could not be sent to {to}. Error: {str(e)}')
        successful = False
    finally:
        server.quit()
    return successful

if __name__ == "__main__":
    send_email('udemezue@gmail.com', 'testing smtp email', "testing without cc")
    send_email('udemezue@gmail.com', 'testing smtp email', "testing with cc", "ezue1@yahoo.com")