from __future__ import annotations

DEFAULT_MAX_INVALID_RATE = 0.20
DEFAULT_MAX_DUPLICATE_RATE = 0.95
DEFAULT_MIN_DEDUPED_ROWS = 1


def evaluate_ingest_quality(
    raw_count: int,
    matched_count: int,
    deduped_count: int,
    invalid_count: int,
    max_invalid_rate: float = DEFAULT_MAX_INVALID_RATE,
    max_duplicate_rate: float = DEFAULT_MAX_DUPLICATE_RATE,
    min_deduped_rows: int = DEFAULT_MIN_DEDUPED_ROWS,
) -> dict[str, float | int | bool]:
    invalid_rate = 0.0 if raw_count == 0 else invalid_count / raw_count
    duplicate_rate = 0.0 if matched_count == 0 else 1.0 - (deduped_count / matched_count)

    passed = (
        invalid_rate <= max_invalid_rate
        and duplicate_rate <= max_duplicate_rate
        and deduped_count >= min_deduped_rows
    )

    return {
        "invalid_rate": round(invalid_rate, 6),
        "duplicate_rate": round(duplicate_rate, 6),
        "deduped_count": deduped_count,
        "passed": passed,
    }
