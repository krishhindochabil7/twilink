# from googletrans import Translator
 
# def translate_to_language(text: str, target_language: str) -> str:
#     """
#     Translate English text into the specified European language.
 
#     :param text: English text to translate.
#     :param target_language: Target language code (e.g., 'fr' for French, 'de' for German).
#     :return: Translated text.
#     """
#     translator = Translator()
    
#     try:
#         translated = translator.translate(text, src='en', dest=target_language)
#         return translated.text
#     except Exception as e:
#         return f"Translation failed: {e}"
 
# Example usage:
#print(translate_to_language("Hello, how are you?", "fr"))  # French
#print(translate_to_language("Let's meet tomorrow at noon.", "de"))  # German
 
from deep_translator import GoogleTranslator
 
def translate_to_language_google(text: str, target: str):
    return GoogleTranslator(source='auto', target=target).translate(text)
 
#print(translate_text("Hello, how are you?", "fr"))
 
 
import openai
import os
from dotenv import load_dotenv
load_dotenv()
 
# Set your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
from langchain_openai import ChatOpenAI
 
 
def translate_to_language(text, target_language):
 
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=api_key  
        #"...",  # if you prefer to pass api key in directly instaed of using env vars
        # base_url="...",
        # organization="...",
        # other params...
    )
    prompt = f"Translate the following text to {target_language}:\n\n{text}"
    ai_msg = llm.invoke(prompt)
    print(ai_msg.content)
    return ai_msg.content
 
 
 
import pyttsx3
 
def speak_text(text):
    """
    Converts the given text to speech.
    
    Args:
        text (str): The text to be spoken.
    """
    engine = pyttsx3.init()
    
    # Optional: Change properties
    engine.setProperty('rate', 150)     # Speed of speech (default ~200)
    engine.setProperty('volume', 1.0)   # Volume (0.0 to 1.0)
    
    engine.say(text)
    engine.runAndWait()

