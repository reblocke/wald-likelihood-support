export const APP_TITLE = "Wald Likelihood Support";
export const APP_VERSION = "0.1.4";
export const CORE_VERSION = "0.4.2";
export const PYODIDE_VERSION = "0.29.3";
export const REPOSITORY_URL =
  "https://github.com/reblocke/wald-likelihood-support";
export const HOSTED_URL =
  "https://reblocke.github.io/wald-likelihood-support/";

export const EFFECT_OPTIONS = [
  {
    key: "odds_ratio",
    label: "Odds ratio",
    family: "ratio",
    defaultNull: 1,
  },
  {
    key: "risk_ratio",
    label: "Risk ratio",
    family: "ratio",
    defaultNull: 1,
  },
  {
    key: "hazard_ratio",
    label: "Hazard ratio",
    family: "ratio",
    defaultNull: 1,
  },
  {
    key: "incidence_rate_ratio",
    label: "Incidence rate ratio",
    family: "ratio",
    defaultNull: 1,
  },
  {
    key: "ratio_of_means",
    label: "Ratio of means",
    family: "ratio",
    defaultNull: 1,
  },
  {
    key: "mean_difference",
    label: "Mean difference",
    family: "additive",
    defaultNull: 0,
  },
  {
    key: "risk_difference",
    label: "Risk difference",
    family: "additive",
    defaultNull: 0,
  },
  {
    key: "rate_difference",
    label: "Rate difference",
    family: "additive",
    defaultNull: 0,
  },
  {
    key: "regression_coefficient",
    label: "Regression coefficient",
    family: "additive",
    defaultNull: 0,
  },
];

export function effectOption(key) {
  return EFFECT_OPTIONS.find((option) => option.key === key) || EFFECT_OPTIONS[0];
}
