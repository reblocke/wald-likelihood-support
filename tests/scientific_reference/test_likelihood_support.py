from __future__ import annotations

import math
import sys

import numpy as np
import pytest
from wald_inference import (
    log_support_ratio,
    relative_likelihood,
    support_ratio,
)

from wald_likelihood_support import (
    SupportRequest,
    ValidationError,
    calculate,
)

RTOL = 1e-12
ATOL = 1e-14


def _calculate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "effect_type": "odds_ratio",
        "lower": 1.2,
        "upper": 2.7,
        "null_value": 1.0,
        "thresholds": [1.25],
        "grid_points": 401,
    }
    payload.update(overrides)
    return calculate(SupportRequest.from_mapping(payload))


def test_b01_additive_legacy_likelihood_and_s_minus_2_anchors() -> None:
    response = _calculate(
        effect_type="mean_difference",
        lower=0.11,
        upper=0.73,
        null_value=0.0,
        thresholds=[0.2],
    )
    reconstruction = response["reconstruction"]
    interval = response["support_interval"]
    null, threshold = response["reference_support"]

    assert reconstruction["estimate_display"] == pytest.approx(0.42, rel=RTOL, abs=ATOL)
    assert reconstruction["standard_error_working"] == pytest.approx(
        0.15816617164664273, rel=RTOL, abs=ATOL
    )
    assert [interval["lower_display"], interval["upper_display"]] == pytest.approx(
        [0.10366765670671452, 0.7363323432932855],
        rel=RTOL,
        abs=ATOL,
    )
    assert null["relative_likelihood"] == pytest.approx(0.02943214834382319, rel=RTOL, abs=ATOL)
    assert null["log_relative_likelihood"] == pytest.approx(-3.52566772097005, rel=RTOL, abs=ATOL)
    assert null["likelihood_ratio_estimate_to_candidate"] == pytest.approx(
        33.976452833755374, rel=RTOL, abs=ATOL
    )
    assert threshold["relative_likelihood"] == pytest.approx(0.3800851100076333, rel=RTOL, abs=ATOL)
    assert threshold["likelihood_ratio_candidate_to_null"] == pytest.approx(
        12.913943812987075, rel=RTOL, abs=ATOL
    )


def test_b02_ratio_legacy_likelihood_and_s_minus_2_anchors() -> None:
    response = _calculate()
    reconstruction = response["reconstruction"]
    interval = response["support_interval"]
    null, threshold = response["reference_support"]

    assert reconstruction["estimate_display"] == pytest.approx(1.8, rel=RTOL, abs=ATOL)
    assert reconstruction["estimate_working"] == pytest.approx(
        0.5877866649021191, rel=RTOL, abs=ATOL
    )
    assert reconstruction["standard_error_working"] == pytest.approx(
        0.20687375447019513, rel=RTOL, abs=ATOL
    )
    assert [interval["lower_display"], interval["upper_display"]] == pytest.approx(
        [1.1901021645028553, 2.722455345968936],
        rel=RTOL,
        abs=ATOL,
    )
    assert null["relative_likelihood"] == pytest.approx(0.017660203420580514, rel=RTOL, abs=ATOL)
    assert null["log_likelihood_ratio_estimate_to_candidate"] == pytest.approx(
        4.036441565153495, rel=RTOL, abs=ATOL
    )
    assert threshold["relative_likelihood"] == pytest.approx(
        0.21151852001347865, rel=RTOL, abs=ATOL
    )
    assert threshold["likelihood_ratio_candidate_to_null"] == pytest.approx(
        11.977128177752654, rel=RTOL, abs=ATOL
    )


def test_curve_peak_and_closed_form_log_support_identity() -> None:
    response = _calculate()
    relative = np.asarray(response["grid"]["relative_likelihood"])
    log_relative = np.asarray(response["grid"]["log_relative_likelihood"])
    z_values = np.asarray(response["grid"]["standardized_distance"])
    peak = int(np.argmax(relative))

    assert relative[peak] == pytest.approx(1.0, rel=RTOL, abs=ATOL)
    assert log_relative[peak] == pytest.approx(0.0, rel=RTOL, abs=ATOL)
    np.testing.assert_allclose(
        log_relative,
        -0.5 * np.square(z_values),
        rtol=RTOL,
        atol=ATOL,
    )


