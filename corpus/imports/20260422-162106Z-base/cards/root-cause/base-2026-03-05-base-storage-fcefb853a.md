# Root-Cause Card

## Metadata

- ID: `base-2026-03-05-base-storage-fcefb853a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: If this validator is used to decide whether a dispute game should be challenged, it must validate every expected checkpoint against recomputed L2-derived data, reject structurally invalid parameters such as mismatched checkpoint counts or zero intervals, and avoid trusting RPC header metadata without consistency checks.

## Trust Boundary

- Boundary: `chain state, checkpoint, or persistent storage input->proposer or validator logic`

## Attack Surface

- Entrypoint type: `checkpoint-or-state-validation`
- Sensitive sink: `reuse of cached checkpoint or execution data that drives proposer or validator actions`

## Impact Pattern

- Primary impact: `validation-bypass`
- Secondary impact: `none`

## Short Reusable Lesson

- If this validator is used to decide whether a dispute game should be challenged, it must validate every expected checkpoint against recomputed L2-derived data, reject structurally invalid parameters such as mismatched checkpoint counts or zero intervals, and avoid trusting RPC header metadata without consistency checks. According to the commit body, the initial validator implementation did not enforce all structural and arithmetic preconditions before iterating checkpoints and did not fully cross-check externally supplied header data. That created a risk that malformed inputs could alter or truncate validation instead of causing an immediate failure. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
