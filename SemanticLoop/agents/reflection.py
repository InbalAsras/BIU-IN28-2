from langchain_google_genai import ChatGoogleGenerativeAI
from core.state import AgentState
from core.logger import AgentLogger

class ReflectionAgent:
    """
    The Reflection Agent formulates a strategy to fix a failing translation.
    
    Architecture Decision:
    This agent acts as a 'meta-thinker,' analyzing WHY a translation failed 
    rather than just trying again blindly. This demonstrates true Agentic Behavior.
    """
    
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
        
    def reflect(self, state: AgentState) -> dict:
        AgentLogger.log_agent_start("Reflection", "Synthesizing Correction Strategy")
        
        source_text = state["source_text"]
        failed_translation = state["current_translation"]
        feedback = state["last_critic_feedback"]
        retry_count = state["retry_count"] + 1
        
        AgentLogger.log_reflection(feedback)
        
        # If we have too many retries, we might just accept it or log a failure
        if retry_count >= state["max_retries"]:
            AgentLogger.log_event("WARNING", "Max retries reached. Moving forward with best effort.")
            return {
                "retry_count": retry_count,
                "reflection_needed": False,
                "current_thoughts": "Maximum retries reached. Preserving current version to ensure chain completion."
            }

        prompt = f"""
        Analyze why the following translation failed based on the critic feedback.
        Generate a concise, actionable correction strategy for the next translation attempt.
        
        ORIGINAL SOURCE:
        {source_text}
        
        FAILED TRANSLATION:
        {failed_translation}
        
        CRITIC FEEDBACK:
        {feedback}
        
        Output ONLY the strategy (e.g., "Avoid translating the idiomatic expression literally", "Increase formality in the target language").
        """
        
        response = self.llm.invoke(prompt)
        
        # Handle cases where content might be a list or a string
        if isinstance(response.content, str):
            strategy = response.content.strip()
        elif isinstance(response.content, list):
            strategy = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content]).strip()
        else:
            strategy = str(response.content).strip()
        
        AgentLogger.log_event("STRATEGY", strategy)
        AgentLogger.log_agent_end("Reflection")
        
        thoughts = f"Synthesized repair strategy: {strategy} (Attempt {retry_count}/{state['max_retries']})."

        return {
            "retry_count": retry_count,
            "reflection_needed": True,
            "correction_strategy": strategy,
            "current_thoughts": thoughts
        }
