import os
import subprocess
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# Define the database path based on your codespace structure
DB_PATH = "data/esg_simulation.db"

@st.cache_resource
def get_engine():
    """Establishes the database connection."""
    return create_engine(f"sqlite:///{DB_PATH}", future=True)

def load_emissions_view() -> pd.DataFrame:
    """Queries the SQLite database to join the supplier, true, and reported tables."""
    query = """
    SELECT 
        s.id AS supplier_id,
        s.industry,
        s.size,
        s.region,
        ROUND(s.esg_maturity, 3) AS esg_maturity,
        ROUND(t.reported_emissions, 2) AS true_emissions,
        ROUND(r.reported_emissions, 2) AS reported_emissions,
        ROUND((t.reported_emissions - r.reported_emissions), 2) AS emissions_delta
    FROM supplier s
    JOIN true_esg_metrics t ON s.id = t.supplier_id
    JOIN reported_esg_metrics r ON s.id = r.supplier_id;
    """
    engine = get_engine()
    return pd.read_sql_query(query, engine)

# --- UI Layout & Configuration ---
st.set_page_config(page_title="ProcGen: ESG Synthetic Data Engine", layout="wide")
st.title("🌱 ProcGen: ESG Supplier Data Simulation")
st.markdown("Generate and analyze synthetic supplier data to detect greenwashing behaviors.")

# --- Interactive Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Pipeline Controls")
    
    # 1. Generate New Data Button
    st.subheader("1. Run Simulation")
    num_suppliers = st.slider("Suppliers to generate:", min_value=50, max_value=500, value=100, step=50)
    
    if st.button("🔄 Generate New Suppliers"):
        with st.spinner(f"Running mathematical simulation for {num_suppliers} suppliers..."):
            try:
                # Executes your backend python script via terminal command
                subprocess.run(["python", "src/run_pipeline.py", "--n-suppliers", str(num_suppliers)], check=True)
                st.success("Successfully generated new supplier data!")
                st.rerun() # Refreshes the web page to show new data
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                
    st.divider()
    
    # 2. Export Flat Dataset Button
    st.subheader("2. Prepare for ML")
    if st.button("💾 Export Flat CSV"):
        with st.spinner("Exporting to data/exporters/flat_esg_dataset.csv..."):
            try:
                # Executes your newly fixed flat exporter script
                subprocess.run(["python", "src/exporters/flat_exporter.py"], check=True)
                st.success("Dataset flattened and exported successfully!")
            except Exception as e:
                st.error(f"Export failed: {e}")

# --- Main Dashboard Visualizers ---
try:
    df = load_emissions_view()
    
    # Top KPI Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Suppliers Simulated", len(df))
    col2.metric("Avg ESG Maturity", f"{df['esg_maturity'].mean():.2f}")
    col3.metric("Avg Emissions Gap (Bias)", f"{df['emissions_delta'].mean():.2f}")
    
    # Interactive Dataframe View
    st.subheader("Simulated Metrics Explorer")
    st.dataframe(df, use_container_width=True)
    
except Exception as e:
    st.info("Database not found or empty. Click 'Generate New Suppliers' in the sidebar to initialize the engine.") 



    