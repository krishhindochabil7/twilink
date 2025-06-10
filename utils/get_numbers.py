import mysql.connector
from mysql.connector import Error

def get_all_phone_numbers():
    # Database connection parameters
    db_config = {
        'host': 'localhost', 
        'user': 'twilio_user', 
        'password': 'your_password', 
        'database': 'lendingkart_db', 
        'charset': "utf8mb4",
        'auth_plugin': 'mysql_native_password' 
    }
    results = []
    phone_numbers = []

    try:
        # Establishing the connection
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to fetch the actionplan by phone number
            select_query = """
            SELECT * FROM dummy_number
            """
            cursor.execute(select_query)

            # Fetch the record

            results = cursor.fetchall()

            # Check if a record was found
            if results:
                # print(results)
                for i in results:
                    phone_numbers.append(i[0])
            else:
                print(f"No employee found with the phone number")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return phone_numbers 

def get_total_calls_for_number(phone):
    db_config = {
        'host': 'localhost', 
        'user': 'twilio_user', 
        'password': 'your_password', 
        'database': 'lendingkart_db', 
        'charset': "utf8mb4",
        'auth_plugin': 'mysql_native_password' 
    }

    total_calls = ""

    try:
        # Establishing the connection
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to fetch the actionplan by phone number
            select_query = """
            SELECT number_of_calls FROM Call_Summary where phone_number = %s
            """
            cursor.execute(select_query, (phone,))

            # Fetch the record

            results = cursor.fetchone()

            # Check if a record was found
            if results:
                total_calls = results[0]
            else:
                print(f"No employee found with the phone number")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return total_calls 


def update_records(phone,duration,total_calls,complete_transcription):
    db_config = {
        'host': 'localhost', 
        'user': 'twilio_user', 
        'password': 'your_password', 
        'database': 'lendingkart_db', 
        'charset': "utf8mb4",
        'auth_plugin': 'mysql_native_password' 
    }


    try:
    # Establishing the connection
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to update the call summary
            update_query = """
            UPDATE Call_Summary
            SET call_duration = %s,
                number_of_calls = %s,
                complete_call_transcription = %s
            WHERE phone_number = %s
            """

            # Execute the update query
            cursor.execute(update_query, (duration, total_calls, complete_transcription, phone))

            connection.commit()
            print("Update successful")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")



# ret = get_all_phone_numbers()
# print(ret)