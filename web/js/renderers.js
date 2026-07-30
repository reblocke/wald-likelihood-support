function formatNumber(value) {
  if (value === null || value === undefined) {
    return "not representable";
  }
  const magnitude = Math.abs(value);
  if ((magnitude !== 0 && magnitude < 0.0001) || magnitude >= 1_000_000) {
    return Number(value).toExponential(5);
  }
  return Number(value).toLocaleString("en-US", {
    maximumSignificantDigits: 8,
  });
}

function formatRelativeLikelihood(value) {
  if (value === 0) {
    return "0 (underflow; use log value)";
  }
  return Number(value).toLocaleString("en-US", {
    maximumSignificantDigits: 7,
  });
}

function formatRatio(value, status) {
  if (status === "overflow") {
    return "overflow (see log ratio)";
  }
  if (status === "underflow_zero") {
    return "0 by underflow (see log ratio)";
  }
  return formatNumber(value);
}

function formatRange(values) {
  return `${formatNumber(values[0])} to ${formatNumber(values[1])}`;
}

function locationLabel(value) {
  return value.replaceAll("_", " ");
}

export function buildSummary(response) {
  const reconstruction = response.reconstruction;
  const nullRow = response.reference_support[0];
  const ratioText = formatRatio(
    nullRow.likelihood_ratio_estimate_to_candidate,
    nullRow.estimate_to_candidate_ratio_status,
  );
  const pairwise =
    response.pairwise_comparisons.length === 0
      ? ""
      : ` ${response.pairwise_comparisons[0].sentence}`;
  return (
    `The null value ${formatNumber(
      reconstruction.null_display,
    )} has normalized relative likelihood ` +
    `${formatRelativeLikelihood(
      nullRow.relative_likelihood,
    )}; the CI-implied estimate is ${ratioText} times as supported when the ` +
    `ordinary ratio is representable. The selected ${
      response.support_interval.criterion_label
    } support interval is ${formatNumber(
      response.support_interval.lower_display,
    )} to ${formatNumber(response.support_interval.upper_display)}.${pairwise}`
  );
}

export function buildCaption(response, displayOptions) {
  const effect = response.meta.effect_spec;
  const reconstruction = response.reconstruction;
  const interval = response.support_interval;
  const thresholds =
    response.reference_support.length === 1
      ? "No user reference thresholds are shown."
      : `User reference thresholds are marked at ${response.reference_support
          .slice(1)
          .map((row) => formatNumber(row.effect_display))
          .join(", ")}.`;
  const spacing =
    effect.family === "ratio"
      ? `${displayOptions.axisSpacing} natural-scale spacing`
      : "linear identity-scale spacing";
  const view =
    displayOptions.viewMode === "log"
      ? "log relative support, with zero at the estimate"
      : "normalized relative likelihood, with a maximum of 1 at the estimate";
  return (
    `Figure. Normalized Wald relative-likelihood curve for ${effect.label.toLowerCase()} ` +
    `reconstructed from the reported 95% confidence interval (${formatRange(
      reconstruction.reported_95_ci_display,
    )}). The likelihood is normalized at the CI-implied estimate ` +
    `${formatNumber(reconstruction.estimate_display)}; the null is ${formatNumber(
      reconstruction.null_display,
    )}. The shaded ${interval.criterion_label} support interval is ${formatNumber(
      interval.lower_display,
    )} to ${formatNumber(
      interval.upper_display,
    )}, using an estimate-to-bound ratio of ${formatNumber(
      interval.mle_to_bound_ratio,
    )}:1 and a log-relative-likelihood cutoff of ${formatNumber(
      interval.log_relative_likelihood_cutoff,
    )}. The plot shows ${view} and uses ${spacing}. ${thresholds} This is an ` +
    `approximate profile-likelihood-style view under Wald assumptions, not the original ` +
    `fitted-model likelihood or an exact profile likelihood. Relative-support ratios are not ` +
    `posterior odds or probabilities that an effect value is true.`
  );
}

