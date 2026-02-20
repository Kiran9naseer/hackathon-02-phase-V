import google.generativeai as genai
import os

api_key = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=api_key)

print("AVAILABLE MODELS FOR generateContent:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
