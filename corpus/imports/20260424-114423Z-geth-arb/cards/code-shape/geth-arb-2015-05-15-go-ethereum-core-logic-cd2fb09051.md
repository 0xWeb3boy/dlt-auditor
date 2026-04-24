# Code-Shape Card

## Metadata

- ID: `geth-arb-2015-05-15-go-ethereum-core-logic-cd2fb09051`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `duplicate-hash-replay`

## Code Shape Summary

- The downloader did not treat a non-final batch of only duplicate hashes as a protocol failure, allowing replayed responses to consume sync work without progress.

## Search Motifs

- hash queue insertion ignores count of actually new entries
- duplicate response is accepted as progress
- non-final peer batch can replay already queued identifiers
- signature or signed feed omits chain/domain/type/sequence binding
- authenticated object is accepted before freshness or publisher identity is checked
- same signing primitive serves multiple semantic object types without prefixing

## Typical Asymmetry

- The vulnerable asymmetry is semantic mismatch: an object valid in one signing, feed, chain, or sequence context could be accepted near sync queue insertion and peer scoring without the full context binding.

## Patch Pattern

- Count newly inserted hashes and reject non-final responses that add no new queue entries.

## False Match Warnings

- the signature covers chain ID, message type, domain, nonce, and freshness at the sink
- the object is never accepted from an untrusted boundary
- a later verifier rejects mismatched signer, domain, or sequence before side effects
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
