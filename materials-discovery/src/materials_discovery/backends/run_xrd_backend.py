from __future__ import annotations

from materials_discovery.backends.native_providers import evaluate_xrd_provider
from materials_discovery.backends.runner_common import (
    build_parser,
    load_runner_inputs,
    write_runner_output,
)
from materials_discovery.backends.validation_real_fixtures import FixtureBackedXrdAdapter


def main() -> None:
    parser = build_parser("Execute the pinned no-DFT XRD backend")
    args = parser.parse_args()
    config, candidate = load_runner_inputs(args.input)

    provider = config.backend.xrd_provider or "pinned"
    if provider == "pinned":
        adapter = FixtureBackedXrdAdapter()
        info = adapter.info()
        result = adapter.evaluate_candidate(config, candidate)
        backend_name = info.name
        backend_version = info.version
    else:
        result = evaluate_xrd_provider(config, candidate)
        backend_name = provider
        backend_version = "native"
    write_runner_output(
        args.output,
        {
            "confidence": result.confidence,
            "backend_name": backend_name,
            "backend_version": backend_version,
            "candidate_id": candidate.candidate_id,
        },
    )


if __name__ == "__main__":
    main()
