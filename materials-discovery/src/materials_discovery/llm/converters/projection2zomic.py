from __future__ import annotations

from typing import Any

from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm.converters.record2zomic import candidate_to_zomic


def projection_payload_to_zomic(payload: dict[str, Any]) -> Any:
    positions = payload.get("positions", [])
    composition = payload.get("composition") or {}
    model_id = str(payload.get("model_id", "pyqcstrc_projection"))
    system = str(payload.get("system", "Unknown"))
    candidate = CandidateRecord.model_validate(
        {
            "candidate_id": model_id,
            "system": system,
            "template_family": "pyqcstrc_projection",
            "cell": {
                "a": 10.0,
                "b": 10.0,
                "c": 10.0,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            "sites": [
                {
                    "label": str(position["label"]),
                    "qphi": position["qphi"],
                    "species": str(position["species"]),
                    "occ": 1.0,
                }
                for position in positions
            ],
            "composition": composition,
            "provenance": {
                "source_model_id": model_id,
                "coordinate_system": payload.get("coordinate_system"),
                "source": payload.get("source"),
            },
        }
    )
    example = candidate_to_zomic(candidate)
    provenance = example.provenance.model_copy(
        update={
            "source_family": "pyqcstrc_projection",
            "source_path": f"pyqcstrc_projection:{model_id}",
            "source_record_id": model_id,
        }
    )
    properties = dict(example.properties)
    properties["coordinate_system"] = payload.get("coordinate_system")
    properties["source_model_id"] = model_id
    properties["projection_source"] = payload.get("source")
    return example.model_copy(update={"provenance": provenance, "properties": properties})
