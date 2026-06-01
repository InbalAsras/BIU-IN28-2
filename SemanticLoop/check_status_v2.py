import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def verify():
    path = find_dotenv()
    if path:
        load_dotenv(path, override=True)
    
    key = os.getenv('GOOGLE_API_KEY')
    print(f"Checking Key Fingerprint: {key[:10]}...{key[-4:]}")
    
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', google_api_key=key)
    try:
        response = llm.invoke('hi')
        print("✅ Quota Status: AVAILABLE")
        return True
    except Exception as e:
        print("❌ Quota Status: EXHAUSTED")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    verify()
