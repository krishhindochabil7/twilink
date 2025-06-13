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

def get_special_record(phone_number):
    """Get special record for a given phone number."""
    query = """
    SELECT 
        Record_ID, Phone_Number, Record_Type,
        Record_Details, Status, Created_Date,
        Updated_Date, Notes
    FROM Special_Records 
    WHERE Phone_Number = :phone_number
    """
    try:
        result = execute_query(query, {"phone_number": phone_number})
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error getting special record: {str(e)}")
        return None

def update_special_record(phone_number, update_data):
    """Update special record for a given phone number."""
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
        UPDATE Special_Records 
        SET {', '.join(set_clauses)}
        WHERE Phone_Number = :phone_number
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error updating special record: {str(e)}")
        return False

def insert_special_record(record_data):
    """Insert new special record."""
    try:
        # Build the INSERT query dynamically
        columns = []
        placeholders = []
        params = {}
        
        for key, value in record_data.items():
            if value is not None:  # Only insert non-None values
                columns.append(key)
                placeholders.append(f":{key}")
                params[key] = value
        
        if not columns:
            logger.warning("No valid fields to insert")
            return False
            
        query = f"""
        INSERT INTO Special_Records 
        ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error inserting special record: {str(e)}")
        return False

def delete_special_record(phone_number):
    """Delete special record for a given phone number."""
    try:
        query = """
        DELETE FROM Special_Records 
        WHERE Phone_Number = :phone_number
        """
        execute_query(query, {"phone_number": phone_number})
        return True
    except Exception as e:
        logger.error(f"Error deleting special record: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Example phone number
    phone = "+19787319274"
    
    # Get special record
    record = get_special_record(phone)
    print("Current special record:", record)
    
    # Update example
    update_data = {
        "Status": "Processed",
        "Notes": "Updated on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if update_special_record(phone, update_data):
        print("Update successful")
    
    # Get updated record
    updated_record = get_special_record(phone)
    print("Updated special record:", updated_record)