---
case_id: case_20260425_384b6f788
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2026-04-25
source_refs:
  - git:384b6f7884dbe33f24117330377dae3bcb2a6d29
  - "src/ballet/bls/fd_bls12_381.c:524"
  - "src/ballet/bls/fd_bls12_381.c:507"
  - "src/ballet/bls/test_bls12_381.c:1110"
  - "src/ballet/bls/test_bls12_381.c:1155"
bug_class: cryptographic-transcript-validation
impact_type:
  - signature-validation-bypass-risk
confidence: medium
tags:
  - blockchain-core
  - cryptography
  - bls
  - proof-of-possession
  - signature-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Firedancer's BLS proof-of-possession verifier to align the verified hash input with the documented Agave shape, H(msg || public_key, POP_DST), and adds an upper bound for the current vote-program message size. This is plausibly security relevant cryptographic correctness work, but the supplied evidence does not prove a vulnerability, exploit path, or prior acceptance of an attacker-controlled invalid proof. Treat as unclear rather than a confirmed or likely security fix.

## Observed Patch Facts

1. In `src/ballet/bls/fd_bls12_381.c`, the patch replaces `if( FD_UNLIKELY( msg_sz<48 ) ) {` with `if( FD_UNLIKELY( msg_sz<48 || msg_sz>FD_BLS12_381_POP_MSG_MAX ) ) {`.

2. In `src/ballet/bls/fd_bls12_381.c`, the patch replaces `fd_bls12_381_proof_of_possession_verify( uchar const msg[], /* msg_sz */` with `/* The maximum msg size accepted by fd_bls12_381_proof_of_possession_verify.`.

3. In `src/ballet/bls/test_bls12_381.c`, the patch replaces `.p = "966668cb06354807f59e5ab52139dc0c62588caf224b64b869f2e04b7fb76b326c56b32a71c6933...` with `.p = "86f10df775ec42e34d0c541839c45250607bf21f2ae3d967f0e659905d7d27c4962697105b10ae8...`.

4. In `src/ballet/bls/test_bls12_381.c`, the patch replaces `.m = "b7234f70d097e3c4aec83cac68bc800eab507990a53527e4978ca49818c50ae1611d8d8a1233751...` with `.m = "a4f08db1846a6aa02d3cb88870d15859409dc87eed6da500fab89f076710c7e3c82b0d6fc0e8443...`.

## Project Context

The changed code sits primarily in `src/ballet/bls`, `src/ballet`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/ballet/bls/fd_bls12_381.h`, `src/ballet/bls/Local.mk` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ballet/ed25519/fd_ed25519_user.c`, `src/ballet/bls/fd_bls12_381.h`. The strongest project-level identifiers around this patch are `msg_sz`, `test`, `a4f08db1846a6aa02d3cb88870d15859409dc87eed6da500fab89f076710c7e3c82b0d6fc0e8443bd952dc5b4bb8e7a8`, and `public_key`. Nearby tests or test-like files include `src/ballet/zksdk/tests/test_zksdk_create_ledger.sh`, `src/ballet/txn/fuzz_txn_parse.c`.

## Before/After Behavior

Before the patch, fd_bls12_381_proof_of_possession_verify rejected only msg_sz < 48 and then verified the caller-provided msg directly under the POP domain. After the patch, it rejects msg_sz < 48 and msg_sz > FD_BLS12_381_POP_MSG_MAX, copies msg into a bounded local buffer, appends the 48-byte public_key, and verifies msg || public_key under the POP domain. Tests were rekeyed and updated for negative and successful proof-of-possession vectors.

# Root Cause

The previous verifier did not match the transcript shape documented by the patch comment for Agave-compatible proof-of-possession verification. It checked the caller-provided message bytes directly instead of checking msg || public_key. The evidence supports a protocol-alignment issue, but not a demonstrated vulnerability root cause.

## Walkthrough

1. The changed function is fd_bls12_381_proof_of_possession_verify in src/ballet/bls/fd_bls12_381.c.

2. Before the change, the function rejected messages shorter than 48 bytes and passed msg and msg_sz directly to fd_bls12_381_core_verify with the POP domain.

3. The patch adds FD_BLS12_381_POP_MSG_MAX set to 89 bytes, with a comment tying that bound to the current vote-program callsite.

4. The verifier now rejects messages shorter than 48 bytes or larger than the configured maximum.

5. The verifier constructs a bounded buffer containing msg followed by the 48-byte public_key.

6. The final verification call uses the concatenated buffer and length msg_sz + 48, matching the added comment that Agave hashes msg || public_key with POP_DST.

7. The tests update proof-of-possession vectors, including negative cases for too-small or non-POP messages and success cases for the revised message shape.

