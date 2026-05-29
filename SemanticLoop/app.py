import streamlit as st
from core.graph import SemanticLoopOrchestrator
from ui.components import create_drift_chart, render_agent_log, get_mermaid_graph
from utils.secrets import get_api_key

# Page Config
st.set_page_config(
    page_title="SemanticLoop | AI Research Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache the orchestrator to prevent redundant model reloads
@st.cache_resource
def get_orchestrator(api_key):
    return SemanticLoopOrchestrator(api_key)

# Load Secrets
api_key = get_api_key()

# Custom CSS for that "Enterprise AI" look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .agent-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00d1b2;
        background-color: #161b22;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar: Configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("SemanticLoop")
    st.caption("Agentic Linguistic Intelligence Platform")
    
    # Credential Status
    if api_key:
        st.success("🔒 System Credentials Active")
    else:
        st.error("❌ Credentials Missing")

    st.markdown("---")
    
    st.subheader("🧪 Experiment Design")
    source_text = st.text_area(
        "Source Text", 
        "The butterfly's wings shimmered in the afternoon sun, a transient masterpiece of nature's design.",
        help="The original text that will be recursively translated."
    )
    
    skill = st.selectbox(
        "Research Profile (Skill)", 
        ["Academic", "Poetic", "Legal", "Emotional", "Cybersecurity"],
        help="Injects specific domain knowledge and tone constraints into the Agentic Workflow."
    )
    
    with st.expander("⚙️ Advanced Parameters"):
        chain_input = st.text_input(
            "Language Chain", 
            "English, French, Arabic, Hebrew, English",
            help="Comma-separated list of languages for the translation hops."
        )
        language_chain = [lang.strip() for lang in chain_input.split(",")]
        
        max_retries = st.slider(
            "Max Reflection Retries", 
            1, 3, 2,
            help="Number of times the Reflection Agent can attempt to fix a rejected translation."
        )
    
    st.markdown("###")
    run_button = st.button("🚀 Execute Research Chain", use_container_width=True, type="primary")

    st.markdown("---")
    with st.expander("ℹ️ About SemanticLoop"):
        st.markdown("""
        **SemanticLoop** investigates *Semantic Drift* using a multi-agent state machine.
        
        **Agentic Workflow:**
        1. **Translator**: Gemini-powered translation.
        2. **Analyzer**: Local vector similarity.
        3. **Critic**: Linguistic quality evaluation.
        4. **Reflector**: Autonomous error correction.
        
        Developed for research into recursive linguistic degradation.
        """)

# Main Area
st.title("🌐 SemanticLoop: Agentic Linguistic Research")
st.markdown("""
Welcome to the **SemanticLoop Command Center**. This platform orchestrates a multi-agent workflow to analyze 
how meaning shifts through recursive translation hops.
""")

if run_button:
    if not api_key:
        st.error("Google API Key MISSING. Please configure 'GOOGLE_API_KEY' in your Streamlit Secrets.")
    else:
        # Initialize Orchestrator with caching
        orchestrator = get_orchestrator(api_key)
        
        # Initialize State
        initial_state = {
            "source_text": source_text,
            "language_chain": language_chain,
            "selected_skill": skill,
            "current_index": 0,
            "history": [],
            "current_translation": None,
            "current_semantic_score": 1.0,
            "current_thoughts": "",
            "retry_count": 0,
            "max_retries": max_retries,
            "reflection_needed": False,
            "last_critic_feedback": None,
            "correction_strategy": None,
            "final_result": None,
            "is_complete": False
        }
        
        col_trace, col_arch = st.columns([1.5, 1])
        
        with col_arch:
            st.subheader("🏗️ System Architecture Flow")
            st.code(get_mermaid_graph(), language="mermaid")
            st.caption("Active multi-agent state machine visualizing nodes and conditional transitions.")

        with col_trace:
            st.subheader("⚡ Live Agent Execution Trace")
            progress_bar = st.progress(0)
            
            # Run the Graph and Stream results
            final_state = initial_state
            step_count = 0
            # Total expected steps is roughly len(chain) * nodes per hop
            total_expected_steps = (len(language_chain) - 1) * 4 
            
            with st.container():
                for output in orchestrator.graph.stream(initial_state):
                    for key, value in output.items():
                        step_count += 1
                        render_agent_log(key, value)
                        progress_bar.progress(min(step_count / total_expected_steps, 1.0))
                        
                        # Update internal state tracker
                        final_state.update(value)
            
            progress_bar.progress(1.0)
            st.success("Research Chain Complete.")

        # --- Analysis Section ---
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Semantic Drift Visualization")
            drift_fig = create_drift_chart(final_state["history"])
            if drift_fig:
                st.plotly_chart(drift_fig, use_container_width=True)
                
        with col2:
            st.subheader("📊 Research Metrics")
            if final_state.get("history"):
                final_score = final_state["history"][-1].semantic_score
                avg_score = sum(s.semantic_score for s in final_state["history"]) / len(final_state["history"])
                
                st.metric("Final Semantic Fidelity", f"{final_score:.2f}")
                st.metric("Average Chain Stability", f"{avg_score:.2f}")
                
                if final_score < 0.8:
                    st.warning("Significant Semantic Drift detected.")
                else:
                    st.success("High Semantic Preservation achieved.")

        # --- Final Results Section ---
        st.subheader("📝 Translation Evolution")
        for i, step in enumerate(final_state.get("history", [])):
            with st.expander(f"Hop {i+1}: {step.source_language} ➔ {step.target_language}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.text_area(f"Input ({step.source_language})", step.original_text if i==0 else final_state["history"][i-1].translated_text, height=100, key=f"in_{i}")
                with c2:
                    st.text_area(f"Output ({step.target_language})", step.translated_text, height=100, key=f"out_{i}")
                
                if step.critic_feedback:
                    st.caption(f"**Critic Feedback:** {step.critic_feedback}")

else:
    # Placeholder when not running
    st.info("Configure the experiment in the sidebar and click 'Execute Research Chain' to begin.")
    
    # Show a static example of what the UI provides
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3208/3208726.png", width=50)
        st.markdown("**Multi-Agent Orchestration**\nWatch Translator, Critic, and Reflection agents collaborate.")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=50)
        st.markdown("**Semantic Analysis**\nReal-time vector similarity scoring using local embedding models.")
    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/1541/1541413.png", width=50)
        st.markdown("**Reflection Loops**\nAutonomous self-correction when translation quality drops.")
