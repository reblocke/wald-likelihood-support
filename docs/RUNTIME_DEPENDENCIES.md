# Runtime Dependencies and Provenance

## Scientific core

`wald-inference` is the sole numerical authority for reconstruction, scale conversion, grid
construction, standardized distance, normalized relative likelihood, log relative likelihood,
support ratios, pairwise log support ratios, and support intervals. The app imports only
root-public APIs and does not copy their formulas.

The exact dependency target is the official v0.4.1 prerelease wheel published on 2026-07-30:

```text
Release: https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.1
Wheel:   https://github.com/reblocke/wald-inference-core/releases/download/v0.4.1/wald_inference-0.4.1-py3-none-any.whl
SHA-256: d7272023f65088729d3ff997cab7cac57b84f22ac6108244ec2170434557d99b
Size:    37939 bytes
Tag:     v0.4.1
Commit:  f4613177b6dc81d194aa70762152de2bfa86663b
License: MIT, Copyright (c) 2026 Brian Locke
```

GitHub records this official release as a prerelease. Version 0.4.1 preserves the finite support
endpoint checks and repairs pairwise support-ratio coherence by delegating the pairwise result to
the authoritative log-domain primitive. It also rejects unrepresentable natural-scale ratio
underflow. The focused app adds or copies no numerical formula.

The wheel URL and digest must agree in `pyproject.toml`, `uv.lock`, and `browser-stage.toml` before
any app release. A local sibling checkout, branch dependency, editable external core, localhost
URL, or unverified substitute artifact is prohibited.

## Browser runtime

- Pyodide 0.29.3 is loaded from its versioned jsDelivr path.
- Plotly.js 3.1.0 is loaded from Plotly’s versioned CDN path.
- NumPy and SciPy are loaded as Pyodide-provided packages for the staged core.
- Generated local app/core files are listed and hashed by `web/assets/py/manifest.json`.

These CDN requests are static and do not include user values. Availability still depends on the
user reaching the CDNs. Their URLs are versioned, but the generated Python stage manifest does not
content-hash CDN responses. The current HTML/worker loading path therefore relies on HTTPS and the
named CDN for those assets; any URL update, SRI addition, or decision to vendor assets requires
explicit review.

## Python packages

`uv.lock` controls local and CI resolution. `browser-stage.toml` independently states which
installed package directories are copied into the browser and the exact expected versions.
The stage verifies the configured artifact URL and SHA-256 against the installed distribution
metadata, then records file, package, and aggregate hashes.

Direct runtime requirements are:

- `wald-inference` 0.4.1 prerelease, exact URL/checksum above, MIT;
- NumPy `>=2.2.5,<2.3`, numerical array support required by the core, BSD-3-Clause; and
- SciPy `>=1.14.1,<1.15` through the core/Pyodide runtime, BSD-3-Clause.

Development-only tools such as uv, Ruff, pytest, Hypothesis, and Playwright do not execute in the
published static browser bundle. Their resolved versions remain lockfile and CI provenance.

## Scientific-reference provenance

Terminology for evidential likelihood, likelihood ratios, support, and S−2 intervals is attributed
to:

> Zampieri FG, Cahusac PMB, Maia IS, Yehya N, Meyer NJ, Li F, Harhay MO. Trial Analysis and
> Interpretation in Critical Care Using the Evidential (Likelihood) Approach: Rationale and
> Practical Considerations. *American Journal of Respiratory and Critical Care Medicine*.
> 2025;211(9):1610–1621. doi:10.1164/rccm.202504-0809TR.

- Article URL: `https://academic.oup.com/ajrccm/article/211/9/1610/8300617`
- DOI URL: `https://doi.org/10.1164/rccm.202504-0809TR`
- Repository retrieval date: 2026-04-23
- Article license: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International
  (CC BY-NC-ND 4.0)

The article is a cited interpretive source, not executable code. No article figure, table, code,
or substantial text was copied. The citation does not imply that a confidence-interval-based Wald
reconstruction is the original study’s exact fitted likelihood.

## Frozen-behavior provenance

B01–B03 and likelihood-relevant B08 behavior originates in `reblocke/conf_curve_likelihood` at
commit `830756ecb11b4e8161f8dfe1fc75afc346ef4467`. The named migration fixtures were frozen at
commit `5fd501dd947d9b951d736014cfc2b310efa5e7b0` under tag
`pre-split-baseline-2026-07-29`. They are behavioral anchors at the hashes and tolerances
documented in `docs/VALIDATION.md`; they are not runtime dependencies.

## Creation provenance

The engineering scaffold is `reblocke/scientific-applet-template` v0.1.0 at exact commit
`a360bde95c192d8de4f9a3b531e73600ebf3d8b8` and tree
`6a6c8c33cbef24b5dcbd35706d2292d9d3e5e359`. It was copied at repository creation and is not a
runtime dependency.

## Licenses

This repository is MIT licensed, Copyright (c) 2026 Brian Locke. The creation template and
`wald-inference` are separately MIT licensed by the same copyright holder. Pyodide, Plotly,
Python, NumPy, SciPy, development tools, papers, and publisher assets retain their own licenses.

No external paper license is transferred to app code. Do not copy an external artifact, figure,
table, code block, or substantial text without confirming rights, attribution, and compatibility.
