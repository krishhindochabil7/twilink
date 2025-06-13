import os
import json
import base64
import asyncio
import argparse
import re
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from dotenv import load_dotenv, find_dotenv,dotenv_values
from twilio.rest import Client
import uvicorn
import aiohttp
import audioop
import whisper
import numpy as np
from collections import deque
from utils.get_func_calls import extract_function_call,create_function_call_output,execute_function
from utils.get_numbers import get_phone_numbers,get_total_calls_for_number,update_records
from utils.mysql_greet import fetch_explanation_by_phone
from utils.get_target_result import get_targets_and_results
from utils.conversarion_insights import get_insights
from utils.send_email import send_email_1,get_recipents
from enum import Enum
from pydantic import BaseModel

load_dotenv(override=True)

call_queue = []
csid = ""
caller_number = None  # default global variable
call_number = None  # default global variable

class CallStatus(Enum):
    IDLE = 0
    IN_PROGRESS = 1
    COMPLETED = 2

current_call_status = CallStatus.IDLE

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PHONE_NUMBER_FROM = os.getenv('PHONE_NUMBER_FROM')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
raw_domain = os.getenv('DOMAIN', '')
DOMAIN = re.sub(r'(^\w+:|^)\/\/|\/+$', '', raw_domain)
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
HUMAN_AGENT_NUMBER = os.getenv('HUMAN_AGENT_NUMBER')
print("Twilio Account SID: ", TWILIO_ACCOUNT_SID)
print("Twilio Auth Token: ", TWILIO_AUTH_TOKEN)
print("Phone Number From: ", PHONE_NUMBER_FROM)
print("OpenAI API Key: ", OPENAI_API_KEY)
print("Sender Email: ", SENDER_EMAIL)
print("Sender Password: ", SENDER_PASSWORD)
print("HUMAN_AGENT_NUMBER: ", HUMAN_AGENT_NUMBER)
print("domain is : ",DOMAIN)


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
text=""" """

PORT = int(os.getenv('PORT', 5050))
SHOW_TIMING_MATH = False
SYSTEM_MESSAGE = (
""" 
    You are an AI assistant with strict limitations.
    You may only respond to queries that fall within the five defined categories. When responding, include only the subfields relevant to the specific request — unless the user asks for "all insurance details," in which case you return all groups under Insurance.

    1. Insurance Details
    Respond based on the specific type of detail requested:

        If user requests:
        "policy details" → return only:

            Policy ID, Policy Type, Policy Start Date, Policy Maturity Date, Premium Amount, Premium Payment Frequency, Policy Status, Sum Assured, Bonus Amount, Surrender Value, Loan Against Policy, Policy Documents Received, Policy Documents Received Date

        "claim details" → return only:

            Claim ID, Claim Type, Claim Amount, Claim Submission Date, Claim Status, Claim Rejection Reason

        "policyholder details" → return only:

            Policyholder ID, Name, Address, City, State, Pincode, Phone Number, Email, Date of Birth, Gender

        "nominee details" / "bank and nominee details" → return only:

            Bank Name (no IFSC or sensitive info), Nominee Name, Nominee Relationship, Nominee Contact Number

        If the user requests "insurance details" or "all insurance details" →
        Return all of the following:

            Policyholder Details

            Bank and Nominee Info

            Policy Information

            Claim Information
   
    2. Employee Details
    Respond only with what is asked:

        Performance Review: Date, Action Plan, Achieved Result, Result Explanation, Meeting Time, Meeting Duration, Summary

        Contact Info: Name, Phone, Email

        Manager Info: Manager Phone, Manager Email, Group Manager Email
    
    3. Horoscope of the Caller

    4. Current Weather Details of Bilvantis

    5. Incentive Details of the Caller

    Special Rules for Reading and Interpretation

    1. Amounts (Rupees):
    Read amounts with absolute accuracy, digit by digit.

        Example:

        3054906.2 → Three million fifty-four thousand nine hundred six rupees

        3190265.91 → Three million one hundred ninety thousand two hundred sixty-five and ninety-one rupees

    2.Dates:
    Read full dates in a descriptive format.

        Example:

        2025-02-26 → February twenty-sixth, two thousand twenty-five

    3.Policy IDs:
    Always read out every digit of policy IDs clearly.

        Example:

        147258369301 → One four seven two five eight three six nine three zero one

    Strict Limitations
    Do not share any sensitive information like Aadhar number, PAN, or IFSC code. If asked, respond:
    → "I am sorry, I am not in possession of these details."

    If a user asks anything outside of the five categories above, respond exactly with:
    → "I am sorry, this is out of my scope."

   """
)
VOICE = 'coral'

LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]

# Initialize Whisper model
# whisper_model = whisper.load_model("base")
transcriptions = []
audio_buffer = deque()

app = FastAPI()

if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and PHONE_NUMBER_FROM and OPENAI_API_KEY):
    raise ValueError('Missing Twilio and/or OpenAI environment variables. Please set them in the .env file.')

@app.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

class MobileNumberRequest(BaseModel):
    mobile_number : str

@app.post("/call-number/")
async def make_a_call(data:MobileNumberRequest):
    await make_call(data.mobile_number)

async def send_to_openai(audio_payload, openai_ws):
    """Send audio data to the OpenAI Realtime API."""
    try:
        audio_append = {
            "type": "input_audio_buffer.append",
            "audio": audio_payload
        }
        await openai_ws.send_json(audio_append)
    except Exception as e:
        print(f"Error sending audio to OpenAI: {e}")


async def send_functions_response(msg, openai_ws):
 try:
     print('Sending function result to model :', json.dumps(msg))
     await openai_ws.send_json(msg)
     await openai_ws.send_json({"type": "response.create"})
 except Exception as e:
        print(f"Error sending send_functions_response to OpenAI: {e}")

# async def process_transcription(audio_payload):
#     """Process audio for live transcription using Whisper."""
#     global transcription_text
#     try:
#         combined_bytes = b""
#         for i in audio_payload:
#             audio = base64.b64decode(i)
#             audio = audioop.ulaw2lin(audio, 2)
#             audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
#             combined_bytes += audio

#         audio_np = np.frombuffer(combined_bytes, dtype=np.int16)
#         audio_np = audio_np.astype(np.float32) / 32768.0 

#         result = whisper_model.transcribe(audio_np, language='en')
#         t_eng = result["text"].strip()
#         # transcriptions.append(transcription_text)
#     except Exception as e:
#         print(f"Error processing transcription: {e}")

async def print_transcriptions():
    """Print all transcriptions collected so far."""
    for i, text in enumerate(transcriptions):
        print(f"{i}. {text}")

async def handler_buffer_wait():
    """Process audio buffer periodically for transcription."""
    global audio_buffer
    while True:
        if audio_buffer:
            await asyncio.sleep(10)
            payloads_to_process = list(audio_buffer)
            audio_buffer.clear()
            # await process_transcription(payloads_to_process)
            print("=================================================================")
            # await print_transcriptions()
            print("=================================================================")
        else:
            await asyncio.sleep(1)