def test_reported_ci_bounds_retain_legacy_relative_likelihood() -> None:
    response = _calculate()
    reconstruction = response["reconstruction"]
    observed = relative_likelihood(
        reconstruction["reported_95_ci_working"],
        reconstruction["estimate_working"],
        reconstruction["standard_error_working"],
    )

    np.testing.assert_allclose(
        observed,
        [0.14650006448608416, 0.14650006448608416],
        rtol=RTOL,
        atol=ATOL,
    )


def test_pairwise_order_is_antisymmetric_and_identity_is_one() -> None:
    a_to_b = _calculate(candidate_a=1.25, candidate_b=1.0)["pairwise_comparisons"][0]
    b_to_a = _calculate(candidate_a=1.0, candidate_b=1.25)["pairwise_comparisons"][0]
    same = _calculate(candidate_a=1.25, candidate_b=1.25)["pairwise_comparisons"][0]

    assert a_to_b["log_likelihood_ratio_a_to_b"] == pytest.approx(
        -b_to_a["log_likelihood_ratio_a_to_b"],
        rel=RTOL,
        abs=ATOL,
    )
    assert a_to_b["direction"] == "candidate_a_more_supported"
    assert b_to_a["direction"] == "candidate_b_more_supported"
    assert same["log_likelihood_ratio_a_to_b"] == 0.0
    assert same["likelihood_ratio_a_to_b"] == 1.0
    assert same["direction"] == "approximately_equal"


@pytest.mark.parametrize(
    ("criterion", "ratio"),
    [
        ("2_to_1", 2.0),
        ("4_to_1", 4.0),
        ("8_to_1", 8.0),
        ("custom", 6.5),
    ],
)
def test_support_interval_endpoints_meet_selected_ratio(
    criterion: str,
    ratio: float,
) -> None:
    overrides: dict[str, object] = {"support_criterion": criterion}
    if criterion == "custom":
        overrides["custom_support_ratio"] = ratio
    response = _calculate(**overrides)
    reconstruction = response["reconstruction"]
    interval = response["support_interval"]

    for endpoint in (interval["lower_working"], interval["upper_working"]):
        assert support_ratio(
            reconstruction["estimate_working"],
            endpoint,
            theta_hat=reconstruction["estimate_working"],
            se=reconstruction["standard_error_working"],
        ) == pytest.approx(ratio, rel=RTOL, abs=ATOL)
    assert interval["mle_to_bound_ratio"] == pytest.approx(ratio, rel=RTOL, abs=ATOL)


def test_larger_support_ratio_produces_wider_interval() -> None:
    widths = []
    for criterion in ("2_to_1", "4_to_1", "8_to_1"):
        interval = _calculate(support_criterion=criterion)["support_interval"]
        widths.append(interval["upper_working"] - interval["lower_working"])

    assert widths[0] < widths[1] < widths[2]


def test_s_minus_2_is_the_legacy_interval_not_two_to_one() -> None:
    s_minus_2 = _calculate(support_criterion="s_minus_2")["support_interval"]
    two_to_one = _calculate(support_criterion="2_to_1")["support_interval"]

    assert s_minus_2["log_relative_likelihood_cutoff"] == -2.0
    assert s_minus_2["mle_to_bound_ratio"] == pytest.approx(7.38905609893065, rel=RTOL, abs=ATOL)
    assert s_minus_2["lower_working"] < two_to_one["lower_working"]
    assert s_minus_2["upper_working"] > two_to_one["upper_working"]


