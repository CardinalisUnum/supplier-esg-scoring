import os
import subprocess
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

DB_PATH = "data/esg_simulation.db"

@st.cache_resource
def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}", future=True)

def load_data():
    """Queries the final esg_scores and joined survey data."""
    query = """
    SELECT 
        s.id AS supplier_id, s.industry, s.region, s.size_tier, s.esg_maturity,
        sc.environment_score, sc.social_score, sc.governance_score, 
        sc.overall_esg_score, sc.risk_tier
    FROM suppliers s
    JOIN esg_scores sc ON s.id = sc.supplier_id;
    """
    engine = get_engine()
    return pd.read_sql_query(query, engine)

# --- UI Layout ---
st.set_page_config(page_title="Project ProcGen | Anomaly Engine", layout="wide", page_icon="👁️‍🗨️")

# Custom CSS for "Lively" UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

st.title("👁️‍🗨️ Project ProcGen: ESG Anomaly Engine")
st.markdown("Interactive supply chain simulation for detecting greenwashing in the Philippines.")

# --- Sidebar: SME Control Panel ---
with st.sidebar:
    st.header("🔬 SME Parameter Lab")
    st.info("Adjust these parameters to model different levels of reporting bias.")
    
    alpha = st.slider("Alpha (Bias Magnitude)", 0.0, 0.5, 0.15, help="Baseline intensity of reporting distortion.")
    beta = st.slider("Beta (Maturity Curve)", 1.0, 3.0, 1.5, help="How maturity accelerates reporting bias.")
    
    n_suppliers = st.number_input("Suppliers to Generate", 50, 1000, 250)
    
    if st.button("🚀 Re-Run Simulation", use_container_width=True):
        with st.spinner("Calibrating mathematical distributions..."):
            try:
                # Passing alpha and beta directly to your pipeline
                subprocess.run([
                    "python", "-m", "src.run_pipeline", 
                    "--n-suppliers", str(n_suppliers),
                    "--alpha", str(alpha),
                    "--beta", str(beta)
                ], check=True)
                st.balloons() # Success Animation
                st.success("Simulation Complete!")
            except Exception as e:
                st.error(f"Engine Error: {e}")

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Risk Dashboard", "🔍 Anomaly Analysis", "💾 Data Export"])

with tab1:
    try:
        df = load_data()
        
        # Row 1: KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Suppliers", len(df))
        m2.metric("Avg ESG Score", f"{df['overall_esg_score'].mean():.1f}")
        m3.metric("High Risk Count", len(df[df['risk_tier'] == 'high']))
        m4.metric("Avg Maturity", f"{df['esg_maturity'].mean():.2f}")

        # Row 2: Business Charts
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Risk Tiers by Philippine Region")
            fig_reg = px.histogram(df, x="region", color="risk_tier", 
                                  barmode="group", color_discrete_map={'high':'#ef4444', 'med':'#f59e0b', 'low':'#10b981'})
            st.plotly_chart(fig_reg, use_container_width=True)
        
        with c2:
            st.subheader("Industry Risk Distribution")
            fig_ind = px.sunburst(df, path=['industry', 'risk_tier'], values='overall_esg_score',
                                  color='overall_esg_score', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_ind, use_container_width=True)

    except Exception:
        st.warning("Database empty. Use the sidebar to generate data.")

with tab2:
    if 'df' in locals():
        st.subheader("The Maturity vs. Score Relationship")
        st.markdown("This chart visualizes how latent ESG maturity correlates with final scores [cite: 49-50, 162].")
        fig_scatter = px.scatter(df, x="esg_maturity", y="overall_esg_score", 
                                 color="risk_tier", hover_data=['industry', 'region'],
                                 trendline="ols", title="Latent Maturity vs. Calculated ESG Score")
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Raw Relational Export")
    if 'df' in locals():
        st.dataframe(df, use_container_width=True)
        if st.button("📥 Export Flattened Dataset"):
             subprocess.run(["python", "-m", "src.exporters.flat_exporter"], check=True)
             st.toast("File saved to data/exports/", icon="✅")        