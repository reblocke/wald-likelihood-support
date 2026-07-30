function fieldError(control, message) {
  control.setAttribute("aria-invalid", "true");
  return { controlId: control.id, message };
}

function parseRequiredNumber(form, name, label) {
  const control = form.elements.namedItem(name);
  const value = control.value.trim();
  if (value === "") {
    return { error: fieldError(control, `${label} is required.`) };
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return {
      error: fieldError(control, `${label} must be a finite number.`),
    };
  }
  return { value: parsed };
}

function parseOptionalNumber(form, name, label) {
  const control = form.elements.namedItem(name);
  const value = control.value.trim();
  if (value === "") {
    return { value: null };
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return {
      error: fieldError(control, `${label} must be a finite number or blank.`),
    };
  }
  return { value: parsed };
}

function parseThresholds(form) {
  const control = form.elements.namedItem("thresholds");
  const text = control.value.trim();
  if (text === "") {
    return { value: [] };
  }
  const values = text.split(/[,\s]+/).map(Number);
  if (values.some((value) => !Number.isFinite(value))) {
    return {
      error: fieldError(
        control,
        "Reference thresholds must be finite numbers separated by commas or spaces.",
      ),
    };
  }
  return { value: values };
}

function requirePair(errors, left, right, leftControl, rightControl, message) {
  if (left.error || right.error) {
    return;
  }
  if ((left.value === null) === (right.value === null)) {
    return;
  }
  errors.push(
    fieldError(left.value === null ? leftControl : rightControl, message),
  );
}

export function readRequest(form) {
  const estimate = parseOptionalNumber(form, "estimate", "Point estimate");
  const lower = parseRequiredNumber(form, "lower", "Lower 95% CI");
  const upper = parseRequiredNumber(form, "upper", "Upper 95% CI");
  const nullValue = parseOptionalNumber(form, "null_value", "Null value");
  const thresholds = parseThresholds(form);
  const candidateA = parseOptionalNumber(form, "candidate_a", "Candidate A");
  const candidateB = parseOptionalNumber(form, "candidate_b", "Candidate B");
  const rangeLower = parseOptionalNumber(
    form,
    "display_range_lower",
    "Plausible display range lower",
  );
  const rangeUpper = parseOptionalNumber(
    form,
    "display_range_upper",
    "Plausible display range upper",
  );
  const criterion = form.elements.namedItem("support_criterion").value;
  const customRatio =
    criterion === "custom"
      ? parseRequiredNumber(form, "custom_support_ratio", "Custom support ratio")
      : { value: null };
  const errors = [
    estimate.error,
    lower.error,
    upper.error,
    nullValue.error,
    thresholds.error,
    candidateA.error,
    candidateB.error,
    rangeLower.error,
    rangeUpper.error,
    customRatio.error,
  ].filter(Boolean);

  requirePair(
    errors,
    rangeLower,
    rangeUpper,
    form.elements.namedItem("display_range_lower"),
    form.elements.namedItem("display_range_upper"),
    "Plausible display range lower and upper must be supplied together.",
  );
  requirePair(
    errors,
    candidateA,
    candidateB,
    form.elements.namedItem("candidate_a"),
    form.elements.namedItem("candidate_b"),
    "Candidate A and candidate B must be supplied together.",
  );
  if (
    errors.length === 0 &&
    criterion === "custom" &&
    customRatio.value <= 1
  ) {
    errors.push(
      fieldError(
        form.elements.namedItem("custom_support_ratio"),
        "Custom support ratio must be greater than 1.",
      ),
    );
  }
  if (errors.length > 0) {
    return { errors, request: null };
  }

  const request = {
    effect_type: form.elements.namedItem("effect_type").value,
    estimate: estimate.value,
    lower: lower.value,
    upper: upper.value,
    null_value: nullValue.value,
    thresholds: thresholds.value,
    support_criterion: criterion,
    grid_points: Number(form.elements.namedItem("grid_points").value),
  };
  if (candidateA.value !== null && candidateB.value !== null) {
    request.candidate_a = candidateA.value;
    request.candidate_b = candidateB.value;
  }
  if (criterion === "custom") {
    request.custom_support_ratio = customRatio.value;
  }
  if (rangeLower.value !== null && rangeUpper.value !== null) {
    request.display_range_lower = rangeLower.value;
    request.display_range_upper = rangeUpper.value;
  }
  return { errors: [], request };
}

export function readDisplayOptions(form) {
  return {
    axisSpacing: form.elements.namedItem("axis_spacing").value,
    viewMode: form.elements.namedItem("view_mode").value,
  };
}
