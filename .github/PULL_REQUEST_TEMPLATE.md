## Scope

Describe the engineering, scientific-boundary, documentation, governance, or maintenance problem
addressed. Name `wald-inference-core` when the released numerical package owns the affected
behavior.

## Risk and release impact

Describe silent-failure risks, privacy/accessibility implications, generated-stage effects, and
whether the change requires a new release.

## Verification

List the exact commands run and their outcomes. Include skipped checks and warnings.

## Checklist

- [ ] Any scientific-method change is implemented and released in `wald-inference-core`; this
      repository adds or copies no Wald, likelihood, support-ratio, or support-interval formula.
- [ ] The response remains normalized-support-only and adds no compatibility/p-value primary
      output, repeated-study design metric, selection rule, Type S/M, information multiplier,
      precision target, prior, posterior, Bayes factor, clinical threshold, or decision support.
- [ ] Pairwise output remains `log L(A)/L(B)`, finite log-domain results remain authoritative when
      ordinary ratios overflow or underflow, and S−2 remains distinct from a 2:1 interval.
- [ ] Public copy consistently describes a normalized, approximate Wald relative likelihood and
      does not imply an exact fitted-model likelihood, clinical readiness, or regulatory status.
- [ ] Examples and fixtures are synthetic and contain no credentials, sensitive data, or protected
      health information.
- [ ] No backend, telemetry, persistence, cookies, hidden state, upload, or input-bearing URL was
      added.
- [ ] Generated Python under `web/assets/py/` was produced by `make stage-web`, not edited by hand.
- [ ] Every third-party GitHub Action remains pinned to a full commit SHA with a version comment.
- [ ] `uv sync --locked` and `make verify` pass.
- [ ] README, scientific scope, validation, privacy, decisions, maintenance, citation, and
      changelog were reviewed for synchronization.