def escalate_call(call_sid):
    client.calls(call_sid).update(
        twiml=f"<Response><Say>Transferring you to a human agent. Please hold.</Say><Dial><Number>{HUMAN_AGENT_NUMBER}</Number></Dial></Response>"
    )

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    openai_url = 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01'
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(openai_url, headers=headers) as openai_ws:
            await initialize_session(openai_ws)
            stream_sid = None
            latest_media_timestamp = 0
            last_assistant_item = None
            mark_queue = []
            response_start_timestamp_twilio = None

            asyncio.create_task(handler_buffer_wait())

            async def receive_from_twilio():
                global current_call_status
                """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
                nonlocal stream_sid, latest_media_timestamp
                try:
                    async for message in websocket.iter_text():
                        data = json.loads(message)
                        if data['event'] == 'media' and not openai_ws.closed:
                            audio_payload = data['media']['payload']
                            latest_media_timestamp = int(data['media']['timestamp'])
                            audio_buffer.append(audio_payload)
                            asyncio.create_task(send_to_openai(audio_payload, openai_ws))
                        elif data['event'] == 'start':
                            stream_sid = data['start']['streamSid']
                            print(f"Incoming stream has started {stream_sid}")
                            response_start_timestamp_twilio = None
                            latest_media_timestamp = 0
                            last_assistant_item = None
                        elif data['event'] == 'stop':
                            current_call_status = CallStatus.COMPLETED
                            await process_call_queue()
                        elif data['event'] == 'mark':
                            if mark_queue:
                                mark_queue.pop(0)

                except WebSocketDisconnect:
                    print("Client disconnected.")
                    if current_call_status == CallStatus.IN_PROGRESS:
                        current_call_status = CallStatus.COMPLETED
                        await process_call_queue()
                    if not openai_ws.closed:
                        await openai_ws.close()
                except Exception as e:
                    print(f"Error in receive_from_twilio: {e}")
                
                finally:
                    if current_call_status == CallStatus.IN_PROGRESS:
                        current_call_status = CallStatus.COMPLETED
                        await process_call_queue()

            async def send_to_twilio():
                """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
                nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
                global call_number,transcription_text

                try:
                    async for openai_message in openai_ws:
                        response = json.loads(openai_message.data)
                        rsp= extract_function_call(response)
                        if rsp:
                            if rsp["function_name"] == "escalate_call" :
                                escalate_call(csid)
                            else :
                                out=execute_function(rsp,call_number)
                                ret = create_function_call_output(rsp['call_id'], out)
                                await send_functions_response(ret, openai_ws)

                        print(f"Received event: {response['type']}", response)

                        if response.get('type') == 'response.audio_transcript.done':
                            tenglish = response["transcript"]
                            transcription_text = transcription_text + "AI: " + tenglish + "\n"
                            # openai_transcriptions.append(tenglish)
                            # print(f"The response transcription is : {tenglish}")
                            

                        if response.get('type') == 'response.audio.delta' and 'delta' in response:
                            try:
                                audio_payload = base64.b64decode(response['delta'])
                            except Exception as e:
                                print(f"Base64 Decode Error: {e}")
                                continue

                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": base64.b64encode(audio_payload).decode('utf-8')
                                }
                            }
                            await websocket.send_json(audio_delta)

                            if response_start_timestamp_twilio is None:
                                response_start_timestamp_twilio = latest_media_timestamp
                                if SHOW_TIMING_MATH:
                                    print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")

                            if response.get('item_id'):
                                last_assistant_item = response['item_id']

                            await send_mark(websocket, stream_sid)

                        if response.get('type') == 'conversation.item.input_audio_transcription.delta':
                            delta = response.get("delta")
                            if isinstance(delta,dict):
                                transcription = delta.get('text')
                                if transcription is not None:
                                    transcription_text = transcription_text + "User: " + " " + transcription + "\n"

                                    print("transcriptions is ::: ",transcription)
                            else:
                                if delta is not None:
                                    transcription_text = transcription_text + "User: " + " " + delta + "\n"
                                    print("transcriptions is ::: ",delta)

                        if response.get('type') == 'input_audio_buffer.speech_started':
                            print("Speech started detected.")
                            if last_assistant_item:
                                print(f"Interrupting response with id: {last_assistant_item}")
                                await handle_speech_started_event()
                except Exception as e:
                    print(f"Error in send_to_twilio: {e}")

            async def handle_speech_started_event():
                """Handle interruption when the caller's speech starts."""
                nonlocal response_start_timestamp_twilio, last_assistant_item
                print("Handling speech started event.")
                if mark_queue and response_start_timestamp_twilio is not None:
                    elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                    if SHOW_TIMING_MATH:
                        print(f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms")

                    if last_assistant_item:
                        if SHOW_TIMING_MATH:
                            print(f"Truncating item with ID: {last_assistant_item}, Truncated at: {elapsed_time}ms")

                        truncate_event = {
                            "type": "conversation.item.truncate",
                            "item_id": last_assistant_item,
                            "content_index": 0,
                            "audio_end_ms": elapsed_time
                        }
                        await openai_ws.send_json(truncate_event)

                    await websocket.send_json({
                        "event": "clear",
                        "streamSid": stream_sid
                    })

                    mark_queue.clear()
                    last_assistant_item = None
                    response_start_timestamp_twilio = None

            async def send_mark(connection, stream_sid):
                """Send mark event to Twilio."""
                if stream_sid:
                    mark_event = {
                        "event": "mark",
                        "streamSid": stream_sid,
                        "mark": {"name": "responsePart"}
                    }
                    await connection.send_json(mark_event)
                    mark_queue.append('responsePart')

            await asyncio.gather(receive_from_twilio(), send_to_twilio())

async def send_initial_conversation_item(openai_ws,text):
    """Send initial conversation item if AI talks first."""
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": f"Greet the user with the following text: {text}"
                }
            ]
        }
    }
    await openai_ws.send_json(initial_conversation_item)
    await openai_ws.send_json({"type": "response.create"})