function verticalShape(x, dash, color, width = 2) {
  return {
    type: "line",
    x0: x,
    x1: x,
    xref: "x",
    y0: 0,
    y1: 1,
    yref: "paper",
    line: { color, dash, width },
    layer: "above",
  };
}

function markerAnnotation(x, text, y, color) {
  return {
    x,
    xref: "x",
    y,
    yref: "paper",
    text,
    showarrow: false,
    font: { color, size: 13 },
    bgcolor: "rgba(255,255,255,0.9)",
    borderpad: 2,
  };
}

function plotLayout(response, displayOptions) {
  const reconstruction = response.reconstruction;
  const effect = response.meta.effect_spec;
  const interval = response.support_interval;
  const xRange = [
    response.grid.effect_display[0],
    response.grid.effect_display.at(-1),
  ];
  const insideXRange = (value) => value >= xRange[0] && value <= xRange[1];
  const usesLogX =
    effect.family === "ratio" && displayOptions.axisSpacing === "log";
  const annotationX = (value) => (usesLogX ? Math.log10(value) : value);
  const shapes = [];
  const annotations = [];

  if (
    interval.upper_display >= xRange[0] &&
    interval.lower_display <= xRange[1]
  ) {
    shapes.push({
      type: "rect",
      x0: Math.max(interval.lower_display, xRange[0]),
      x1: Math.min(interval.upper_display, xRange[1]),
      xref: "x",
      y0: 0,
      y1: 1,
      yref: "paper",
      fillcolor: "rgba(44, 122, 123, 0.13)",
      line: { width: 0 },
      layer: "below",
    });
    annotations.push(
      markerAnnotation(
        annotationX(reconstruction.estimate_display),
        `${interval.criterion_label} support interval`,
        0.08,
        "#285e61",
      ),
    );
  }

  const markerRows = [
    {
      value: reconstruction.estimate_display,
      label: "CI-implied estimate",
      dash: "solid",
      color: "#006d77",
      width: 3,
      y: 0.94,
    },
    {
      value: reconstruction.null_display,
      label: "Null",
      dash: "dot",
      color: "#263238",
      width: 2.5,
      y: 0.86,
    },
    ...response.reference_support.slice(1).map((row, index) => ({
      value: row.effect_display,
      label: row.label,
      dash: "dashdot",
      color: "#a44a3f",
      width: 2,
      y: 0.76 - ((index % 4) * 0.09),
    })),
  ];
  if (response.pairwise_comparisons.length > 0) {
    const comparison = response.pairwise_comparisons[0];
    markerRows.push(
      {
        value: comparison.candidate_a_display,
        label: "Candidate A",
        dash: "dash",
        color: "#6b46a1",
        width: 2,
        y: 0.42,
      },
      {
        value: comparison.candidate_b_display,
        label: "Candidate B",
        dash: "dash",
        color: "#9c5b17",
        width: 2,
        y: 0.33,
      },
    );
  }
  for (const marker of markerRows) {
    if (!insideXRange(marker.value)) {
      continue;
    }
    shapes.push(
      verticalShape(marker.value, marker.dash, marker.color, marker.width),
    );
    annotations.push(
      markerAnnotation(
        annotationX(marker.value),
        marker.label,
        marker.y,
        marker.color,
      ),
    );
  }

  const cutoff =
    displayOptions.viewMode === "log"
      ? interval.log_relative_likelihood_cutoff
      : interval.relative_likelihood_cutoff;
  shapes.push({
    type: "line",
    x0: 0,
    x1: 1,
    xref: "paper",
    y0: cutoff,
    y1: cutoff,
    yref: "y",
    line: { color: "#4a686b", dash: "dot", width: 1.4 },
    layer: "below",
  });
  annotations.push({
    x: 1,
    xref: "paper",
    y: cutoff,
    yref: "y",
    text: `${interval.criterion_label} cutoff`,
    showarrow: false,
    xanchor: "right",
    yanchor: "bottom",
    font: { color: "#3d5759", size: 12 },
    bgcolor: "rgba(255,255,255,0.84)",
  });

  const displayedRange =
    xRange[0] === xRange[1]
      ? null
      : usesLogX
        ? xRange.map((value) => Math.log10(value))
        : xRange;
  const isLogView = displayOptions.viewMode === "log";
  return {
    title: {
      text: isLogView
        ? `Log relative support across ${effect.label.toLowerCase()} values`
        : `Normalized Wald relative likelihood across ${effect.label.toLowerCase()} values`,
      font: { size: 20 },
    },
    xaxis: {
      title: { text: effect.label },
      type: usesLogX ? "log" : "linear",
      ...(displayedRange ? { range: displayedRange } : {}),
      tickformat: "~g",
      automargin: true,
    },
    yaxis: {
      title: {
        text: isLogView
          ? "Log relative support (0 at estimate)"
          : "Normalized relative likelihood (maximum 1)",
      },
      ...(isLogView ? {} : { range: [0, 1.03] }),
      automargin: true,
      zeroline: isLogView,
    },
    shapes,
    annotations,
    autosize: true,
    margin: { b: 104, l: 92, r: 34, t: 100 },
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    font: { color: "#17202a", size: 14 },
    showlegend: false,
  };
}

