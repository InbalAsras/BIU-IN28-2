from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from core.state import AgentState
from core.logger import AgentLogger

class CriticEvaluation(BaseModel):
    is_acceptable: bool = Field(description="Whether the translation preserves the core meaning and tone.")
    feedback: str = Field(description="Detailed feedback on hallucinations, tone degradation, or linguistic errors.")
    confidence_score: float = Field(description="Confidence in the evaluation from 0.0 to 1.0.")

class CriticAgent:
    """
    The Critic Agent evaluates the translation against the original source.
    """
    
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
        self.structured_llm = self.llm.with_structured_output(CriticEvaluation)
        
    def evaluate(self, state: AgentState) -> dict:
        AgentLogger.log_agent_start("Critic", "Evaluating Translation Quality")
        
        source_text = state["source_text"]
        translated_text = state["current_translation"]
        target_lang = state["language_chain"][state["current_index"] + 1]
        
        prompt = f"""
        Act as a professional linguist and critic.
        Evaluate the quality of the translation into {target_lang} based on the original English source.
        
        ORIGINAL SOURCE:
        {source_text}
        
        TRANSLATION TO EVALUATE:
        {translated_text}
        
        CRITERIA:
        1. Does it preserve the semantic meaning?
        2. Is the tone appropriate for the selected skill ({state['selected_skill']})?
        3. Are there any hallucinations or added information?
        
        If the semantic score ({state['current_semantic_score']:.2f}) is low, be extra critical.
        """
        
        evaluation = self.structured_llm.invoke(prompt)
        
        AgentLogger.log_event("CRITIC FEEDBACK", evaluation.feedback)
        AgentLogger.log_agent_end("Critic", "SUCCESS" if evaluation.is_acceptable else "REJECTED")
        
        # Determine if reflection is needed based on Critic's decision OR very low semantic score
        reflection_needed = not evaluation.is_acceptable or state["current_semantic_score"] < 0.75
        
        thoughts = f"Linguistic Evaluation: {'APPROVED' if evaluation.is_acceptable else 'REJECTED'}. "
        thoughts += f"Critic Confidence: {evaluation.confidence_score:.2f}. "
        if reflection_needed:
            thoughts += "Action: Triggering Reflection Loop to rectify issues."
        else:
            thoughts += "Action: Proceeding to next language in the chain."

        return {
            "last_critic_feedback": evaluation.feedback,
            "reflection_needed": reflection_needed,
            "current_thoughts": thoughts
        }
