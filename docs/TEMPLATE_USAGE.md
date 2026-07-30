# Creation-Template Provenance

This file records how `wald-likelihood-support` was created. It is not an instruction to
reinitialize the repository.

## Exact source

The repository was initialized from:

```text
Repository: reblocke/scientific-applet-template
Template tag: v0.1.0
Commit: a360bde95c192d8de4f9a3b531e73600ebf3d8b8
Tree: 6a6c8c33cbef24b5dcbd35706d2292d9d3e5e359
Commit date: 2026-07-29T22:52:31-06:00
License: MIT, Copyright (c) 2026 Brian Locke
```

The exact commit and tree matter because the tag identifies template engineering provenance, not
scientific authority.

## Initialization identity

The guarded initializer recorded:

```text
repository_name: wald-likelihood-support
distribution_name: wald-likelihood-support
import_name: wald_likelihood_support
app_title: Wald Likelihood Support
description: Explore normalized Wald relative support reconstructed from a reported estimate and
             95% confidence interval.
```

It renamed `src/template_applet/` to `src/wald_likelihood_support/`, updated repository identity
through the working tree, removed template-maintainer-only self-tests and provenance files, and
wrote the ignored `.applet-template-initialized.json` replacement report. The initializer did not
create scientific authority and did not modify Git history.

## What was reused

The creation template supplied:

- a static responsive HTML/CSS shell;
- a dedicated Pyodide Web Worker;
- manifest-driven package staging and byte-integrity verification;
- strict JSON request/response plumbing;
- accessible labels, linked errors, visible focus, and live status;
- explicit CSV, PNG, and caption export hooks;
- client-side privacy guardrails; and
- uv, Ruff, pytest, Hypothesis, Playwright, and GitHub workflow scaffolding.

The template contained only a conspicuous arithmetic demonstration. No Wald formula, scientific
claim, likelihood-support interpretation, fixture, figure, or app-specific prose came from the
template.

## What this app owns

`wald-likelihood-support` replaces the demonstration with:

- its focused request and seven-key response contract;
- likelihood-only browser controls, summaries, plot, warnings, and exact five-column CSV;
- delegation to root-public APIs in the published `wald-inference` prerelease;
- B01–B03/B08 and generic-support validation;
- normalized approximate-likelihood and clinical-scope boundaries;
- Zampieri citation provenance; and
- app-specific maintenance, privacy, accessibility, and release gates.

## Ongoing relationship

The creation template is not installed, imported, fetched, or loaded at runtime. There is no
automatic upstream synchronization. Future engineering ideas may be reviewed and adopted as
ordinary, explicit changes; the app must never overwrite its scientific scope or behavior merely
to match a newer template.

Do not rerun the initializer on this repository. Development and verification use the app’s own
instructions:

```bash
uv sync --locked
uv run playwright install chromium webkit
make verify
git diff --check
git status --short
```

These commands do not themselves establish a release or deployment. Release requirements are in
`docs/VALIDATION.md` and `docs/MAINTENANCE.md`.
