from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Database connection configuration
DB_USER = os.getenv('DB_USER', 'twilio_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
DB_HOST = os.getenv('DB_HOST', 'mysql')  # Changed to 'mysql' for Docker service name
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'lendingkart_db')

# Create database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_connection(max_retries=5, retry_delay=5):
    """Create and return a database connection with retry logic."""
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except SQLAlchemyError as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Error creating database connection after {max_retries} attempts: {str(e)}")
                return None

def execute_sql_commands(sql_commands: List[str]) -> List[Dict[str, Any]]:
    """
    Execute a list of SQL commands and return the results.
    
    Args:
        sql_commands (List[str]): List of SQL commands to execute
        
    Returns:
        List[Dict[str, Any]]: List of results from the executed commands
    """
    engine = create_connection()
    if not engine:
        return []
    
    results = []
    
    try:
        with engine.connect() as connection:
            for sql_command in sql_commands:
                try:
                    # Execute the SQL command
                    result = connection.execute(text(sql_command))
                    
                    # If the command returns data (like SELECT), fetch it
                    if result.returns_rows:
                        rows = result.fetchall()
                        column_names = result.keys()
                        result_dict = [dict(zip(column_names, row)) for row in rows]
                        results.append(result_dict)
                    else:
                        results.append({"affected_rows": result.rowcount})
                        
                except SQLAlchemyError as e:
                    print(f"Error executing SQL command: {sql_command}")
                    print(f"Error details: {str(e)}")
                    results.append({"error": str(e)})
                    
    except SQLAlchemyError as e:
        print(f"Error with database connection: {str(e)}")
    finally:
        engine.dispose()
    
    return results

