from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.active_learning.train_surrogate import feature_names
from materials_discovery.common.benchmarking import load_calibration_profile
from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import SystemConfig


def test_benchmark_profile_loads_for_real_config() -> None:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))

    names = feature_names(config)
    profile = load_calibration_profile(config, feature_names=names)

    assert profile.source.endswith("al_cu_fe_benchmark.json")
    assert set(profile.stable_feature_centroid) == set(names)
    assert set(profile.unstable_feature_centroid) == set(names)
    assert 0.0 < profile.delta_hull_soft_cap < 0.10
    assert 0.0 < profile.uncertainty_soft_cap < 0.05
    assert 0.5 < profile.md_stability_floor < 0.9
    assert 0.5 < profile.xrd_confidence_floor < 0.9
    assert 0.05 < profile.report_distinctiveness_floor < 0.2
    assert 0.2 < profile.ood_ceiling < 0.6
    assert 0.4 < profile.active_learning_threshold < 0.8


# ---------------------------------------------------------------------------
# Phase 4: reference-aware benchmark config assertions
# ---------------------------------------------------------------------------


class TestAlCuFeReferenceAwareConfig:
    """Al-Cu-Fe Phase 4 benchmark lane config assertions."""

    @pytest.fixture()
    def config(self) -> SystemConfig:
        workspace = Path(__file__).resolve().parents[1]
        config_path = workspace / "configs" / "systems" / "al_cu_fe_reference_aware.yaml"
        return SystemConfig.model_validate(load_yaml(config_path))

    def test_config_validates_as_system_config(self, config: SystemConfig) -> None:
        assert config.system_name == "Al-Cu-Fe"
        assert config.template_family == "icosahedral_approximant_1_1"

    def test_config_uses_source_registry_ingest_adapter(self, config: SystemConfig) -> None:
        assert config.backend.ingest_adapter == "source_registry_v1"

    def test_config_uses_real_backend_mode(self, config: SystemConfig) -> None:
        assert config.backend.mode == "real"

    def test_config_has_benchmark_corpus(self, config: SystemConfig) -> None:
        assert config.backend.benchmark_corpus is not None
        assert "al_cu_fe" in config.backend.benchmark_corpus.lower()

    def test_config_has_validation_snapshot(self, config: SystemConfig) -> None:
        assert config.backend.validation_snapshot is not None
        assert "al_cu_fe" in config.backend.validation_snapshot.lower()

    def test_config_has_reference_pack_block(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None

    def test_reference_pack_id_is_explicit(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        assert config.ingestion.reference_pack.pack_id == "al_cu_fe_v1"

    def test_reference_pack_has_two_members(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        assert len(config.ingestion.reference_pack.members) == 2

    def test_reference_pack_member_source_keys_are_deterministic(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        keys = [m.source_key for m in config.ingestion.reference_pack.members]
        assert "hypodx" in keys
        assert "materials_project" in keys

    def test_reference_pack_priority_order_is_explicit(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        order = config.ingestion.reference_pack.priority_order
        assert len(order) >= 2
        # hypodx (QC-specific) must be first
        assert order[0] == "hypodx"
        assert "materials_project" in order

    def test_reference_pack_staged_paths_are_set(self, config: SystemConfig) -> None:
        """Both members declare explicit staged paths — no guessing required."""
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        for member in config.ingestion.reference_pack.members:
            assert member.staged_canonical_path is not None
            assert member.staged_canonical_path.endswith("canonical_records.jsonl")

    def test_reference_pack_member_snapshot_ids_are_deterministic(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        for member in config.ingestion.reference_pack.members:
            assert member.snapshot_id  # non-empty
            assert member.snapshot_id.strip() == member.snapshot_id

    def test_benchmark_corpus_and_validation_snapshot_wired(self, config: SystemConfig) -> None:
        """Both corpus and snapshot must be set for a benchmark-ready lane."""
        assert config.backend.benchmark_corpus is not None
        assert config.backend.validation_snapshot is not None

    def test_reference_pack_genuinely_multi_source(self, config: SystemConfig) -> None:
        """Pack members come from distinct source keys — not the same source twice."""
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        keys = [m.source_key for m in config.ingestion.reference_pack.members]
        assert len(keys) == len(set(keys)), "all member source_keys must be distinct"


class TestScZnReferenceAwareConfig:
    """Sc-Zn Phase 4 benchmark lane config assertions."""

    @pytest.fixture()
    def config(self) -> SystemConfig:
        workspace = Path(__file__).resolve().parents[1]
        config_path = workspace / "configs" / "systems" / "sc_zn_reference_aware.yaml"
        return SystemConfig.model_validate(load_yaml(config_path))

    def test_config_validates_as_system_config(self, config: SystemConfig) -> None:
        assert config.system_name == "Sc-Zn"
        assert config.template_family == "cubic_proxy_1_0"

    def test_config_uses_source_registry_ingest_adapter(self, config: SystemConfig) -> None:
        assert config.backend.ingest_adapter == "source_registry_v1"

    def test_config_uses_real_backend_mode(self, config: SystemConfig) -> None:
        assert config.backend.mode == "real"

    def test_config_preserves_zomic_design_path(self, config: SystemConfig) -> None:
        """Zomic authoring path from sc_zn_real.yaml must be preserved."""
        assert config.zomic_design is not None
        assert "sc_zn" in config.zomic_design.lower()
        assert config.zomic_design.endswith(".yaml")

    def test_config_has_benchmark_corpus(self, config: SystemConfig) -> None:
        assert config.backend.benchmark_corpus is not None
        assert "sc_zn" in config.backend.benchmark_corpus.lower()

    def test_config_has_validation_snapshot(self, config: SystemConfig) -> None:
        assert config.backend.validation_snapshot is not None
        assert "sc_zn" in config.backend.validation_snapshot.lower()

    def test_config_has_reference_pack_block(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None

    def test_reference_pack_id_is_explicit(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        assert config.ingestion.reference_pack.pack_id == "sc_zn_v1"

    def test_reference_pack_has_two_members(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        assert len(config.ingestion.reference_pack.members) == 2

    def test_reference_pack_member_source_keys_are_deterministic(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        keys = [m.source_key for m in config.ingestion.reference_pack.members]
        assert "hypodx" in keys
        # second source must be from Phase 2 adapter set
        second_sources = {"cod", "oqmd", "jarvis", "materials_project"}
        assert any(k in second_sources for k in keys), f"expected a Phase 2 second source, got {keys}"

    def test_reference_pack_priority_order_is_explicit(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        order = config.ingestion.reference_pack.priority_order
        assert len(order) >= 2
        # hypodx (QC-specific) must be first
        assert order[0] == "hypodx"

    def test_reference_pack_genuinely_multi_source(self, config: SystemConfig) -> None:
        assert config.ingestion is not None
        assert config.ingestion.reference_pack is not None
        keys = [m.source_key for m in config.ingestion.reference_pack.members]
        assert len(keys) == len(set(keys)), "all member source_keys must be distinct"

    def test_benchmark_corpus_and_validation_snapshot_wired(self, config: SystemConfig) -> None:
        assert config.backend.benchmark_corpus is not None
        assert config.backend.validation_snapshot is not None


# ---------------------------------------------------------------------------
# Second-source fixture existence
# ---------------------------------------------------------------------------


def test_mp_fixture_exists_for_al_cu_fe() -> None:
    """The thin Materials Project fixture for Al-Cu-Fe multi-source proof exists."""
    workspace = Path(__file__).resolve().parents[1]
    fixture_path = workspace / "data" / "external" / "sources" / "materials_project" / "mp_fixture_v1" / "canonical_records.jsonl"
    assert fixture_path.exists(), f"missing second-source fixture: {fixture_path}"
    rows = [line for line in fixture_path.read_text().splitlines() if line.strip()]
    assert len(rows) >= 1, "MP fixture must have at least 1 record"


def test_cod_fixture_exists_for_sc_zn() -> None:
    """The thin COD fixture for Sc-Zn multi-source proof exists."""
    workspace = Path(__file__).resolve().parents[1]
    fixture_path = workspace / "data" / "external" / "sources" / "cod" / "cod_fixture_v1" / "canonical_records.jsonl"
    assert fixture_path.exists(), f"missing second-source fixture: {fixture_path}"
    rows = [line for line in fixture_path.read_text().splitlines() if line.strip()]
    assert len(rows) >= 1, "COD fixture must have at least 1 record"


def test_hypodx_pinned_fixture_exists_for_al_cu_fe() -> None:
    """The staged HYPOD-X pinned canonical records fixture exists."""
    workspace = Path(__file__).resolve().parents[1]
    fixture_path = workspace / "data" / "external" / "sources" / "hypodx" / "hypodx_pinned_2026_03_09" / "canonical_records.jsonl"
    assert fixture_path.exists(), f"missing hypodx pinned fixture: {fixture_path}"


def test_hypodx_local_fixture_exists_for_sc_zn() -> None:
    """The staged HYPOD-X local fixture for Sc-Zn exists."""
    workspace = Path(__file__).resolve().parents[1]
    fixture_path = workspace / "data" / "external" / "sources" / "hypodx" / "hypodx_fixture_local" / "canonical_records.jsonl"
    assert fixture_path.exists(), f"missing hypodx local fixture: {fixture_path}"
