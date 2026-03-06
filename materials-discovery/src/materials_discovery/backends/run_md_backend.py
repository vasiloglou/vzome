from __future__ import annotations

from materials_discovery.backends.runner_common import (
    build_parser,
    load_runner_inputs,
    write_runner_output,
)
from materials_discovery.backends.validation_real_fixtures import FixtureBackedMdAdapter


def main() -> None:
    parser = build_parser("Execute the pinned no-DFT MD backend")
    args = parser.parse_args()
    config, candidate = load_runner_inputs(args.input)

    adapter = FixtureBackedMdAdapter()
    info = adapter.info()
    result = adapter.evaluate_candidate(config, candidate)
    write_runner_output(
        args.output,
        {
            "stability_score": result.stability_score,
            "backend_name": info.name,
            "backend_version": info.version,
            "candidate_id": candidate.candidate_id,
        },
    )


if __name__ == "__main__":
    main()
