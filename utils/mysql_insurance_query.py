import os
import re
import mysql
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import mysql.connector
from utils.db_config import execute_query
import sys
import logging
from datetime import datetime
CALLER_NUMBER="780-607-0572"
api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=api_key)
db_config = {
        "dbname": "lendingkart_db",
        "user": "root",
        "password": "gbr123",
        "host": "localhost"
    }

    # Table fields description
master_table_fields = {
        "Policyholder_ID": "A unique identifier for each policyholder, automatically generated as a serial number.",
        "Name": "Full name of the policyholder.",
        "Address": "Residential address of the policyholder.",
        "City": "City of residence of the policyholder.",
        "State": "State of residence of the policyholder.",
        "Pincode": "Postal code of the policyholder's address.",
        "Phone_Number": "Contact number of the policyholder.",
        "Email": "Email address of the policyholder.",
        "Date_of_Birth": "Birthdate of the policyholder.",
        "Gender": "Gender of the policyholder.",
        "PAN_Number": "Permanent Account Number (PAN) of the policyholder.",
        "Aadhaar_Number": "Aadhaar number of the policyholder.",
        "Bank_Account_Number": "Bank account number linked to the policy.",
        "Bank_Name": "Name of the bank where the account is held.",
        "IFSC_Code": "IFSC code of the bank branch.",
        "Nominee_Name": "Name of the nominee for the policy.",
        "Nominee_Relationship": "Relationship of the nominee to the policyholder.",
        "Nominee_Contact_Number": "Contact number of the nominee.",
        "Policy_ID": "Unique identifier for the policy.",
        "Policy_Type": "Type of insurance policy (e.g., term, endowment, etc.).",
        "Policy_Start_Date": "Date when the policy was started.",
        "Policy_Maturity_Date": "Date when the policy matures.",
        "Premium_Amount": "Amount of the premium to be paid.",
        "Premium_Payment_Frequency": "Frequency of premium payments (e.g., monthly, quarterly, annually).",
        "Policy_Status": "Current status of the policy (e.g., active, lapsed, surrendered).",
        "Sum_Assured": "Total sum assured by the policy.",
        "Bonus_Amount": "Bonus amount accrued under the policy.",
        "Surrender_Value": "Surrender value of the policy if terminated early.",
        "Loan_Against_Policy": "Loan amount taken against the policy.",
        "Policy_Documents_Received": "Indicates whether policy documents have been received (Yes/No).",
        "Policy_Documents_Received_Date": "Date when policy documents were received.",
        "Policy_Assignment_Status": "Status of policy assignment (e.g., assigned, unassigned).",
        "Policy_Revival_Date": "Date when a lapsed policy was revived.",
        "Policy_Cancellation_Date": "Date when the policy was canceled.",
        "Policy_Cancellation_Reason": "Reason for policy cancellation.",
        "Complaint_ID": "Unique identifier for a complaint.",
        "Complaint_Date": "Date when the complaint was filed.",
        "Complaint_Type": "Type of complaint (e.g., service, claim, etc.).",
        "Complaint_Description": "Detailed description of the complaint.",
        "Complaint_Status": "Current status of the complaint (e.g., open, resolved).",
        "Resolution_Date": "Date when the complaint was resolved.",
        "Resolution_Details": "Details of the resolution.",
        "Grievance_Officer_Name": "Name of the grievance officer handling the complaint.",
        "Grievance_Officer_Contact": "Contact number of the grievance officer.",
        "Escalation_Level": "Level to which the complaint has been escalated.",
        "Claim_ID": "Unique identifier for a claim.",
        "Claim_Type": "Type of claim (e.g., death, maturity, etc.).",
        "Claim_Amount": "Amount claimed under the policy.",
        "Claim_Submission_Date": "Date when the claim was submitted.",
        "Claim_Settlement_Date": "Date when the claim was settled.",
        "Claim_Status": "Current status of the claim (e.g., pending, approved, rejected).",
        "Claim_Rejection_Reason": "Reason for claim rejection.",
        "Claim_Documents_Submitted": "Indicates whether claim documents were submitted (Yes/No).",
        "Claim_Documents_Verified": "Indicates whether claim documents were verified (Yes/No).",
        "Premium_Payment_ID": "Unique identifier for a premium payment.",
        "Premium_Due_Date": "Due date for the premium payment.",
        "Premium_Paid_Date": "Date when the premium was paid.",
        "Premium_Payment_Mode": "Mode of premium payment (e.g., online, cheque).",
        "Premium_Payment_Status": "Status of premium payment (e.g., paid, overdue).",
        "Premium_Receipt_Received": "Indicates whether the premium receipt was received (Yes/No).",
        "Premium_Receipt_Date": "Date when the premium receipt was received.",
        "Auto_Debit_Failure_Reason": "Reason for auto-debit failure.",
        "Premium_Notice_Sent_Date": "Date when the premium notice was sent.",
        "Premium_Notice_Received": "Indicates whether the premium notice was received (Yes/No).",
        "Agent_ID": "Unique identifier for the agent.",
        "Agent_Name": "Name of the agent.",
        "Agent_Contact_Number": "Contact number of the agent.",
        "Agent_Email": "Email address of the agent.",
        "Agent_Branch": "Branch where the agent is located.",
        "Agent_Commission": "Commission earned by the agent.",
        "Agent_Misconduct_Reported": "Indicates whether misconduct by the agent was reported (Yes/No).",
        "Agent_Misconduct_Details": "Details of the agent's misconduct.",
        "Agent_Complaint_Resolution_Status": "Status of the resolution of complaints against the agent.",
        "Customer_Service_ID": "Unique identifier for customer service interaction.",
        "Customer_Service_Representative_Name": "Name of the customer service representative.",
        "Customer_Service_Contact_Number": "Contact number of the customer service representative.",
        "Customer_Service_Email": "Email address of the customer service representative.",
        "Customer_Service_Response_Time": "Time taken to respond to the customer query.",
        "Customer_Service_Feedback_Rating": "Rating provided by the customer for the service.",
        "Customer_Service_Feedback_Comments": "Comments provided by the customer.",
        "Website_Login_ID": "Login ID for the policyholder on the website.",
        "Website_Password": "Password for the policyholder's website account.",
        "Website_Complaint_Submission_Date": "Date when a complaint was submitted via the website.",
        "Website_Complaint_Status": "Status of the website complaint.",
        "Website_User_Experience_Rating": "Rating provided by the user for the website experience.",
        "Website_User_Feedback": "Feedback provided by the user about the website.",
        "Social_Media_Complaint_Submitted": "Indicates whether a complaint was submitted via social media (Yes/No).",
        "Social_Media_Platform_Name": "Name of the social media platform where the complaint was submitted.",
        "Social_Media_Complaint_Status": "Status of the social media complaint.",
        "Social_Media_Response_Time": "Time taken to respond to the social media complaint."
    }

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_prompt(question):
        """
        Generate a prompt for the LLM to create an SQL query based on the user's question and the global CALLER_NUMBER.
        
        Args:
            question (str): User's question/query about the data
            
        Returns:
            str: Formatted prompt for the LLM
        """
        # Convert the fields dictionary to a formatted string
        fields_description = "\n".join([f"- {field}: {desc}" for field, desc in master_table_fields.items()])
        
        prompt = f"""
        **Objective:**
        You are provided with a relational table and field descriptions.
        use the primary key {CALLER_NUMBER} which is a Phone_Nember while constructing the query.
        **Table Information: `Insurance`**
        The table contains the following fields and descriptions:
        {fields_description}

        **User Question:**
        {question}

        **Instructions:**
        1. Analyze the user's question and identify the relevant fields and filters and if required make them case insensitive.
        2. Ensure that the field names in the query exactly match the field names in the table (case-sensitive).lower case eg: 'pending' should be matched with 'Pending',similarly 'rejected' with 'Rejected'.
        3. If the user provides values for filtering (e.g., policy numbers, statuses), ensure the query handles case insensitivity for these values.
        4. Construct an SQL query to fetch the requested information based on the user's question. ensure that you don't include all the fields unless asked for.
        5. Ensure the query is syntactically correct and efficient.
        6. Always use the table name `Insurance`.
        7. here inside columns values might case sensitive in sql query u provide all possible cases of case sesnitive values eg: 'pending' is there but inside table that value may me 'Pending' so u need to provide all possible cases of values. so use LOWER()
        **Example SQL Query:**
        ```sql
        SELECT <fields> 
        FROM Insurance 
        WHERE Phone_Number={CALLER_NUMBER};
        ```

        **Your Task:**
        Generate the SQL query for the user's question.
        """
        return prompt

