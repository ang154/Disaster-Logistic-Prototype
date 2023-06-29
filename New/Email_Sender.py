import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(title, content: str, receiver_email="tony.q.xiang@icloud.com"):
    smtp_obj = smtplib.SMTP('smtp.mail.me.com', 587)
    smtp_obj.starttls()
    smtp_obj.login("tony.q.xiang@icloud.com", "vkfi-dnle-mdka-imqr")
    sender_email = "no-reply@disaster-logix.com"

    # Create a secure SSL context
    message = MIMEMultipart("alternative")
    message["Subject"] = title  # Subject
    message["From"] = "Disaster Logix <{}>".format(sender_email)
    message["To"] = receiver_email
    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    Below are the details for this alert / update:
    {}
    Please log in to the portal to take further action:
    https://disaster-logix.com""".format(content)
    html = """\
    <html>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="stylesheet" href="https://www.w3schools.com/lib/w3-theme-blue-grey.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
      <body>
        <div class="w3-container w3-light-grey">
        <h2>{}</h2>
        <p>Hi,<br>
            Below are the details for this alert / update:<br></p>
           {}<br>
           <br>
        </div>
        <div class="w3-container w3-dark-grey">  
           <p>Please log in to the <a href="https://disaster-logix.com">Portal</a> to take further action.
        </div>
        </p>
      </body>
    </html>
    """.format(title, content)
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Send email
    try:
        send_status = smtp_obj.sendmail(sender_email, receiver_email, message.as_string())
        if send_status != {}:
            print('There was a problem sending mail to {}.\n{}'.format(receiver_email, send_status))
    except smtplib.SMTPDataError:
        print('Sending email to {} failed.'.format(receiver_email))
    finally:
        print("Email sent.")
        smtp_obj.quit()


def test_email(receiver_email="tony.q.xiang@icloud.com"):
    smtp_obj = smtplib.SMTP('smtp.mail.me.com', 587)
    smtp_obj.starttls()
    smtp_obj.login("tony.q.xiang@icloud.com", "vkfi-dnle-mdka-imqr")
    sender_email = "no-reply@disaster-logix.com"

    # Create a secure SSL context
    message = MIMEMultipart("alternative")
    message["Subject"] = "Test Email"  # Subject
    message["From"] = sender_email
    message["To"] = receiver_email
    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    Below are the details for this alert / update:
    {}
    Please log in to the portal to take further action:
    https://disaster-logix.com""".format("Test content")
    html = """\
    <html>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="stylesheet" href="https://www.w3schools.com/lib/w3-theme-blue-grey.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
      <body>
        <div class="w3-container w3-light-grey">
        <h2>{}</h2>
        <p>Hi,<br>
            Below are the details for this alert / update:<br></p>
           {}<br>
           <br>
        </div>
        <div class="w3-container w3-dark-grey">  
           <p>Please log in to the <a href="https://disaster-logix.com">Portal</a> to take further action.
        </div>
        </p>
      </body>
    </html>
    """.format("Test Subject", "Test content")
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Send email
    try:
        send_status = smtp_obj.sendmail(sender_email, receiver_email, message.as_string())
        if send_status != {}:
            print('There was a problem sending mail to {}.\n{}'.format(receiver_email, send_status))
    except smtplib.SMTPDataError:
        print('Sending email to {} failed.'.format(receiver_email))
    finally:
        smtp_obj.quit()
