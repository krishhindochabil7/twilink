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

def get_employee_details(phone_number):
    """Get employee details for a given phone number."""
    query = """
    SELECT 
        Employee_ID, Name, Department, Position,
        Email, Phone_Number, Hire_Date, Salary,
        Manager_ID, Office_Location
    FROM Employee_Details 
    WHERE Phone_Number = :phone_number
    """
    try:
        result = execute_query(query, {"phone_number": phone_number})
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error getting employee details: {str(e)}")
        return None

def update_employee_details(phone_number, update_data):
    """Update employee details for a given phone number."""
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
        UPDATE Employee_Details 
        SET {', '.join(set_clauses)}
        WHERE Phone_Number = :phone_number
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error updating employee details: {str(e)}")
        return False

def insert_employee_details(employee_data):
    """Insert new employee details."""
    try:
        # Build the INSERT query dynamically
        columns = []
        placeholders = []
        params = {}
        
        for key, value in employee_data.items():
            if value is not None:  # Only insert non-None values
                columns.append(key)
                placeholders.append(f":{key}")
                params[key] = value
        
        if not columns:
            logger.warning("No valid fields to insert")
            return False
            
        query = f"""
        INSERT INTO Employee_Details 
        ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error inserting employee details: {str(e)}")
        return False

def delete_employee_details(phone_number):
    """Delete employee details for a given phone number."""
    try:
        query = """
        DELETE FROM Employee_Details 
        WHERE Phone_Number = :phone_number
        """
        execute_query(query, {"phone_number": phone_number})
        return True
    except Exception as e:
        logger.error(f"Error deleting employee details: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Example phone number
    phone = "+19787319274"
    
    # Get details
    details = get_employee_details(phone)
    print("Current details:", details)
    
    # Update example
    update_data = {
        "Position": "Senior Developer",
        "Salary": 120000.00
    }
    if update_employee_details(phone, update_data):
        print("Update successful")
    
    # Get updated details
    updated_details = get_employee_details(phone)
    print("Updated details:", updated_details)