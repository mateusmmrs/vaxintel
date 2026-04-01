"""Weights for the composite opportunity index."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScoreWeights:
    """Store weights for the three analytic blocks."""

    animal: float
    sanitary: float
    economic: float

    def normalized(self) -> "ScoreWeights":
        """Rescale weights so they sum to one."""
        total = self.animal + self.sanitary + self.economic
        if total <= 0:
            raise ValueError("Weights must sum to a positive value.")
        return ScoreWeights(
            animal=self.animal / total,
            sanitary=self.sanitary / total,
            economic=self.economic / total,
        )


DEFAULT_WEIGHTS = ScoreWeights(animal=0.40, sanitary=0.30, economic=0.30)

