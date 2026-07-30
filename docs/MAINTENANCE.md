# Maintenance

## Status

Maintenance status: **experimental released software**.

Version 0.1.1 is the current experimental app prerelease and is deployed as a static GitHub Pages
site. Its release and hosted availability do not establish scientific, clinical, or regulatory
validity.

## Ownership

Maintainer: Brian Locke (`@reblocke`). Use repository issues and pull requests for public project
coordination.

Scientific, code, privacy, accessibility, and release review currently remain with the
maintainer. Security or privacy-sensitive reports should avoid real input values and PHI; use a
minimal synthetic reproduction through the repository’s issue or pull-request workflow.

## Dependency updates

Review Pyodide, Plotly, Python, uv, Ruff, pytest, Hypothesis, Playwright, and GitHub Actions
updates deliberately. `wald-inference` is scientific authority, not an incidental dependency.
For a core update:

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

Only then create an annotated tag on the reviewed merge commit. Deployment is a separate action.
Do not describe a hosted app as available until an actual deployment has completed and a hosted
smoke has passed.

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
