# Decisions

## 2026-07-29 — Keep the app likelihood-support only

The repository answers one question: relative support for candidate effects under a
confidence-interval-based Wald reconstruction.

The strict response is limited to `meta`, `reconstruction`, the five-field `grid`,
`support_interval`, `reference_support`, `pairwise_comparisons`, and `warnings`. The grid and CSV
contain only display effect, working effect, standardized distance, relative likelihood, and log
relative likelihood.

Compatibility curves and p-values as primary outputs, critical/design behavior, selection, Type
S/M, information multipliers, precision targets, priors, posteriors, and Bayes factors belong
elsewhere and are prohibited here.

## 2026-07-29 — Use published core APIs as the sole numerical authority

The app does not implement or copy Wald, likelihood, support-ratio, or support-interval formulas.
It delegates numerical work to root-public `wald_inference` APIs and owns only request validation,
orchestration, payload assembly, warnings, display, and exports.

The dependency target is the `wald-inference` v0.2.0 prerelease wheel at:

```text
https://github.com/reblocke/wald-inference-core/releases/download/v0.2.0/wald_inference-0.2.0-py3-none-any.whl
SHA-256 3d1cd3f3c48478bcd898a60c7ac0c645e808b5f98bd6f843d0c75ef954cec2ab
```

Exact-version and checksum agreement across package metadata, lockfile, and browser-stage
configuration is a release gate.

## 2026-07-29 — Describe the likelihood as normalized and approximate

Public wording must say that the display is a normalized, approximate Wald relative-likelihood
reconstruction from a reported 95% confidence interval. It must not claim to recover the exact
fitted-model profile likelihood, original data, model, variance estimator, or study design.

The Zampieri et al. article supports evidential-likelihood terminology and S−2 interpretation. It
does not convert this CI reconstruction into an exact model likelihood.

## 2026-07-29 — Preserve explicit A:B order and log-domain authority

Pairwise output is labeled `log L(A)/L(B)`. Positive values favor A and negative values favor B.
The finite signed log result is retained and remains authoritative when the ordinary A:B ratio
overflows or underflows.

Candidate A and B must be supplied together. Summaries and captions must name numerator and
denominator instead of presenting an unlabeled ratio.

## 2026-07-29 — Keep S−2 distinct from 2:1

S−2 uses the evidential criterion whose MLE-to-bound ratio is `exp(2)`, approximately 7.4:1. It is
not a 2:1 interval. The UI and response offer separate 2:1, 4:1, 8:1, and custom criteria, with a
finite custom ratio strictly greater than 1.

The existing integrated S−2 behavior is preserved through the core’s dedicated legacy-compatible
entry point; generic ratio-based intervals use the generic core entry point.

## 2026-07-29 — Keep display settings scientifically inert

A plausible display range changes only the plotted and exported grid. Natural-label logarithmic
versus linear ratio-axis spacing is browser presentation only. Neither choice may change the
reconstruction, reference support, pairwise comparisons, or selected support interval.

Warnings identify important values or interval endpoints outside the visible range and any finite
clipping.

## 2026-07-29 — Use strict JSON and accessible text

Successful responses contain only finite JSON numbers or documented `null` values. Nonstandard
numeric tokens are rejected before serialization. A natural ratio may be `null` on overflow while
its finite log result is retained.

Every substantive plot result has a textual or tabular equivalent. Inputs have labels, browser
parsing errors link to their controls, worker-domain errors remain focused in the alert summary,
focus remains visible, status changes are announced, and keyboard use does not depend on pointer
interaction.

When an explicit display range contains the CI-implied estimate, the grid includes that exact
working-scale value while preserving the requested endpoints and point count. A range that
genuinely excludes the estimate remains presentation-only and produces an explicit warning.

## 2026-07-29 — Preserve a strict client-side privacy boundary

The architecture has no backend, account, telemetry, persistence, cookie, input-bearing URL, or
upload path. Static CDN requests do not contain entered values. Exports and caption copies require
an explicit user action.

The app is intended for aggregate values and must not solicit or log PHI.

## 2026-07-29 — Record creation-template provenance without a live dependency

The repository was initialized from `reblocke/scientific-applet-template` v0.1.0 at commit
`a360bde95c192d8de4f9a3b531e73600ebf3d8b8`, tree
`6a6c8c33cbef24b5dcbd35706d2292d9d3e5e359`.

The template supplied creation-time engineering structure only. It is not a runtime framework and
does not authorize scientific formulas or claims.

## 2026-07-29 — Remain experimental and unreleased

Package metadata may carry a working development version, but no app release or deployment is
claimed. A release requires exact dependency reconciliation, clean-checkout staging, the full
scientific/contract/browser/privacy/accessibility suite, reviewed provenance, and a hosted smoke
only after an actual deployment.

Future decisions that change scientific meaning, dependencies, validation, privacy, exports,
accessibility, or maintenance must be appended with a date and rationale.
