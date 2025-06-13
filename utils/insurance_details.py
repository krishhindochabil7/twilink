from utils.db_config import execute_query

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
    result = execute_query(query, {"phone_number": phone_number})
    return result[0] if result and isinstance(result, list) and len(result) > 0 else None

# Example usage
if __name__ == "__main__":
    result = get_insurance_details("+19787319274")
    print(result)