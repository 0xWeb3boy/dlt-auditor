# Code-Shape Card

## Metadata

- ID: `geth-arb-2020-12-08-go-ethereum-transaction-processing-ed0670cb17`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-protection-hardening`

## Code Shape Summary

- Contract binding helpers exposed signing paths that did not force chain-ID-aware transaction signing, so applications could accidentally produce replayable transactions.

## Search Motifs

- transaction signer helper omits chain ID
- contract binding defaults to legacy signing
- API has protected and unprotected signing paths with unsafe default
- signature or signed feed omits chain/domain/type/sequence binding
- authenticated object is accepted before freshness or publisher identity is checked
- same signing primitive serves multiple semantic object types without prefixing

## Typical Asymmetry

- The vulnerable asymmetry is semantic mismatch: an object valid in one signing, feed, chain, or sequence context could be accepted near signed transaction accepted for broadcast without the full context binding.

## Patch Pattern

- Expose and route through chain-ID-aware transactor helpers that construct EIP-155 protected signatures.

## False Match Warnings

- the signature covers chain ID, message type, domain, nonce, and freshness at the sink
- the object is never accepted from an untrusted boundary
- a later verifier rejects mismatched signer, domain, or sequence before side effects
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
