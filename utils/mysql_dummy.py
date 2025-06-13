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

def get_dummy_data(phone_number):
    """Get dummy data for a given phone number."""
    query = """
    SELECT 
        ID, Phone_Number, Name, Email,
        Status, Created_Date, Updated_Date
    FROM Dummy_Table 
    WHERE Phone_Number = :phone_number
    """
    try:
        result = execute_query(query, {"phone_number": phone_number})
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error getting dummy data: {str(e)}")
        return None

def update_dummy_data(phone_number, update_data):
    """Update dummy data for a given phone number."""
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
        UPDATE Dummy_Table 
        SET {', '.join(set_clauses)}
        WHERE Phone_Number = :phone_number
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error updating dummy data: {str(e)}")
        return False

def insert_dummy_data(data):
    """Insert new dummy data."""
    try:
        # Build the INSERT query dynamically
        columns = []
        placeholders = []
        params = {}
        
        for key, value in data.items():
            if value is not None:  # Only insert non-None values
                columns.append(key)
                placeholders.append(f":{key}")
                params[key] = value
        
        if not columns:
            logger.warning("No valid fields to insert")
            return False
            
        query = f"""
        INSERT INTO Dummy_Table 
        ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"Error inserting dummy data: {str(e)}")
        return False

def delete_dummy_data(phone_number):
    """Delete dummy data for a given phone number."""
    try:
        query = """
        DELETE FROM Dummy_Table 
        WHERE Phone_Number = :phone_number
        """
        execute_query(query, {"phone_number": phone_number})
        return True
    except Exception as e:
        logger.error(f"Error deleting dummy data: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Example phone number
    phone = "+19787319274"
    
    # Get dummy data
    data = get_dummy_data(phone)
    print("Current dummy data:", data)
    
    # Update example
    update_data = {
        "Status": "Active",
        "Updated_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if update_dummy_data(phone, update_data):
        print("Update successful")
    
    # Get updated data
    updated_data = get_dummy_data(phone)
    print("Updated dummy data:", updated_data)
