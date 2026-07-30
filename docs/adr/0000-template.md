# ADR 0000: Creation-time applet template

- Status: accepted
- Date: 2026-07-29
- Owner: Brian Locke

## Context

The focused app needed a static, client-side engineering shell with a verified Pyodide worker,
accessible text output, explicit exports, privacy guardrails, and reproducible browser staging.
Those mechanisms are engineering infrastructure, not scientific authority.

## Decision

Initialize this repository once from `reblocke/scientific-applet-template` v0.1.0 at commit
`a360bde95c192d8de4f9a3b531e73600ebf3d8b8`, then own the resulting code locally. The template is
not installed or fetched at runtime. Released root-public `wald_inference` APIs remain the sole
authority for every numerical reconstruction and likelihood-support calculation.

## Alternatives

- A live shared UI package was rejected because it would couple app availability and scientific
  releases to an unrelated runtime framework.
- Rebuilding the worker, staging, privacy, accessibility, and export shell from scratch was
  rejected because the reviewed template already provides those bounded mechanisms.

## Consequences

The repository may evolve its copied UI independently, but must deliberately review upstream
engineering ideas rather than silently resynchronize. Template provenance stays recorded in
`docs/TEMPLATE_USAGE.md`. Scientific behavior, validation, dependencies, public wording, and
release evidence remain this repository's responsibility.
