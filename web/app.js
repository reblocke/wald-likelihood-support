import { clearFieldErrors, setStatus, showErrors } from "./js/accessibility.js";
import { APP_TITLE, EFFECT_OPTIONS, effectOption } from "./js/config.js";
import {
  copyCaption,
  exportCsv,
  exportDashboardPng,
  exportManuscriptPng,
} from "./js/exports.js";
import { readDisplayOptions, readRequest } from "./js/inputs.js";
import { renderResult } from "./js/renderers.js";
import { WorkerRuntime } from "./js/runtime.js";

const form = document.querySelector("#applet-form");
const errorSummary = document.querySelector("#error-summary");
const status = document.querySelector("#runtime-status");
const retryButton = document.querySelector("#retry-worker");
const calculateButton = document.querySelector("#calculate");
const result = document.querySelector("#result");
const plot = document.querySelector("#plot");
const exportButtons = [...document.querySelectorAll("[data-export]")];
const copyButton = document.querySelector("#copy-caption");
const emptyState = document.querySelector(".empty-state");
const effectSelect = document.querySelector("#effect-type");
const nullInput = document.querySelector("#null-value");
const axisGroup = document.querySelector("#axis-spacing-group");
const axisSpacing = document.querySelector("#axis-spacing");
const viewMode = document.querySelector("#view-mode");
const criterionSelect = document.querySelector("#support-criterion");
const customRatioField = document.querySelector("#custom-ratio-field");
const customRatioInput = document.querySelector("#custom-support-ratio");
const runtime = new WorkerRuntime();
const renderElements = {
  caption: document.querySelector("#figure-caption"),
  pairwiseEmpty: document.querySelector("#pairwise-empty"),
  pairwiseSentence: document.querySelector("#pairwise-sentence"),
  pairwiseTable: document.querySelector("#pairwise-table"),
  plot,
  plotDescription: document.querySelector("#plot-description"),
  reconstruction: document.querySelector("#reconstruction-summary"),
  referenceTable: document.querySelector("#reference-table"),
  result,
  summary: document.querySelector("#result-summary"),
  supportInterval: document.querySelector("#support-interval-summary"),
  warningList: document.querySelector("#warnings-list"),
  warningSection: document.querySelector("#warnings-section"),
};
let currentResponse = null;
let currentCaption = "";
let currentSummary = "";
let previousEffect = EFFECT_OPTIONS[0];

function setExportAvailability(enabled) {
  for (const button of [...exportButtons, copyButton]) {
    button.disabled = !enabled;
  }
}

function initializeEffectOptions() {
  effectSelect.replaceChildren();
  for (const option of EFFECT_OPTIONS) {
    const element = document.createElement("option");
    element.value = option.key;
    element.textContent = option.label;
    effectSelect.append(element);
  }
  effectSelect.value = EFFECT_OPTIONS[0].key;
}

function updateEffectControls() {
  const selected = effectOption(effectSelect.value);
  const currentNull = nullInput.value.trim();
  if (
    currentNull === "" ||
    Number(currentNull) === previousEffect.defaultNull
  ) {
    nullInput.value = String(selected.defaultNull);
  }
  const isRatio = selected.family === "ratio";
  axisGroup.hidden = !isRatio;
  axisSpacing.disabled = !isRatio;
  previousEffect = selected;
}

function updateCriterionControls() {
  const isCustom = criterionSelect.value === "custom";
  customRatioField.hidden = !isCustom;
  customRatioInput.disabled = !isCustom;
  customRatioInput.required = isCustom;
}

async function startRuntime() {
  calculateButton.disabled = true;
  retryButton.hidden = true;
  setStatus(status, "Loading the local Python runtime…", "loading");
  try {
    const ready = await runtime.restart();
    document.querySelector("#runtime-versions").textContent = ready.packages
      .map((entry) => `${entry.distribution} ${entry.version}`)
      .join(" · ");
    const corePackage = ready.packages.find(
      (entry) => entry.distribution === "wald-inference",
    );
    document.querySelector("#core-version").textContent = corePackage
      ? `wald-inference core ${corePackage.version}`
      : "Core version unavailable";
    calculateButton.disabled = false;
    setStatus(status, "Ready. Calculations stay in this browser.", "ready");
  } catch {
    retryButton.hidden = false;
    setStatus(status, "The calculation worker could not start.", "error");
  }
}

async function rerenderPresentation() {
  if (!currentResponse) {
    return;
  }
  const rendered = await renderResult(
    currentResponse,
    renderElements,
    readDisplayOptions(form),
  );
  currentCaption = rendered.caption;
  currentSummary = rendered.summary;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFieldErrors(form);
  const { errors, request } = readRequest(form);
  showErrors(errorSummary, errors);
  if (errors.length > 0) {
    return;
  }

  calculateButton.disabled = true;
  setExportAvailability(false);
  setStatus(status, "Calculating…", "loading");
  try {
    const response = await runtime.calculate(request);
    const rendered = await renderResult(
      response,
      renderElements,
      readDisplayOptions(form),
    );
    emptyState.hidden = true;
    currentResponse = response;
    currentCaption = rendered.caption;
    currentSummary = rendered.summary;
    setExportAvailability(true);
    setStatus(status, "Likelihood-support curve updated.", "ready");
  } catch (error) {
    currentResponse = null;
    currentCaption = "";
    currentSummary = "";
    result.hidden = true;
    emptyState.hidden = false;
    showErrors(errorSummary, [
      {
        controlId: null,
        message:
          error.code === "validation_error"
            ? error.message
            : "Calculation failed safely. Restart the worker and try again.",
      },
    ]);
    retryButton.hidden = false;
    setStatus(status, "Calculation failed.", "error");
  } finally {
    calculateButton.disabled = false;
  }
});

form.addEventListener("reset", () => {
  requestAnimationFrame(() => {
    clearFieldErrors(form);
    showErrors(errorSummary, []);
    result.hidden = true;
    emptyState.hidden = false;
    currentResponse = null;
    currentCaption = "";
    currentSummary = "";
    previousEffect = EFFECT_OPTIONS[0];
    updateEffectControls();
    updateCriterionControls();
    setExportAvailability(false);
    setStatus(status, "Ready. Calculations stay in this browser.", "ready");
  });
});

effectSelect.addEventListener("change", updateEffectControls);
criterionSelect.addEventListener("change", updateCriterionControls);
axisSpacing.addEventListener("change", rerenderPresentation);
viewMode.addEventListener("change", rerenderPresentation);
retryButton.addEventListener("click", startRuntime);

document.querySelector("#export-csv").addEventListener("click", () => {
  exportCsv(currentResponse, APP_TITLE);
});
document
  .querySelector("#export-manuscript")
  .addEventListener("click", async () => {
    await exportManuscriptPng(plot, APP_TITLE);
  });
document
  .querySelector("#export-dashboard")
  .addEventListener("click", async () => {
    await exportDashboardPng(plot, currentSummary, APP_TITLE);
  });
copyButton.addEventListener("click", async () => {
  await copyCaption(currentCaption);
  setStatus(status, "Caption copied.", "ready");
});

initializeEffectOptions();
updateEffectControls();
updateCriterionControls();
setExportAvailability(false);
startRuntime();
