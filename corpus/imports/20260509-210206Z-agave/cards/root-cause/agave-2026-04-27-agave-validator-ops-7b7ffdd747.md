# Root-Cause Card

## Metadata

- ID: `agave-2026-04-27-agave-validator-ops-7b7ffdd747`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cli-validator-info-signer-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signer-bit-propagation`

## Violated Invariant

- Invariant: Tools that select or trust identity metadata must carry signer/authenticity bits from parsing into the downstream decision, and malformed records must be rejected without panics.

## Trust Boundary

- Boundary: `on-chain-metadata-or-rpc-response->operator-cli`

## Attack Surface

- Entrypoint type: `cli-metadata-scan`
- Sensitive sink: validator-info display and publish metadata selection
- Attacker capability: Create unsigned or malformed validator-info-like records that appear during CLI scans.
- Key precondition: The CLI treats parsed metadata as existing validator-owned metadata without checking the signer bit.

## Impact Pattern

- Primary impact: `metadata-authenticity`
- Secondary impact: `operator-misleading`
- Severity guidance: `low` because The issue affects CLI trust and robustness around validator metadata, with no proven protocol-state, fund, consensus, or takeover impact.

## Short Reusable Lesson

- A CLI parser extracts validator metadata but drops whether the validator pubkey actually signed, then selection/display logic treats unsigned or malformed records like trusted entries.
- Structural fix: Return signer/authenticity metadata from parsing, require it in publish/get selection logic, and convert malformed account parsing to graceful rejection.
