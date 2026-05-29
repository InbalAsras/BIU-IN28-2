from sentence_transformers import SentenceTransformer, util
import torch
from core.state import AgentState
from core.logger import AgentLogger

class SemanticAnalyzer:
    """
    Computes semantic similarity between the source text and the current translation.
    """
    
    _model_instance = None  # Class-level cache for the model

    def __init__(self):
        if SemanticAnalyzer._model_instance is None:
            AgentLogger.log_event("SYSTEM", "Loading Multilingual Embedding Model...")
            # Use a fast, reliable model for production
            SemanticAnalyzer._model_instance = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        self.model = SemanticAnalyzer._model_instance
        
    def analyze(self, state: AgentState) -> dict:
        AgentLogger.log_agent_start("Semantic Analyzer", "Calculating Drift Score")
        
        source_text = state["source_text"]
        current_text = state["current_translation"]
        
        # Compute embeddings
        # Note: We are comparing the source (e.g. English) with the current translation (e.g. Arabic)
        # Multilingual models are designed to map these to the same vector space.
        embeddings = self.model.encode([source_text, current_text], convert_to_tensor=True)
        
        # Compute Cosine Similarity
        cosine_scores = util.cos_sim(embeddings[0], embeddings[1])
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
