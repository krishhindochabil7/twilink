from utils.db_config import execute_query

def fetch_explanation_by_phone(phone_number):
    """Fetch greeting message and language preference for a phone number."""
    query = """
    SELECT greet_message, language 
    FROM Dummy 
    WHERE number = :phone_number
    """
    result = execute_query(query, {"phone_number": phone_number})
    
    if result and isinstance(result, list) and len(result) > 0:
        greet_message = result[0]['greet_message']
        language = result[0]['language']
        if language == "English":
            greet_message = "Hello, I am the lendingkart AI. How may I help you?"
        elif language == "Spanish":
            greet_message = "Hola, soy la inteligencia artificial de Lendingkart. ¿En qué puedo ayudarte?"
        return greet_message,language
    return "Hello, I am the lendingkart AI. I am here to help you.", "English"

# # Example usage
# ret= fetch_explanation_by_phone("+17043693803")
# print(ret)