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
- challenge-response handshakes where liveness or replay resistance depends on freshness from both sides; a signature over only the verifier's challenge may prove key control but still fail to bind response-side freshness or transcript state
- compatibility or legacy verification branches that reconstruct or hash a message shape different from what older clients actually signed
- challenge or transcript construction that may omit a hash, commitment, version, mode, or selector that later governs the sensitive decision

Search patterns:
- Cryptographic transcript builders that convert variable-length bytes into field elements before hashing. Check whether length, purpose, protocol version, and domain separator are absorbed before the field sequence.
- Native and circuit or gadget verifiers that are intended to verify the same signature, proof, encryption, or commitment. Compare transcript fields, domain labels, length delimiters, and ordering across both implementations.
- Sponge or hash derivations that absorb bare key coordinates, ECDH outputs, commitments, or message fields without a scheme-specific label.
- Verify* calls followed by separate extraction of method, body, chain ID, domain ID, runtime ID, app ID, bridge ID, or signer role
- code that verifies a signature over one payload but authorizes or dispatches based on parallel fields from headers, wrapper metadata, or side arguments
- legacy or backward-compatibility paths that do not call the same canonical serializer or hashing routine as the main path
- signature contexts that omit chain ID, app ID, runtime ID, domain ID, nonce, epoch, height, fork, or purpose
- emitter and verifier code that construct signed bytes separately. Compare nonce order, transcript fields, peer identity, role, version, domain, and mode flags; both sides should sign and verify the exact same canonical byte sequence
- proof or transcript builders that bind part of an artifact while downstream verification or execution depends on additional detached identifiers or commitments
- proof verification paths that are weaker for historical queries, latest-state queries, or bridge messages than for normal execution
- verifier APIs returning `Result<bool, _>`, status enums, per-item outcomes, or indexed roots where callers may treat "no error" as success
- request-controlled proof or signature bytes parsed with low-level helpers, compatibility decoders, fallback signatures, or unchecked recovery. Prefer domain-specific canonical signature types, exact length and format rejection, and explicit invalid-signature errors before signer authorization or proof acceptance continues.
- signed network payloads should authenticate the exact raw payload bytes and domain context before deeper decoding, scheduling, or block construction. Check minimum length and signature/payload split before slicing
- Signature validation loops where attacker-supplied signatures are tried against many candidate keys before a cheap key-id, hint, signer index, or domain prefilter. Expensive cryptographic verification should run only after cheap candidate binding, and unused authentication material should be rejected rather than silently ignored.
- signing APIs should accept structured domain fields or one canonical message object, not detached byte buffers plus side-channel chain IDs, payload hashes, signer roles, or version flags that can disagree
- proof or challenge flows where the protocol names one challenged root, index, query height, or hash but the code validates a batch, all roots, or the first invalid item
- enum-based verification branches where one proof type recomputes and compares expected output but another only parses or looks up helper data
- wrappers that deserialize twice or carry typed values instead of raw authenticated bytes
- key-rotation or manifest formats where a long-term master key authorizes an ephemeral validation, committee, or signing key. Verify both signatures, revocation status, sequence or epoch, and namespace-specific cache lookups before accepting signed consensus artifacts
- signed objects whose payload schema can be confused with a different transaction, manifest, validation, proposal, state object, or descriptor type. Include object type and protocol domain in the signed bytes
- signed consensus objects with internal, exported, cached, or serialized representations of the same identity. Compare the fields used to clear or write the signature, compute the ID, select the parent, serialize bytes, sign, verify, and store the object. A signature over one representation must not authorize routing or parentage from another.
- code that checks signer public key equality but not signer membership in the active authorized role set
- multisig validation that accepts "a signer" instead of "the required signers"
- aggregate, batch, certificate, or checkpoint signatures where an empty item list, duplicate signer, stale committee, or missing inner-user signature can still produce a syntactically valid wrapper. Verify that the wrapper proves every required inner authorization, not just committee approval of a container
- epoch or committee-scoped signatures where the data is signed by the previous, current, or next committee. Check that the verifier names the exact epoch relation required by the protocol and rejects off-by-one or default-epoch authentication
- signed or certified objects that can be mutated, reconstructed, or compared after verification. Ensure equality, ordering, hashing, and storage keys use the authenticated identity and not an incidental representation
- signed envelopes whose inner payload verifies but whose wrapper metadata, ID, namespace, height, route, storage key, or replay coordinate is trusted later. The signed digest should include every field that affects identity, replay domain, routing, or downstream authorization.
- Sealed, signed, certified, or delegated messages whose contents are destructured, routed, cached, or applied before verification succeeds. The verified object, not the unpacked side fields, should drive every downstream status update or authority change.
- Delegation, preconfirmation, vote, or ephemeral-key messages where nonce, epoch, expiration, height, or replay coordinate is carried beside the signed payload instead of inside the signed domain.
- signed, certified, or authenticated network object types that expose production constructors or builders which can create unauthenticated/default-signature instances. Test helpers for unsigned construction should be private or test-only, and production insertion/broadcast APIs should accept only authenticated wrappers or force signing at construction.
- startup or constructor paths that can build a consumer without successfully constructing the verifier, signer-scope, or chain-context object that later code assumes exists
- live paths wired to placeholder, trusting, noop, or development verifiers or signers while tests or helper code use stronger verification
- read or streaming APIs that return proof-bearing, signature-bearing, committee-certified, or verifier-dependent data. Verify that the same verifier used by ingestion, write, or producer paths also gates response serialization, not only submission.
- protocol pipelines where emission and ingestion use different commitment, sequence, or signing rules, such as a sender producing one representation while the receiver verifies another or verifies nothing at all
- account association, address binding, or identity-linking transactions where signer recovery uses a placeholder hash, empty message, legacy compatibility signer, or side-channel message field instead of the exact serialized message the user signed
- replay-domain checks that differ between legacy and typed transaction formats. Verify that compatibility branches reject unsafe unprotected formats unless an explicit non-production or test mode is active
- account-control, key-rotation, withdrawal-address, validator-key, or permission-change signatures where SDK signing, node verification, contract verification, and legacy compatibility branches do not bind the same chain/domain, action type, account, nonce, new key or permission, fee/batch context, and time range
- wallet signing APIs that sign opaque bytes for privileged actions while verification later interprets those bytes as a protocol-specific authorization; prefer typed or canonical messages that make the action and domain explicit
- account-type or auth-mode branches, such as deterministic accounts, contract accounts, create2-like accounts, multisig accounts, or legacy accounts, where one branch accepts signature material that should be forbidden for that authority model
- signer, validator, or committee messages whose validity depends on an epoch, reward cycle, view, round, tenure, fork, or active signer-set snapshot. Verify that the signed payload, signer membership lookup, and downstream action all use the same scoped context.
- vote, block-approval, or signer-command messages represented as raw hashes, marker bytes, tuple fragments, or generic signature containers. Prefer typed protocol messages whose serialized form includes message type, domain, signer role, payload hash, and replay coordinate.
- verifier APIs that return `Result<bool>`, optional booleans, or mixed transport/semantic status. Callers must distinguish malformed input, invalid signature, wrong signer, and valid signature rather than treating API success as cryptographic success.
- new typed or compatibility transaction formats that intentionally bypass legacy replay checks. Compare mempool admission, block validation, signer recovery, fork gating, and runtime-visible domain values such as chain ID; every layer should enforce the same signed domain and reject pre-activation or wrong-domain forms.
- signed authorization deadlines, permit expirations, replay windows, or validity ranges where wallet-facing units differ from runtime units. Normalize time, block, epoch, and nonce units before comparison, fail closed on overflow, and verify the expiration check protects the final state-changing sink.
- transaction admission policies split across RPC, mempool, runtime config, and tests. Replay-unsafe legacy or compatibility formats should be rejected consistently at every layer unless explicitly scoped to non-production mode.

- p2p/control-plane group negotiation where packet or chunk signatures authenticate an outer sender, but prepare/confirm/invite/update payloads carry an inner validator id, peer list, group id, or role. Verify the recovered signer equals the entity authorized to create or confirm that group before mutating pending groups, confirmed groups, peer metadata, or routing tables.
- multi-hop routers, primary/secondary protocols, relays, or demuxers that forward only the decoded inner payload and drop the recovered author. If downstream checks cannot recover the author, the signature binding is incomplete even if the outer packet signature was valid.

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
10. For key-rotation, manifest, or delegation formats, are the long-term identity key, ephemeral signing key, revocation state, sequence, and signer namespace all checked together?
11. In two-party handshakes, does the signed transcript include freshness contributed by both parties when the response itself is later treated as live and non-replayable?
12. If an outer packet signature is stripped by a router, what evidence remains at the final sink to prove the inner claimed validator, role, or group owner was the signer?

Severity guidance:
- High for signer-authorization gaps, registration-signature gaps, bridge or validator signature binding failures, or domain-separation failures in consensus-sensitive paths.
- Medium for query-verification gaps and signed-wrapper inconsistencies unless they directly enable forged state acceptance.
```