async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""

    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "input_audio_transcription": {
                "model": "whisper-1"
                },
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.7,
            "tools": [
                    {
                        "type": "function",
                        "name": "generate_horoscope_people",
                        "description": "Give today's horoscope for an astrological sign.",
                        "parameters": {
                        "type": "object",
                        "properties": {
                            "sign": {
                            "type": "string",
                            "description": "The sign for the horoscope.",
                            "enum": [
                                "Aries",
                                "Taurus",
                                "Gemini",
                                "Cancer",
                                "Leo",
                                "Virgo",
                                "Libra",
                                "Scorpio",
                                "Sagittarius",
                                "Capricorn",
                                "Aquarius",
                                "Pisces"
                            ]
                            }
                        },
                        "required": ["sign"]
                        }
                  },

                {
                    "type": "function",
                    "name": "get_target_status",
                    "description": "Retrieve the target status comparison and gap details.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": { "type": "string" }
                        },
                        "required": ["phone_number"]
                    }
                },
                {
                    "type":"function",
                    "name":"escalate_call",
                    "description":"Escalates the call to a human support agent when the user wants to talk to an agent or customer support."

                },
                {
                    "type": "function",
                    "name": "incentive_details",
                    "description": "Get incentive details for a given phone number, including additional benefits for exceeding the target.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": { "type": "string" }
                        },
                    }
                },
                {
                    "type": "function",
                    "name": "get_emp_details",
                    "description": "Get the employee details including name, phone number, email, manager contact information, meeting time and duration, along with the action plan, achieved results, result explanation, and a brief summary",
                    
                },
                {
                    "type": "function",
                    "name": "penalty_details",
                    "description": "Fetch details of penalty charges applicable after the due date.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": { "type": "string" }
                        },
                        "required": ["phone_number"]
                    }
                },
                {
                    "type": "function",
                    "name": "collection_improvements",
                    "description": "Provide guidelines for improving collections, including strategies for top customers and defaulters.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": { "type": "string" }
                        },
                        "required": ["phone_number"]
                    }
                },
                {
                    "type": "function",
                    "name": "top_defaulters",
                    "description": "Retrieve a list of top defaulters along with their outstanding amounts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": { "type": "string" }
                        },
                        "required": ["phone_number"]
                    }
                },
                  {
                "type": "function",
                "name": "get_my_report_mysql",
                "description": "Gets the information from the database of the enterprise...",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": { "type": "string" }
                    },
                    "required": ["question"]
                }
            },
            {
                "type": "function",
                "name": "get_insurance_details",
                "description": "Gets the information on insurance,ploicy,nominee,bank details of the caller from the insurance table of the database. The details include Policyholder_ID, Name,Address,City, State ,Pincode,Phone_Number ,Email, Date_of_Birth , Gender, PAN_Number, Aadhaar_Number, Bank_Account_Number, Bank_Name , IFSC_Code, Nominee_Name , Nominee_Relationship ,Nominee_Contact_Number,Policy_ID , Policy_Type ,Policy_Start_Date , Policy_Maturity_Date , Premium_Amount , Premium_Payment_Frequency , Policy_Status, Sum_Assured, Bonus_Amount , Surrender_Value ,Loan_Against_Policy, Policy_Documents_Received, Policy_Documents_Received_Date , Claim_ID ,  Claim_Type , Claim_Amount, Claim_Submission_Date, Claim_Status, Claim_Rejection_Reason  etc of the caller.",
            },

            {
                "type": "function",
                "name": "send_status_to_managers",
                "description": "this function sends status to managers..."
            },
            {
                "type": "function",
                "name": "get_weather_bilvantis",
                "description": "Get the current weather...",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": { "type": "string" }
                    },
                    "required": ["location"]
                }
            },
            {
            "type": "function",
            "name": "search_knowledge_base_enterprise",
            "description": "Query a knowledge base to retrieve relevant info on a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user question or search query."
                    },
                    "options": {
                        "type": "object",
                        "properties": {
                            "num_results": {
                                "type": "number",
                                "description": "Number of top results to return."
                            },
                            "domain_filter": {
                                "type": [
                                    "string",
                                    "null"
                                ],
                                "description": "Optional domain to narrow the search (e.g. 'finance', 'medical'). Pass null if not needed."
                            },
                            "sort_by": {
                                "type": [
                                    "string",
                                    "null"
                                ],
                                "enum": [
                                    "relevance",
                                    "date",
                                    "popularity",
                                    "alphabetical"
                                ],
                                "description": "How to sort results. Pass null if not needed."
                            }
                        },
                        "required": [
                            "num_results",
                            "domain_filter",
                            "sort_by"
                        ],
                        "additionalProperties": False
                    }
                },
                "required": [
                    "query",
                    "options"
                ],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "send_email_1",
            "description": "Send an email to a given recipient with a subject and message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "The recipient email address."
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line."
                    },
                    "body": {
                        "type": "string",
                        "description": "Body of the email message."
                    }
                },
                "required": [
                    "to",
                    "subject",
                    "body"
                ],
                "additionalProperties": False
            }
        }

        ],
        "tool_choice": "auto",
        }
    }
    
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send_json(session_update)

