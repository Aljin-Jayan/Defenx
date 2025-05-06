import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.yandex.ru"
SMTP_PORT = 465  # SSL port
SENDER_EMAIL = "Defenx.secure@yandex.com"
SENDER_PASSWORD = "dsgadsfgaeha"  # App-specific password if 2FA enabled
RECIPIENT_EMAIL = "sample@gmail.com"

def send_email(subject: str, body: str):
    # Create email message
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Establish SSL connection
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            # Log in to the SMTP server
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            # Send the email
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Email content
subject = "URGENT: Website Defacement Detected - Immediate Action Required"
body = (
    "Dear User,\n\n"
    "We have detected a defacement on your website, indicating possible unauthorized access or malicious activity. "
    "Immediate action is required to prevent further security risks.\n\n"
    "What Happened?\n"
    "Our automated monitoring system at DefenX identified suspicious changes to your website’s content. "
    "This could be due to:\n"
    "✅ Unauthorized access to your website files.\n"
    "✅ Malicious scripts injected into your web pages.\n"
    "✅ Changes to homepage content, displaying unwanted messages or images.\n\n"
    "Initial Precautions to Take Immediately:\n"
    "🔹 Take your website offline temporarily to prevent further damage.\n"
    "🔹 Reset all administrator passwords, including database and hosting credentials.\n"
    "🔹 Scan your website files for malware using an updated antivirus tool.\n"
    "🔹 Restore a recent backup if available, but ensure the backup is clean.\n"
    "🔹 Check user access logs for any unauthorized login attempts.\n\n"
    "Next Steps with DefenX:\n"
    "Our security team is actively investigating the incident. We will provide you with a detailed security report and recommendations "
    "to enhance your website’s protection.\n\n"
    "If you need immediate assistance, please contact our support team at support@defenx.com or call [your helpline number].\n\n"
    "Your website’s security is our priority. We strongly advise implementing web application firewalls (WAF), "
    "regular backups, and security patches to prevent future attacks.\n\n"
    "Best regards,\n"

    
    "DefenX Security Team\n"
    "📧 support@defenx.com\n"
)

# Send the email
send_email(subject, body)