def test_natural_and_log_working_scale_pairwise_results_are_equivalent() -> None:
    natural = _calculate(candidate_a=1.25, candidate_b=1.0)["pairwise_comparisons"][0]
    working = _calculate(
        effect_type="mean_difference",
        lower=math.log(1.2),
        upper=math.log(2.7),
        null_value=0.0,
        thresholds=[],
        candidate_a=math.log(1.25),
        candidate_b=0.0,
    )["pairwise_comparisons"][0]

    assert natural["log_likelihood_ratio_a_to_b"] == pytest.approx(
        working["log_likelihood_ratio_a_to_b"],
        rel=RTOL,
        abs=ATOL,
    )
    assert natural["likelihood_ratio_a_to_b"] == pytest.approx(
        working["likelihood_ratio_a_to_b"],
        rel=RTOL,
        abs=ATOL,
    )


def test_b03_display_range_changes_only_grid_and_warnings() -> None:
    baseline = _calculate()
    narrowed = _calculate(display_range_lower=0.9, display_range_upper=1.1)

    assert narrowed["reconstruction"] == baseline["reconstruction"]
    assert narrowed["support_interval"] == baseline["support_interval"]
    assert narrowed["reference_support"] == baseline["reference_support"]
    assert narrowed["pairwise_comparisons"] == baseline["pairwise_comparisons"]
    assert narrowed["grid"]["effect_display"][0] == 0.9
    assert narrowed["grid"]["effect_display"][-1] == 1.1
    assert narrowed["grid"]["relative_likelihood"][0] == pytest.approx(
        0.003649390717838349,
        rel=RTOL,
        abs=ATOL,
    )
    assert {warning["code"] for warning in narrowed["warnings"]} == {
        "display_excludes_estimate",
        "display_excludes_lower_ci",
        "display_excludes_upper_ci",
        "display_excludes_threshold",
        "display_excludes_support_interval",
    }


def test_asymmetric_explicit_range_includes_in_range_estimate_and_normalized_peak() -> None:
    response = _calculate(
        effect_type="mean_difference",
        lower=-0.0001,
        upper=0.0001,
        null_value=0.0,
        thresholds=[],
        display_range_lower=-1.0,
        display_range_upper=0.9,
        grid_points=101,
    )
    grid = response["grid"]

    assert grid["effect_working"][0] == -1.0
    assert grid["effect_working"][-1] == 0.9
    assert len(grid["effect_working"]) == 101
    estimate_indices = [
        index
        for index, value in enumerate(grid["effect_working"])
        if value == response["reconstruction"]["estimate_working"]
    ]
    assert len(estimate_indices) == 1
    estimate_index = estimate_indices[0]
    assert grid["standardized_distance"][estimate_index] == 0.0
    assert grid["relative_likelihood"][estimate_index] == 1.0
    assert grid["log_relative_likelihood"][estimate_index] == 0.0
    assert max(grid["relative_likelihood"]) == 1.0


def test_b08a_large_additive_midpoint_stays_finite() -> None:
    response = _calculate(
        effect_type="mean_difference",
        lower=-1e308,
        upper=1e308,
        null_value=0.0,
        thresholds=[],
    )

    assert response["reconstruction"]["estimate_working"] == 0.0
    assert response["reconstruction"]["standard_error_working"] == pytest.approx(
        5.10213456924654e307, rel=RTOL, abs=0.0
    )
    assert [
        response["support_interval"]["lower_working"],
        response["support_interval"]["upper_working"],
    ] == pytest.approx(
        [-1.020426913849308e308, 1.020426913849308e308],
        rel=RTOL,
        abs=0.0,
    )
    assert {warning["code"] for warning in response["warnings"]} == {"grid_truncated"}


def test_b08b_working_support_endpoint_clipping_is_explicit() -> None:
    response = _calculate(
        effect_type="mean_difference",
        lower=1e308,
        upper=1.79e308,
        null_value=None,
        thresholds=[],
    )

    interval = response["support_interval"]
    assert interval["upper_working"] == sys.float_info.max
    assert interval["upper_working_clipped"] is True
    assert "support_interval_working_clipped" in {
        warning["code"] for warning in response["warnings"]
    }


