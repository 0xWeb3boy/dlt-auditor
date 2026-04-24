# Code-Shape Card

## Metadata

- ID: `geth-arb-2025-04-08-go-ethereum-transaction-processing-2e739fce58`
- Bug family: `resource_accounting_and_limits`
- Bug class: `txpool-resource-exhaustion-hardening`

## Code Shape Summary

- Blobpool and delegated-authority handling needed additional constraints so EIP-7702 or pending-delegation senders could not occupy incompatible pool resources.

## Search Motifs

- new transaction type bypasses existing txpool account limits
- delegated authority conflicts with blobpool admission
- pool validates intrinsic fields but not cross-pool sender state
- attacker-controlled count or loop bound reaches allocation or scheduling
- metadata validation happens after network or storage work is queued
- duplicate, stale, or known items consume work instead of being skipped

## Typical Asymmetry

- The vulnerable asymmetry is cost mismatch: cheap attacker-controlled input could trigger more expensive work at mempool resource reservation and peer propagation before bounds or progress checks ran.

## Patch Pattern

- Reject delegated/pending-delegation sender conflicts and enforce authority/resource constraints before pool insertion.

## False Match Warnings

- a hard request cap is enforced before allocation or network work
- peer scoring or authentication makes repeated abuse impractical
- the path is operator-only and unreachable from untrusted clients
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
