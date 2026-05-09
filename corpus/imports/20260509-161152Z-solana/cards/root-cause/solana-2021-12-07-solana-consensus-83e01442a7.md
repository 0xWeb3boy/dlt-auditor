# Root-Cause Card

## Metadata

- ID: `solana-2021-12-07-solana-consensus-83e01442a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-invariant-hardening`
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

The grounded issue is that the shown pre-patch withdraw path had no Rent context and the provided excerpt shows no check for whether a partial withdrawal left the vote account rent exempt. The stronger claim that this was an exploitable rent-exemption bypass is not established by the provided evidence.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch changes Solana vote-program withdrawal handling to compute the post-withdraw balance and to pass optional Rent sysvar context into `vote_state::withdraw` when the `reject_non_rent_exempt_vote_withdraws` feature is active. This is plausibly security-relevant state-validity hardening, but the supplied evidence does not show the actual rent-exemption rejection conditional or establish an exploitable vulnerability. Treat as unclear rather than a c...
