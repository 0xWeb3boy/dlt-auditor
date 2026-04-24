# Code-Shape Card

## Metadata

- ID: `geth-arb-2021-02-23-go-ethereum-transaction-processing-142fbcfd6f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-replay-protection-enforcement`

## Code Shape Summary

- The RPC submission path forwarded non-EIP-155 transactions unless configured otherwise, allowing replayable transactions to enter normal propagation.

## Search Motifs

- RPC transaction submission accepts legacy signatures by default
- replay protection enforced only in wallet path not raw submit
- operator override exists but default is permissive
- signature or signed feed omits chain/domain/type/sequence binding
- authenticated object is accepted before freshness or publisher identity is checked
- same signing primitive serves multiple semantic object types without prefixing

## Typical Asymmetry

- The vulnerable asymmetry is semantic mismatch: an object valid in one signing, feed, chain, or sequence context could be accepted near transaction pool admission and peer propagation without the full context binding.

## Patch Pattern

- Add a fail-closed replay-protection check before SendTx and require an explicit override for legacy acceptance.

## False Match Warnings

- the signature covers chain ID, message type, domain, nonce, and freshness at the sink
- the object is never accepted from an untrusted boundary
- a later verifier rejects mismatched signer, domain, or sequence before side effects
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