8. No provided evidence shows an end-to-end exploit, a failed security invariant at the vote-program level, or a previously accepted malicious proof.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ballet/bls/fd_bls12_381.c | 507 | Defines FD_BLS12_381_POP_MSG_MAX as the maximum proof-of-possession message size for the vote-program callsite. |
| src/ballet/bls/fd_bls12_381.c | 524 | Verifies BLS proof of possession; now bounds msg_sz and verifies over msg concatenated with public_key under the POP domain. |
| src/ballet/bls/test_bls12_381.c | 1110 | Updates negative proof-of-possession vectors for too-small or non-POP messages. |
| src/ballet/bls/test_bls12_381.c | 1155 | Updates successful proof-of-possession vectors for the new key/domain/message-binding behavior. |

## Code Snippets

## Snippet 1

Context: `src/ballet/bls/fd_bls12_381.c:524` (changes a sensitive control or state-update path)

Before
```c
Since the public key must be part of the message, we check that
     msg_sz >= public key size, again to avoid accidental mistakes. */
  if( FD_UNLIKELY( msg_sz<48 ) ) {
    return -1;
  }

  return fd_bls12_381_core_verify( msg, msg_sz, proof, public_key, FD_BLS_SIG_DOMAIN_POP );
}
```
After
```c
Since the public key must be part of the message, we check that
     msg_sz >= public key size, again to avoid accidental mistakes. */
  if( FD_UNLIKELY( msg_sz<48 || msg_sz>FD_BLS12_381_POP_MSG_MAX ) ) {
    return -1;
  }

  /* Agave adds the public key into the hash input:
     H(msg || public_key, POP_DST).
```

## Snippet 2

Context: `src/ballet/bls/fd_bls12_381.c:507` (changes bounds, limits, or capacity handling)

Before
```c
}

int
fd_bls12_381_proof_of_possession_verify( uchar const msg[], /* msg_sz */
```
After
```c
}

/* The maximum msg size accepted by fd_bls12_381_proof_of_possession_verify.
   Currently the only callsite is from the vote program, so we know the
   upper bound required is FD_VOTE_BLS_MSG_SZ. */
#define FD_BLS12_381_POP_MSG_MAX (89UL)

int
```

## Snippet 3

Context: `src/ballet/bls/test_bls12_381.c:1110` (changes a sensitive control or state-update path)

Before
```c
{ /* invalid, msg_sz too small - this is a valid test passing the public key as msg */
        .m = "",
        .p = "966668cb06354807f59e5ab52139dc0c62588caf224b64b869f2e04b7fb76b326c56b32a71c6933fca876e1d87bbaea40b97dc12307eb791e5ca08b6a24b1cf966b0ed94073521543808dcee74e1c4a095ab9a256e33d7a9e0fbf396d0e899aa",
        .k = "b7234f70d097e3c4aec83cac68bc800eab507990a53527e4978ca49818c50ae1611d8d8a1233751decd693f37425844c",
      },
      // test 1
      { /* invalid, msg_sz too small - this is valid test in agave - but it's definitely not a pop */
        .m = "53494d442d303338372d636f6e746578742d64617461",
```
After
```c
{ /* invalid, msg_sz too small - this is a valid test passing the public key as msg */
        .m = "",
        .p = "86f10df775ec42e34d0c541839c45250607bf21f2ae3d967f0e659905d7d27c4962697105b10ae860cde2d5889c697bc09fe88af0641fb7f31d2a9fce1cab3fc8f615cc0fd556b21aa55d96a2d7eb3d8332b3d5dfca4fe56a4dc67c9a4bbd10b",
        .k = "a4f08db1846a6aa02d3cb88870d15859409dc87eed6da500fab89f076710c7e3c82b0d6fc0e8443bd952dc5b4bb8e7a8",
      },
      // test 1
      { /* invalid, msg_sz too small - this is valid test in agave - but it's definitely not a pop */
        .m = "53494d442d303338372d636f6e746578742d64617461",
```

## Snippet 4

Context: `src/ballet/bls/test_bls12_381.c:1155` (changes a sensitive control or state-update path)

