from typing import Annotated, List, Optional, TypedDict
import operator
from pydantic import BaseModel, Field

class TranslationStep(BaseModel):
    """Represents a single step in the translation chain."""
    source_language: str
    target_language: str
    original_text: str
    translated_text: str
    skill_applied: str
    semantic_score: float = 0.0
    critic_feedback: Optional[str] = None
    is_reflected: bool = False

class AgentState(TypedDict):
    """
    The central state object for the SemanticLoop orchestration.
    """
    # Input configuration
    source_text: str
    language_chain: List[str]
    selected_skill: str
    
    # State tracking
    current_index: int
    
    # History & Analysis
    history: Annotated[List[TranslationStep], operator.add]
    
    # Current operation state
    current_translation: Optional[str]
    current_semantic_score: float
    current_thoughts: str  # Added for UI transparency
    
    # Reflection & Loop control
    retry_count: int
    max_retries: int
    reflection_needed: bool
    last_critic_feedback: Optional[str]
    correction_strategy: Optional[str] # New field for synthesized strategy
    
    # Final Output
    final_result: Optional[str]
    is_complete: bool