def main():
    # Example usage
    sql_commands = [
        # Drop existing tables if they exist
        "DROP TABLE IF EXISTS Dummy;",
        "DROP TABLE IF EXISTS Call_Summary;",
        "DROP TABLE IF EXISTS Insurance;",
        
        # Create tables
        """CREATE TABLE Dummy (
            number VARCHAR(14) NOT NULL PRIMARY KEY,
            name VARCHAR(500),
            language VARCHAR(200),
            greet_message VARCHAR(1000),
            preferred_voice VARCHAR(10)
        );""",
        
        # Insert data into Dummy
        """INSERT INTO Dummy (number, name, language, greet_message, preferred_voice) 
        VALUES
        ('+917799117204', 'Krish', 'Spanish', 'Hola, estoy aquí para ayudarte.', 'Male'),
        ('+919963029130', 'Bhaskar', 'English', 'Hi, this the the lendingkart AI. I am here to help you', 'Male');""",
        
        # Select from Dummy
        "SELECT * FROM Dummy;",
        
        # Create Call_Summary table
        """CREATE TABLE Call_Summary (
            name VARCHAR(500),
            phone_number VARCHAR(14) NOT NULL PRIMARY KEY,
            call_duration INT,
            number_of_calls INT,
            complete_call_transcription TEXT
        );""",
        
        # Insert data into Call_Summary
        """INSERT INTO Call_Summary (name, phone_number, call_duration, number_of_calls, complete_call_transcription) 
        VALUES
        ('Krish', '+917799117204', 0, 0, ''),
        ('Dr. Bhaskar', '+919963029130', 0, 0, '');""",
        
        # Select from Call_Summary
        "SELECT * FROM Call_Summary;",
        
        # Create Insurance table
        """CREATE TABLE Insurance (
            Policyholder_ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            Name VARCHAR(255),
            Address TEXT,
            City VARCHAR(100),
            State VARCHAR(100),
            Pincode VARCHAR(10),
            Phone_Number VARCHAR(255),
            Email VARCHAR(255),
            Date_of_Birth VARCHAR(10),
            Gender ENUM('Male','Female','Other'),
            PAN_Number VARCHAR(10),
            Aadhaar_Number VARCHAR(12),
            Bank_Account_Number VARCHAR(20),
            Bank_Name VARCHAR(255),
            IFSC_Code VARCHAR(20),
            Nominee_Name VARCHAR(255),
            Nominee_Relationship VARCHAR(50),
            Nominee_Contact_Number VARCHAR(255),
            Policy_ID VARCHAR(50),
            Policy_Type VARCHAR(50),
            Policy_Start_Date VARCHAR(10),
            Policy_Maturity_Date VARCHAR(10),
            Premium_Amount VARCHAR(20),
            Premium_Payment_Frequency ENUM('Monthly','Quarterly','Annually'),
            Policy_Status ENUM('Active','Lapsed','Surrendered'),
            Sum_Assured VARCHAR(20),
            Bonus_Amount VARCHAR(20),
            Surrender_Value VARCHAR(20),
            Loan_Against_Policy VARCHAR(20),
            Policy_Documents_Received ENUM('Yes','No'),
            Policy_Documents_Received_Date VARCHAR(10),
            Claim_ID VARCHAR(50),
            Claim_Type VARCHAR(50),
            Claim_Amount VARCHAR(20),
            Claim_Submission_Date VARCHAR(10),
            Claim_Status ENUM('Pending','Approved','Rejected'),
            Claim_Rejection_Reason TEXT
        );""",
        
        # Insert data into Insurance
        """INSERT INTO Insurance (
            Name, Address, City, State, Pincode, Phone_Number, Email, Date_of_Birth, Gender, 
            PAN_Number, Aadhaar_Number, Bank_Account_Number, Bank_Name, IFSC_Code, 
            Nominee_Name, Nominee_Relationship, Nominee_Contact_Number, Policy_ID, 
            Policy_Type, Policy_Start_Date, Policy_Maturity_Date, Premium_Amount, 
            Premium_Payment_Frequency, Policy_Status, Sum_Assured, Bonus_Amount, 
            Surrender_Value, Loan_Against_Policy, Policy_Documents_Received, 
            Policy_Documents_Received_Date, Claim_ID, Claim_Type, Claim_Amount, 
            Claim_Submission_Date, Claim_Status, Claim_Rejection_Reason
        ) VALUES
        (
            'Krish', 'India', 'Hyderabad', 'Louisiana', '33716', '+917799117204', 
            'krishhindocha@gmail.com', '1949-1-29', 'Other', 'Ekkmm1001W', '182167699220',
            'ZXUN56003052381022', 'Nguyen and Sons', 'NPSKGBQN', 'John Parker', 'Parent', 
            '478-571-5793', '12b0075f-b71e-4c64-a862-b8e3e86cea32', 'Whole Life', 
            '2021-2-27', '2043-10-11', '94996.86', 'Quarterly', 'Lapsed', '691556.59', 
            '23690.51', '36179.72', '15467.48', 'Yes', '2025-3-7', 
            '209e02a7-e691-4eee-a6c1-2edebda0a3e8', 'Maturity', '831048.19', 
            '2025-1-30', 'Rejected', 'Exactly history admit girl will.'
        ),
        (
            'Dr. Bhaskar', 'India', 'Hyderabad', 'Louisiana', '33716', '+919963029130', 
            'bhaskarrao.g@gmail.com', '1949-1-29', 'Male', 'Ekkmm1001W', '182167699220',
            'ZXUN56003052381022', 'Nguyen and Sons', 'NPSKGBQN', 'John Parker', 'Parent', 
            '478-571-5793', '12b0075f-b71e-4c64-a862-b8e3e86cea32', 'Whole Life', 
            '2021-2-27', '2043-10-11', '94996.86', 'Quarterly', 'Lapsed', '691556.59', 
            '23690.51', '36179.72', '15467.48', 'Yes', '2025-3-7', 
            '209e02a7-e691-4eee-a6c1-2edebda0a3e8', 'Maturity', '831048.19', 
            '2025-1-30', 'Rejected', 'Exactly history admit girl will.'
        );""",

        # Select from Insurance
        "SELECT * FROM Insurance;"
    ]
    
    results = execute_sql_commands(sql_commands)
    
    # Print results
    for i, result in enumerate(results):
        print(f"\nCommand {i + 1} Results:")
        print(result)

if __name__ == "__main__":
    main() 