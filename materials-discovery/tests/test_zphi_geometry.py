from __future__ import annotations

from materials_discovery.generator.zphi_geometry import (
    cell_scale_multiplier,
    construct_site_qphi,
    phi_scale_pair,
)


def test_phi_scale_pair_matches_basic_zphi_arithmetic() -> None:
    assert phi_scale_pair((1, 0), 1) == (0, 1)
    assert phi_scale_pair((1, 0), 2) == (1, 1)
    assert phi_scale_pair((0, 1), -1) == (1, 0)



def test_construct_site_qphi_is_deterministic_and_bounded() -> None:
    base_qphi = ((1, 0), (0, 1), (-1, 1))
    first = construct_site_qphi(
        base_qphi,
        template_family="icosahedral_approximant_1_1",
        candidate_index=3,
        site_index=2,
        seed=17,
        min_coeff=-3,
        max_coeff=3,
    )
    second = construct_site_qphi(
        base_qphi,
        template_family="icosahedral_approximant_1_1",
        candidate_index=3,
        site_index=2,
        seed=17,
        min_coeff=-3,
        max_coeff=3,
    )

    assert first == second
    assert first != base_qphi
    for pair in first:
        assert -3 <= pair[0] <= 3
        assert -3 <= pair[1] <= 3


def test_cell_scale_multiplier_uses_tight_window_for_anchored_templates() -> None:
    generic = {cell_scale_multiplier(31, idx) for idx in range(1, 7)}
    anchored = {
        cell_scale_multiplier(31, idx, template_source_kind="zomic_export_anchor_fitted")
        for idx in range(1, 7)
    }

    assert generic == {0.618034, 1.0, 1.618034}
    assert anchored == {0.97, 0.985, 1.0, 1.015, 1.03}