def query_llm(prompt):
        """
        Query the LLM and return the SQL query response.
        
        Args:
            prompt (str): Formatted prompt for the LLM
            
        Returns:
            str: SQL query generated by the LLM
        """
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate SQL queries based on the user's question."},
                {"role": "user", "content": prompt}
            ]
        )
        # Clean the SQL query before returning
        # return await clean_sql_query(response.choices[0].message.content.strip())
        return clean_sql_query(response.choices[0].message.content.strip())

def clean_sql_query(sql_query):
        """
        Clean the SQL query by removing Markdown code block syntax and extra spaces.
        
        Args:
            sql_query (str): Raw SQL query from LLM
            
        Returns:
            str: Cleaned SQL query
        """
        # Remove ```sql and ```
        cleaned_query = re.sub(r'```sql|```', '', sql_query).strip()
        # Remove extra spaces and newlines
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
        return cleaned_query

def execute_sql_query(query):
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="gbr123",
            database="lendingkart_db"
        )
        
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Concatenating results meaningfully
        concatenated_result = " | ".join([" | ".join(map(str, row)) for row in results])
        
        return concatenated_result
    
    except mysql.connector.Error as e:
        return f"Error: {str(e)}"
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_insurance_details(phone_number):
    """Get insurance details for a given phone number."""
    query = """
    SELECT 
        Policyholder_ID, Name, Address, City, State, Pincode, 
        Phone_Number, Email, Date_of_Birth, Gender,
        Bank_Name, Nominee_Name, Nominee_Relationship, Nominee_Contact_Number,
        Policy_ID, Policy_Type, Policy_Start_Date, Policy_Maturity_Date,
        Premium_Amount, Premium_Payment_Frequency, Policy_Status,
        Sum_Assured, Bonus_Amount, Surrender_Value, Loan_Against_Policy,
        Policy_Documents_Received, Policy_Documents_Received_Date,
        Claim_ID, Claim_Type, Claim_Amount, Claim_Submission_Date,
        Claim_Status, Claim_Rejection_Reason
    FROM Insurance_Details 
    WHERE Phone_Number = :phone_number
    """
    try:
        result = execute_query(query, {"phone_number": phone_number})
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error getting insurance details: {str(e)}")
        return None