function renderDefinitionList(container, rows) {
  container.replaceChildren();
  for (const [label, value] of rows) {
    const wrapper = document.createElement("div");
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = label;
    description.textContent = value;
    wrapper.append(term, description);
    container.append(wrapper);
  }
}

function renderReconstruction(response, container) {
  const reconstruction = response.reconstruction;
  renderDefinitionList(container, [
    ["CI-implied estimate", formatNumber(reconstruction.estimate_display)],
    ["Reported 95% CI", formatRange(reconstruction.reported_95_ci_display)],
    ["Null value", formatNumber(reconstruction.null_display)],
    ["Working-scale SE", formatNumber(reconstruction.standard_error_working)],
    ["Working scale", response.meta.effect_spec.working_scale],
    [
      "Estimate source",
      response.meta.estimate_source === "provided_validated"
        ? "Provided estimate validated; CI midpoint used"
        : "Inferred from 95% CI midpoint",
    ],
  ]);
}

function renderSupportInterval(response, container) {
  const interval = response.support_interval;
  renderDefinitionList(container, [
    ["Criterion", interval.criterion_label],
    ["Display-scale interval", formatRange([interval.lower_display, interval.upper_display])],
    ["Working-scale interval", formatRange([interval.lower_working, interval.upper_working])],
    ["Estimate-to-bound ratio", `${formatNumber(interval.mle_to_bound_ratio)}:1`],
    [
      "Log-relative-likelihood cutoff",
      formatNumber(interval.log_relative_likelihood_cutoff),
    ],
    [
      "Relative-likelihood cutoff",
      formatRelativeLikelihood(interval.relative_likelihood_cutoff),
    ],
  ]);
}

function appendCells(tableRow, values) {
  values.forEach((text, index) => {
    const cell = document.createElement(index === 0 ? "th" : "td");
    if (index === 0) {
      cell.scope = "row";
    }
    cell.textContent = text;
    tableRow.append(cell);
  });
}

