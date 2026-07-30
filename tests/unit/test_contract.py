from __future__ import annotations

import json
from pathlib import Path

import pytest

from wald_likelihood_support import (
    SupportRequest,
    ValidationError,
    calculate,
    calculate_json,
)


def _request(**overrides: object) -> SupportRequest:
    payload: dict[str, object] = {
        "effect_type": "odds_ratio",
        "lower": 1.2,
        "upper": 2.7,
        "null_value": 1.0,
        "thresholds": [1.25],
        "grid_points": 401,
    }
    payload.update(overrides)
    return SupportRequest.from_mapping(payload)


def test_focused_contract_has_exact_sections_and_grid_fields() -> None:
    response = calculate(_request(candidate_a=1.25, candidate_b=1.0))

    assert set(response) == {
        "meta",
        "reconstruction",
        "grid",
        "support_interval",
        "reference_support",
        "pairwise_comparisons",
        "warnings",
    }
    assert set(response["grid"]) == {
        "effect_display",
        "effect_working",
        "standardized_distance",
        "relative_likelihood",
        "log_relative_likelihood",
    }
    assert response["meta"]["core_version"] == "0.2.0"
    assert response["meta"]["app_version"] == "0.1.0"
    assert response["pairwise_comparisons"][0]["sentence"].endswith(
        "the reported order is L(A)/L(B)."
    )


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_contract_rejects_nonstandard_json_numbers(constant: str) -> None:
    with pytest.raises(ValidationError, match="Non-finite JSON constant"):
        calculate_json(f'{{"lower": {constant}, "upper": 1}}')


def test_contract_rejects_integer_too_large_for_binary64_as_validation_error() -> None:
    huge_integer = "9" * 401

    with pytest.raises(ValidationError, match="Lower 95% confidence limit must be finite"):
        calculate_json(f'{{"lower": {huge_integer}, "upper": 1}}')


def test_contract_returns_strict_json() -> None:
    response_json = calculate_json(
        json.dumps(
            {
                "effect_type": "mean_difference",
                "lower": 0.11,
                "upper": 0.73,
                "null_value": 0.0,
            }
        )
    )

    assert "NaN" not in response_json
    assert "Infinity" not in response_json
    payload = json.loads(response_json)
    assert payload["reconstruction"]["estimate_display"] == pytest.approx(0.42)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "Missing required field"),
        ({"lower": 0, "upper": 1, "extra": 3}, "Unexpected field"),
        ({"lower": True, "upper": 1}, "Lower 95% confidence limit must be a number"),
        ({"lower": 0, "upper": "1"}, "Upper 95% confidence limit must be a number"),
        ({"lower": 0, "upper": 1, "thresholds": "0.2"}, "JSON array"),
        ({"lower": 0, "upper": 1, "candidate_a": 0.2}, "must be supplied together"),
        (
            {"lower": 0, "upper": 1, "support_criterion": "custom"},
            "Custom support ratio is required",
        ),
        (
            {
                "lower": 0,
                "upper": 1,
                "support_criterion": "custom",
                "custom_support_ratio": 1.0,
            },
            "must be greater than 1",
        ),
        (
            {
                "lower": 0,
                "upper": 1,
                "support_criterion": "2_to_1",
                "custom_support_ratio": 3.0,
            },
            "only with the custom criterion",
        ),
        ({"lower": 0, "upper": 1, "grid_points": 400}, "must be odd"),
        ({"lower": 0, "upper": 1, "grid_points": 99}, "between 101 and 1601"),
        ({"lower": 0, "upper": 1, "design_enabled": True}, "Unexpected field"),
    ],
)
def test_request_validation_is_explicit(payload: object, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        SupportRequest.from_mapping(payload)


def test_frozen_baseline_provenance_identifies_behavior_and_fixture_commits() -> None:
    provenance_path = (
        Path(__file__).resolve().parents[1] / "regression" / "baseline_provenance.json"
    )
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))

    assert provenance == {
        "baseline_fixture_commit": "5fd501dd947d9b951d736014cfc2b310efa5e7b0",
        "baseline_tag": "pre-split-baseline-2026-07-29",
        "behavior_source_commit": "830756ecb11b4e8161f8dfe1fc75afc346ef4467",
        "cases": ["B01", "B02", "B03", "B08a", "B08b", "B08c", "B08d"],
        "fixture_manifest_sha256": (
            "f54bb2d8311788c07adcf23fc9f038e35702449e4a77a474abea9411246cabcc"
        ),
        "fixture_set_sha256": ("81c341b39e711caffc85a444f0c1e4bc1e2d00633474c82e720afeb60def3c4d"),
        "schema_version": 1,
    }


@pytest.mark.parametrize(
    "criterion",
    ["s_minus_2", "2_to_1", "4_to_1", "8_to_1"],
)
def test_named_support_criteria_are_accepted(criterion: str) -> None:
    response = calculate(_request(support_criterion=criterion))

    assert response["support_interval"]["criterion_key"] == criterion


def test_custom_support_criterion_is_explicit() -> None:
    response = calculate(
        _request(
            support_criterion="custom",
            custom_support_ratio=6.5,
        )
    )

    assert response["support_interval"]["criterion_label"] == "Custom 6.5:1"
    assert response["support_interval"]["mle_to_bound_ratio"] == pytest.approx(6.5)


def test_ratio_effect_inputs_remain_strictly_positive() -> None:
    with pytest.raises(ValidationError, match="strictly positive"):
        calculate(_request(lower=-1.0))


def test_provided_estimate_is_validation_evidence_not_a_new_center() -> None:
    response = calculate(_request(estimate=1.8))

    assert response["meta"]["estimate_source"] == "provided_validated"
    assert response["reconstruction"]["estimate_display"] == pytest.approx(1.8)

    with pytest.raises(ValidationError, match="inconsistent"):
        calculate(_request(estimate=2.4))
