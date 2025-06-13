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

def get_targets_and_results(phone_number):
    """Get action plan and achieved result for a given phone number from employees table."""
    query = """
    SELECT actionplan, acheived_result 
    FROM employees_table 
    WHERE phone = :phone_number
    """
    try:
        result = execute_query(query, {"phone_number": phone_number})
        if result and isinstance(result, list) and len(result) > 0:
            target = result[0][0] if result[0][0] is not None else "No target information available"
            result_value = result[0][1] if result[0][1] is not None else "No result information available"
            return target, result_value
        return "No target information available", "No result information available"
    except Exception as e:
        logger.error(f"Error getting targets and results: {str(e)}")
        return "No target information available", "No result information available"

def get_target_result(phone_number):
    """Get target result for a given phone number."""
    query = """
    SELECT 
        Target_ID, Phone_Number, Target_Type,
        Target_Amount, Achieved_Amount, Status,
        Start_Date, End_Date, Notes
    FROM Target_Results 
    WHERE Phone_Number = :phone_number
    """
    try:
        result = execute_query(query, {"phone_number": phone_number})
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error getting target result: {str(e)}")
        return None

def update_target_result(phone_number, update_data):
    """Update target result for a given phone number."""
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
        UPDATE Target_Results 
        SET {', '.join(set_clauses)}
        WHERE Phone_Number = :phone_number
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error updating target result: {str(e)}")
        return False

def insert_target_result(target_data):
    """Insert new target result."""
    try:
        # Build the INSERT query dynamically
        columns = []
        placeholders = []
        params = {}
        
        for key, value in target_data.items():
            if value is not None:  # Only insert non-None values
                columns.append(key)
                placeholders.append(f":{key}")
                params[key] = value
        
        if not columns:
            logger.warning("No valid fields to insert")
            return False
            
        query = f"""
        INSERT INTO Target_Results 
        ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error inserting target result: {str(e)}")
        return False

def delete_target_result(phone_number):
    """Delete target result for a given phone number."""
    try:
        query = """
        DELETE FROM Target_Results 
        WHERE Phone_Number = :phone_number
        """
        execute_query(query, {"phone_number": phone_number})
        return True
    except Exception as e:
        logger.error(f"Error deleting target result: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Example phone number
    phone = "+19787319274"
    
    # Get target result
    result = get_target_result(phone)
    print("Current target result:", result)
    
    # Update example
    update_data = {
        "Achieved_Amount": 50000.00,
        "Status": "Completed"
    }
    if update_target_result(phone, update_data):
        print("Update successful")
    
    # Get updated result
    updated_result = get_target_result(phone)
    print("Updated target result:", updated_result)