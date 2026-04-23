# Code-Shape Card

## Metadata

- ID: `go-ethereum-2016-10-28-go-ethereum-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-separation`

## Code Shape Summary

- The supported root cause is that account-signing RPC behavior was tied too closely to raw ECDSA hash-signing semantics. Without explicit message-prefix domain separation before signing, caller-supplied signing input could be used in a less clearly scoped signature context. The evidence does not establish transaction replay, nonce handling failure, or a concrete private-key leakage exploit.

## Search Motifs

- Motif 1: rpc method missing exact checks for signature domain separation
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Apply signature domain separation at the RPC/account-signing boundary by prefixing arbitrary messages, hashing the prefixed payload, and then invoking the ECDSA signing primitive; keep raw hash signing as an internal or trusted low-level operation with explicit warnings

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Apply signature domain separation at the RPC/account-signing boundary by prefixing arbitrary messages, hashing the prefixed payload, and then invoking the ECDSA signing primitive; keep raw hash signing as an internal or trusted low-level operation with explicit warnings.

## False Match Warnings

- Classify as RPC/account-signing hardening, not transaction-processing.
- Do not claim a confirmed transaction replay vulnerability.
