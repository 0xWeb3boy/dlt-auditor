# Code-Shape Card

## Metadata

- ID: `nitro-2024-12-20-nitro-transaction-processing-a719c5c92`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-machine-hardening`

## Code Shape Summary

- Short description of what the buggy code looked like: This patch tightens express-lane transaction sequencing by binding processing to the current round and adding an explicit notifier before advancing to the next queued transaction. The code is security-relevant, and one inline comment mentions a security concern, but the provided evidence does not establish a concrete vulnerability or exploit path.

## Search Motifs

- Motif 1: queue workers keep processing after the round or epoch used for authorization has changed
- Motif 2: next-item advancement happens before an explicit result or notifier is delivered
- Motif 3: security-relevant ordering fixes add per-item channels or acknowledgements to queue entries

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed formatting or shallow admission checks at ingress, but the authoritative policy, payment, version, or sequencing invariant was enforced only later or from weaker context.

## Patch Pattern

- What the fix changed structurally: Constrain a sequencing loop to the valid protocol scope and require explicit downstream acknowledgement before advancing state.

## False Match Warnings

- What looks similar but is often not a bug: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
