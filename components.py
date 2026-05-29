import plotly.graph_objects as go
import pandas as pd

def create_drift_chart(history):
    """
    Creates an interactive Plotly chart showing semantic similarity over the chain.
    """
    if not history:
        return None
        
    data = []
    # Start with original text at index 0 and score 1.0
    data.append({"Hop": 0, "Language": history[0].source_language, "Score": 1.0, "Type": "Baseline"})
    
    for i, step in enumerate(history):
        data.append({
            "Hop": i + 1,
            "Language": step.target_language,
            "Score": step.semantic_score,
            "Type": "Reflection" if step.is_reflected else "Standard"
        })
        
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    # Add the main line
    fig.add_trace(go.Scatter(
        x=df["Hop"],
        y=df["Score"],
        mode='lines+markers',
        name='Semantic Similarity',
        line=dict(color='#00d1b2', width=4),
        marker=dict(size=12, color=df["Score"], colorscale='Viridis', showscale=False),
        hovertemplate="<b>Hop %{x}</b><br>Language: %{customdata}<br>Score: %{y:.4f}<extra></extra>",
        customdata=df["Language"]
    ))
    
    # Add a horizontal line for the threshold
    fig.add_shape(
        type="line", line=dict(dash="dash", color="red", width=2),
        x0=0, x1=len(history), y0=0.75, y1=0.75
    )
    
    fig.update_layout(
        title="Semantic Drift Analysis",
        xaxis_title="Translation Hop",
        yaxis_title="Similarity Score (Cosine)",
        yaxis_range=[0, 1.05],
        template="plotly_dark",
        margin=dict(l=40, r=40, t=60, b=40),
        height=400
    )
    
    return fig

def render_agent_log(step_name, data):
    """Renders a professional looking log entry for the UI."""
    import streamlit as st
    
    # Map step names to icons and colors
    meta = {
        "translate": ("🤖", "blue"),
        "analyze": ("🔍", "green"),
        "critic": ("⚖️", "orange"),
        "reflect": ("🔄", "red"),
        "record_step": ("💾", "gray")
    }
    icon, color = meta.get(step_name, ("⚙️", "gray"))
    
    with st.expander(f"{icon} Agent: {step_name.upper()}", expanded=True):
        if "current_thoughts" in data:
            st.markdown(f"**Agent Reasoning:** *{data['current_thoughts']}*")
            
        if step_name == "translate":
            st.info(f"**Draft Output:** {data.get('current_translation', '')[:200]}...")
        elif step_name == "analyze":
            st.metric("Semantic Score", f"{data.get('current_semantic_score', 0):.4f}")
        elif step_name == "critic":
            if data.get("reflection_needed"):
                st.error(f"**Critic rejected translation:** {data.get('last_critic_feedback', 'No feedback')}")
            else:
                st.success("**Critic approved translation.**")
        elif step_name == "reflect":
            st.warning(f"**Reflection Loop Triggered.** Strategy formulated.")

def get_mermaid_graph():
    """Returns the Mermaid JS code for the architecture."""
    return """
    graph TD
        A[Start] --> B(Translate Agent)
        B --> C(Semantic Analyzer)
        C --> D(Critic Agent)
        D -- Reject --> E(Reflection Agent)
        E --> B
        D -- Approve --> F(Record History)
        F -- Next Language --> B
        F -- Complete --> G[Final Research Report]
        
        style B fill:#f9f,stroke:#333,stroke-width:2px
        style C fill:#ccf,stroke:#333,stroke-width:2px
        style D fill:#fcf,stroke:#333,stroke-width:2px
        style E fill:#f99,stroke:#333,stroke-width:2px
    """
