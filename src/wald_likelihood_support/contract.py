"""Strict likelihood-support browser contract backed only by public ``wald_inference`` APIs."""

from __future__ import annotations

import json
import math

import numpy as np
from wald_inference import (
    SupportInterval,
    ValidationError,
    build_grid,
    from_working_scale,
    get_effect_spec,
    log_relative_likelihood,
    log_support_ratio,
    max_safe_grid_span,
    reconstruct_wald_from_95_ci,
    relative_likelihood,
    standardized_distance,
    support_interval,
    support_interval_for_ratio,
    support_ratio,
    to_working_scale,
)
from wald_inference import (
    __version__ as CORE_VERSION,
)

from .models import (
    PairwiseComparisonPayload,
    ReferenceSupportPayload,
    SupportCriterion,
    SupportRequest,
    SupportResponse,
    WarningPayload,
)
from .version import __version__

DEFAULT_GRID_SPAN_IN_STANDARD_ERRORS = 4.5
PAIRWISE_EQUAL_ABSOLUTE_TOLERANCE = 1e-12
NAMED_SUPPORT_RATIOS: dict[SupportCriterion, float] = {
    "2_to_1": 2.0,
    "4_to_1": 4.0,
    "8_to_1": 8.0,
}
CRITERION_LABELS: dict[SupportCriterion, str] = {
    "s_minus_2": "S−2 / exp(2):1",
    "2_to_1": "2:1",
    "4_to_1": "4:1",
    "8_to_1": "8:1",
    "custom": "Custom ratio",
}


def _reject_nonstandard_constant(value: str) -> None:
    raise ValidationError(f"Non-finite JSON constant is not allowed: {value}.")


def _float_list(values: object) -> list[float]:
    return [float(value) for value in np.asarray(values, dtype=float).reshape(-1)]


