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
- login, registration, session, or challenge-response flows where a nonce, challenge, token, or request identifier appears in both signed content and transport metadata
- compatibility or legacy verification branches that reconstruct or hash a message shape different from what older clients actually signed
- challenge or transcript construction that may omit a hash, commitment, version, mode, or selector that later governs the sensitive decision

Search patterns:
- Verify* calls followed by separate extraction of method, body, chain ID, domain ID, runtime ID, app ID, bridge ID, or signer role
- code that verifies a signature over one payload but authorizes or dispatches based on parallel fields from headers, wrapper metadata, or side arguments
- legacy or backward-compatibility paths that do not call the same canonical serializer or hashing routine as the main path
- signature contexts that omit chain ID, app ID, runtime ID, domain ID, nonce, epoch, height, fork, or purpose
- proof or transcript builders that bind part of an artifact while downstream verification or execution depends on additional detached identifiers or commitments
- proof verification paths that are weaker for historical queries, latest-state queries, or bridge messages than for normal execution
- verifier APIs returning `Result<bool, _>`, status enums, per-item outcomes, or indexed roots where callers may treat "no error" as success
- signed network payloads should authenticate the exact raw payload bytes and domain context before deeper decoding, scheduling, or block construction. Check minimum length and signature/payload split before slicing
- signing APIs should accept structured domain fields or one canonical message object, not detached byte buffers plus side-channel chain IDs, payload hashes, signer roles, or version flags that can disagree
- proof or challenge flows where the protocol names one challenged root, index, query height, or hash but the code validates a batch, all roots, or the first invalid item
- enum-based verification branches where one proof type recomputes and compares expected output but another only parses or looks up helper data
- wrappers that deserialize twice or carry typed values instead of raw authenticated bytes
- code that checks signer public key equality but not signer membership in the active authorized role set
- multisig validation that accepts "a signer" instead of "the required signers"
- startup or constructor paths that can build a consumer without successfully constructing the verifier, signer-scope, or chain-context object that later code assumes exists
- live paths wired to placeholder, trusting, noop, or development verifiers or signers while tests or helper code use stronger verification
- protocol pipelines where emission and ingestion use different commitment, sequence, or signing rules, such as a sender producing one representation while the receiver verifies another or verifies nothing at all

Questions to answer:
1. What exact bytes are authenticated?
2. What scope should be authenticated but may not be: chain, app, bridge, shard, committee role, method, version, nonce, or query height?
3. Is cryptographic validity separated from signer authorization?
4. Could a valid signature or proof from one chain, runtime, committee, bridge domain, or context be replayed in another?
5. Are historical queries and latest-state queries verified by equally strong paths?
6. Does the caller require explicit semantic success from the verifier, or only absence of an API error?
7. Is the code validating the exact challenged or indexed object that governs the decision?
8. If verifier creation depends on chain context, contract state, signer registries, or feature mode, does startup fail closed when that context is unavailable?
9. Do emitters and receivers bind the same bytes, metadata, counters, and mode flags, or is one side still using a weaker placeholder representation?

Severity guidance:
- High for signer-authorization gaps, registration-signature gaps, bridge or validator signature binding failures, or domain-separation failures in consensus-sensitive paths.
- Medium for query-verification gaps and signed-wrapper inconsistencies unless they directly enable forged state acceptance.
```
