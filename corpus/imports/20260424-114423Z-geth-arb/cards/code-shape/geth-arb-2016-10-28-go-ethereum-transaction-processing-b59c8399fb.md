# Code-Shape Card

## Metadata

- ID: `geth-arb-2016-10-28-go-ethereum-transaction-processing-b59c8399fb`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signing-api-domain-separation`

## Code Shape Summary

- The generic message-signing path needed an Ethereum-specific prefix and hash so arbitrary messages could not be confused with transactions or structured protocol payloads.

## Search Motifs

- raw bytes are signed with the same primitive as transactions
- signing API lacks prefix/domain/type separation
- wallet signs attacker-controlled message without semantic binding
- signature or signed feed omits chain/domain/type/sequence binding
- authenticated object is accepted before freshness or publisher identity is checked
- same signing primitive serves multiple semantic object types without prefixing

## Typical Asymmetry

- The vulnerable asymmetry is semantic mismatch: an object valid in one signing, feed, chain, or sequence context could be accepted near signature generation with reusable private key without the full context binding.

## Patch Pattern

- Prefix and hash arbitrary messages under a dedicated domain before signing, and keep transaction signing on a distinct typed path.

## False Match Warnings

- the signature covers chain ID, message type, domain, nonce, and freshness at the sink
- the object is never accepted from an untrusted boundary
- a later verifier rejects mismatched signer, domain, or sequence before side effects
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
