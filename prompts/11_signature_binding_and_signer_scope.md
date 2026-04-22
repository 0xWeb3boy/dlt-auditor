# Prompt Family: Signature Binding And Signer Scope

## Use This For

- Missing signer authorization after a signature verifies.
- Missing domain separation or chain or app binding.
- Signed wrapper misuse where verified bytes are not carried through.
- Query or proof verification gaps.
- Registration or descriptor signatures that do not require the right principals.

## Prompt

```text
Hunt for signature, proof, and authenticated-message binding bugs in a blockchain or DLT codebase.

Do not stop at "the signature verifies". Check what the signature or proof is actually bound to.

Focus on:
- signed envelopes and multisig envelopes
- committee, validator, bridge, relayer, or multisig signatures
- node, validator, runtime, bridge, checkpoint, batch, block, or registration descriptors
- query verification and proof-bearing responses
- domain-specific or chain-specific signature contexts
- verified wrappers that may be unpacked and reconstructed incorrectly

Search patterns:
- Verify* calls followed by separate extraction of method, body, chain ID, domain ID, runtime ID, app ID, bridge ID, or signer role
- signature contexts that omit chain ID, app ID, runtime ID, domain ID, nonce, epoch, height, fork, or purpose
- proof verification paths that are weaker for historical queries, latest-state queries, or bridge messages than for normal execution
- verifier APIs returning `Result<bool, _>`, status enums, per-item outcomes, or indexed roots where callers may treat "no error" as success
- proof or challenge flows where the protocol names one challenged root, index, query height, or hash but the code validates a batch, all roots, or the first invalid item
- enum-based verification branches where one proof type recomputes and compares expected output but another only parses or looks up helper data
- wrappers that deserialize twice or carry typed values instead of raw authenticated bytes
- code that checks signer public key equality but not signer membership in the active authorized role set
- multisig validation that accepts "a signer" instead of "the required signers"

Questions to answer:
1. What exact bytes are authenticated?
2. What scope should be authenticated but may not be: chain, app, bridge, shard, committee role, method, version, nonce, or query height?
3. Is cryptographic validity separated from signer authorization?
4. Could a valid signature or proof from one chain, runtime, committee, bridge domain, or context be replayed in another?
5. Are historical queries and latest-state queries verified by equally strong paths?
6. Does the caller require explicit semantic success from the verifier, or only absence of an API error?
7. Is the code validating the exact challenged or indexed object that governs the decision?

Severity guidance:
- High for signer-authorization gaps, registration-signature gaps, bridge or validator signature binding failures, or domain-separation failures in consensus-sensitive paths.
- Medium for query-verification gaps and signed-wrapper inconsistencies unless they directly enable forged state acceptance.
```
