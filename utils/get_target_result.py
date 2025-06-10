import mysql.connector
from mysql.connector import Error

def get_targets_and_results(phone_number):
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
            SELECT actionplan,acheived_result FROM employees_table WHERE phone = %s;
            """
            cursor.execute(select_query, (phone_number,))

            # Fetch the record
            record = cursor.fetchone()

            # Check if a record was found
            if record:
                print(record)
                target = record[0]
                result = record[1]
            else:
                print(f"No employee found with the phone number: {phone_number}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return target,result 

# # Example usage
# target,result = fetch_explanation_by_phone("+17043693803")
# print(target,result)