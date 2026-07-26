"""Stage tracker — deployment stage definitions and progress calculation."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# Ordered deployment stages with their weight in percentage.
STAGES: List[Tuple[str, int]] = [
    ('VALIDATION', 5),
    ('PROVISIONING', 20),
    ('ARTIFACT_TRANSFER', 5),
    ('TERRAFORM', 15),
    ('ANSIBLE', 15),
    ('DOCKER', 15),
    ('VERIFICATION', 10),
    ('COMPLETED', 15),
]

STAGE_NAMES = [name for name, _ in STAGES]
STAGE_WEIGHTS: Dict[str, int] = {name: weight for name, weight in STAGES}


class StageTracker:
    """Pure functions for deployment stage tracking and progress calculation."""

    @staticmethod
    def calculate_progress(completed_stages: List[str]) -> int:
        """Return 0–100 based on sum of completed stage weights."""
        total = sum(
            STAGE_WEIGHTS.get(s, 0)
            for s in completed_stages
            if s in STAGE_WEIGHTS
        )
        return min(total, 100)

    @staticmethod
    def get_stage_info(stage_name: str) -> Optional[dict]:
        """Return {name, weight, order} for a given stage."""
        for i, (name, weight) in enumerate(STAGES):
            if name == stage_name:
                return {'name': name, 'weight': weight, 'order': i}
        return None

    @staticmethod
    def get_all_stages() -> List[dict]:
        """Return all stages with metadata."""
        return [
            {'name': name, 'weight': weight, 'order': i}
            for i, (name, weight) in enumerate(STAGES)
        ]

    @staticmethod
    def get_next_stage(current: str) -> Optional[str]:
        """Return the stage after current, or None if last."""
        for i, (name, _) in enumerate(STAGES):
            if name == current and i + 1 < len(STAGES):
                return STAGES[i + 1][0]
        return None

    @staticmethod
    def map_phase_to_stage(phase: str) -> Optional[str]:
        """Map an orchestrator phase string to a stage name."""
        mapping = {
            'initializing': 'VALIDATION',
            'provisioning': 'PROVISIONING',
            'deploying': 'DOCKER',
            'completed': 'COMPLETED',
            'failed': None,
        }
        return mapping.get(phase)
