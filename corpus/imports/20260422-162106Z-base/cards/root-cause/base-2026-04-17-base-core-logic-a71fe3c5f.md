# Root-Cause Card

## Metadata

- ID: `base-2026-04-17-base-core-logic-a71fe3c5f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `policy-enforcement-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `policy-gating`

## Violated Invariant

- Invariant: When `verifier_l1_confs` is configured, the verifier/client derivation path should not read L1 blocks newer than the configured confirmation-depth cutoff derived from the observed L1 head.

## Trust Boundary

- Boundary: `external state input->privileged control path`

## Attack Surface

- Entrypoint type: `external-state-ingestion`
- Sensitive sink: `policy-gated game creation or environment construction`

## Impact Pattern

- Primary impact: `state-consistency`
- Secondary impact: `client-view-divergence`

## Short Reusable Lesson

- When `verifier_l1_confs` is configured, the verifier/client derivation path should not read L1 blocks newer than the configured confirmation-depth cutoff derived from the observed L1 head. The confirmation-depth policy was applied at a signaling/scheduling boundary instead of the actual L1 block access boundary. Because the provider API remained uncapped, direct reads could bypass the intended `verifier_l1_confs` limit. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