async def check_number_allowed(to):
    """Check if a number is allowed to be called."""
    try:
        incoming_numbers = client.incoming_phone_numbers.list(phone_number=to)
        if incoming_numbers:
            return True

        outgoing_caller_ids = client.outgoing_caller_ids.list(phone_number=to)
        if outgoing_caller_ids:
            return True

        return False
    except Exception as e:
        print(f"Error checking phone number: {e}")
        return False

async def make_call(phone_number_to_call: str):
    # global phone_number = phone_number_to_call
    if not phone_number_to_call:
        raise ValueError("Please provide a phone number to call.")

    is_allowed = await check_number_allowed(phone_number_to_call)
    if not is_allowed:
        raise ValueError(f"The number {phone_number_to_call} is not recognized as a valid outgoing number or caller ID.")
    
    call_queue.append((phone_number_to_call, text))

    if current_call_status != CallStatus.IN_PROGRESS:
        await process_call_queue()

async def process_call_queue():
    """Process the next call in the queue if available."""
    global current_call_status
    if call_queue and current_call_status != CallStatus.IN_PROGRESS:
        phone_number, text = call_queue.pop(0)
        await make_call_with_status(phone_number)

class TCallStatus(str, Enum):
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    CANCELED = "canceled"

BAD_STATUS_CODES = {TCallStatus.FAILED, TCallStatus.BUSY, TCallStatus.NO_ANSWER, TCallStatus.CANCELED}