Before
```c
// test 0
      { /* m is the public key */
        .m = "b7234f70d097e3c4aec83cac68bc800eab507990a53527e4978ca49818c50ae1611d8d8a1233751decd693f37425844c",
        .p = "966668cb06354807f59e5ab52139dc0c62588caf224b64b869f2e04b7fb76b326c56b32a71c6933fca876e1d87bbaea40b97dc12307eb791e5ca08b6a24b1cf966b0ed94073521543808dcee74e1c4a095ab9a256e33d7a9e0fbf396d0e899aa",
        .k = "b7234f70d097e3c4aec83cac68bc800eab507990a53527e4978ca49818c50ae1611d8d8a1233751decd693f37425844c",
      },
      // test 1
      { /* m is ALPENGLOW:vote_account_pubkey:bls_pubkey */
```
After
```c
// test 0
      { /* m is the public key */
        .m = "a4f08db1846a6aa02d3cb88870d15859409dc87eed6da500fab89f076710c7e3c82b0d6fc0e8443bd952dc5b4bb8e7a8",
        .p = "86f10df775ec42e34d0c541839c45250607bf21f2ae3d967f0e659905d7d27c4962697105b10ae860cde2d5889c697bc09fe88af0641fb7f31d2a9fce1cab3fc8f615cc0fd556b21aa55d96a2d7eb3d8332b3d5dfca4fe56a4dc67c9a4bbd10b",
        .k = "a4f08db1846a6aa02d3cb88870d15859409dc87eed6da500fab89f076710c7e3c82b0d6fc0e8443bd952dc5b4bb8e7a8",
      },
      // test 1
      { /* m is ALPENGLOW:vote_account_pubkey:bls_pubkey */
```

# Fix Pattern

Align cryptographic verification with the intended protocol transcript and bound accepted input sizes for the known callsite.

## How It Was Fixed

The patch adds a maximum accepted POP message size, extends the size check, builds a local msg || public_key buffer, and verifies that concatenated input under the POP domain. The test vectors were updated to match the new key/domain/message-binding behavior.

# Why It Matters

1. Proof-of-possession checks depend on verifying the intended transcript.

2. Binding the public key into the verified input can be security relevant for POP semantics.

3. The new maximum size constrains accepted inputs to the documented callsite requirement.

4. The evidence does not prove exploitability or prior malicious acceptance.

# Evidence Notes

Grounded evidence is limited to the implementation change in src/ballet/bls/fd_bls12_381.c and updated tests in src/ballet/bls/test_bls12_381.c. The added comment states Agave uses H(msg || public_key, POP_DST). The evidence does not show the caller, the vote-program acceptance path, attacker control, consensus impact, BLS forgery, private-key recovery, or denial of service from the old missing upper bound. Protocol security invariant: A BLS proof-of-possession verifier should verify the exact protocol-defined transcript and domain for the intended callsite. The provided evidence shows this implementation was changed to verify over msg || public_key under the POP domain and to reject messages outside the expected size range, but it does not establish that the previous behavior enabled an exploitable security violation. Verification notes: No exploit path through the vote program is shown in the provided evidence. No state-changing acceptance of an invalid proof is demonstrated. The patch does not prove forgery of BLS signatures or private-key recovery. The max message size change may be resource/control hardening, but no denial-of-service condition is proven. Feature-map and generated feature changes are not enough on their own to establish a security fix. Implementation evidence supports transcript and size-check changes. Tests support intended behavior changes but do not prove a vulnerability. No exploit path is demonstrated in the provided input. Security relevance is plausible but the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cryptographic-transcript-validation`
Final impact type: `signature-validation-bypass-risk`
Final confidence: `medium`
Final tags: `blockchain-core, cryptography, bls, proof-of-possession, signature-validation, security-hardening`

The evidence does not prove a concrete exploitable vulnerability, but it does show a security-sensitive cryptographic verifier being tightened: proof-of-possession verification changes from checking the caller-provided message directly to verifying the protocol-shaped transcript msg || public_key under the POP domain, with an explicit maximum message size for the vote-program callsite. That is stronger than ordinary maintenance or compatibility cleanup, but should be retained conservatively as security hardening rather than a confirmed security fix.

## Security Evidence

1. BLS proof-of-possession verification is a security-sensitive cryptographic validation path.
2. The verifier now binds public_key into the hash input as H(msg || public_key, POP_DST).
3. The patch rejects messages larger than FD_BLS12_381_POP_MSG_MAX before building a bounded local buffer.
4. Comments explicitly describe avoiding unsupported POP behavior for security reasons and preventing accidental future changes.
5. Tests update negative and success vectors around the revised POP transcript behavior.

## Missing Evidence

1. No exploit path through the vote program is shown.
2. No evidence demonstrates prior acceptance of an attacker-controlled invalid proof.
3. No consensus failure, request forgery, replay, or validator-impact example is provided.
4. No denial-of-service condition from the old missing upper bound is proven.
5. Commit subject suggests protocol/domain update work, not an explicit security advisory or vulnerability fix.

## Claim Boundaries

1. Treat as cryptographic validation hardening, not a proven vulnerability repair.
2. Do not claim BLS private-key recovery or signature forgery.
3. Do not claim confirmed replay or request forgery from the supplied patch alone.
4. Do not claim the old code was exploitable at an external boundary without caller evidence.
5. The supported claim is limited to tighter POP transcript validation and input-size bounding.
