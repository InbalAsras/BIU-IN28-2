import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import json

def diagnostic():
    load_dotenv(find_dotenv(), override=True)
    key = os.getenv('GOOGLE_API_KEY')
    print(f"Active Key Fingerprint: {key[:10]}...{key[-4:]}")
    print(f"Active Model: gemini-2.0-flash")
    
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', google_api_key=key)
    try:
        llm.invoke('hi')
        print("Status: AVAILABLE")
    except Exception as e:
        print("\n--- FULL GOOGLE API ERROR DETAILS ---")
        # Attempt to parse or print the raw error
        print(str(e))
        
        # Check for Project IDs or Quota IDs in the error string
        error_str = str(e)
        if "quotaId" in error_str:
            # Try to extract the quotaId which often contains project info
            import re
            quota_ids = re.findall(r"'quotaId': '([^']+)'", error_str)
            if quota_ids:
                print(f"\nDetected Quota IDs: {quota_ids}")
        
        if "violations" in error_str:
            print("\nSpecific Violations Found: RPD (Daily) or RPM (Minute) likely exceeded.")

if __name__ == "__main__":
    diagnostic()
