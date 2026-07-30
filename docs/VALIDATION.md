# Validation

## Status

This repository is experimental. No app release or hosted deployment has been validated or
claimed. The checks below are acceptance requirements; their presence in this document is not a
claim that the full suite has passed.

Engineering verification demonstrates implementation consistency. It does not establish that a
source study used a valid Wald model, that a chosen threshold is clinically meaningful, or that
the app is scientifically, clinically, or regulatorily validated.

## Numerical authority

All numerical acceptance tests must exercise root-public APIs from the exact `wald-inference`
v0.2.0 prerelease wheel:

```text
https://github.com/reblocke/wald-inference-core/releases/download/v0.2.0/wald_inference-0.2.0-py3-none-any.whl
SHA-256 3d1cd3f3c48478bcd898a60c7ac0c645e808b5f98bd6f843d0c75ef954cec2ab
```

The app must not maintain an independent formula oracle. Direct root-public core calls are
compared with app responses, while source-controlled fixtures preserve integrated-browser
migration behavior.

## Frozen migration baseline

The baseline source is `reblocke/conf_curve_likelihood` at exact commit
`830756ecb11b4e8161f8dfe1fc75afc346ef4467`:

```text
tests/golden/requests/B01.json
tests/golden/responses/B01.json
tests/golden/requests/B02.json
tests/golden/responses/B02.json
tests/golden/requests/B03.json
tests/golden/responses/B03.json
tests/golden/requests/B08a-additive-midpoint.json
tests/golden/responses/B08a-additive-midpoint.json
tests/golden/requests/B08b-s-minus-2-clipping.json
tests/golden/responses/B08b-s-minus-2-clipping.json
tests/golden/requests/B08c-log-likelihood-fallback.json
tests/golden/responses/B08c-log-likelihood-fallback.json
tests/golden/requests/B08d-ratio-natural-clipping.json
tests/golden/responses/B08d-ratio-natural-clipping.json
```

B01–B03 store complete 401-point integrated responses. B08a–d are compact edge summaries rather
than replacement full-response contracts. Scientific floating-point comparisons use
`rtol=1e-12` and `atol=1e-14`; effect-registry identity/configuration values remain exact.

The focused app extracts only likelihood-support behavior:

- **B01:** additive reconstruction, peak normalization, null and threshold support, and S−2
  endpoints;
- **B02:** ratio reconstruction on the log working scale with natural-scale output;
- **B03:** exact display-window endpoints while reconstruction, support interval, and reference
  summaries remain unchanged from B02;
- **B08a:** a safe finite midpoint for opposite-signed extreme additive bounds;
- **B08b:** finite support-interval endpoint clipping with an explicit warning;
- **B08c:** retention of a finite signed log comparison when the ordinary ratio overflows; and
- **B08d:** finite natural-scale ratio output and clipping warnings near floating-point limits.

The integrated B08e case is specific to repeated-study design distance. Design behavior is outside
this repository’s scope and is not migrated. Its general fail-before-nonstandard-JSON principle is
retained.

## Scientific and contract targets

Required tests cover:

- reconstruction parity for additive and ratio effect families;
- normalized peak support and zero log support at the estimate;
- symmetry around the estimate on the working scale;
- expected 95% confidence-limit behavior inherited from the core;
- reference-support identities for the estimate, null, and thresholds;
- explicit A:B order, sign reversal when A and B are swapped, and ordinary-ratio reciprocity when
  both ratios are representable;
- endpoint agreement for S−2, 2:1, 4:1, 8:1, and custom criteria;
- wider intervals for larger MLE-to-bound ratios;
- the legacy S−2 behavior and its distinction from 2:1;
- equality of scientific results across natural-label logarithmic and linear ratio-axis spacing;
- strict validation of finite values, positive ratio inputs, paired A/B fields, paired display
  limits, odd grid bounds, and custom ratios greater than 1;
- finite log-domain retention across ordinary-ratio overflow and underflow;
- strict JSON with no `NaN`, positive infinity, or negative infinity; and
- exact response top-level keys and exact five-field grid/CSV order.

Compatibility, p-value, design, selection, Type S/M, information, precision, prior, posterior, and
Bayes-factor fields are prohibited from the focused response.

## Browser parity and accessibility

The same source-controlled request must produce equivalent local-Python and Pyodide responses at
the documented tolerance. The stage manifest records Python package versions, Pyodide 0.29.3,
every staged file hash, each package hash, and the aggregate bundle hash.

Browser acceptance covers:

- initial worker load and calculation recovery after a validation error;
- accessible labels, linked errors, visible focus, keyboard operation, and live status;
- textual reconstruction, interval, reference, and pairwise results independent of the plot;
- direct estimate, null, threshold, candidate, and interval markers where visible;
- ratio-axis spacing and display-range isolation;
- exact five-column CSV output;
- dashboard and figure-only PNG output plus a copyable, scope-correct caption;
- Chromium end-to-end coverage and an initial WebKit smoke; and
- confirmation that entered synthetic values do not appear in URLs or network requests.

Fixtures and screenshots must be synthetic or clearly public aggregate examples and must contain
no protected health information.

## Interpretation review

Public copy, visible labels, captions, warnings, tables, and exports must consistently say
“normalized, approximate Wald relative likelihood” and must not say or imply “exact fitted-model
profile likelihood.”

Pairwise labels must identify numerator and denominator as `log L(A)/L(B)` and explain the sign.
The ordinary ratio may be unavailable while the finite log result remains valid. S−2 must be
described as approximately 7.4:1 from the MLE to a boundary, not as 2:1.

## Release gate

Before any app tag, release, or deployment claim:

1. verify the exact reviewed commit and intended semantic version;
2. confirm `pyproject.toml`, `uv.lock`, and `browser-stage.toml` resolve the same core wheel and
   checksum;
3. run `uv sync --locked`, `make stage-web`, `make fmt-check`, `make lint`, `make test`,
   `make e2e`, `make e2e-webkit-smoke`, and `make verify`;
4. reproduce the stage from a clean checkout without a sibling repository;
5. review generated stage hashes and strict-JSON output;
6. confirm B01–B03/B08 and generic-support acceptance targets;
7. review privacy, accessibility, provenance, and public copy;
8. record failures, skips, browser/runtime versions, and known limitations; and
9. only after deployment, run and record a hosted smoke test.

Until those gates are complete, the only truthful status is experimental and unreleased.
