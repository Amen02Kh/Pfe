import random
import smtplib
import argparse
from email.mime.text import MIMEText

# Create the parser
parser = argparse.ArgumentParser(description='Send emails from the terminal')

# Add the arguments
parser.add_argument('Domain', metavar='sender', type=str, help='the domain')
parser.add_argument('Receiver', metavar='receiver', type=str, nargs='+', help='the receiver emails')
parser.add_argument('SMTP_Username', metavar='smtp_username', type=str, help='the SMTP username')
parser.add_argument('SMTP_Password', metavar='smtp_password', type=str, help='the SMTP password')

# Execute the parse_args() method
args = parser.parse_args()

# Specifying sender and receivers
sender = 'test@example.com'
receiver = args.Receiver
domain=args.Domain
# Specifying smtp port
port = 587

# Specifying Smtp Address and Connecting to the server
with smtplib.SMTP(domain, port) as server:
    for i in range(20):  # You can change the value inside the range to the number of emails you wanna send
        randnum = random.randint(0, 999)  # Generating random number
        msg = MIMEText(f'this is the body of the email')  # Body of the email
        msg['Subject'] = 'Subject of the email'  # Subject Of the email
        # From of email again but i'm adding random number between so that in the inbox it stacks causing to flood the inbox
        msg['From'] = f'from{randnum}@example.com'
        msg['To'] = receiver# To email again
        #server.login(args.SMTP_Username, args.SMTP_Password) # SMTP Credentials
        server.sendmail(sender, receiver, msg.as_string()) # Composing the email
    print("Successfully sent 20 email") # Printing Success Msg