@pytest.mark.parametrize("criterion", ["s_minus_2", "4_to_1"])
def test_adjacent_float_extreme_support_boundary_fails_closed(criterion: str) -> None:
    center = 1e308

    with pytest.raises(
        ValidationError,
        match=(
            "Lower support interval endpoint cannot represent the requested "
            "log-relative-likelihood cutoff at finite floating-point precision"
        ),
    ):
        _calculate(
            effect_type="mean_difference",
            lower=math.nextafter(center, -math.inf),
            upper=math.nextafter(center, math.inf),
            null_value=0.0,
            thresholds=[],
            support_criterion=criterion,
            grid_points=101,
        )


def test_b08c_overflow_retains_finite_authoritative_log_result() -> None:
    response = _calculate(
        effect_type="mean_difference",
        lower=-0.0001,
        upper=0.0001,
        null_value=100.0,
        thresholds=[],
        candidate_a=0.0,
        candidate_b=100.0,
    )
    null = response["reference_support"][0]
    pairwise = response["pairwise_comparisons"][0]

    assert null["relative_likelihood"] == 0.0
    assert null["likelihood_ratio_estimate_to_candidate"] is None
    assert null["estimate_to_candidate_ratio_status"] == "overflow"
    assert math.isfinite(null["log_likelihood_ratio_estimate_to_candidate"])
    assert null["log_likelihood_ratio_estimate_to_candidate"] == pytest.approx(
        1920729410347.0623, rel=RTOL, abs=ATOL
    )
    assert pairwise["likelihood_ratio_a_to_b"] is None
    assert pairwise["ratio_status"] == "overflow"
    assert pairwise["log_likelihood_ratio_a_to_b"] > 0

    reverse = _calculate(
        effect_type="mean_difference",
        lower=-0.0001,
        upper=0.0001,
        null_value=100.0,
        thresholds=[],
        candidate_a=100.0,
        candidate_b=0.0,
    )["pairwise_comparisons"][0]
    assert reverse["likelihood_ratio_a_to_b"] == 0.0
    assert reverse["ratio_status"] == "underflow_zero"
    assert reverse["log_likelihood_ratio_a_to_b"] == pytest.approx(
        -pairwise["log_likelihood_ratio_a_to_b"],
        rel=RTOL,
        abs=ATOL,
    )


def test_b08d_ratio_display_clipping_is_explicit_and_finite() -> None:
    response = _calculate(
        effect_type="odds_ratio",
        lower=8.988465674311579e307,
        upper=sys.float_info.max,
        null_value=None,
        thresholds=[],
    )
    interval = response["support_interval"]
    null = response["reference_support"][0]
    warning_codes = {warning["code"] for warning in response["warnings"]}

    assert interval["upper_display"] == sys.float_info.max
    assert interval["upper_display_clipped"] is True
    assert null["likelihood_ratio_estimate_to_candidate"] is None
    assert null["log_likelihood_ratio_estimate_to_candidate"] == pytest.approx(
        8048257.661802234,
        rel=RTOL,
        abs=ATOL,
    )
    assert {
        "grid_truncated",
        "natural_axis_clipped",
        "support_interval_display_clipped",
        "estimate_to_null_ratio_overflow",
    } <= warning_codes


@pytest.mark.parametrize("ratio", [1.0, 0.5, -2.0, math.inf, math.nan])
def test_invalid_custom_support_ratios_fail_clearly(ratio: float) -> None:
    with pytest.raises(ValidationError, match="support ratio"):
        _calculate(
            support_criterion="custom",
            custom_support_ratio=ratio,
        )


def test_app_pairwise_matches_public_core_ordering() -> None:
    response = _calculate(candidate_a=1.25, candidate_b=1.0)
    reconstruction = response["reconstruction"]
    pairwise = response["pairwise_comparisons"][0]

    observed = log_support_ratio(
        pairwise["candidate_a_working"],
        pairwise["candidate_b_working"],
        theta_hat=reconstruction["estimate_working"],
        se=reconstruction["standard_error_working"],
    )
    assert pairwise["log_likelihood_ratio_a_to_b"] == observed
