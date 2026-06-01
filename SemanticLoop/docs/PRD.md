# Product Requirements Document (PRD): SemanticLoop Research Platform

## 1. Executive Summary
**SemanticLoop** is an agentic AI research platform designed to investigate **Semantic Drift**—the phenomenon where meaning degrades across recursive multilingual translation chains. The platform utilizes a multi-agent state machine to orchestrate translation, semantic analysis, and autonomous self-correction.

## 2. Core Objectives
- **Quantify Semantic Drift**: Measure the degradation of meaning using high-dimensional vector embeddings and cosine similarity.
- **Enable Autonomous Self-Correction**: Implement recursive reflection loops where agents critique their own output and reformulate strategies for improvement.
- **Maintain Tone Fidelity**: Utilize domain-specific "Skills" (Academic, Legal, Poetic, etc.) to ensure stylistic consistency across language transitions.
- **Provide Workflow Transparency**: Expose the internal reasoning ("thoughts") of AI agents to provide a white-box research environment.

## 3. Technical Architecture (The SemanticLoop Engine)
The system is built on a **Hybrid AI Architecture**:
- **Orchestration Layer**: `LangGraph` state machine for deterministic flow control.
- **Cognitive Layer**: `Gemini 2.0 Flash` for translation, critique, and reflection.
- **Analytical Layer**: `SentenceTransformers` (Local ML) for multilingual semantic vector comparison.
- **Interface Layer**: `Streamlit` for real-time visualization and experiment management.

## 4. Functional Requirements
### 4.1 Multi-Agent Workflow
- **Translator Agent**: Must adapt to specific skill profiles and incorporate corrective feedback.
- **Semantic Analyzer**: Must provide a numerical drift score (0.0 to 1.0) using local embedding models to avoid LLM-evaluating-LLM circularity.
- **Critic Agent**: Must produce structured JSON evaluations based on semantic preservation and tone.
- **Reflection Agent**: Must synthesize actionable strategies when quality thresholds (Score < 0.75) are breached.

### 4.2 Research Interface
- **Dynamic Visualization**: Real-time Plotly charts tracking semantic fidelity across the chain.
- **Architecture Mapping**: Live Mermaid.js visualization of the active graph state.
- **Audit Logs**: Comprehensive streaming of agentic thought traces.

## 5. Security & Deployment
- **Secret Management**: Must utilize Streamlit Secrets for production-grade API protection.
- **Cloud Readiness**: Optimized for Streamlit Community Cloud with class-level resource caching.
- **Modularity**: All agent logic must be decoupled from the UI for CLI-based research execution.

## 6. Success Metrics
- **Correction Rate**: Percentage of rejected translations successfully rectified in the reflection loop.
- **Latency Efficiency**: Startup time optimization via local model class-level caching.
- **Metric Reliability**: Correlation between human-perceived drift and the Analyzer's cosine similarity score.

## 7. Research Objectives
This project investigates the robustness and sensitivity of multi-agent translation workflows.
Research questions:
1. How much semantic drift accumulates across multilingual translation chains?
2. Can a reflection agent reduce semantic degradation?
3. How do different language paths affect semantic stability?
4. How effective are vector embeddings as a semantic measurement mechanism?