from sentence_transformers import SentenceTransformer, util
import torch
import logging
from core.state import AgentState
from core.logger import AgentLogger

# Global model instance to ensure it's only loaded once across all instances
_MODEL_INSTANCE = None

try:
    _MODEL_INSTANCE = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
except Exception as e:
    logging.error(f"Failed to load SentenceTransformer model: {e}")

class SemanticAnalyzer:
    """
    Computes semantic similarity between the source text and the current translation.
    Uses a robust embedding and similarity calculation logic.
    """
    
    def __init__(self):
        self.model = _MODEL_INSTANCE
        if self.model is None:
             AgentLogger.log_event("ERROR", "Semantic Model NOT INITIALIZED.")
        
    def analyze(self, state: AgentState) -> dict:
        AgentLogger.log_agent_start("Semantic Analyzer", "Calculating Drift Score")
        
        source_text = state["source_text"]
        current_text = state["current_translation"]
        
        # 1. Validation: Handle missing model or empty inputs
        if not self.model:
            AgentLogger.log_event("ERROR", "Model is not initialized.")
            return {"current_semantic_score": 0.0, "current_thoughts": "Error: Semantic model failed to load."}
        
        if not source_text or not current_text:
            AgentLogger.log_event("WARNING", "One of the input texts is empty.")
            return {"current_semantic_score": 0.0, "current_thoughts": "Warning: Received empty text for analysis."}

        try:
            # 2. Compute Embeddings
            # Explicitly casting to string to handle potential non-string objects
            embeddings = self.model.encode([str(source_text), str(current_text)], convert_to_tensor=True)
            
            # 3. Compute Cosine Similarity
            cosine_scores = util.cos_sim(embeddings[0], embeddings[1])
            
            # 4. Extract scalar score
            score = float(cosine_scores[0][0])
            
            AgentLogger.log_event("SCORE", f"Semantic Similarity: {score:.4f}")
            AgentLogger.log_agent_end("Semantic Analyzer")
            
            thoughts = f"Computed a cosine similarity of {score:.4f} between the original source and the translation."
            if score < 0.75:
                thoughts += " ⚠️ HIGH DRIFT DETECTED."
            else:
                thoughts += " ✅ Meaning successfully preserved."

            return {
                "current_semantic_score": score,
                "current_thoughts": thoughts
            }

        except Exception as e:
            AgentLogger.log_event("ERROR", f"Error during similarity calculation: {e}")
            return {
                "current_semantic_score": 0.0, 
                "current_thoughts": f"Error: Analysis failed during vector calculation."
            }
