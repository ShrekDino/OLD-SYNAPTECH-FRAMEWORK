import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Simplified threshold map derived from DSM-6 (example: Module 01)
THRESHOLDS = {
    "neurodevelopmental": {
        "max_saccade_latency": 300, # ms
        "min_breath_hold": 20      # s
    }
}

class BiologicalConstraintValidator:
    @staticmethod
    def validate(phenotype: str, metrics: Dict[str, float]) -> float:
        """
        Validates completion against DSM-6 markers.
        Returns a penalty factor: 1.0 = pass, >1.0 = fail (higher = worse).
        """
        if phenotype not in THRESHOLDS:
            return 1.0

        thresholds = THRESHOLDS[phenotype]
        penalty = 1.0

        # Example validation logic
        if "saccade_latency" in metrics:
            if metrics["saccade_latency"] > thresholds["max_saccade_latency"]:
                penalty += 0.5
                logger.warning(
                    f"Phenotype {phenotype} failed validation: High saccade latency."
                )

        return penalty