function renderReferences(response, table) {
  const body = table.querySelector("tbody");
  body.replaceChildren();
  for (const row of response.reference_support) {
    const tableRow = document.createElement("tr");
    appendCells(tableRow, [
      `${row.label}: ${formatNumber(row.effect_display)}`,
      formatNumber(row.effect_working),
      formatRelativeLikelihood(row.relative_likelihood),
      formatNumber(row.log_relative_likelihood),
      formatRatio(
        row.likelihood_ratio_estimate_to_candidate,
        row.estimate_to_candidate_ratio_status,
      ),
      formatRatio(
        row.likelihood_ratio_candidate_to_null,
        row.candidate_to_null_ratio_status,
      ),
      locationLabel(row.relative_to_estimate),
      locationLabel(row.relative_to_null),
      row.inside_selected_support_interval ? "Yes" : "No",
    ]);
    body.append(tableRow);
  }
}

function renderPairwise(response, table, empty, sentence) {
  const body = table.querySelector("tbody");
  body.replaceChildren();
  if (response.pairwise_comparisons.length === 0) {
    table.hidden = true;
    empty.hidden = false;
    sentence.textContent = "";
    return;
  }
  const comparison = response.pairwise_comparisons[0];
  const tableRow = document.createElement("tr");
  appendCells(tableRow, [
    formatNumber(comparison.candidate_a_display),
    formatNumber(comparison.candidate_b_display),
    formatNumber(comparison.log_likelihood_ratio_a_to_b),
    formatRatio(comparison.likelihood_ratio_a_to_b, comparison.ratio_status),
    locationLabel(comparison.direction),
  ]);
  body.append(tableRow);
  table.hidden = false;
  empty.hidden = true;
  sentence.textContent = comparison.sentence;
}

function renderWarnings(response, list, section) {
  list.replaceChildren();
  for (const warning of response.warnings) {
    const item = document.createElement("li");
    item.dataset.warningCode = warning.code;
    item.textContent = warning.message;
    list.append(item);
  }
  section.hidden = response.warnings.length === 0;
}

export async function renderResult(response, elements, displayOptions) {
  const summary = buildSummary(response);
  const caption = buildCaption(response, displayOptions);
  elements.summary.textContent = summary;
  elements.plotDescription.textContent =
    `${summary} The shaded region is the selected support interval. Direct markers identify ` +
    `the estimate, null, ${response.reference_support.length - 1} reference threshold(s), and ` +
    `${response.pairwise_comparisons.length > 0 ? "two pairwise candidates" : "no pairwise candidates"}.`;
  elements.caption.textContent = caption;
  renderReconstruction(response, elements.reconstruction);
  renderSupportInterval(response, elements.supportInterval);
  renderReferences(response, elements.referenceTable);
  renderPairwise(
    response,
    elements.pairwiseTable,
    elements.pairwiseEmpty,
    elements.pairwiseSentence,
  );
  renderWarnings(response, elements.warningList, elements.warningSection);

  if (!globalThis.Plotly) {
    throw new Error("The plotting library did not load.");
  }
  const isLogView = displayOptions.viewMode === "log";
  const trace = {
    type: "scatter",
    mode: "lines",
    name: "Normalized Wald relative likelihood",
    x: response.grid.effect_display,
    y: isLogView
      ? response.grid.log_relative_likelihood
      : response.grid.relative_likelihood,
    customdata: response.grid.effect_working.map((working, index) => [
      working,
      response.grid.standardized_distance[index],
      response.grid.relative_likelihood[index],
      response.grid.log_relative_likelihood[index],
    ]),
    line: { color: "#006d77", width: 3 },
    hovertemplate:
      "Effect: %{x:.6g}<br>Working scale: %{customdata[0]:.6g}" +
      "<br>Standardized distance: %{customdata[1]:.5g}" +
      "<br>Relative likelihood: %{customdata[2]:.5g}" +
      "<br>Log relative support: %{customdata[3]:.5g}<extra></extra>",
  };
  await globalThis.Plotly.react(
    elements.plot,
    [trace],
    plotLayout(response, displayOptions),
    {
      displaylogo: false,
      responsive: true,
      scrollZoom: false,
      modeBarButtonsToRemove: ["lasso2d", "select2d"],
    },
  );
  elements.result.hidden = false;
  return { caption, summary };
}
