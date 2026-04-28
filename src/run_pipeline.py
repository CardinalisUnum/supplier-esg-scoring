import argparse
from sqlalchemy.orm import Session
from src.db.base import engine, Base, init_db
from src.pipeline import (
    load_config, generate_suppliers, seed_indicators, 
    generate_surveys, generate_audits, calculate_scores
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-suppliers", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=0.15)
    parser.add_argument("--beta", type=float, default=1.5)
    args = parser.parse_args()

    # 1. Reset Database [cite: 215]
    Base.metadata.drop_all(engine)
    init_db()
    config = load_config()

    with Session(engine) as session:
        try:
            # 2. Seed Definitions & Suppliers [cite: 226-227]
            indicators = seed_indicators()
            session.add_all(indicators)
            
            suppliers = generate_suppliers(args.n_suppliers, config)
            session.add_all(suppliers)
            session.flush() # Ensure suppliers have IDs

            # 3. Generate Surveys (True vs. Reported) [cite: 228]
            surveys = generate_surveys(suppliers, indicators, alpha=args.alpha, beta=args.beta)
            session.add_all(surveys)
            session.flush()

            # 4. FIXED: Call Audits and Calculate Scores! [cite: 231-232]
            print("Generating sparse audits and calculating risk tiers...")
            audits = generate_audits(suppliers)
            session.add_all(audits)

            scores = calculate_scores(suppliers, surveys)
            session.add_all(scores)

            session.commit()
            print("Success: Full relational dataset committed.")

        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
            raise e

if __name__ == "__main__":
    main()   