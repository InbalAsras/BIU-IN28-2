from typing import Literal
from langgraph.graph import StateGraph, END
from core.state import AgentState, TranslationStep
from agents.translator import TranslatorAgent
from agents.semantic import SemanticAnalyzer
from agents.critic import CriticAgent
from agents.reflection import ReflectionAgent
from core.logger import AgentLogger

class SemanticLoopOrchestrator:
    """
    The Orchestrator defines the LangGraph state machine.
    
    Architecture Decision:
    Using a formal StateGraph allows for non-linear workflows (loops, 
    conditional routing) that are impossible with basic chains.
    """
    
    def __init__(self, api_key: str):
        self.translator = TranslatorAgent(api_key)
        self.semantic = SemanticAnalyzer()
        self.critic = CriticAgent(api_key)
        self.reflector = ReflectionAgent(api_key)
        
        self.builder = StateGraph(AgentState)
        self._build_graph()
        self.graph = self.builder.compile()
        
    def _build_graph(self):
        # 1. Define Nodes
        self.builder.add_node("translate", self.translator.translate)
        self.builder.add_node("analyze", self.semantic.analyze)
        self.builder.add_node("critic", self.critic.evaluate)
        self.builder.add_node("reflect", self.reflector.reflect)
        self.builder.add_node("record_step", self._record_step)
        
        # 2. Define Edges (The Workflow)
        self.builder.set_entry_point("translate")
        
        self.builder.add_edge("translate", "analyze")
        self.builder.add_edge("analyze", "critic")
        
        # 3. Conditional Logic: Should we reflect or proceed?
        self.builder.add_conditional_edges(
            "critic",
            self._should_reflect,
            {
                "reflect": "reflect",
                "record": "record_step"
            }
        )
        
        self.builder.add_edge("reflect", "translate")
        
        # 4. After recording, should we continue the chain or finish?
        self.builder.add_conditional_edges(
            "record_step",
            self._is_chain_complete,
            {
                "next": "translate",
                "finish": END
            }
        )

    def _should_reflect(self, state: AgentState) -> Literal["reflect", "record"]:
        if state["reflection_needed"] and state["retry_count"] < state["max_retries"]:
            return "reflect"
        return "record"

    def _is_chain_complete(self, state: AgentState) -> Literal["next", "finish"]:
        if state["current_index"] >= len(state["language_chain"]) - 1:
            return "finish"
        return "next"

    def _record_step(self, state: AgentState) -> dict:
        """Saves the current translation hop to history and increments index."""
        current_idx = state["current_index"]
        step = TranslationStep(
            source_language=state["language_chain"][current_idx],
            target_language=state["language_chain"][current_idx + 1],
            original_text=state["source_text"],
            translated_text=state["current_translation"],
            skill_applied=state["selected_skill"],
            semantic_score=state["current_semantic_score"],
            critic_feedback=state["last_critic_feedback"],
            is_reflected=state["retry_count"] > 0
        )
        
        AgentLogger.log_event("HISTORY", f"Recorded hop {current_idx + 1}")
        
        return {
            "history": [step], # operator.add will append this
            "current_index": current_idx + 1,
            "retry_count": 0, # Reset for next hop
            "last_critic_feedback": None,
            "correction_strategy": None, # Reset for next hop
            "reflection_needed": False
        }
