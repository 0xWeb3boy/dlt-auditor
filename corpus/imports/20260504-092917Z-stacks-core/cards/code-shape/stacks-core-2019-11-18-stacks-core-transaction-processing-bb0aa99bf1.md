# Code-Shape Card

## Metadata

- ID: `stacks-core-2019-11-18-stacks-core-transaction-processing-bb0aa99bf1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-validation-hardening`

## Code Shape Summary

- The patch changes transaction postcondition asset lookups from origin_account.principal to account.principal for STX, fungible-token, and non-fungible-token checks, and adds a guard that rejects sponsored token-transfer transactions before token-transfer processing. This is plausibly security-relevant validation logic, but the supplied evidence does not prove exploitability, consensus impact, loss of funds, or that the previous behavior was reachable in an unsafe way.

## Search Motifs

- Motif 1: manual construction bypasses constructor checks
- Motif 2: noncanonical preimage or type accepted at signing or validation boundary
- Motif 3: VM or transaction error interpreted inconsistently

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Centralize canonical construction or validation and reject ambiguous representations before using them in sensitive logic.

## False Match Warnings

- The constructor may be used only with trusted constants.
- The changed path may improve diagnostics without changing acceptance behavior.
