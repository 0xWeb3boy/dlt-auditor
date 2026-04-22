# Root-Cause Card

## Metadata

- ID: `base-2026-04-20-base-transaction-processing-88b36d5a2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-guard`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `runtime-guard-consistency`

## Violated Invariant

- Invariant: When Base V1/Azul rules are active for a timestamp, every EVM environment construction path should apply the same fork-specific transaction gas-limit cap.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `policy-gated game creation or environment construction`

## Impact Pattern

- Primary impact: `policy-bypass`
- Secondary impact: `none`

## Short Reusable Lesson

- When Base V1/Azul rules are active for a timestamp, every EVM environment construction path should apply the same fork-specific transaction gas-limit cap. Fork-specific gas-limit policy for Base V1/Azul was omitted from the duplicated inline `CfgEnv` construction paths, so some execution environments could be built without the fork-specific cap even when the timestamp-selected rules were active. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