def _strict_finite_tree(value: object, *, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            _strict_finite_tree(nested, path=f"{path}.{key}")
        return
    if isinstance(value, list | tuple):
        for index, nested in enumerate(value):
            _strict_finite_tree(nested, path=f"{path}[{index}]")
        return
    if isinstance(value, float) and not math.isfinite(value):
        raise ValidationError(
            f"Computed response value at {path} exceeds the finite floating-point range."
        )


def _warning(code: str, message: str) -> WarningPayload:
    return {"code": code, "message": message}


def _direction(value: float, reference: float, reference_name: str) -> str:
    if math.isclose(value, reference, rel_tol=1e-12, abs_tol=1e-12):
        return f"at_{reference_name}"
    return f"below_{reference_name}" if value < reference else f"above_{reference_name}"


def _ratio_status(ratio: float | None, log_ratio: float) -> str:
    if ratio is None:
        return "overflow"
    if ratio == 0.0 and log_ratio < 0.0:
        return "underflow_zero"
    return "finite"


def _display_values(
    effect_type: str,
    working_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Transform display values while keeping all scientific calculations on the working scale."""

    spec = get_effect_spec(effect_type)
    if spec.family == "additive":
        values = np.asarray(from_working_scale(effect_type, working_values), dtype=float)
        return values, np.zeros(values.shape, dtype=bool)

    smallest_positive = float(np.nextafter(0.0, 1.0))
    largest_finite = float(np.finfo(float).max)
    lower_working = float(to_working_scale(effect_type, smallest_positive))
    upper_working = float(to_working_scale(effect_type, largest_finite))
    safe_values = np.clip(working_values, lower_working, upper_working)
    lower_clipped = working_values <= lower_working
    upper_clipped = working_values >= upper_working
    clipped = lower_clipped | upper_clipped
    display_values = np.asarray(
        from_working_scale(effect_type, safe_values),
        dtype=float,
    )
    if np.any(clipped):
        display_values = display_values.copy()
        display_values[lower_clipped] = smallest_positive
        display_values[upper_clipped] = largest_finite
    return display_values, clipped


def _selected_interval(
    request: SupportRequest,
    *,
    theta_hat: float,
    se: float,
) -> tuple[SupportInterval, str, float]:
    if request.support_criterion == "s_minus_2":
        interval = support_interval(theta_hat, se)
    else:
        ratio = (
            request.custom_support_ratio
            if request.support_criterion == "custom"
            else NAMED_SUPPORT_RATIOS[request.support_criterion]
        )
        if ratio is None:
            raise ValidationError("The selected support ratio is unavailable.")
        interval = support_interval_for_ratio(
            theta_hat,
            se,
            mle_to_bound_ratio=ratio,
        )

    interval_ratio = interval.likelihood_ratio_mle_to_bound
    if interval_ratio is None or not math.isfinite(interval_ratio):
        raise ValidationError("The selected support interval ratio must be finite.")
    label = CRITERION_LABELS[request.support_criterion]
    if request.support_criterion == "custom":
        label = f"Custom {interval_ratio:g}:1"
    return interval, label, float(interval_ratio)


def _display_range_warnings(
    display_range_working: tuple[float, float] | None,
    *,
    estimate_working: float,
    lower_working: float,
    upper_working: float,
    null_working: float,
    thresholds_working: np.ndarray,
    candidate_a_working: float | None,
    candidate_b_working: float | None,
    support_lower_working: float,
    support_upper_working: float,
) -> list[WarningPayload]:
    if display_range_working is None:
        return []
    range_lower, range_upper = display_range_working

    def outside(value: float) -> bool:
        return value < range_lower or value > range_upper

    warnings: list[WarningPayload] = []
    checks = [
        (
            "display_excludes_estimate",
            outside(estimate_working),
            "The chosen display range excludes the CI-implied estimate.",
        ),
        (
            "display_excludes_lower_ci",
            outside(lower_working),
            "The chosen display range excludes the lower 95% CI bound.",
        ),
        (
            "display_excludes_upper_ci",
            outside(upper_working),
            "The chosen display range excludes the upper 95% CI bound.",
        ),
        (
            "display_excludes_null",
            outside(null_working),
            "The chosen display range excludes the null value.",
        ),
        (
            "display_excludes_threshold",
            any(outside(float(value)) for value in thresholds_working),
            "The chosen display range excludes one or more reference thresholds.",
        ),
        (
            "display_excludes_pairwise_candidate",
            any(
                value is not None and outside(value)
                for value in (candidate_a_working, candidate_b_working)
            ),
            "The chosen display range excludes one or more pairwise candidates.",
        ),
        (
            "display_excludes_support_interval",
            outside(support_lower_working) or outside(support_upper_working),
            "The chosen display range excludes part or all of the selected support interval.",
        ),
    ]
    warnings.extend(_warning(code, message) for code, active, message in checks if active)
    return warnings


def _include_value_in_explicit_grid(
    grid: np.ndarray,
    value: float,
) -> np.ndarray:
    """Include an in-range scientific anchor without changing endpoints or size."""

    if value < float(grid[0]) or value > float(grid[-1]) or np.any(grid == value):
        return grid

    insertion = int(np.searchsorted(grid, value))
    candidates = {
        min(max(insertion - 1, 1), grid.size - 2),
        min(max(insertion, 1), grid.size - 2),
    }
    nearest = min(
        candidates,
        key=lambda index: abs((float(grid[index]) * 0.5) - (value * 0.5)),
    )
    included = grid.copy()
    included[nearest] = value
    return included


def _reference_rows(
    *,
    threshold_displays: np.ndarray,
    threshold_workings: np.ndarray,
    estimate_working: float,
    null_display: float,
    null_working: float,
    se: float,
    support_lower_working: float,
    support_upper_working: float,
) -> tuple[list[ReferenceSupportPayload], list[WarningPayload]]:
    candidate_displays = np.asarray([null_display, *threshold_displays], dtype=float)
    candidate_workings = np.asarray([null_working, *threshold_workings], dtype=float)
    z_values = np.asarray(
        standardized_distance(candidate_workings, estimate_working, se),
        dtype=float,
    )
    relative_values = np.asarray(
        relative_likelihood(candidate_workings, estimate_working, se),
        dtype=float,
    )
    log_relative_values = np.asarray(
        log_relative_likelihood(candidate_workings, estimate_working, se),
        dtype=float,
    )

    rows: list[ReferenceSupportPayload] = []
    warnings: list[WarningPayload] = []
    for index, (display, working) in enumerate(
        zip(candidate_displays, candidate_workings, strict=True)
    ):
        log_estimate_to_candidate = float(
            log_support_ratio(
                estimate_working,
                float(working),
                theta_hat=estimate_working,
                se=se,
            )
        )
        estimate_to_candidate = support_ratio(
            estimate_working,
            float(working),
            theta_hat=estimate_working,
            se=se,
        )
        estimate_status = _ratio_status(estimate_to_candidate, log_estimate_to_candidate)

        log_candidate_to_null = float(
            log_support_ratio(
                float(working),
                null_working,
                theta_hat=estimate_working,
                se=se,
            )
        )
        candidate_to_null = support_ratio(
            float(working),
            null_working,
            theta_hat=estimate_working,
            se=se,
        )
        candidate_status = _ratio_status(candidate_to_null, log_candidate_to_null)
        label = "Null" if index == 0 else f"Reference {index}"
        role = "null" if index == 0 else "threshold"

        rows.append(
            {
                "role": role,
                "label": label,
                "effect_display": float(display),
                "effect_working": float(working),
                "standardized_distance": float(z_values[index]),
                "relative_likelihood": float(relative_values[index]),
                "log_relative_likelihood": float(log_relative_values[index]),
                "likelihood_ratio_estimate_to_candidate": estimate_to_candidate,
                "log_likelihood_ratio_estimate_to_candidate": log_estimate_to_candidate,
                "estimate_to_candidate_ratio_status": estimate_status,
                "likelihood_ratio_candidate_to_null": candidate_to_null,
                "log_likelihood_ratio_candidate_to_null": log_candidate_to_null,
                "candidate_to_null_ratio_status": candidate_status,
                "relative_to_estimate": _direction(
                    float(working),
                    estimate_working,
                    "estimate",
                ),
                "relative_to_null": _direction(float(working), null_working, "null"),
                "inside_selected_support_interval": (
                    support_lower_working <= float(working) <= support_upper_working
                ),
            }
        )

        if estimate_status != "finite":
            warnings.append(
                _warning(
                    f"estimate_to_{role}_ratio_{estimate_status}",
                    f"The ordinary estimate-to-{role} support ratio is represented as "
                    f"{estimate_status.replace('_', ' ')}; its finite log ratio remains "
                    "authoritative.",
                )
            )
        if candidate_status != "finite":
            warnings.append(
                _warning(
                    f"{role}_to_null_ratio_{candidate_status}",
                    f"The ordinary {role}-to-null support ratio is represented as "
                    f"{candidate_status.replace('_', ' ')}; its finite log ratio remains "
                    "authoritative.",
                )
            )
    return rows, warnings


def _pairwise_rows(
    *,
    candidate_a_display: float | None,
    candidate_a_working: float | None,
    candidate_b_display: float | None,
    candidate_b_working: float | None,
    estimate_working: float,
    se: float,
) -> tuple[list[PairwiseComparisonPayload], list[WarningPayload]]:
    if (
        candidate_a_display is None
        or candidate_a_working is None
        or candidate_b_display is None
        or candidate_b_working is None
    ):
        return [], []

    log_ratio = float(
        log_support_ratio(
            candidate_a_working,
            candidate_b_working,
            theta_hat=estimate_working,
            se=se,
        )
    )
    ratio = support_ratio(
        candidate_a_working,
        candidate_b_working,
        theta_hat=estimate_working,
        se=se,
    )
    status = _ratio_status(ratio, log_ratio)
    if math.isclose(log_ratio, 0.0, rel_tol=0.0, abs_tol=PAIRWISE_EQUAL_ABSOLUTE_TOLERANCE):
        direction = "approximately_equal"
        sentence = (
            "Candidate A and candidate B are approximately equally supported; "
            "the reported order is L(A)/L(B)."
        )
    elif log_ratio > 0.0:
        direction = "candidate_a_more_supported"
        sentence = (
            "Candidate A is more supported than candidate B; the reported order is L(A)/L(B)."
        )
    else:
        direction = "candidate_b_more_supported"
        sentence = (
            "Candidate B is more supported than candidate A; the reported order is L(A)/L(B)."
        )

    warnings = []
    if status != "finite":
        warnings.append(
            _warning(
                f"pairwise_ratio_{status}",
                "The ordinary L(A)/L(B) value is represented as "
                f"{status.replace('_', ' ')}; the finite log L(A)/L(B) result and its sign "
                "remain authoritative.",
            )
        )
    return (
        [
            {
                "candidate_a_display": candidate_a_display,
                "candidate_a_working": candidate_a_working,
                "candidate_b_display": candidate_b_display,
                "candidate_b_working": candidate_b_working,
                "log_likelihood_ratio_a_to_b": log_ratio,
                "likelihood_ratio_a_to_b": ratio,
                "ratio_status": status,
                "direction": direction,
                "sentence": sentence,
            }
        ],
        warnings,
    )


def calculate(request: SupportRequest) -> SupportResponse:
    """Construct one focused, strict likelihood-support response."""

    spec = get_effect_spec(request.effect_type)
    reconstruction = reconstruct_wald_from_95_ci(
        effect_type=request.effect_type,
        estimate=request.estimate,
        lower=request.lower,
        upper=request.upper,
        null_value=request.null_value,
    )
    interval, criterion_label, criterion_ratio = _selected_interval(
        request,
        theta_hat=reconstruction.estimate_working,
        se=reconstruction.standard_error,
    )

    thresholds_display = np.asarray(request.thresholds, dtype=float)
    thresholds_working = np.asarray(
        to_working_scale(request.effect_type, thresholds_display),
        dtype=float,
    )
    candidate_a_working = (
        None
        if request.candidate_a is None
        else float(to_working_scale(request.effect_type, request.candidate_a))
    )
    candidate_b_working = (
        None
        if request.candidate_b is None
        else float(to_working_scale(request.effect_type, request.candidate_b))
    )

    display_range_working: tuple[float, float] | None = None
    safe_span: float | None = None
    included_values = np.asarray(
        [
            reconstruction.null_working,
            *thresholds_working,
            *(
                []
                if candidate_a_working is None or candidate_b_working is None
                else [candidate_a_working, candidate_b_working]
            ),
            interval.lower_working,
            interval.upper_working,
        ],
        dtype=float,
    )
    if request.display_range is None:
        natural_axis_upper_bound = (
            float(to_working_scale(request.effect_type, float(np.finfo(float).max)))
            if spec.family == "ratio"
            else None
        )
        safe_span = max_safe_grid_span(
            reconstruction.estimate_working,
            reconstruction.standard_error,
            natural_axis_upper_bound=natural_axis_upper_bound,
        )
        grid_working = build_grid(
            reconstruction.estimate_working,
            reconstruction.standard_error,
            n=request.grid_points,
            include_values=included_values,
            max_span=safe_span,
        )
    else:
        range_lower, range_upper = request.display_range
        if range_lower >= range_upper:
            raise ValidationError(
                "Plausible display range lower must be less than plausible display range upper."
            )
        transformed = np.asarray(
            to_working_scale(request.effect_type, request.display_range),
            dtype=float,
        )
        display_range_working = (float(transformed[0]), float(transformed[1]))
        grid_working = np.linspace(
            display_range_working[0],
            display_range_working[1],
            num=request.grid_points,
            dtype=float,
        )
        grid_working = _include_value_in_explicit_grid(
            grid_working,
            reconstruction.estimate_working,
        )

    z_values = np.asarray(
        standardized_distance(
            grid_working,
            reconstruction.estimate_working,
            reconstruction.standard_error,
        ),
        dtype=float,
    )
    relative_values = np.asarray(
        relative_likelihood(
            grid_working,
            reconstruction.estimate_working,
            reconstruction.standard_error,
        ),
        dtype=float,
    )
    log_relative_values = np.asarray(
        log_relative_likelihood(
            grid_working,
            reconstruction.estimate_working,
            reconstruction.standard_error,
        ),
        dtype=float,
    )
    grid_display, grid_display_clipped = _display_values(request.effect_type, grid_working)
    if request.display_range is not None:
        grid_display[0], grid_display[-1] = request.display_range

    interval_working = np.asarray(
        [interval.lower_working, interval.upper_working],
        dtype=float,
    )
    interval_display, interval_display_clipped = _display_values(
        request.effect_type,
        interval_working,
    )

    warnings = [_warning("wald_reconstruction", message) for message in reconstruction.warnings]
    grid_was_truncated = safe_span is not None and (
        safe_span < DEFAULT_GRID_SPAN_IN_STANDARD_ERRORS * reconstruction.standard_error
        or any(
            value < float(grid_working[0]) or value > float(grid_working[-1])
            for value in included_values
        )
    )
    if grid_was_truncated:
        warnings.append(
            _warning(
                "grid_truncated",
                "Grid expansion was truncated to keep the plotted payload finite. "
                "An extreme reference, pairwise candidate, or support bound may fall "
                "outside the x-axis.",
            )
        )
    if safe_span == 0.0:
        warnings.append(
            _warning(
                "grid_collapsed",
                "The estimate is at the finite working-scale boundary, so the x-grid "
                "collapses to the estimate.",
            )
        )
    warnings.extend(
        _display_range_warnings(
            display_range_working,
            estimate_working=reconstruction.estimate_working,
            lower_working=reconstruction.lower_working,
            upper_working=reconstruction.upper_working,
            null_working=reconstruction.null_working,
            thresholds_working=thresholds_working,
            candidate_a_working=candidate_a_working,
            candidate_b_working=candidate_b_working,
            support_lower_working=interval.lower_working,
            support_upper_working=interval.upper_working,
        )
    )
    if bool(np.any(grid_display_clipped)):
        warnings.append(
            _warning(
                "natural_axis_clipped",
                "Natural-axis grid values were clipped to finite positive values. "
                "Working-scale calculations are unchanged.",
            )
        )
    if interval.working_clipped:
        warnings.append(
            _warning(
                "support_interval_working_clipped",
                "A selected support-interval working-scale endpoint was clipped at the finite "
                "floating-point boundary.",
            )
        )
    if bool(np.any(interval_display_clipped)):
        warnings.append(
            _warning(
                "support_interval_display_clipped",
                "A selected support-interval natural-scale endpoint was clipped to a finite "
                "positive display value. Working-scale calculations are unchanged.",
            )
        )

    reference_rows, reference_warnings = _reference_rows(
        threshold_displays=thresholds_display,
        threshold_workings=thresholds_working,
        estimate_working=reconstruction.estimate_working,
        null_display=reconstruction.null_display,
        null_working=reconstruction.null_working,
        se=reconstruction.standard_error,
        support_lower_working=interval.lower_working,
        support_upper_working=interval.upper_working,
    )
    warnings.extend(reference_warnings)
    pairwise_rows, pairwise_warnings = _pairwise_rows(
        candidate_a_display=request.candidate_a,
        candidate_a_working=candidate_a_working,
        candidate_b_display=request.candidate_b,
        candidate_b_working=candidate_b_working,
        estimate_working=reconstruction.estimate_working,
        se=reconstruction.standard_error,
    )
    warnings.extend(pairwise_warnings)

    response: SupportResponse = {
        "meta": {
            "schema_version": 1,
            "app_version": __version__,
            "core_version": CORE_VERSION,
            "effect_spec": {
                "key": spec.key,
                "label": spec.label,
                "family": spec.family,
                "working_scale": spec.working_scale,
                "default_null": spec.default_null,
                "positive_only": spec.positive_only,
            },
            "estimate_source": reconstruction.estimate_source,
            "default_null_applied": reconstruction.default_null_applied,
            "grid_points": len(grid_working),
            "display_axis_scale": "natural" if spec.family == "ratio" else "identity",
            "display_range_active": request.display_range is not None,
            "display_range_display": (
                None
                if request.display_range is None
                else [float(value) for value in request.display_range]
            ),
            "display_range_working": (
                None
                if display_range_working is None
                else [float(value) for value in display_range_working]
            ),
            "selected_support_criterion": {
                "key": request.support_criterion,
                "label": criterion_label,
                "mle_to_bound_ratio": criterion_ratio,
            },
        },
        "reconstruction": {
            "estimate_display": reconstruction.estimate_display,
            "estimate_working": reconstruction.estimate_working,
            "provided_estimate_display": reconstruction.provided_estimate_display,
            "provided_estimate_working": reconstruction.provided_estimate_working,
            "reported_95_ci_display": [
                reconstruction.lower_display,
                reconstruction.upper_display,
            ],
            "reported_95_ci_working": [
                reconstruction.lower_working,
                reconstruction.upper_working,
            ],
            "null_display": reconstruction.null_display,
            "null_working": reconstruction.null_working,
            "standard_error_working": reconstruction.standard_error,
            "standard_error_method": reconstruction.se_method,
            "standard_error_lower_side": reconstruction.se_lower,
            "standard_error_upper_side": reconstruction.se_upper,
            "standard_error_from_width": reconstruction.se_width,
            "relative_asymmetry": reconstruction.relative_asymmetry,
        },
        "grid": {
            "effect_display": _float_list(grid_display),
            "effect_working": _float_list(grid_working),
            "standardized_distance": _float_list(z_values),
            "relative_likelihood": _float_list(relative_values),
            "log_relative_likelihood": _float_list(log_relative_values),
        },
        "support_interval": {
            "criterion_key": request.support_criterion,
            "criterion_label": criterion_label,
            "definition": (
                "The interval contains candidate values for which the CI-implied estimate is "
                "no more than R times as supported under the reconstructed Wald likelihood."
            ),
            "mle_to_bound_ratio": criterion_ratio,
            "log_relative_likelihood_cutoff": interval.log_relative_likelihood_cutoff,
            "relative_likelihood_cutoff": interval.relative_likelihood_cutoff,
            "lower_display": float(interval_display[0]),
            "upper_display": float(interval_display[1]),
            "lower_working": interval.lower_working,
            "upper_working": interval.upper_working,
            "lower_working_clipped": interval.lower_clipped,
            "upper_working_clipped": interval.upper_clipped,
            "lower_display_clipped": bool(interval_display_clipped[0]),
            "upper_display_clipped": bool(interval_display_clipped[1]),
        },
        "reference_support": reference_rows,
        "pairwise_comparisons": pairwise_rows,
        "warnings": warnings,
    }
    _strict_finite_tree(response)
    return response


def calculate_json(request_json: str) -> str:
    """Validate a strict JSON request and return strict JSON."""

    try:
        payload = json.loads(request_json, parse_constant=_reject_nonstandard_constant)
    except json.JSONDecodeError as exc:
        raise ValidationError("Request must be valid JSON.") from exc
    response = calculate(SupportRequest.from_mapping(payload))
    return json.dumps(
        response,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
