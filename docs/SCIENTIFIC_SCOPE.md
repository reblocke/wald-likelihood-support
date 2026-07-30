# Scientific Scope

## Question

Under a one-parameter Wald reconstruction of a reported estimate and two-sided 95% confidence
interval, how much relative support do the data provide for selected candidate effect values?

## Intended users and setting

The app is an experimental educational and research-facing tool for researchers, educators,
reviewers, and scientifically trained readers working with aggregate published estimates. It is
designed to make candidate-effect comparisons explicit, inspectable, and exportable.

It is not intended for patient-specific use, clinical decision support, operational trial
monitoring, or regulatory submission.

## Inputs

All numerical inputs must be finite JSON numbers.

- **Effect measure:** a non-empty key from the effect registry exposed by the root-public
  `wald_inference` API. Additive effects use an identity working scale. Ratio effects require
  strictly positive natural-scale values and use a log working scale.
- **Lower and upper limits:** required, ordered limits of a two-sided 95% confidence interval in
  display-scale effect units.
- **Point estimate:** optional, in the same display units. It validates consistency with the
  confidence interval but does not replace the confidence-interval-implied reconstruction.
- **Null:** optional, in display units. When absent, the effect registry’s default null is used.
- **Reference thresholds:** an optional ordered JSON array of zero or more display-scale candidate
  effects. They are comparison markers, not validated clinical cutoffs.
- **Candidate A and candidate B:** optional finite display-scale effects that must be supplied
  together. Their order defines the A:B comparison.
- **Support criterion:** one of S−2, 2:1, 4:1, 8:1, or custom. A custom MLE-to-bound ratio is
  required only for the custom criterion and must be finite and greater than 1.
- **Plausible display range:** optional paired, strictly ordered display-scale limits. Both or
  neither must be supplied.
- **Grid points:** an odd integer from 101 through 1601; the default is 801.
- **Ratio-axis spacing:** a browser presentation choice between logarithmic and linear spacing.
  It does not change the Python reconstruction.

These fields are aggregate numerical summaries, but a user could still treat them as sensitive.
The application does not require names, dates, identifiers, free text, or patient-level records.

## Outputs

The strict top-level response contains only:

- `meta`: schema, app/core versions, effect metadata, reconstruction source, display state, and
  the selected support criterion;
- `reconstruction`: display- and working-scale estimate, interval, null, reconstructed standard
  error details, and asymmetry metadata;
- `grid`: the aligned five-field normalized relative-likelihood grid;
- `support_interval`: the selected criterion, cutoff metadata, finite endpoints, and clipping
  status;
- `reference_support`: one row for the null and one for each user threshold, including
  log-domain and ordinary support comparisons when representable;
- `pairwise_comparisons`: zero rows or one explicit candidate A versus candidate B row; and
- `warnings`: structured reconstruction, display, clipping, and overflow messages.

The five grid and CSV fields, in order, are:

1. `effect_display`;
2. `effect_working`;
3. `standardized_distance`;
4. `relative_likelihood`; and
5. `log_relative_likelihood`.

The primary output is the normalized Wald relative-likelihood curve together with accessible
textual summaries of the selected support interval, null and threshold comparisons, and optional
A:B comparison. A plot is supplementary and is never the only carrier of a result.

## Interpretation and ordering

The result is a normalized, approximate Wald relative-likelihood reconstruction from aggregate
confidence-interval information. It is not the exact fitted-model profile likelihood from the
original analysis.

Pairwise output is labeled in the explicit order `log L(A)/L(B)`. Positive values favor A,
negative values favor B, and zero indicates equal reconstructed support. The signed finite log
result remains authoritative when the corresponding ordinary ratio cannot be represented.

S−2 uses an MLE-to-bound ratio of `exp(2)`, approximately 7.4:1. It must not be described as a 2:1
interval. The separately selectable 2:1 criterion is narrower and has its own literal
MLE-to-bound ratio.

## Assumptions and numerical authority

- The reported limits are a two-sided 95% confidence interval that can reasonably be summarized
  by a one-parameter Wald approximation on the registered working scale.
- The confidence-interval midpoint and width determine the reconstruction; a supplied estimate
  is validation input.
- Relative likelihood is normalized to its peak at the reconstructed estimate.
- Display ranges and ratio-axis spacing affect presentation only.
- Finite log-domain comparisons take precedence over overflowed or underflowed ordinary ratios.
- Root-public functions from the published `wald_inference` prerelease are the sole numerical
  authority. This app owns request validation, orchestration, response assembly, warnings, display
  choices, and exports; it does not copy numerical formulas.

The dependency target is the `wald-inference` v0.2.0 prerelease wheel recorded in
`docs/RUNTIME_DEPENDENCIES.md`.

## Limitations and non-goals

The app does not:

- recover the original study data, fitted model, variance estimator, likelihood, or design;
- establish that a reported confidence interval is actually Wald-based;
- support arbitrary confidence levels;
- produce compatibility curves or p-values as primary outputs;
- calculate critical effects, power, repeated-study design behavior, selection, Type S, Type M,
  information multipliers, or precision targets;
- use priors or return posterior probabilities, Bayes factors, or Bayesian inferences;
- validate reference thresholds or identify clinically important effects;
- diagnose, recommend treatment, select a trial action, or provide medical-device functionality;
  or
- establish scientific or clinical validity merely by passing engineering tests.

## Clinical and regulatory boundary

This repository is an experimental scientific communication tool, not a validated clinical tool
or regulated medical device. It must not be used as the sole basis for patient care, treatment,
diagnosis, trial conduct, or policy. Do not enter protected health information or identifying
patient data.
