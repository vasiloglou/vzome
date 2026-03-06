from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from materials_discovery.common.schema import CandidateRecord, SystemConfig


@dataclass(frozen=True)
class IngestBackendInfo:
    name: str
    version: str


@dataclass(frozen=True)
class AdapterInfo:
    name: str
    version: str


@dataclass(frozen=True)
class CommitteeEvaluation:
    energies: dict[str, float]


@dataclass(frozen=True)
class PhononEvaluation:
    imaginary_modes: int


@dataclass(frozen=True)
class MdEvaluation:
    stability_score: float


@dataclass(frozen=True)
class XrdEvaluation:
    confidence: float


class IngestBackend(Protocol):
    def info(self) -> IngestBackendInfo:
        ...

    def load_rows(self, config: SystemConfig, fixture_path: Path | None) -> list[dict[str, Any]]:
        ...


class CommitteeAdapter(Protocol):
    def info(self) -> AdapterInfo:
        ...

    def evaluate_candidate(
        self,
        config: SystemConfig,
        candidate: CandidateRecord,
    ) -> CommitteeEvaluation:
        ...


class PhononAdapter(Protocol):
    def info(self) -> AdapterInfo:
        ...

    def evaluate_candidate(
        self,
        config: SystemConfig,
        candidate: CandidateRecord,
    ) -> PhononEvaluation:
        ...


class MdAdapter(Protocol):
    def info(self) -> AdapterInfo:
        ...

    def evaluate_candidate(
        self,
        config: SystemConfig,
        candidate: CandidateRecord,
    ) -> MdEvaluation:
        ...


class XrdAdapter(Protocol):
    def info(self) -> AdapterInfo:
        ...

    def evaluate_candidate(
        self,
        config: SystemConfig,
        candidate: CandidateRecord,
    ) -> XrdEvaluation:
        ...
