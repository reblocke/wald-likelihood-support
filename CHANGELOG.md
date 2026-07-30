# Changelog

All notable app changes use a release-oriented record here. The app has not issued a release.
Future releases will follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
- Adopted the `wald-inference` v0.2.0 prerelease wheel:
  `https://github.com/reblocke/wald-inference-core/releases/download/v0.2.0/wald_inference-0.2.0-py3-none-any.whl`,
  SHA-256
  `3d1cd3f3c48478bcd898a60c7ac0c645e808b5f98bd6f843d0c75ef954cec2ab`.
- Recorded B01–B03 and likelihood-relevant B08 migration provenance from
  `reblocke/conf_curve_likelihood` commit
  `830756ecb11b4e8161f8dfe1fc75afc346ef4467`, with `rtol=1e-12` and `atol=1e-14`.
- Added scientific-scope, validation, privacy/no-PHI, decisions, maintenance, dependency,
  creation-template, citation, licensing, and LLM-facing documentation.
- Attributed evidential-likelihood and S−2 terminology to Zampieri et al.,
  doi:10.1164/rccm.202504-0809TR, retrieved 2026-04-23, under CC BY-NC-ND 4.0; no article figure,
  table, code, or substantial text was copied.
- Kept status experimental. This unreleased record does not claim a tag, app release, or hosted
  deployment.

## Creation template v0.1.0 — provenance only — 2026-07-29

- The generic creation scaffold supplied locked Python tooling, deterministic browser staging, a
  dedicated Web Worker, accessibility and privacy guardrails, export hooks, documentation
  structure, and test scaffolding.
- The template’s arithmetic demonstration carried no scientific authority and is not an app
  release in this repository.
