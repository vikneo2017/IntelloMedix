import smtplib
from email.mime.text import MIMEText

def send_mail(orderEmail, orderPhone, order, date):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = '91ab2fb8cef720'
    password = 'ef256670b6f933'
    message = f"<h3>New Order Submission</h3><ul><li>E-mail: {orderEmail}</li><li>Phone: {orderPhone}</li>" \
              f"<li>Order: {order}</li><li>Date: {date}</li></ul>"
    sender_email = 'email1@example.com'
    receiver_email = 'email2@example.com'
    msg = MIMEText(message, 'html')
    msg['Subject'] = 'Intellomedix Order'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Send email
    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())