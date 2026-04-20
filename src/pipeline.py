from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sqlalchemy.orm import Session

from src.db.base import get_session_factory, init_db
from src.db.models import ReportedESGMetrics, Supplier, TrueESGMetrics
from src.generators.bias_engine import BiasEngine
from src.generators.tiers import BehavioralTierGenerator, DeclarativeTierGenerator, MechanisticTierGenerator


@dataclass
class DataPipeline:
    db_path: str | None = None
    seed: int = 42

    def __post_init__(self) -> None:
        self.rng = np.random.default_rng(self.seed)
        self.bias_engine = BiasEngine(alpha_factor=0.2)

        self.mechanistic_tier = MechanisticTierGenerator(
            emission_factor_by_industry={
                "manufacturing": 0.95,
                "technology": 0.35,
                "retail": 0.55,
                "logistics": 1.15,
                "agriculture": 1.35,
            },
            grid_intensity_by_region={
                "NA": 0.45,
                "EMEA": 0.35,
                "APAC": 0.65,
                "LATAM": 0.55,
            },
        )
        self.behavioral_tier = BehavioralTierGenerator(
            base_rate=6.0,
            size_factor_by_size={"small": 0.6, "medium": 1.0, "large": 1.5},
        )
        self.declarative_tier = DeclarativeTierGenerator(
            size_effect_by_size={"small": -0.2, "medium": 0.0, "large": 0.2}
        )

        init_db(self.db_path)
        self.session_factory = get_session_factory(self.db_path)

    def _sample_supplier_features(self) -> dict[str, float | str]:
        industry = self.rng.choice(["manufacturing", "technology", "retail", "logistics", "agriculture"])
        size = self.rng.choice(["small", "medium", "large"], p=[0.45, 0.4, 0.15])
        region = self.rng.choice(["NA", "EMEA", "APAC", "LATAM"])

        headcount_map = {"small": 120.0, "medium": 600.0, "large": 2500.0}
        spend_map = {"small": 1.2e6, "medium": 8.5e6, "large": 3.5e7}

        esg_maturity = float(self.rng.uniform(0.05, 0.95))
        efficiency = float(self.rng.uniform(0.3, 1.0))

        return {
            "industry": str(industry),
            "size": str(size),
            "region": str(region),
            "esg_maturity": esg_maturity,
            "efficiency": efficiency,
            "headcount": headcount_map[str(size)] * float(self.rng.uniform(0.7, 1.3)),
            "spend_or_output": spend_map[str(size)] * float(self.rng.uniform(0.7, 1.4)),
        }

    def _compute_true_metrics(self, supplier_features: dict[str, float | str]) -> dict[str, float | int | bool]:
        outputs: dict[str, float | int | bool] = {}
        outputs.update(self.mechanistic_tier.generate(supplier_features, self.rng))
        outputs.update(self.behavioral_tier.generate(supplier_features, self.rng))
        outputs.update(self.declarative_tier.generate(supplier_features, self.rng))
        return outputs

    def _compute_reported_metrics(
        self,
        true_metrics: dict[str, float | int | bool],
        esg_maturity: float,
    ) -> dict[str, float | int | bool]:
        reported_emissions = self.bias_engine.distort(
            true_value=float(true_metrics["true_emissions"]),
            esg_maturity=esg_maturity,
            bias_direction=-1,
            noise_variance=0.015,
            rng=self.rng,
            floor=0.0,
        )
        reported_violations = self.bias_engine.distort(
            true_value=float(true_metrics["true_violations"]),
            esg_maturity=esg_maturity,
            bias_direction=-1,
            noise_variance=0.03,
            rng=self.rng,
            floor=0.0,
        )
        reported_injury_rate = self.bias_engine.distort(
            true_value=float(true_metrics["true_injury_rate"]),
            esg_maturity=esg_maturity,
            bias_direction=-1,
            noise_variance=0.03,
            rng=self.rng,
            floor=0.0,
        )

        true_policy = bool(true_metrics["true_policy_exists"])
        if true_policy:
            policy_claim_probability = min(1.0, 0.85 + 0.15 * esg_maturity)
        else:
            policy_claim_probability = max(0.0, 0.35 - 0.25 * esg_maturity)
        reported_policy_exists = bool(self.rng.uniform(0.0, 1.0) < policy_claim_probability)

        return {
            "reported_emissions": float(reported_emissions),
            "reported_violations": int(round(reported_violations)),
            "reported_injury_rate": float(reported_injury_rate),
            "reported_policy_exists": reported_policy_exists,
        }

    def generate_one(self, session: Session) -> Supplier:
        features = self._sample_supplier_features()

        supplier = Supplier(
            industry=str(features["industry"]),
            size=str(features["size"]),
            region=str(features["region"]),
            esg_maturity=float(features["esg_maturity"]),
            efficiency=float(features["efficiency"]),
        )
        session.add(supplier)
        session.flush()

        true_metrics = self._compute_true_metrics(features)
        reported_metrics = self._compute_reported_metrics(true_metrics, float(features["esg_maturity"]))

        session.add(
            TrueESGMetrics(
                supplier_id=supplier.id,
                true_emissions=float(true_metrics["true_emissions"]),
                true_violations=int(true_metrics["true_violations"]),
                true_injury_rate=float(true_metrics["true_injury_rate"]),
                true_policy_exists=bool(true_metrics["true_policy_exists"]),
            )
        )
        session.add(
            ReportedESGMetrics(
                supplier_id=supplier.id,
                reported_emissions=float(reported_metrics["reported_emissions"]),
                reported_violations=int(reported_metrics["reported_violations"]),
                reported_injury_rate=float(reported_metrics["reported_injury_rate"]),
                reported_policy_exists=bool(reported_metrics["reported_policy_exists"]),
            )
        )

        return supplier

    def run(self, n_suppliers: int = 100) -> None:
        with self.session_factory() as session:
            for _ in range(n_suppliers):
                self.generate_one(session)
            session.commit()
