import os
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = "data/esg_simulation.db"
OUTPUT_DIR = "data/exports"

def export_flat_dataset():
    """
    Connects to the SQLite database, joins the true and reported metrics,
    and exports a flattened CSV for Machine Learning use.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    query = """
    SELECT 
        s.id AS supplier_id,
        s.industry,
        s.region,
        s.size,
        s.esg_maturity,
        t.reported_emissions AS true_emissions, 
        r.reported_emissions,
        (t.reported_emissions - r.reported_emissions) AS emissions_bias_gap
    FROM supplier s
    JOIN true_esg_metrics t ON s.id = t.supplier_id
    JOIN reported_esg_metrics r ON s.id = r.supplier_id;
    """
    
    try:
        print("Extracting relational data from SQLite...")
        df = pd.read_sql_query(query, engine)
        
        output_path = os.path.join(OUTPUT_DIR, "flat_esg_dataset.csv")
        df.to_csv(output_path, index=False)
        
        print(f"Success! Exported {len(df)} flattened records to {output_path}")
        
    except Exception as e:
        print(f"An error occurred during export: {e}")

if __name__ == "__main__":
    export_flat_dataset()