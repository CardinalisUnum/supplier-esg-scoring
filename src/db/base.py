import os
from sqlalchemy import create_engine
from src.db.models import Base

# Ensure the data directories exist so SQLite doesn't crash on a fresh run
os.makedirs("data/exports", exist_ok=True)

DB_PATH = "data/esg_simulation.db"
# Initialize the SQLAlchemy engine
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

def init_db():
    """Reads models.py and creates the 6-table schema in the database."""
    Base.metadata.create_all(engine)