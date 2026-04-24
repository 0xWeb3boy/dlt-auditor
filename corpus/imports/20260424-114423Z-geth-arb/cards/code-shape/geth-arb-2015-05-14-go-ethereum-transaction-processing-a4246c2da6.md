# Code-Shape Card

## Metadata

- ID: `geth-arb-2015-05-14-go-ethereum-transaction-processing-a4246c2da6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unknown-parent-sync-stall`

## Code Shape Summary

- The downloader returned the same result for no-ready-work and unknown-parent cases, making a parent gap harder to treat as invalid peer input.

## Search Motifs

- sync queue returns nil for both empty queue and invalid parent
- parent lookup failure is treated as benign no progress
- peer block batch can leave downloader waiting without peer penalty
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that parent-availability-progress-check was enforced only partially, late, or in one branch while another path could still reach download scheduling and canonical chain extension.

## Patch Pattern

- Return an explicit unknown-parent signal and handle it as a peer or queue validation failure instead of ordinary no-work state.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
