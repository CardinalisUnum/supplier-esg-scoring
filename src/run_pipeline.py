from __future__ import annotations

import argparse

from src.pipeline import DataPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic ESG data and persist to SQLite.")
    parser.add_argument("--n-suppliers", type=int, default=200, help="Number of suppliers to generate.")
    parser.add_argument("--db-path", type=str, default="data/esg_simulation.db", help="SQLite database path.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = DataPipeline(db_path=args.db_path, seed=args.seed)
    pipeline.run(n_suppliers=args.n_suppliers)
    print(f"Generated {args.n_suppliers} suppliers into {args.db_path}")


if __name__ == "__main__":
    main()
