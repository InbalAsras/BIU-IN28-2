import os
import sys
from dotenv import load_dotenv

def verify():
    print("🔍 SemanticLoop Environment Verification\n" + "="*40)
    
    # 1. Check Python Version
    print(f"✅ Python Version: {sys.version.split()[0]}")
    
    # 2. Check Environment Variables / Secrets
    from utils.secrets import get_api_key
    api_key = get_api_key()
    if api_key:
        print("✅ Google API Key found (via Secrets or Env)")
    else:
        print("❌ Google API Key MISSING")
        
    # 3. Check Dependencies
    try:
        import langgraph
        import streamlit
        import sentence_transformers
        import plotly
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ All major dependencies (LangGraph, Streamlit, etc.) are installed.")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        
    # 4. Check Folder Structure
    required_folders = ['core', 'agents', 'skills', 'ui', 'utils']
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"✅ Directory found: /{folder}")
        else:
            print(f"❌ Missing directory: /{folder}")
            
    # 5. Check Skill Files
    skills = ['academic', 'poetic', 'legal', 'emotional', 'cybersecurity']
    for s in skills:
        path = f"skills/{s}_skill.md"
        if os.path.exists(path):
            print(f"✅ Skill file found: {path}")
        else:
            print(f"❌ Missing skill file: {path}")

    print("="*40 + "\nVerification Complete.")

if __name__ == "__main__":
    verify()
