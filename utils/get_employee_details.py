import mysql.connector
from mysql.connector import Error

def get_emp_details(phone_number):
    # Database connection parameters
    db_config = {
        'host': 'localhost',  # Change if your MySQL server is not localhost
        'user': 'twilio_user',  # Update with your MySQL username
        'password': 'your_password',  # Update with your MySQL password
        'database': 'lendingkart_db',  # Your database name
        'charset': "utf8mb4",
        'auth_plugin': 'mysql_native_password' 
    }
    target=""
    result = ""

    try:
        # Establishing the connection
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            # SQL query to fetch the actionplan by phone number
            select_query = """
            SELECT * FROM employees_table WHERE phone = %s;
            """
            cursor.execute(select_query, (phone_number,))

            # Fetch the record
            record = cursor.fetchone()

            # Check if a record was found
            if record:
                print(record)
                data = f"The name is '{record[0]}' with phone_number '{record[1]}' having an email '{record[2]}' whose manager  phone no is '{record[3]}' with the managers email as '{record[4]}'. The group manager mail is '{record[5]}' with date as '{record[6]}'. The action plan is  '{record[7]}' with result explanation as '{record[8]}' and the acheived result is '{record[9]}'. The meeting time is '{record[10]}' with a meeting duration of '{record[11]}' minutes. The summary is '{record[12]}'"
                
                # target = record[0]
            else:
                print(f"No employee found with the phone number: {phone_number}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return data 

# # Example usage
# target = get_emp_details("+17043693803")
# print(target)