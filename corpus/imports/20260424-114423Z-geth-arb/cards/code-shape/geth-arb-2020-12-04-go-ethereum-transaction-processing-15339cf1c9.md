# Code-Shape Card

## Metadata

- ID: `geth-arb-2020-12-04-go-ethereum-transaction-processing-15339cf1c9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `advisory-feed-authentication`

## Code Shape Summary

- A vulnerability-check mechanism needed signed feed validation so remote advisory content could not be trusted solely by transport or URL.

## Search Motifs

- remote advisory JSON consumed without signature check
- version warning trusts feed transport only
- security metadata lacks publisher authentication
- signature or signed feed omits chain/domain/type/sequence binding
- authenticated object is accepted before freshness or publisher identity is checked
- same signing primitive serves multiple semantic object types without prefixing

## Typical Asymmetry

- The vulnerable asymmetry is semantic mismatch: an object valid in one signing, feed, chain, or sequence context could be accepted near security warning, update recommendation, or operator trust decision without the full context binding.

## Patch Pattern

- Verify advisory feed signatures and trusted keys before accepting feed contents for version or vulnerability checks.

## False Match Warnings

- the signature covers chain ID, message type, domain, nonce, and freshness at the sink
- the object is never accepted from an untrusted boundary
- a later verifier rejects mismatched signer, domain, or sequence before side effects
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
