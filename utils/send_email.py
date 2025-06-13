import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import sys
from datetime import datetime
from utils.db_config import execute_query


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv


load_dotenv(override=True)
# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# SENDER_EMAIL = "varuninmail@gmail.com"  # Replace with your Gmail address
# SENDER_PASSWORD="wrmm fguv ptqv uqnk"

# RECIPIENTS = ["varuninmail@gmail.com", "varunsekhar208@gmail.com"]  # Replace with actual emails

def get_email_recipients(phone_number):
    """Get email recipients for a given phone number."""
    query = """
    SELECT 
        Email, Name, Manager_Email,
        Group_Manager_Email, Department
    FROM Email_Recipients 
    WHERE Phone_Number = :phone_number
    """
    try:
        result = execute_query(query, {"phone_number": phone_number})
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error getting email recipients: {str(e)}")
        return None

def update_email_recipients(phone_number, update_data):
    """Update email recipients for a given phone number."""
    try:
        # Build the SET clause dynamically based on provided update_data
        set_clauses = []
        params = {"phone_number": phone_number}
        
        for key, value in update_data.items():
            if value is not None:  # Only update non-None values
                set_clauses.append(f"{key} = :{key}")
                params[key] = value
        
        if not set_clauses:
            logger.warning("No valid fields to update")
            return False
            
        query = f"""
        UPDATE Email_Recipients 
        SET {', '.join(set_clauses)}
        WHERE Phone_Number = :phone_number
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error updating email recipients: {str(e)}")
        return False

def insert_email_recipients(recipient_data):
    """Insert new email recipients."""
    try:
        # Build the INSERT query dynamically
        columns = []
        placeholders = []
        params = {}
        
        for key, value in recipient_data.items():
            if value is not None:  # Only insert non-None values
                columns.append(key)
                placeholders.append(f":{key}")
                params[key] = value
        
        if not columns:
            logger.warning("No valid fields to insert")
            return False
            
        query = f"""
        INSERT INTO Email_Recipients 
        ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error inserting email recipients: {str(e)}")
        return False

def delete_email_recipients(phone_number):
    """Delete email recipients for a given phone number."""
    try:
        query = """
        DELETE FROM Email_Recipients 
        WHERE Phone_Number = :phone_number
        """
        execute_query(query, {"phone_number": phone_number})
        return True
    except Exception as e:
        logger.error(f"Error deleting email recipients: {str(e)}")
        return False

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

    # Example phone number
    phone = "+19787319274"
    
    # Get email recipients
    recipients = get_email_recipients(phone)
    print("Current email recipients:", recipients)
    
    # Update example
    update_data = {
        "Manager_Email": "new.manager@example.com",
        "Updated_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if update_email_recipients(phone, update_data):
        print("Update successful")
    
    # Get updated recipients
    updated_recipients = get_email_recipients(phone)
    print("Updated email recipients:", updated_recipients)
