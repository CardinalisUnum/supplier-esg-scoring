import os
import subprocess
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

DB_PATH = "data/esg_simulation.db"

@st.cache_resource
def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}", future=True)

def load_emissions_view() -> pd.DataFrame:
    # FIXED: Changed t.reported_emissions to t.true_emissions
    query = """
    SELECT 
        s.id AS supplier_id,
        s.industry,
        s.size,
        s.region,
        ROUND(s.esg_maturity, 3) AS esg_maturity,
        ROUND(t.true_emissions, 2) AS true_emissions,
        ROUND(r.reported_emissions, 2) AS reported_emissions,
        ROUND((t.true_emissions - r.reported_emissions), 2) AS emissions_delta
    FROM suppliers s
    JOIN true_esg_metrics t ON s.id = t.supplier_id
    JOIN reported_esg_metrics r ON s.id = r.supplier_id;
    """
    engine = get_engine()
    return pd.read_sql_query(query, engine)

# --- UI Layout & Configuration ---
st.set_page_config(page_title="Project ProcGen | ESG Anomaly Engine", layout="wide")
st.title("👁️‍🗨️ Project ProcGen: ESG Anomaly Engine")
st.markdown("Synthetic data pipeline for detecting corporate greenwashing and ESG reporting bias.")

# --- Interactive Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Pipeline Controls")
    
    st.subheader("1. Run Simulation")
    num_suppliers = st.slider("Suppliers to generate:", min_value=50, max_value=500, value=100, step=50)
    
    if st.button("🔄 Generate New Suppliers"):
        with st.spinner(f"Running mathematical simulation for {num_suppliers} suppliers..."):
            try:
                subprocess.run(["python", "-m", "src.run_pipeline", "--n-suppliers", str(num_suppliers)], check=True)
                st.success("Successfully generated new supplier data! (Refresh the page to view)")
                # Removed st.rerun() so the success message stays on screen
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                
    st.divider()
    
    st.subheader("2. Prepare for ML")
    if st.button("💾 Export Flat CSV"):
        with st.spinner("Exporting to data/exporters/flat_esg_dataset.csv..."):
            try:
                subprocess.run(["python", "-m", "src.exporters.flat_exporter"], check=True)
                st.success("Dataset flattened and exported successfully!")
            except Exception as e:
                st.error(f"Export failed: {e}")

# --- Main Dashboard Visualizers ---
try:
    df = load_emissions_view()
    
    if df.empty:
        st.info("Database exists but is empty. Please run the simulation.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Suppliers Simulated", len(df))
        col2.metric("Avg ESG Maturity", f"{df['esg_maturity'].mean():.2f}")
        col3.metric("Avg Emissions Gap (Bias)", f"{df['emissions_delta'].mean():.2f}")
        
        st.subheader("Simulated Metrics Explorer")
        st.dataframe(df, use_container_width=True)
        
except Exception as e:
    # This will now print the EXACT error if the database or columns fail
    st.error(f"⚠️ SQL Data Error: {e}")