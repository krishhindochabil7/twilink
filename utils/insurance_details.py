import mysql.connector
from mysql.connector import Error

def get_insurance_details(phone_number):
    # Database connection parameters
    db_config = {
        'host': 'localhost',  # Change if your MySQL server is not localhost
        'user': 'twilio_user',  # Update with your MySQL username
        'password': 'your_password',  # Update with your MySQL password
        'database': 'lendingkart_db',  # Your database name
        'charset': "utf8mb4",
        'auth_plugin': 'mysql_native_password' 
    }
    data = ""

    try:
        # Establishing the connection
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to fetch the actionplan by phone number
            select_query = """
            SELECT * FROM Insurance WHERE Phone_Number = %s;
            """
            cursor.execute(select_query, (phone_number,))

            # Fetch the record
            record = cursor.fetchone()

            # Check if a record was found
            if record:
                data = {
                    "Policyholder ID":record[0],
                    "Name":record[1],
                    "Address":record[2],
                    "City":record[3],
                    "State":record[4],
                    "Pincode":record[5],
                    "Phone Number":record[6],
                    "Email":record[7],
                    "Date of Birth":record[8],
                    "Gender":record[9],
                    "PAN Number":record[10],
                    "Aadhaar Number":record[11],
                    "Bank Account Number":record[12],
                    "Bank Name":record[13],
                    "IFSC Code":record[14],
                    "Nominee Name":record[15],
                    "Nominee Relationship":record[16],
                    "Nominee Contact Number":record[17],
                    "Policy ID":record[18],
                    "Policy Type":record[19],
                    "Policy Start Date":record[20],
                    "Policy Maturity Date":record[21],
                    "Premium Amount":record[22],
                    "Premium Payment Frequency":record[23],
                    "Policy Status":record[24],
                    "Sum Assured":record[25],
                    "Bonus Amount":record[26],
                    "Surrender Value":record[27],
                    "Loan Against Policy":record[28],
                    "Policy Documents Received":record[29],
                    "Policy Documents Received Date":record[30],
                    "Claim ID":record[31],
                    "Claim Type":record[32],
                    "Claim Amount":record[33],
                    "Claim Submission Date":record[34],
                    "Claim Status":record[35],
                    "Claim Rejection Reason":record[36],
                }
                # data = f"The Policyholder_ID is '{record[0]}' with Name '{record[1]}' having an Address '{record[2]}' living in the city '{record[3]}' . The state is  '{record[4]}'. The Pincode is '{record[5]}'. The Phone Number of the policy holder is '{record[6]}'. The Email is  '{record[7]}'. The date of birth as '{record[8]}'.Gender '{record[9]}', The PAN Number is '{record[10]}' , The Aadhaar Number is '{record[11]}', The Bank Account Number is '{record[12]}', The Bank Name is '{record[13]}', The IFSC Code is '{record[14]}',The  Nominee Name is  '{record[15]}', The Nominee Relationship is '{record[16]}',The Nominee Contact Number is '{record[17]}',The  Policy ID is '{record[18]}',The Policy Type is '{record[19]}', The Policy Start Date is '{record[20]}',The Policy Maturity Date is '{record[21]}', The Premium Amount is '{record[22]}', The Premium Payment Frequency is '{record[23]}', The Policy Status is '{record[24]}', The  Sum Assured is '{record[25]}', The Bonus Amount is '{record[26]}',The Surrender Value is '{record[27]}', The Loan Against Policy is '{record[28]}', The Policy Documents Received is '{record[29]}', The Policy Documents Received Date is '{record[30]}', The Claim ID is '{record[31]}', The Claim Type is '{record[32]}', The Claim Amount is '{record[33]}', The Claim Submission Date is '{record[34]}',The Claim Status is '{record[35]}', The Claim Rejection Reason is '{record[36]}'"

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

# Example usage
result = get_insurance_details("+19787319274")
print(result)