import os
import json

from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(override=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(model="gpt-4", openai_api_key=OPENAI_API_KEY, temperature=0)

async def get_insights(conversation):

    prompt = PromptTemplate.from_template("""
                    Role: You are an expert communication analyst specializing in extracting key insights from a call transcript.
                    Instructions: Given the following transcript of a call conversation, extract deep insights with a focus on context, tone, topics discussed, action items, emotions, and speaker dynamics.
                        
                        Please analyze the conversation and return the following:

                        Conversation Summary: A concise summary of what the conversation was about.

                        Key Topics Discussed: A bullet list of main subjects or themes covered.

                        Action Items & Decisions: Any decisions made, follow-ups required, or tasks assigned.

                        Emotional Tone: Sentiment of the participants (e.g., enthusiastic, concerned, frustrated) and any emotional shifts.

                        Speaker Dynamics: Who spoke more, any interruptions, dominance or passivity, etc.

                        Potential Risks or Issues Raised: Anything that might require attention or signal a problem.

                    call transcript : {transcript} 
                     
            """)
           
    input = prompt.format(transcript = conversation)

    try:
        resp = llm.invoke(input)
        response = resp.content.strip()
        # print(response)
        return response
    except Exception as e:
        print(e)
    