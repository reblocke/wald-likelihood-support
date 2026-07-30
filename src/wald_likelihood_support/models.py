"""Typed request and response models for the focused likelihood-support applet."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, TypedDict

from wald_inference import DEFAULT_EFFECT_TYPE, ValidationError

DEFAULT_GRID_POINTS = 801
MIN_GRID_POINTS = 101
MAX_GRID_POINTS = 1601
SupportCriterion = Literal["s_minus_2", "2_to_1", "4_to_1", "8_to_1", "custom"]
SUPPORT_CRITERIA: tuple[SupportCriterion, ...] = (
    "s_minus_2",
    "2_to_1",
    "4_to_1",
    "8_to_1",
    "custom",
)


def _finite_number(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValidationError(f"{field} must be a number.")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValidationError(f"{field} must be finite.") from exc
    if not math.isfinite(number):
        raise ValidationError(f"{field} must be finite.")
    return number


def _optional_number(payload: dict[str, object], key: str, *, field: str) -> float | None:
    value = payload.get(key)
    return None if value is None else _finite_number(value, field=field)


def _thresholds(value: object) -> tuple[float, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValidationError("Reference thresholds must be supplied as a JSON array.")
    return tuple(
        _finite_number(item, field=f"Reference threshold {index}")
        for index, item in enumerate(value, start=1)
    )


def _grid_points(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError("Grid points must be an integer.")
    if value < MIN_GRID_POINTS or value > MAX_GRID_POINTS:
        raise ValidationError(
            f"Grid points must be between {MIN_GRID_POINTS} and {MAX_GRID_POINTS}."
        )
    if value % 2 == 0:
        raise ValidationError("Grid points must be odd.")
    return value


def _support_criterion(value: object) -> SupportCriterion:
    if not isinstance(value, str) or value not in SUPPORT_CRITERIA:
        choices = ", ".join(SUPPORT_CRITERIA)
        raise ValidationError(f"Support criterion must be one of: {choices}.")
    return value  # type: ignore[return-value]


@dataclass(frozen=True)
class SupportRequest:
    """Validated app inputs before scientific reconstruction."""

    effect_type: str
    estimate: float | None
    lower: float
    upper: float
    null_value: float | None
    thresholds: tuple[float, ...]
    candidate_a: float | None
    candidate_b: float | None
    support_criterion: SupportCriterion
    custom_support_ratio: float | None
    display_range: tuple[float, float] | None
    grid_points: int

    @classmethod
    def from_mapping(cls, payload: object) -> SupportRequest:
        if not isinstance(payload, dict) or not all(isinstance(key, str) for key in payload):
            raise ValidationError("Request must be a JSON object.")

        allowed = {
            "candidate_a",
            "candidate_b",
            "custom_support_ratio",
            "display_range_lower",
            "display_range_upper",
            "effect_type",
            "estimate",
            "grid_points",
            "lower",
            "null_value",
            "support_criterion",
            "thresholds",
            "upper",
        }
        unexpected = sorted(set(payload) - allowed)
        if unexpected:
            raise ValidationError(f"Unexpected field: {unexpected[0]}.")
        for required in ("lower", "upper"):
            if required not in payload:
                raise ValidationError(f"Missing required field: {required}.")

        effect_type = payload.get("effect_type", DEFAULT_EFFECT_TYPE)
        if not isinstance(effect_type, str) or not effect_type:
            raise ValidationError("Effect measure must be a non-empty string.")

        range_lower = _optional_number(
            payload,
            "display_range_lower",
            field="Plausible display range lower",
        )
        range_upper = _optional_number(
            payload,
            "display_range_upper",
            field="Plausible display range upper",
        )
        if (range_lower is None) != (range_upper is None):
            raise ValidationError(
                "Plausible display range lower and upper must be supplied together."
            )
        display_range = (
            None if range_lower is None or range_upper is None else (range_lower, range_upper)
        )

        candidate_a = _optional_number(payload, "candidate_a", field="Candidate A")
        candidate_b = _optional_number(payload, "candidate_b", field="Candidate B")
        if (candidate_a is None) != (candidate_b is None):
            raise ValidationError("Candidate A and candidate B must be supplied together.")

        criterion = _support_criterion(payload.get("support_criterion", "s_minus_2"))
        custom_ratio = _optional_number(
            payload,
            "custom_support_ratio",
            field="Custom support ratio",
        )
        if criterion == "custom":
            if custom_ratio is None:
                raise ValidationError(
                    "Custom support ratio is required when the custom criterion is selected."
                )
            if custom_ratio <= 1.0:
                raise ValidationError("Custom support ratio must be greater than 1.")
        elif custom_ratio is not None:
            raise ValidationError(
                "Custom support ratio may be supplied only with the custom criterion."
            )

        return cls(
            effect_type=effect_type,
            estimate=_optional_number(payload, "estimate", field="Point estimate"),
            lower=_finite_number(payload["lower"], field="Lower 95% confidence limit"),
            upper=_finite_number(payload["upper"], field="Upper 95% confidence limit"),
            null_value=_optional_number(payload, "null_value", field="Null value"),
            thresholds=_thresholds(payload.get("thresholds")),
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            support_criterion=criterion,
            custom_support_ratio=custom_ratio,
            display_range=display_range,
            grid_points=_grid_points(payload.get("grid_points", DEFAULT_GRID_POINTS)),
        )


class EffectSpecPayload(TypedDict):
    key: str
    label: str
    family: Literal["additive", "ratio"]
    working_scale: Literal["identity", "log"]
    default_null: float
    positive_only: bool


class CriterionPayload(TypedDict):
    key: SupportCriterion
    label: str
    mle_to_bound_ratio: float


class MetaPayload(TypedDict):
    schema_version: int
    app_version: str
    core_version: str
    effect_spec: EffectSpecPayload
    estimate_source: Literal["inferred_from_ci", "provided_validated"]
    default_null_applied: bool
    grid_points: int
    display_axis_scale: Literal["identity", "natural"]
    display_range_active: bool
    display_range_display: list[float] | None
    display_range_working: list[float] | None
    selected_support_criterion: CriterionPayload


class ReconstructionPayload(TypedDict):
    estimate_display: float
    estimate_working: float
    provided_estimate_display: float | None
    provided_estimate_working: float | None
    reported_95_ci_display: list[float]
    reported_95_ci_working: list[float]
    null_display: float
    null_working: float
    standard_error_working: float
    standard_error_method: Literal["ci_width", "mean_side_se"]
    standard_error_lower_side: float
    standard_error_upper_side: float
    standard_error_from_width: float
    relative_asymmetry: float


class GridPayload(TypedDict):
    effect_display: list[float]
    effect_working: list[float]
    standardized_distance: list[float]
    relative_likelihood: list[float]
    log_relative_likelihood: list[float]


class SupportIntervalPayload(TypedDict):
    criterion_key: SupportCriterion
    criterion_label: str
    definition: str
    mle_to_bound_ratio: float
    log_relative_likelihood_cutoff: float
    relative_likelihood_cutoff: float
    lower_display: float
    upper_display: float
    lower_working: float
    upper_working: float
    lower_working_clipped: bool
    upper_working_clipped: bool
    lower_display_clipped: bool
    upper_display_clipped: bool


RatioStatus = Literal["finite", "overflow", "underflow_zero"]
DirectionFromEstimate = Literal["below_estimate", "at_estimate", "above_estimate"]
DirectionFromNull = Literal["below_null", "at_null", "above_null"]


class ReferenceSupportPayload(TypedDict):
    role: Literal["null", "threshold"]
    label: str
    effect_display: float
    effect_working: float
    standardized_distance: float
    relative_likelihood: float
    log_relative_likelihood: float
    likelihood_ratio_estimate_to_candidate: float | None
    log_likelihood_ratio_estimate_to_candidate: float
    estimate_to_candidate_ratio_status: RatioStatus
    likelihood_ratio_candidate_to_null: float | None
    log_likelihood_ratio_candidate_to_null: float
    candidate_to_null_ratio_status: RatioStatus
    relative_to_estimate: DirectionFromEstimate
    relative_to_null: DirectionFromNull
    inside_selected_support_interval: bool


PairwiseDirection = Literal[
    "candidate_a_more_supported",
    "candidate_b_more_supported",
    "approximately_equal",
]


class PairwiseComparisonPayload(TypedDict):
    candidate_a_display: float
    candidate_a_working: float
    candidate_b_display: float
    candidate_b_working: float
    log_likelihood_ratio_a_to_b: float
    likelihood_ratio_a_to_b: float | None
    ratio_status: RatioStatus
    direction: PairwiseDirection
    sentence: str


class WarningPayload(TypedDict):
    code: str
    message: str


class SupportResponse(TypedDict):
    meta: MetaPayload
    reconstruction: ReconstructionPayload
    grid: GridPayload
    support_interval: SupportIntervalPayload
    reference_support: list[ReferenceSupportPayload]
    pairwise_comparisons: list[PairwiseComparisonPayload]
    warnings: list[WarningPayload]
