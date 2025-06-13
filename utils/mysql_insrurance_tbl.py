from utils.db_config import execute_query

def create_insurance_table():
    """Create the insurance details table if it doesn't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS Insurance_Details (
        Policyholder_ID VARCHAR(50) PRIMARY KEY,
        Name VARCHAR(100),
        Address TEXT,
        City VARCHAR(50),
        State VARCHAR(50),
        Pincode VARCHAR(10),
        Phone_Number VARCHAR(15),
        Email VARCHAR(100),
        Date_of_Birth DATE,
        Gender VARCHAR(10),
        Bank_Name VARCHAR(100),
        Nominee_Name VARCHAR(100),
        Nominee_Relationship VARCHAR(50),
        Nominee_Contact_Number VARCHAR(15),
        Policy_ID VARCHAR(50),
        Policy_Type VARCHAR(50),
        Policy_Start_Date DATE,
        Policy_Maturity_Date DATE,
        Premium_Amount DECIMAL(10,2),
        Premium_Payment_Frequency VARCHAR(20),
        Policy_Status VARCHAR(20),
        Sum_Assured DECIMAL(15,2),
        Bonus_Amount DECIMAL(10,2),
        Surrender_Value DECIMAL(10,2),
        Loan_Against_Policy DECIMAL(10,2),
        Policy_Documents_Received BOOLEAN,
        Policy_Documents_Received_Date DATE,
        Claim_ID VARCHAR(50),
        Claim_Type VARCHAR(50),
        Claim_Amount DECIMAL(10,2),
        Claim_Submission_Date DATE,
        Claim_Status VARCHAR(20),
        Claim_Rejection_Reason TEXT
    )
    """
    return execute_query(query)

def insert_sample_data():
    """Insert sample insurance data."""
    query = """
    INSERT INTO Insurance_Details (
        Policyholder_ID, Name, Phone_Number, Policy_ID, Policy_Type,
        Premium_Amount, Policy_Status, Sum_Assured
    ) VALUES (
        :policyholder_id, :name, :phone_number, :policy_id, :policy_type,
        :premium_amount, :policy_status, :sum_assured
    )
    """
    sample_data = {
        "policyholder_id": "PH001",
        "name": "John Doe",
        "phone_number": "+1234567890",
        "policy_id": "POL001",
        "policy_type": "Life Insurance",
        "premium_amount": 1000.00,
        "policy_status": "Active",
        "sum_assured": 100000.00
    }
    return execute_query(query, sample_data)

if __name__ == "__main__":
    create_insurance_table()
    insert_sample_data()
