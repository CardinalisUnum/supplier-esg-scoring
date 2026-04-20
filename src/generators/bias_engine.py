from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class BiasEngine:
    alpha_factor: float = 0.25

    def distort(
        self,
        true_value: float,
        esg_maturity: float,
        bias_direction: int,
        noise_variance: float,
        rng: np.random.Generator,
        floor: float | None = 0.0,
    ) -> float:
        noise = float(rng.normal(0.0, np.sqrt(noise_variance)))
        distortion = bias_direction * self.alpha_factor * (1.0 - esg_maturity)
        reported_value = true_value * (1.0 + distortion + noise)

        if floor is not None:
            return max(floor, float(reported_value))
        return float(reported_value)
