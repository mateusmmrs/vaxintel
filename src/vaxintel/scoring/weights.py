"""Weights for the VaxIntel v2 opportunity architecture."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpportunityWeights:
    """Store weights for a three-block opportunity score."""

    animal: float
    sanitary: float
    economic: float

    def normalized(self) -> "OpportunityWeights":
        """Return weights rescaled to sum to one."""
        total = self.animal + self.sanitary + self.economic
        if total <= 0:
            raise ValueError("Opportunity weights must sum to a positive value.")
        return OpportunityWeights(
            animal=self.animal / total,
            sanitary=self.sanitary / total,
            economic=self.economic / total,
        )


@dataclass(frozen=True, slots=True)
class CombinedModeWeights:
    """Store the blend between beef and dairy modes."""

    beef: float
    dairy: float

    def normalized(self) -> "CombinedModeWeights":
        """Return weights rescaled to sum to one."""
        total = self.beef + self.dairy
        if total <= 0:
            raise ValueError("Combined mode weights must sum to a positive value.")
        return CombinedModeWeights(
            beef=self.beef / total,
            dairy=self.dairy / total,
        )


@dataclass(frozen=True, slots=True)
class ScoreConfig:
    """Group all scoring weights required by the v2 architecture."""

    beef_opportunity: OpportunityWeights
    dairy_opportunity: OpportunityWeights
    combined_mode: CombinedModeWeights


DEFAULT_SCORE_CONFIG = ScoreConfig(
    beef_opportunity=OpportunityWeights(animal=0.40, sanitary=0.30, economic=0.30),
    dairy_opportunity=OpportunityWeights(animal=0.35, sanitary=0.25, economic=0.40),
    combined_mode=CombinedModeWeights(beef=0.50, dairy=0.50),
)
