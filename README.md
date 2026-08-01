# Wald Likelihood Support

[![CI](https://github.com/reblocke/wald-likelihood-support/actions/workflows/ci.yml/badge.svg)](https://github.com/reblocke/wald-likelihood-support/actions/workflows/ci.yml)

An experimental, static app for exploring normalized Wald relative support reconstructed from a
reported estimate and two-sided 95% confidence interval.

> **Experimental release:** version 0.1.4 is published as an experimental release, and the
> client-side app is available at
> [reblocke.github.io/wald-likelihood-support](https://reblocke.github.io/wald-likelihood-support/).
> Engineering and hosted-contract verification cannot establish scientific, clinical, or
> regulatory validity.

Public engineering, scientific-boundary, and accessibility reports use the scoped issue forms in
`.github/`. Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md); never put
protected health information, credentials, restricted data, or sensitive values in a public
report. Contribution and release requirements are documented in
[CONTRIBUTING.md](CONTRIBUTING.md).

## Focused question

Under a one-parameter Wald reconstruction of a reported estimate and 95% confidence interval, how
much relative support do the data provide for selected candidate effect values?

## Why this app exists and intended audience

A reported confidence interval can be used to compare candidate effects under an explicit Wald
approximation, but that comparison is easily confused with an exact fitted-model likelihood or a
posterior probability. This focused app makes the normalized support curve, interval criterion,
and pairwise comparison order inspectable without claiming to recover the original analysis.

The app is intended for researchers, educators, reviewers, and scientifically trained readers who
need a transparent sensitivity display from aggregate published results. Representative uses are
methodological teaching, manuscript review, and sensitivity discussion. It is not clinical
decision support or a substitute for the original model and data.

## Inputs and outputs

The focused request accepts:

- an effect-measure key supported by `wald_inference`;
- a lower and upper two-sided 95% confidence limit;
- an optional point estimate, used to validate the confidence-interval reconstruction;
- an optional null value and zero or more reference thresholds;
- an optional paired candidate A and candidate B;
- one support-interval criterion: S−2, 2:1, 4:1, 8:1, or a custom ratio greater than 1;
- an optional plausible display range;
- an odd grid size from 101 through 1601 points; and
- browser-only logarithmic or linear spacing for natural-scale ratio labels.

The strict response is deliberately limited to:

```text
meta
reconstruction
grid
support_interval
reference_support
pairwise_comparisons
warnings
```

The grid and CSV export use exactly five aligned fields:

```text
effect_display
effect_working
standardized_distance
relative_likelihood
log_relative_likelihood
```

Textual summaries accompany the plot so that no result depends on color or graphics alone.
Explicit local actions provide the five-column CSV, dashboard PNG, figure-only PNG, and copyable
caption.

## Interpretation boundary

The display is a **normalized, approximate Wald relative-likelihood reconstruction**. It is
normalized to peak at the confidence-interval-implied estimate. It is not the exact fitted-model
profile likelihood from the original analysis, and it does not recover the original model,
variance estimator, study design, or raw data.

Pairwise output uses the explicit order `log L(A)/L(B)`: a positive value favors candidate A, a
negative value favors candidate B, and zero indicates equal support under the reconstruction.
The finite log-domain comparison remains authoritative when an ordinary A:B ratio overflows or
underflows.

S−2 is an evidential support criterion corresponding to an MLE-to-bound ratio of `exp(2)`, about
7.4:1. It is not a 2:1 support interval. The separately selectable 2:1, 4:1, and 8:1 criteria use
their stated MLE-to-bound ratios.

## Deliberate non-goals

This focused app does not provide:

- compatibility curves or p-values as primary outputs;
- critical-effect or power calculations;
- repeated-study design metrics, selection rules, Type S, or Type M;
- information multipliers or precision targets;
- priors, posterior probabilities, Bayes factors, or Bayesian inference;
- clinical thresholds, treatment recommendations, diagnosis, or medical-device functionality; or
- evidence that a reported interval is truly Wald-based beyond the documented reconstruction
  checks.

Reference thresholds are user-supplied comparison markers. The app does not validate their
scientific or clinical importance.

## Numerical authority and provenance

The app does not implement or copy Wald, relative-likelihood, support-ratio, or support-interval
formulas. Root-public APIs from the published Core release
[`wald-inference`](https://github.com/reblocke/wald-inference-core) are the sole numerical
authority.

The current dependency target is the official stable, immutable `wald-inference` v0.4.2 wheel:

```text
https://github.com/reblocke/wald-inference-core/releases/download/v0.4.2/wald_inference-0.4.2-py3-none-any.whl
SHA-256 225331d7b9d7b70e2508eecb92851a92a8c4e245baf412a1eb0f464d85da1349
```

The extracted behavior comes from `reblocke/conf_curve_likelihood` at source commit
`830756ecb11b4e8161f8dfe1fc75afc346ef4467`. The named B01–B03 and likelihood-relevant B08
fixtures were frozen later at commit `5fd501dd947d9b951d736014cfc2b310efa5e7b0` under tag
`pre-split-baseline-2026-07-29`. See [docs/VALIDATION.md](docs/VALIDATION.md) for fixture hashes,
tolerances, and limits.

Terminology for evidential likelihood, likelihood ratios, support, and S−2 intervals is attributed
to Zampieri and colleagues:

> Zampieri FG, Cahusac PMB, Maia IS, Yehya N, Meyer NJ, Li F, Harhay MO. Trial Analysis and
> Interpretation in Critical Care Using the Evidential (Likelihood) Approach: Rationale and
> Practical Considerations. *American Journal of Respiratory and Critical Care Medicine*.
> 2025;211(9):1610–1621. doi:
> [10.1164/rccm.202504-0809TR](https://doi.org/10.1164/rccm.202504-0809TR).

The repository recorded retrieval on 2026-04-23. The article is distributed under
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). No article figure, table,
code, or substantial text is copied into this repository; the citation does not make the paper a
runtime dependency or imply that this CI-based reconstruction is an exact model likelihood.

## Architecture

```text
browser form
  -> dedicated same-origin Web Worker
  -> integrity-verified generated Python bundle
  -> wald_likelihood_support.contract.calculate_json
  -> root-public wald_inference APIs
  -> strict JSON response
  -> accessible text + Plotly figure + explicit local exports
```

- `src/wald_likelihood_support/` is the app source of truth.
- `browser-stage.toml` binds the app and core package identities and artifact provenance.
- `scripts/stage_browser_packages.py` stages installed packages and emits file, package, and
  aggregate SHA-256 hashes.
- `web/pyodide_worker.js` verifies staged bytes before importing Python.
- `web/assets/py/` is generated, ignored, and never edited by hand.

## Privacy

Computation is client-side. There is no backend, database, account, telemetry, cookie, persistent
browser storage, input-bearing URL, or automatic upload. Values exist only in the page and worker
memory unless the user explicitly downloads or copies an output.

The app neither requires nor is designed to receive patient-level data. Do not enter protected
health information or other identifying data. Static CDN requests do not contain entered values,
although CDN operators receive ordinary request metadata such as IP address and browser headers.
See [docs/PRIVACY.md](docs/PRIVACY.md).

## Related Wald tools

- [Wald inference tools catalog](https://reblocke.github.io/wald-inference-tools/)
- [Adjacent focused app: compatibility curve](https://reblocke.github.io/compatibility-curve/)
- [Integrated workbench](https://reblocke.github.io/conf_curve_likelihood/)
- [Source repository](https://github.com/reblocke/wald-likelihood-support)
- [wald-inference Core v0.4.2](https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.2)
- [Privacy note](https://github.com/reblocke/wald-likelihood-support/blob/main/docs/PRIVACY.md)

These are static navigation links, not runtime dependencies.

## Local development

```bash
uv sync --locked
uv run playwright install chromium webkit
make stage-web
make fmt-check
make lint
make test
make e2e
make e2e-webkit-smoke
make verify
```

`make serve` starts a local static server. A clean checkout must be able to stage and verify
without a sibling source repository. A passing local command alone is not evidence that a release
or hosted deployment exists; verify the corresponding GitHub release, Pages deployment, and live
contract.

A new version is published only from an annotated tag whose exact remote tag object resolves to an
event commit already contained in protected `main`. The release workflow binds those identities
before executing repository code, reruns the complete suite with read-only contents permission,
builds a deterministic source archive, browser-stage manifest, and checksums, and transfers them
to a narrowly write-enabled publishing job. Using only the job-scoped GitHub token, that job
creates one draft stable release, re-downloads and compares the exact release body and every
asset, publishes only the verified draft, and verifies the resulting immutable release and asset
attestations. Credentialed commands use an exact checksummed GitHub CLI. Release notes contain
only the tagged version's nonempty changelog section.

## Creation provenance

This repository was initialized from `reblocke/scientific-applet-template` v0.1.0 at exact commit
`a360bde95c192d8de4f9a3b531e73600ebf3d8b8` and tree
`6a6c8c33cbef24b5dcbd35706d2292d9d3e5e359`. The template was a creation-time scaffold and is not
a runtime dependency. Details are in [docs/TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md).

## License and citation

Repository code is MIT licensed, Copyright (c) 2026 Brian Locke. External packages and the cited
article retain their own licenses. Use two complementary citations when applicable:

- **Software:** cite version 0.1.4 and, for exact reproducibility, its tagged commit using
  [CITATION.cff](CITATION.cff).
- **Method context:** cite Zampieri et al. above when using the evidential-likelihood, support,
  likelihood-ratio, or S−2 terminology.

The method citation does not replace the software citation and is not the numerical authority for
the implementation; the exact pinned Core release and its tests govern executed behavior.
