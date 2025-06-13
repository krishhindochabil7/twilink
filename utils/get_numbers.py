import os
import sys
import logging
from datetime import datetime
from utils.db_config import execute_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_phone_numbers():
    """Get all phone numbers from the database."""
    query = """
    SELECT DISTINCT Phone_Number 
    FROM Insurance_Details 
    WHERE Phone_Number IS NOT NULL
    """
    try:
        result = execute_query(query)
        return [row[0] for row in result] if result else []
    except Exception as e:
        logger.error(f"Error getting phone numbers: {str(e)}")
        return []

def get_phone_numbers_by_status(status):
    """Get phone numbers for policies with a specific status."""
    query = """
    SELECT DISTINCT Phone_Number 
    FROM Insurance_Details 
    WHERE Policy_Status = :status 
    AND Phone_Number IS NOT NULL
    """
    try:
        result = execute_query(query, {"status": status})
        return [row[0] for row in result] if result else []
    except Exception as e:
        logger.error(f"Error getting phone numbers by status: {str(e)}")
        return []

def get_phone_numbers_by_policy_type(policy_type):
    """Get phone numbers for a specific policy type."""
    query = """
    SELECT DISTINCT Phone_Number 
    FROM Insurance_Details 
    WHERE Policy_Type = :policy_type 
    AND Phone_Number IS NOT NULL
    """
    try:
        result = execute_query(query, {"policy_type": policy_type})
        return [row[0] for row in result] if result else []
    except Exception as e:
        logger.error(f"Error getting phone numbers by policy type: {str(e)}")
        return []

def get_phone_numbers_by_premium_range(min_premium, max_premium):
    """Get phone numbers for policies within a premium range."""
    query = """
    SELECT DISTINCT Phone_Number 
    FROM Insurance_Details 
    WHERE Premium_Amount BETWEEN :min_premium AND :max_premium 
    AND Phone_Number IS NOT NULL
    """
    try:
        result = execute_query(query, {
            "min_premium": min_premium,
            "max_premium": max_premium
        })
        return [row[0] for row in result] if result else []
    except Exception as e:
        logger.error(f"Error getting phone numbers by premium range: {str(e)}")
        return []

def get_total_calls_for_number(phone_number):
    """Get total calls made to a specific number."""
    query = """
    SELECT Total_Calls 
    FROM Call_Records 
    WHERE Phone_Number = :phone_number
    """
    try:
        result = execute_query(query, {"phone_number": phone_number})
        return result[0][0] if result and isinstance(result, list) and len(result) > 0 else 0
    except Exception as e:
        logger.error(f"Error getting total calls for number: {str(e)}")
        return 0

def update_records(phone_number, duration, total_calls, transcription):
    """Update call records for a phone number."""
    query = """
    UPDATE Call_Records 
    SET Duration = :duration,
        Total_Calls = :total_calls,
        Transcription = :transcription
    WHERE Phone_Number = :phone_number
    """
    params = {
        "phone_number": phone_number,
        "duration": duration,
        "total_calls": total_calls,
        "transcription": transcription
    }
    try:
        execute_query(query, params)
        return True
    except Exception as e:
        logger.error(f"Error updating call records: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Get all phone numbers
    all_numbers = get_phone_numbers()
    print("All phone numbers:", all_numbers)
    
    # Get numbers by status
    active_numbers = get_phone_numbers_by_status("Active")
    print("Active policy numbers:", active_numbers)
    
    # Get numbers by policy type
    life_numbers = get_phone_numbers_by_policy_type("Life")
    print("Life policy numbers:", life_numbers)
    
    # Get numbers by premium range
    premium_numbers = get_phone_numbers_by_premium_range(1000, 5000)
    print("Numbers in premium range:", premium_numbers)