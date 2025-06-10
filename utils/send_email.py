import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import mysql.connector
from mysql.connector import Error


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv


load_dotenv(override=True)
# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# SENDER_EMAIL = "varuninmail@gmail.com"  # Replace with your Gmail address
# SENDER_PASSWORD="wrmm fguv ptqv uqnk"

# RECIPIENTS = ["varuninmail@gmail.com", "varunsekhar208@gmail.com"]  # Replace with actual emails

async def get_recipents(phone_number):
    db_config = {
        'host': 'localhost',  # Change if your MySQL server is not localhost
        'user': 'twilio_user',  # Update with your MySQL username
        'password': 'your_password',  # Update with your MySQL password
        'database': 'lendingkart_db',  # Your database name
        'charset': "utf8mb4",
        'auth_plugin': 'mysql_native_password' 
    }
    recipients = []

    try:
        # Establishing the connection
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            # SQL query to fetch the actionplan by phone number
            select_query = """
            SELECT managers_email,group_manager_mail FROM employees_table WHERE phone = %s;
            """
            cursor.execute(select_query, (phone_number,))

            # Fetch the record
            record = cursor.fetchone()

            # Check if a record was found
            if record:
                for i in record:
                    recipients.append(i)
                
            else:
                print(f"No employee found with the phone number: {phone_number}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return recipients


async def send_email_1(sender, password, RECIPIENTS, subject,body):
    """Send an email from Gmail to two recipients."""
    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = RECIPIENTS[0]
        msg["Subject"] = subject
        msg["CC"] =  ", ".join(RECIPIENTS[1:])
        
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(SENDER_EMAIL, password)
            server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())
            print("Email sent successfully to", ", ".join(RECIPIENTS))
            print("Email content:")
            print(msg.as_string())

        logger.info("Email sent successfully to %s", ", ".join(RECIPIENTS))
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

# Run the function
if __name__ == "__main__":
    import asyncio
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    RECIPIENTS = ["bhaskarrao.g@gmail.com"]
    subject="Action plan for 9963029130"
    body = "Hello,\n\nThis is a test email sent via Python SMTP.\n\nBest regards!"
    asyncio.run(send_email_1(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENTS, subject, body))
    # r = get_recipents("+17043693803")
    # print(r)
