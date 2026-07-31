# Maintenance

## Status

Maintenance status: **experimental released software**.

Version 0.1.4 is the current experimental app release and is deployed as a static GitHub Pages
site. Its release and hosted availability do not establish scientific, clinical, or regulatory
validity.

## Ownership

Maintainer: Brian Locke (`@reblocke`). Use repository issues and pull requests for public project
coordination through the scoped templates.

Scientific, code, privacy, accessibility, and release review currently remain with the
maintainer. Report vulnerabilities and privacy defects privately through
[SECURITY.md](../SECURITY.md), using only the smallest synthetic reproduction needed.

## Dependency updates

Review Pyodide, Plotly, Python, uv, Ruff, pytest, Hypothesis, Playwright, and GitHub Actions
updates deliberately. Dependabot groups weekly `uv` and GitHub Actions updates for review; it does
not authorize automatic merging. Keep each third-party Action pinned to a full commit SHA with its
reviewed version in a comment. `wald-inference` is scientific authority, not an incidental
dependency. For a core update:

1. review its release notes and scientific changes;
2. confirm that every used function remains root-public and behaviorally documented;
3. update the exact package version, wheel URL, and SHA-256 together;
4. regenerate and review `uv.lock`;
5. reconcile `pyproject.toml`, `uv.lock`, and `browser-stage.toml`;
6. run strict JSON, B01–B03/B08, generic-support, clean-stage, Chromium, and WebKit validation; and
7. record the adopted core version, artifact, checksum, and scientific impact in docs and the
   changelog.

Do not replace a prerelease with a differently built artifact under the same version. A checksum
change requires explicit provenance review and a new authoritative release artifact.

## Release

Releases require a reviewed pull request and an exact expected head. Before tagging:

1. verify a clean checkout and the intended semantic version;
2. complete every gate in `docs/VALIDATION.md`;
3. verify dependency and stage provenance without a sibling repository;
4. review public scientific, clinical-scope, privacy, accessibility, citation, and license copy;
5. record exact commands, runtime/browser versions, results, limitations, and skipped checks; and
6. confirm that the changelog and `CITATION.cff` describe the intended release rather than a plan.

Only then create an annotated tag on the reviewed merge commit. The release workflow binds the
exact remote annotated tag object to the event commit before it executes repository code, requires
the event commit to be contained in protected `main`, parses the project version with isolated
Python, reruns the complete suite under read-only contents permission, disables the shared
dependency cache for the release build, and creates the deterministic source archive,
browser-stage manifest, and SHA-256 checksums before a release exists.

A separate job with narrowly scoped contents-write permission uses an exact checksummed GitHub
CLI and the job-scoped GitHub token to create a draft stable release with every asset, re-download
and compare the draft assets and release body, and publish only the verified draft. It then
requires the published release to be immutable and verifies the release and every asset
attestation. The tag must equal `v` plus the authoritative project version, and the public release
body contains only that version's nonempty changelog section.

If the workflow fails after draft creation, retain the draft for inspection. Repair the workflow
and create a new tag only after the failure is understood; never move a published tag or replace a
published asset. Publish once into the intended stable lifecycle state only after hosted Pages and
portfolio-level validation are complete. Deployment remains a separate action; do not describe a
hosted app as available until an actual deployment has completed and a hosted smoke has passed.

Repository settings must retain read-only default workflow permissions, protect `main` and `v*`
tags, enable private vulnerability reporting and Dependabot security updates, and enable immutable
releases before the next tag is created. Confirm that setting operationally before tagging; the
workflow carries no external repository-settings credential and verifies immutability after
publication with its job-scoped GitHub token.

## Routine review

At least at each dependency or scientific-core change, review:

- open security and dependency advisories;
- browser/runtime compatibility;
- staged artifact and CDN integrity values;
- frozen and property-based scientific tests;
- strict response and exact CSV schemas;
- privacy network/storage scans;
- keyboard, focus, live-status, and text-equivalent behavior; and
- links, citation metadata, maintenance status, and known limitations.

## Deprecation

Version 0.1.0 is the first public experimental version. If it or a future released version is
superseded:

- announce the status in the README, changelog, repository description, and visible app;
- identify the last supported version and successor;
- retain reproducibility metadata and release artifacts where safe;
- provide a reasonable transition period appropriate to actual use; and
- never silently redirect, delete, or rewrite scientific history.