def get_policy_details(phone_number):
    """Get policy details for a given phone number."""
    query = """
    SELECT 
        Policy_ID, Policy_Type, Policy_Start_Date, Policy_Maturity_Date,
        Premium_Amount, Premium_Payment_Frequency, Policy_Status,
        Sum_Assured, Bonus_Amount, Surrender_Value, Loan_Against_Policy,
        Policy_Documents_Received, Policy_Documents_Received_Date
    FROM Insurance_Details 
    WHERE Phone_Number = :phone_number
    """
    result = execute_query(query, {"phone_number": phone_number})
    return result[0] if result and isinstance(result, list) and len(result) > 0 else None

def get_claim_details(phone_number):
    """Get claim details for a given phone number."""
    query = """
    SELECT 
        Claim_ID, Claim_Type, Claim_Amount, Claim_Submission_Date,
        Claim_Status, Claim_Rejection_Reason
    FROM Insurance_Details 
    WHERE Phone_Number = :phone_number
    """
    result = execute_query(query, {"phone_number": phone_number})
    return result[0] if result and isinstance(result, list) and len(result) > 0 else None

def get_policyholder_details(phone_number):
    """Get policyholder details for a given phone number."""
    query = """
    SELECT 
        Policyholder_ID, Name, Address, City, State, Pincode,
        Phone_Number, Email, Date_of_Birth, Gender
    FROM Insurance_Details 
    WHERE Phone_Number = :phone_number
    """
    result = execute_query(query, {"phone_number": phone_number})
    return result[0] if result and isinstance(result, list) and len(result) > 0 else None

def get_nominee_details(phone_number):
    """Get nominee and bank details for a given phone number."""
    query = """
    SELECT 
        Bank_Name, Nominee_Name, Nominee_Relationship, Nominee_Contact_Number
    FROM Insurance_Details 
    WHERE Phone_Number = :phone_number
    """
    result = execute_query(query, {"phone_number": phone_number})
    return result[0] if result and isinstance(result, list) and len(result) > 0 else None

def update_insurance_details(phone_number, update_data):
    """Update insurance details for a given phone number."""
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
        UPDATE Insurance_Details 
        SET {', '.join(set_clauses)}
        WHERE Phone_Number = :phone_number
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error updating insurance details: {str(e)}")
        return False

def insert_insurance_details(insurance_data):
    """Insert new insurance details."""
    try:
        # Build the INSERT query dynamically
        columns = []
        placeholders = []
        params = {}
        
        for key, value in insurance_data.items():
            if value is not None:  # Only insert non-None values
                columns.append(key)
                placeholders.append(f":{key}")
                params[key] = value
        
        if not columns:
            logger.warning("No valid fields to insert")
            return False
            
        query = f"""
        INSERT INTO Insurance_Details 
        ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error inserting insurance details: {str(e)}")
        return False

def delete_insurance_details(phone_number):
    """Delete insurance details for a given phone number."""
    try:
        query = """
        DELETE FROM Insurance_Details 
        WHERE Phone_Number = :phone_number
        """
        execute_query(query, {"phone_number": phone_number})
        return True
    except Exception as e:
        logger.error(f"Error deleting insurance details: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Example phone number
    phone = "+19787319274"
    
    # Get details
    details = get_insurance_details(phone)
    print("Current details:", details)
    
    # Update example
    update_data = {
        "Policy_Status": "Active",
        "Premium_Amount": 5000.00
    }
    if update_insurance_details(phone, update_data):
        print("Update successful")
    
    # Get updated details
    updated_details = get_insurance_details(phone)
    print("Updated details:", updated_details)