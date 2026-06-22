from __future__ import annotations

MASTERY_THRESHOLD = 0.7


def estimate_mastery_from_score(score: float) -> float:
    return max(0.0, min(1.0, score))


def is_mastered(mastery_estimate: float, threshold: float = MASTERY_THRESHOLD) -> bool:
    return mastery_estimate >= threshold
