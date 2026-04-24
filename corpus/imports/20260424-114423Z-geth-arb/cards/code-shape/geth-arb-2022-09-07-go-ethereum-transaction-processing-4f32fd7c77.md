# Code-Shape Card

## Metadata

- ID: `geth-arb-2022-09-07-go-ethereum-transaction-processing-4f32fd7c77`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `broadcast-feed-signature-and-ordering-hardening`

## Code Shape Summary

- Feed ingestion added contiguous sequence-number checks and tightened message signing/ordering so gaps or misordered signed messages could not be accepted silently.

## Search Motifs

- signed feed message accepted without contiguous sequence check
- broadcast ordering depends on sender honesty
- signature covers payload but not ordering/domain metadata
- signature or signed feed omits chain/domain/type/sequence binding
- authenticated object is accepted before freshness or publisher identity is checked
- same signing primitive serves multiple semantic object types without prefixing

## Typical Asymmetry

- The vulnerable asymmetry is semantic mismatch: an object valid in one signing, feed, chain, or sequence context could be accepted near transaction stream insertion and sequencer-visible ordering without the full context binding.

## Patch Pattern

- Verify sequence continuity and signature/domain metadata before adding broadcast messages to the stream.

## False Match Warnings

- the signature covers chain ID, message type, domain, nonce, and freshness at the sink
- the object is never accepted from an untrusted boundary
- a later verifier rejects mismatched signer, domain, or sequence before side effects
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
