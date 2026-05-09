# Root-Cause Card

## Metadata

- ID: `solana-2021-12-07-solana-consensus-89d2f34a03`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-invariant-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rent-exemption-invariant`

## Violated Invariant

- Protocol input must satisfy rent exemption invariant before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The withdraw path did not have Rent context on the activated instruction path, so a partial withdrawal could proceed without the supplied evidence showing enforcement that the remaining initialized vote account stayed rent-exempt.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch appears to harden the Solana vote-program withdraw path by adding Rent context under the `reject_non_rent_exempt_vote_withdraws` feature and changing withdrawal handling around the remaining vote-account balance. The supplied evidence supports a rent-exemption invariant fix, but does not establish an exploit, theft, signer bypass, memory issue, or demonstrated consensus failure.
