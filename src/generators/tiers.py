from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class TierGeneratorBase(ABC):
    @abstractmethod
    def generate(self, supplier_features: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
        raise NotImplementedError


class MechanisticTierGenerator(TierGeneratorBase):
    def __init__(self, emission_factor_by_industry: dict[str, float], grid_intensity_by_region: dict[str, float]):
        self.emission_factor_by_industry = emission_factor_by_industry
        self.grid_intensity_by_region = grid_intensity_by_region

    def generate(self, supplier_features: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
        spend_or_output = float(supplier_features["spend_or_output"])
        industry = str(supplier_features["industry"])
        region = str(supplier_features["region"])
        efficiency = float(supplier_features["efficiency"])

        industry_factor = self.emission_factor_by_industry.get(industry, 0.7)
        grid_intensity = self.grid_intensity_by_region.get(region, 0.5)

        true_emissions = spend_or_output * industry_factor * grid_intensity * (1.0 / efficiency)
        return {"true_emissions": max(0.0, true_emissions)}


class BehavioralTierGenerator(TierGeneratorBase):
    def __init__(self, base_rate: float, size_factor_by_size: dict[str, float]):
        self.base_rate = base_rate
        self.size_factor_by_size = size_factor_by_size

    def generate(self, supplier_features: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
        size = str(supplier_features["size"])
        esg_maturity = float(supplier_features["esg_maturity"])

        size_factor = self.size_factor_by_size.get(size, 1.0)
        lam = self.base_rate * size_factor * (1.0 - esg_maturity)
        true_violations = int(rng.poisson(lam=max(0.0, lam)))

        headcount = float(supplier_features["headcount"])
        true_injury_rate = (true_violations / max(1.0, headcount)) * 200000.0

        return {
            "true_violations": max(0, true_violations),
            "true_injury_rate": max(0.0, true_injury_rate),
        }


class DeclarativeTierGenerator(TierGeneratorBase):
    def __init__(self, size_effect_by_size: dict[str, float]):
        self.size_effect_by_size = size_effect_by_size

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + np.exp(-x))

    def generate(self, supplier_features: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
        esg_maturity = float(supplier_features["esg_maturity"])
        size = str(supplier_features["size"])

        size_effect = self.size_effect_by_size.get(size, 0.0)
        p_policy_exists = self._sigmoid(esg_maturity + size_effect)
        true_policy_exists = bool(rng.uniform(0.0, 1.0) < p_policy_exists)

        return {"true_policy_exists": true_policy_exists}