async def make_call_with_status(phone_number: str):
    global current_call_status, call_number, csid
    current_call_status = CallStatus.IN_PROGRESS
    call_number = phone_number
    
    try:
        greet, lang = fetch_explanation_by_phone(phone_number)
        target, result = get_targets_and_results(phone_number)
        
        voice_config = {
            "Spanish": ("es-US", "Polly.Lupe"),  # US Spanish accent
            "Hindi": ("hi-IN", "Polly.Aditi"),   # Keeping Hindi as is since it's specific to Indian accent
            "English": ("en-US", "Polly.Joanna") # US English accent
        }
        lang_text, voice_name = voice_config.get(lang, ("en-US", "Polly.Joanna"))  # Default to US English if language not found
        
        response = VoiceResponse()
        response.say(greet, language=lang_text, voice=voice_name)
        response.pause(length=1)
        response.say(f"These are the targets for today, {target}", language="en-US")
        response.pause(length=1)
        response.say(f"Following are the achievements for yesterday. {result}", language="en-US")
        response.pause(length=1)
        response.say("You need to focus on your target", language="en-US")
        response.pause(length=1)
        response.say("You can start talking now", language="en-US", voice="Polly.Joanna")
        
        connect = Connect()
        connect.stream(url=f"wss://{DOMAIN}/media-stream")
        response.append(connect)
        
        call = client.calls.create(
            from_=PHONE_NUMBER_FROM,
            to=phone_number,
            twiml=str(response),
            machine_detection='DetectMessageEnd',
            status_callback=f"https://{DOMAIN}/call-status",
            status_callback_method="POST",
            status_callback_event=[
                "ringing","in-progress", "completed", "failed",
                "busy", "no-answer", "canceled"
            ],
        )
        
        print(f"Call initiated to {phone_number}, SID: {call.sid}")
        csid = call.sid
        
    except Exception as e:
        current_call_status = CallStatus.COMPLETED
        print(f"Error making call to {phone_number}: {str(e)}")
        raise


@app.post("/call-status")
async def call_status(request: Request):
    # global current_call_status,transcription_text
    global current_call_status, transcription_text, SENDER_EMAIL, SENDER_PASSWORD
    form = await request.form()
    call_sid = form.get("CallSid")
    call_status = form.get("CallStatus", "").lower()
    answered_by = form.get("AnsweredBy")
    duration = form.get("CallDuration")
    to_number = form.get("To")
    
    print(f"[CALL STATUS] SID: {call_sid}, To: {to_number}, Status: {call_status}, Duration: {duration}, Answered by: {answered_by}")

    total_calls = get_total_calls_for_number(to_number)
    
    # Handle different call statuses
    if call_status == TCallStatus.COMPLETED:

        client.calls(call_sid).update(
        status="completed"
        )
        current_call_status = CallStatus.COMPLETED
        
        print(f"The complete transcription is: {transcription_text}")
        
        total_calls = str(int(total_calls) + 1)
        if answered_by == "machine_end_beep":
            duration = 0.0
            transcription_text = ""
            update_records(to_number,duration,total_calls,transcription_text)
        else:
            update_records(to_number,duration,total_calls,transcription_text)
        
        if transcription_text!="":

            insights_task =  asyncio.create_task(get_insights(transcription_text))
            recipients_task =  asyncio.create_task(get_recipents(to_number))
            insights, recipients = await asyncio.gather(insights_task, recipients_task)

            body = f"Hello,\n\n{insights}\n\nBest regards!"

            subject = "Conversation Overview"
            print(f"Recipients are: {recipients}")
            SENDER_EMAIL = os.getenv('SENDER_EMAIL')
            print(f"SENDER_EMAIL is: {SENDER_EMAIL}")
            SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
            resp = await send_email_1(SENDER_EMAIL,SENDER_PASSWORD,recipients,subject,body)

            if resp:
                print("EMAIL SENT")

        transcription_text = ""
        await process_call_queue()
         
    return JSONResponse({"status": "received"})

