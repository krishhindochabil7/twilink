import json
from utils.mysql_email_send import process_employee_performance
from utils.insurance_details import get_insurance_details
# from utils.mysql_insurance_query import get_insurance_details
from utils.lendingkart_dummy import get_target_status,incentive_details,penalty_details,collection_improvements,top_defaulters
from utils.get_employee_details import get_employee_details

def generate_horoscope_people(sign):
     return f"you are going win 1 million lottery tomorrow {sign}"
                    
def  get_my_report_mysql(question):
        return f"you solid health paramters, he happy {question}"
def  get_weather_bilvantis(location):
         return f"temprature is 35 celcius {location}"
def send_email_external(to, subject, body):
     return f"email snet successfully {to}"

def send_status_to_managers():
    phone_number="+919963029130"
    # Simulating actual function logic
    process_employee_performance(phone_number)
    return f"Status sent to manager with phone number {phone_number}"

def execute_function(function_details,call_number):
    function_name = function_details["function_name"]
    arguments = function_details["arguments"]
    # a = ""

    if function_name == "incentive_details" or function_name == "get_emp_details" or function_name == 'get_insurance_details':
 
            if function_name in globals() and callable(globals()[function_name]):
                return globals()[function_name](call_number)
            else:
                raise ValueError(f"Function {function_name} not found")
        
    elif  function_name != "incentive_details" and function_name != "get_emp_details":
        if function_name in globals() and callable(globals()[function_name]):
            return globals()[function_name](**arguments)
        else:
            raise ValueError(f"Function {function_name} not found")
         

def create_function_call_output(callid, message):
    response = {
        "type": "conversation.item.create",
        "item": {
            "type": "function_call_output",
            "call_id": callid,  # You can generate unique IDs dynamically
            "output": json.dumps({"conversation": message})
        }
    }
    return response

# def create_function_call_output_json(callid, message: dict):
#     response = {
#         "type": "conversation.item.create",
#         "item": {
#             "type": "function_call_output",
#             "call_id": callid,  # You can generate unique IDs dynamically
#             "output": json.dumps({"conversation": message})
#         }
#     }
#     return response

def extract_function_call(event_data):
    try:
        # Parse the JSON if it's in string format
        if isinstance(event_data, str):
            event_data = json.loads(event_data)
        
        # Check if the event type is 'response.done'
        if event_data.get("type") == "response.done":
            response = event_data.get("response", {})
            output_items = response.get("output", [])
            
            for item in output_items:
                # Check if the item matches the required conditions
                if (
                    item.get("object") == "realtime.item" and 
                    item.get("type") == "function_call"
                ):
                    function_name = item.get("name")
                    call_id = item.get("call_id")
                    arguments = json.loads(item.get("arguments", "{}"))
                    
                    return {
                        "function_name": function_name,
                        "arguments": arguments,
                        "call_id": call_id
                    }
        
        return None  # Return None if conditions are not met
    except Exception as e:
        print(f"Error parsing event data: {e}")
        return None

# Example usage
#event_data = {"type": "response.done", "response": {"output": [{"object": "realtime.item", "type": "function_call", "name": "send_email_external", "call_id": "call_NqvXI7HV6uaKxE8b", "arguments": "{\"to\":\"baskarao.g@gmail.com\",\"subject\":\"US Open\",\"body\":\"Describe how many tickets are available, what are the various types of tickets and things like that.\"}"}]}}
#event_data1={'type': 'response.done', 'event_id': 'event_BHmJdo2cWWbCrsMi2J1si', 'response': {'object': 'realtime.response', 'id': 'resp_BHmJcU4JJ72RsMn0JoV6c', 'status': 'completed', 'status_details': None, 'output': [{'id': 'item_BHmJcWFTt4WM6Z6zOptL9', 'object': 'realtime.item', 'type': 'function_call', 'status': 'completed', 'name': 'generate_horoscope_people', 'call_id': 'call_nzEeZ7xOyJ79yHoR', 'arguments': '{"sign":"Leo"}'}], 'conversation_id': 'conv_BHmJKUFDgK1MvDPxFTXey', 'modalities': ['audio', 'text'], 'voice': 'coral', 'output_audio_format': 'g711_ulaw', 'temperature': 0.8, 'max_output_tokens': 'inf', 'usage': {'total_tokens': 753, 'input_tokens': 735, 'output_tokens': 18, 'input_token_details': {'text_tokens': 514, 'audio_tokens': 221, 'cached_tokens': 640, 'cached_tokens_details': {'text_tokens': 512, 'audio_tokens': 128}}, 'output_token_details': {'text_tokens': 18, 'audio_tokens': 0}}, 'metadata': None}}
#event_data3 ={'type': 'response.done', 'event_id': 'event_BHm2fqLf7JERQten8OEUT', 'response': {'object': 'realtime.response', 'id': 'resp_BHm2eJJMtuJ7fPOOqMuG7', 'status': 'completed', 'status_details': None, 'output': [{'id': 'item_BHm2e3j6QEuySLlZFKBDp', 'object': 'realtime.item', 'type': 'function_call', 'status': 'completed', 'name': 'get_weather_bilvantis', 'call_id': 'call_Tpn9HLj1GjGRtuKX', 'arguments': '{"location":"New Delhi"}'}], 'conversation_id': 'conv_BHm2bdUV1o6g42EKNcnx0', 'modalities': ['audio', 'text'], 'voice': 'coral', 'output_audio_format': 'g711_ulaw', 'temperature': 0.8, 'max_output_tokens': 'inf', 'usage': {'total_tokens': 407, 'input_tokens': 387, 'output_tokens': 20, 'input_token_details': {'text_tokens': 363, 'audio_tokens': 24, 'cached_tokens': 320, 'cached_tokens_details': {'text_tokens': 320, 'audio_tokens': 0}}, 'output_token_details': {'text_tokens': 20, 'audio_tokens': 0}}, 'metadata': None}}
#event_data2 ={'type': 'response.function_call_arguments.done', 'event_id': 'event_BHm2foz9suuMPOIyuu1PS', 'response_id': 'resp_BHm2eJJMtuJ7fPOOqMuG7', 'item_id': 'item_BHm2e3j6QEuySLlZFKBDp', 'output_index': 0, 'call_id': 'call_Tpn9HLj1GjGRtuKX', 'name': 'get_weather_bilvantis', 'arguments': '{"location":"New Delhi"}'}
#result = extract_function_call(event_data2)
#print(result)
