from __future__ import annotations

from pathlib import Path

from materials_discovery.common.schema import SystemConfig


def load_seed_zomic_text(path: Path | None) -> str | None:
    if path is None:
        return None
    if not path.exists():
        raise FileNotFoundError(f"Seed Zomic file not found: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Seed Zomic file is empty: {path}")
    return text


def build_generation_prompt(
    config: SystemConfig,
    *,
    count: int,
    seed_zomic_text: str | None,
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

    return "\n".join(lines).rstrip() + "\n"
