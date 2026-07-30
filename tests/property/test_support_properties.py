from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from wald_likelihood_support import SupportRequest, calculate


def _pairwise(candidate_a: float, candidate_b: float) -> dict[str, object]:
    request = SupportRequest.from_mapping(
        {
            "effect_type": "mean_difference",
            "lower": -1.96,
            "upper": 1.96,
            "null_value": 0.0,
            "candidate_a": candidate_a,
            "candidate_b": candidate_b,
            "grid_points": 101,
        }
    )
    return calculate(request)["pairwise_comparisons"][0]


@settings(max_examples=40, deadline=None)
@given(
    st.floats(min_value=-25, max_value=25, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-25, max_value=25, allow_nan=False, allow_infinity=False),
)
def test_pairwise_log_support_is_antisymmetric(candidate_a: float, candidate_b: float) -> None:
    forward = _pairwise(candidate_a, candidate_b)
    reverse = _pairwise(candidate_b, candidate_a)

    assert math.isfinite(forward["log_likelihood_ratio_a_to_b"])
    assert forward["log_likelihood_ratio_a_to_b"] == pytest.approx(
        -reverse["log_likelihood_ratio_a_to_b"],
        rel=1e-12,
        abs=1e-14,
    )


@settings(max_examples=30, deadline=None)
@given(st.floats(min_value=-25, max_value=25, allow_nan=False, allow_infinity=False))
def test_pairwise_identity_is_exact(candidate: float) -> None:
    comparison = _pairwise(candidate, candidate)

    assert comparison["log_likelihood_ratio_a_to_b"] == 0.0
    assert comparison["likelihood_ratio_a_to_b"] == 1.0
    assert comparison["direction"] == "approximately_equal"
