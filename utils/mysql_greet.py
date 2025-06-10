import mysql.connector
from mysql.connector import Error

def fetch_explanation_by_phone(phone_number):
    # Database connection parameters
    db_config = {
        'host': 'localhost',  # Change if your MySQL server is not localhost
        'user': 'twilio_user',  # Update with your MySQL username
        'password': 'your_password',  # Update with your MySQL password
        'database': 'lendingkart_db',  # Your database name
        'charset': "utf8mb4",
        'auth_plugin': 'mysql_native_password' 
    }
    ret=""
    language = ""

    try:
        # Establishing the connection
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to fetch the actionplan by phone number
            select_query = """
            SELECT greet_message,language FROM Dummy WHERE number = %s;
            """
            cursor.execute(select_query, (phone_number,))

            # Fetch the record
            record = cursor.fetchone()

            # Check if a record was found
            if record:
                print(record)
                result_explanation = record[0]
                language = record[1]
                # print(f"Action Plan for phone number {phone_number}: {result_explanation}")
                ret=result_explanation
            else:
                print(f"No employee found with the phone number: {phone_number}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return ret ,language 

# # Example usage
# ret= fetch_explanation_by_phone("+17043693803")
# print(ret)