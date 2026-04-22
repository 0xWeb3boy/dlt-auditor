# Root-Cause Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-8f939340a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-confirmation-depth`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `freshness`

## Violated Invariant

- Invariant: If verifier derivation is meant to avoid reorg-prone L1 tip data, it should be able to consume an L1 head that is delayed by a configurable confirmation depth rather than always using the freshest observed head. The provided evidence shows that behavior being added, but does not establish that violating it previously caused a concrete vulnerability.

## Trust Boundary

- Boundary: `external chain or RPC data->node service`

## Attack Surface

- Entrypoint type: `external-state-ingestion`
- Sensitive sink: `selection of the external head consumed by derivation or verifier logic`

## Impact Pattern

- Primary impact: `reorg-exposure`
- Secondary impact: `consensus-safety`

## Short Reusable Lesson

- If verifier derivation is meant to avoid reorg-prone L1 tip data, it should be able to consume an L1 head that is delayed by a configurable confirmation depth rather than always using the freshest observed head. The provided evidence shows that behavior being added, but does not establish that violating it previously caused a concrete vulnerability. The pre-change design did not have a separate verifier-specific confirmation-delay path in the shown head-forwarding logic; derivation received the newest observed L1 head directly. The patch introduces an optional delayed-fetch path, but the provided evidence does not prove that the earlier behavior was a vulnerability rather than a missing hardening control. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
