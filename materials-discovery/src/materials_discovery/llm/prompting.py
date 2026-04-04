from __future__ import annotations

from pathlib import Path

from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.schema import LlmEvalSetExample

_RELEASE_ORDER = {"gold": 0, "silver": 1, "pending": 2, "reject": 3}


def load_seed_zomic_text(path: Path | None) -> str | None:
    if path is None:
        return None
    if not path.exists():
        raise FileNotFoundError(f"Seed Zomic file not found: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Seed Zomic file is empty: {path}")
    return text


def _target_composition(config: SystemConfig) -> dict[str, float]:
    target: dict[str, float] = {}
    for species in config.species:
        bounds = config.composition_bounds[species]
        target[species] = (bounds.min + bounds.max) / 2.0
    total = sum(target.values())
    if total <= 0.0:
        return target
    return {species: value / total for species, value in target.items()}


def _composition_distance(target: dict[str, float], example: LlmEvalSetExample) -> float:
    species = sorted(set(target) | set(example.composition))
    return sum(abs(target.get(key, 0.0) - example.composition.get(key, 0.0)) for key in species)


def select_conditioning_examples(
    config: SystemConfig,
    examples: list[LlmEvalSetExample],
    *,
    max_examples: int,
) -> list[LlmEvalSetExample]:
    target = _target_composition(config)
    same_system = [example for example in examples if example.system == config.system_name]
    pool = same_system if same_system else list(examples)
    pool.sort(
        key=lambda example: (
            _composition_distance(target, example),
            _RELEASE_ORDER.get(example.release_tier, 99),
            example.example_id,
        )
    )
    return pool[:max_examples]


def build_generation_prompt(
    config: SystemConfig,
    *,
    count: int,
    seed_zomic_text: str | None,
    conditioning_examples: list[LlmEvalSetExample] | None = None,
    instruction_deltas: list[str] | None = None,
) -> str:
    prompt_template = (
        config.llm_generate.prompt_template
        if config.llm_generate is not None
        else "zomic_generate_v1"
    )
    lines = [
        f"PROMPT_TEMPLATE: {prompt_template}",
        f"SYSTEM_NAME: {config.system_name}",
        f"TEMPLATE_FAMILY: {config.template_family}",
        f"REQUESTED_COUNT: {count}",
        "COMPOSITION_BOUNDS:",
    ]
    for species in config.species:
        bounds = config.composition_bounds[species]
        lines.append(f"- {species}: min={bounds.min:.4f}, max={bounds.max:.4f}")

    lines.extend(
        [
            "",
            "Generate valid Zomic text for a quasicrystal-compatible motif.",
            "Return only Zomic text with no prose, markdown, explanations, or fences.",
            "Use labels where appropriate and keep the script self-contained.",
        ]
    )
    if instruction_deltas:
        lines.extend(["", "INSTRUCTION_DELTAS"])
        for delta in instruction_deltas:
            lines.append(f"- {delta}")
    if seed_zomic_text is not None:
        lines.extend(
            [
                "",
                "SEED_ZOMIC",
                seed_zomic_text.rstrip(),
                "END_SEED_ZOMIC",
                "Produce a valid variation that stays compatible with the same system constraints.",
            ]
        )

    if conditioning_examples:
        lines.extend(["", "CONDITIONING_EXAMPLES"])
        for index, example in enumerate(conditioning_examples, start=1):
            composition = ", ".join(
                f"{species}={fraction:.4f}" for species, fraction in sorted(example.composition.items())
            )
            lines.extend(
                [
                    f"BEGIN_EXAMPLE {index}",
                    f"EXAMPLE_ID: {example.example_id}",
                    f"SYSTEM: {example.system}",
                    f"RELEASE_TIER: {example.release_tier}",
                    f"COMPOSITION: {composition}",
                    "ZOMIC:",
                    example.zomic_text.rstrip(),
                    f"END_EXAMPLE {index}",
                ]
            )
        lines.append(
            "Use the examples only as conditioning context; preserve the current system and composition bounds."
        )

    return "\n".join(lines).rstrip() + "\n"