async def log_call_sid(call_sid):
    """Log the call SID."""
    print(f"Call started with SID: {call_sid}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Twilio AI voice assistant server.")
    parser.add_argument('--call', help="The phone number to call, e.g., '--call=+18005551212'")
    return parser.parse_args()

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    global caller_number

    """Handle incoming call and return TwiML response to connect to Media Stream."""
    form_data = await request.form()

    # Log caller information
    caller_number = form_data.get("From")
    caller_name = form_data.get("CallerName") 
    caller_city = form_data.get("CallerCity")
    caller_state = form_data.get("CallerState")
    caller_zip = form_data.get("CallerZip")
    caller_country = form_data.get("CallerCountry")

    print(f"Caller Number: {caller_number}")
    print(f"Caller Name: {caller_name}")
    print(f"Caller Location: {caller_city}, {caller_state}, {caller_zip}, {caller_country}")

    try:
        greet, lang = fetch_explanation_by_phone(caller_number)
        target, result = get_targets_and_results(caller_number)
        
        voice_config = {
            "Spanish": ("es-MX", "Polly.Mia"),
            "Hindi": ("hi-IN", "Polly.Aditi"),
            "English": ("en-US", "Polly.Joanna")
        }
        
        lang_text, voice_name = voice_config.get(lang, ("en-US", "Polly.Joanna"))  # Default to English if language not found
        
        response = VoiceResponse()
        response.say(greet, language=lang_text, voice=voice_name)
        response.pause(length=1)
        response.say(f"These are the targets for today, {target}", language="en-US")
        response.pause(length=1)
        response.say(f"Following are the achievements for yesterday. {result}", language="en-US")
        response.pause(length=1)
        response.say("You need to focus on your target", language="en-US")
        response.pause(length=1)
        response.say("You can start talking now", language="en-US", voice="Polly.Joanna")
        host = request.url.hostname
        connect = Connect()
        connect.stream(url=f"wss://{host}/media-stream")
        response.append(connect)
        
        return HTMLResponse(content=str(response), media_type="application/xml")
    except Exception as e:
        print(f"Error handling incoming call: {str(e)}")
        # Return a basic response in case of error
        response = VoiceResponse()
        response.say("We're experiencing technical difficulties. Please try again later.", language="en-US", voice="Polly.Joanna")
        return HTMLResponse(content=str(response), media_type="application/xml")

from typing import List

class OutgoingCallRequest(BaseModel):
    phone_numbers: List[str]

@app.post("/call_from_twilio")
async def trigger_outgoing_calls(data: OutgoingCallRequest):
    outgoing_call_handler(data.phone_numbers)
    return {"status": "Call trigger initiated", "numbers": data.phone_numbers}

import asyncio

def outgoing_call_handler(numbers):
    async def run_all_calls():
        await asyncio.gather(*(make_call(num) for num in numbers))

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already inside an event loop (e.g., FastAPI), use a background task
            asyncio.create_task(run_all_calls())
        else:
            loop.run_until_complete(run_all_calls())
    except RuntimeError:
        # If there's no event loop at all (CLI use case)
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(run_all_calls())


if __name__ == "__main__":
    args = parse_arguments()

    call_queue = []

    current_call_status = CallStatus.IDLE

    transcription_text = ""

    # numbers = get_all_phone_numbers()


    # numbers = ["+19787319274"]
    numbers = ["+917799117204"]

    if args.call=="yes":
        for i in numbers: 
            loop = asyncio.get_event_loop()
            loop.run_until_complete(make_call(i))
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)

    "FIRST RUN THE 'ngrok http 5050' AND THEN RUN THIS FILE"