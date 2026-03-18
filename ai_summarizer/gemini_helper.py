import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_model():
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_text(prompt):
    model = get_gemini_model()
    response = model.generate_content(prompt)
    return response.text
