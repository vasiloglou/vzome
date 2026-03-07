from __future__ import annotations

from materials_discovery.generator.approximant_templates import resolve_template
from materials_discovery.generator.site_positions import site_positions_from_template
from materials_discovery.generator.zphi_geometry import (
    cell_scale_multiplier,
    construct_site_qphi,
)


def _build_qphi_coords(
    system_name: str,
    template_family: str,
    *,
    candidate_index: int = 3,
    seed: int = 17,
) -> tuple[dict[str, float], list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]]:
    template = resolve_template(system_name, template_family)
    qphi_coords = [
        construct_site_qphi(
            site.base_qphi,
            template_family=template_family,
            candidate_index=candidate_index,
            site_index=site_index,
            seed=seed,
            min_coeff=-3,
            max_coeff=3,
        )
        for site_index, site in enumerate(template.sites)
    ]
    multiplier = cell_scale_multiplier(seed, candidate_index)
    cell = {
        axis: round(value * multiplier, 6) if axis in {"a", "b", "c"} else value
        for axis, value in template.base_cell.items()
    }
    return cell, qphi_coords


def test_al_cu_fe_template_has_two_mackay_shells() -> None:
    template = resolve_template("Al-Cu-Fe", "icosahedral_approximant_1_1")
    cell, qphi_coords = _build_qphi_coords("Al-Cu-Fe", "icosahedral_approximant_1_1")

    fractional_positions, _ = site_positions_from_template(template, list(qphi_coords), cell)

    assert len(fractional_positions) == 42
    inner_count = sum(site.orbit.startswith("mackay_inner") for site in template.sites)
    outer_count = sum(site.orbit.startswith("mackay_outer") for site in template.sites)
    assert inner_count == 12
    assert outer_count == 30
    assert template.prototype_key == "al_cu_fe_mackay_1_1"


def test_al_pd_mn_template_uses_decagonal_periodic_cell() -> None:
    template = resolve_template("Al-Pd-Mn", "decagonal_proxy_2_1")
    cell, qphi_coords = _build_qphi_coords("Al-Pd-Mn", "decagonal_proxy_2_1", seed=23)

    fractional_positions, _ = site_positions_from_template(template, list(qphi_coords), cell)

    assert len(fractional_positions) == 51
    assert cell["a"] != cell["b"]
    assert cell["c"] < cell["a"]
    assert sum(site.orbit.startswith("xi_prime_outer") for site in template.sites) == 12
    assert template.prototype_key == "al_pd_mn_xi_prime"


def test_sc_zn_template_has_tsai_shell_hierarchy() -> None:
    template = resolve_template("Sc-Zn", "cubic_proxy_1_0")
    cell, qphi_coords = _build_qphi_coords("Sc-Zn", "cubic_proxy_1_0", seed=31)

    fractional_positions, _ = site_positions_from_template(template, list(qphi_coords), cell)

    assert len(fractional_positions) == 208
    assert template.space_group == "I m -3"
    assert sum(site.orbit == "tsai_sc1" for site in template.sites) == 24
    assert sum(site.orbit == "tsai_zn3" for site in template.sites) == 48
    assert template.prototype_key == "sc_zn_tsai_sczn6"
