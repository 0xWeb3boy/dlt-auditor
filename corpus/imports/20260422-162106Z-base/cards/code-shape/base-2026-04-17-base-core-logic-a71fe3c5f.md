# Code-Shape Card

## Metadata

- ID: `base-2026-04-17-base-core-logic-a71fe3c5f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `policy-enforcement-bypass`

## Code Shape Summary

- Short description of what the buggy code looked like: The confirmation-depth policy was applied at a signaling/scheduling boundary instead of the actual L1 block access boundary. Because the provider API remained uncapped, direct reads could bypass the intended `verifier_l1_confs` limit.

## Search Motifs

- Motif 1: runtime or on-chain policy is read but not enforced before a privileged action
- Motif 2: one execution path applies the environment guard while another path skips it
- Motif 3: local configuration is treated as authoritative even when live chain policy can differ

## Typical Asymmetry

- What was checked in one path but missing in another: One path read or knew the live runtime policy, but the privileged action could still proceed using local assumptions or an alternate path that did not enforce that policy.

## Patch Pattern

- What the fix changed structurally: Move policy enforcement from an upstream signal to the lowest data-access boundary, using current shared state to compute an allowed range and rejecting out-of-policy reads with a temporary error.

## False Match Warnings

- What looks similar but is often not a bug: Supported: a confirmation-depth policy in a consensus-sensitive path was previously ineffective and is now enforced more directly.
