import os
from langchain_google_genai import ChatGoogleGenerativeAI

def check_key(name, key):
    if not key:
        print(f"{name}: NOT FOUND")
        return False
    print(f"{name} Fingerprint: {key[:10]}...{key[-4:]}")
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', google_api_key=key)
    try:
        llm.invoke('hi')
        print(f"{name} Quota Status: AVAILABLE")
        return True
    except Exception as e:
        print(f"{name} Quota Status: EXHAUSTED")
        return False

def check():
    # NO load_dotenv here to check OS variables
    g_key = os.environ.get('GOOGLE_API_KEY')
    gem_key = os.environ.get('GEMINI_API_KEY')
    
    print("--- OS Quota Diagnostic ---")
    any_available = False
    if check_key("GOOGLE_API_KEY (OS)", g_key): any_available = True
    if check_key("GEMINI_API_KEY (OS)", gem_key): any_available = True
    
    if not any_available:
        print("\n🛑 ALL OS KEYS EXHAUSTED.")
    else:
        print("\n✅ At least one OS key is available.")

if __name__ == "__main__":
    check()
