# Changelog

All notable app changes use a release-oriented record here. Releases follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.1] — 2026-07-30

- Publish the navigation-enabled Pages source as a checksum-addressed patch release so the
  deployed app, annotated tag, and release artifacts resolve to the same commit.
- Prevent narrow-screen horizontal overflow by allowing result panels to shrink and resizing the
  Plotly plot only after the results are visible and one animation frame has elapsed.
- Preserve the v0.1.0 focused response/export contracts while upgrading the sole numerical
  authority to checksum-pinned `wald-inference` v0.4.1; no Wald or likelihood formula is added or
  copied locally.

## [0.1.0] — 2026-07-30

- Initialized the `wald-likelihood-support` repository identity from
  `reblocke/scientific-applet-template` v0.1.0 at commit
  `a360bde95c192d8de4f9a3b531e73600ebf3d8b8`, tree
  `6a6c8c33cbef24b5dcbd35706d2292d9d3e5e359`.
- Defined the likelihood-only seven-key response and exact five-field grid/CSV boundary.
- Limited scope to normalized approximate Wald relative likelihood, support intervals, reference
  support, and optional A:B comparisons.
- Excluded compatibility/p-values, critical/design behavior, selection, Type S/M, information,
  precision, priors, posteriors, and Bayes factors.
- Recorded explicit `log L(A)/L(B)` ordering, log-domain overflow behavior, display isolation, and
  the distinction between S−2 and a 2:1 interval.
- Adopted the official `wald-inference` v0.2.1 prerelease wheel:
  `https://github.com/reblocke/wald-inference-core/releases/download/v0.2.1/wald_inference-0.2.1-py3-none-any.whl`,
  SHA-256
  `dcede569ff923061313635f2f680de9e3f8d1ea9415ef1b9391a0756023212fc`, whose
  annotated tag resolves to commit `4628a9ce9a6e051ce4b66e18e1d33536346696ac`.
- Added scientific and browser regressions requiring an authored `ValidationError`, with no
  traceback or local path, when adjacent binary64 confidence limits around `1e308` cannot encode
  the requested support boundary accurately.
- Recorded behavior provenance from `reblocke/conf_curve_likelihood` commit
  `830756ecb11b4e8161f8dfe1fc75afc346ef4467` and the later frozen B01–B03/B08 fixture commit
  `5fd501dd947d9b951d736014cfc2b310efa5e7b0` / tag
  `pre-split-baseline-2026-07-29`, with `rtol=1e-12` and `atol=1e-14`.
- Added scientific-scope, validation, privacy/no-PHI, decisions, maintenance, dependency,
  creation-template, citation, licensing, and LLM-facing documentation.
- Attributed evidential-likelihood and S−2 terminology to Zampieri et al.,
  doi:10.1164/rccm.202504-0809TR, retrieved 2026-04-23, under CC BY-NC-ND 4.0; no article figure,
  table, code, or substantial text was copied.
- Issued v0.1.0 as an experimental app prerelease with a static GitHub Pages deployment.
  Engineering and hosted-contract verification do not establish scientific, clinical, or
  regulatory validity.

## Creation template v0.1.0 — provenance only — 2026-07-29

- The generic creation scaffold supplied locked Python tooling, deterministic browser staging, a
  dedicated Web Worker, accessibility and privacy guardrails, export hooks, documentation
  structure, and test scaffolding.
- The template’s arithmetic demonstration carried no scientific authority and is not an app
  release in this repository.

[Unreleased]: https://github.com/reblocke/wald-likelihood-support/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/reblocke/wald-likelihood-support/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/reblocke/wald-likelihood-support/releases/tag/v0.1.0
