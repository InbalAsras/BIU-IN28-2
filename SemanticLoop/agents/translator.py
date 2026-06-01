import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from core.logger import AgentLogger

class TranslatorAgent:
    """
    The Translator Agent responsible for linguistic transformation.
    
    Architecture Decision:
    Uses 'Skills' injection to modify behavior. Skills are loaded from 
    external markdown files to keep the system modular and prompt-driven.
    """
    
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
        
    def _load_skill(self, skill_name: str) -> str:
        skill_path = f"skills/{skill_name.lower().replace(' ', '_')}_skill.md"
        if os.path.exists(skill_path):
            with open(skill_path, "r", encoding="utf-8") as f:
                return f.read()
        return "You are a professional translator. Maintain the original meaning and tone."

    def translate(self, state: AgentState) -> dict:
        current_idx = state["current_index"]
        source_lang = state["language_chain"][current_idx]
        target_lang = state["language_chain"][current_idx + 1]
        
        # Logic Fix: If we are re-translating (reflection), the 'source' of the current hop 
        # is actually the 'translated_text' of the PREVIOUS hop in history.
        # If it's the first hop, it's the 'source_text'.
        if state["retry_count"] > 0 and state["history"]:
            text_to_translate = state["history"][-1].translated_text
        elif current_idx > 0 and state["history"]:
            text_to_translate = state["history"][-1].translated_text
        else:
            text_to_translate = state["source_text"]
        
        skill_content = self._load_skill(state["selected_skill"])
        
        AgentLogger.log_agent_start("Translator", f"Moving from {source_lang} to {target_lang}")
        
        prompt = f"""
        Translate the following text from {source_lang} to {target_lang}.
        
        TEXT:
        {text_to_translate}
        
        REQUIRED FORMAT:
        Provide ONLY the translated text. Do not include explanations or notes.
        """
        
        # If there's a correction strategy from reflection, apply it
        if state.get("correction_strategy") and state["reflection_needed"]:
            prompt += f"\n\nSTRATEGY FOR CORRECTION:\n{state['correction_strategy']}\nPlease ensure this strategy is followed in the new translation."
        elif state["last_critic_feedback"] and state["reflection_needed"]:
            prompt += f"\n\nCRITICAL FEEDBACK FROM PREVIOUS ATTEMPT:\n{state['last_critic_feedback']}\nPlease correct these issues in this version."

        messages = [
            SystemMessage(content=skill_content),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Handle cases where content might be a list or a string
        if isinstance(response.content, str):
            translated_text = response.content.strip()
        elif isinstance(response.content, list):
            translated_text = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content]).strip()
        else:
            translated_text = str(response.content).strip()
        
        AgentLogger.log_agent_end("Translator")
        
        thoughts = f"Translating from {source_lang} to {target_lang} using the '{state['selected_skill']}' skill profile."
        if state["reflection_needed"]:
            thoughts += " This is a RE-TRANSLATION attempt based on Critic feedback."

        return {
            "current_translation": translated_text,
            "current_thoughts": thoughts,
            "reflection_needed": False 
        }
