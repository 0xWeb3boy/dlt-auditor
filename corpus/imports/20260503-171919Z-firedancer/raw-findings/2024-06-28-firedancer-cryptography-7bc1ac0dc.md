---
case_id: case_20240628_7bc1ac0dc
project: firedancer
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2024-06-28
source_refs:
  - git:7bc1ac0dc65f187f617b4911ed57120ee1a5ce30
  - "src/waltz/quic/crypto/fd_quic_crypto_suites.h:201"
  - "src/waltz/quic/fd_quic.c:1389"
  - "src/waltz/quic/fd_quic.c:5021"
  - "src/waltz/quic/crypto/fd_quic_crypto_suites.c:598"
bug_class: unchecked-cryptographic-rng-failure
impact_type:
  - connection-id-randomness-integrity
  - fail-open-on-rng-failure
tags:
  - cryptography
  - quic
  - rng
  - connection-id
  - fail-closed
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a QUIC connection ID RNG failure-handling hardening. The strongest evidence is that server Initial handling previously called a random-byte function for a new connection ID without checking its documented failure return, while the patched code uses fd_quic_conn_id_rand and aborts on failure. Client connection setup also now uses checked connection ID random generation for both IDs. The evidence does not support serialization, access-control, key compromise, authentication bypass, or a proven attacker-triggerable vulnerability.

## Observed Patch Facts

1. In `src/waltz/quic/crypto/fd_quic_crypto_suites.h`, the patch replaces `/* fd_quic_crypto_rand retrieves cryptographic quality random bytes` with `/* fd_quic_crypto_ctx_init initializes the given QUIC crypto context`.

2. In `src/waltz/quic/fd_quic.c`, the patch replaces `fd_quic_conn_id_t new_conn_id = {8u,{0},{0}};` with `fd_quic_conn_id_t new_conn_id;`.

3. In `src/waltz/quic/fd_quic.c`, the patch replaces `fd_quic_conn_id_t our_conn_id = fd_quic_create_conn_id( quic );` with `fd_quic_conn_id_t our_conn_id;`.

4. In `src/waltz/quic/crypto/fd_quic_crypto_suites.c`, the patch replaces `fd_quic_crypto_rand( uchar * buf,` with `fd_quic_retry_token_encrypt(`.

## Project Context

The changed code sits primarily in `src/waltz/quic/crypto`, `src/waltz/quic`, `src/waltz`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/waltz/quic/fd_quic_private.h`, `src/waltz/quic/fd_quic_conn_id.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/waltz/quic/fd_quic_private.h`, `src/waltz/quic/fd_quic_conn_id.h`. The strongest project-level identifiers around this patch are `fd_quic_conn_id_t`, `buf_sz`, `new_conn_id`, and `fd_quic_conn_id_rand`. Nearby tests or test-like files include `src/waltz/quic/tests/fuzz_quic_wire.c`, `src/waltz/quic/tests/fd_quic_sandbox.c`.

## Before/After Behavior

Before the patch, server Initial handling initialized a connection ID struct with zeroed storage, called fd_quic_crypto_rand(new_conn_id.conn_id, 8u), and had no shown local branch for RNG failure before continuing. After the patch, it calls fd_quic_conn_id_rand(&new_conn_id), logs failure, and returns FD_QUIC_PARSE_FAIL. Before the patch, client connection setup obtained local and peer IDs through fd_quic_create_conn_id with no shown call-site error branch. After the patch, it calls fd_quic_conn_id_rand for both IDs and returns NULL if either fails. The fd_quic_crypto_rand wrapper/API is also removed from the crypto suite files.

# Root Cause

The grounded root cause is missing or non-propagated secure RNG failure handling in QUIC connection ID generation paths. The server-side evidence is direct because fd_quic_crypto_rand was documented to return success or failure and its result was ignored. The client-side evidence is weaker: the diff shows newly added fail-closed handling, but the provided evidence does not show the old fd_quic_create_conn_id implementation.

## Walkthrough

1. Server Initial handling needs to choose a new local connection ID that the peer will use later as a destination connection ID.

2. Before the patch, that path initialized the connection ID storage to zero and called fd_quic_crypto_rand on the ID bytes without checking the return value.

3. The removed fd_quic_crypto_rand API was documented as returning success or failure, including failure when entropy is unavailable.

4. Ignoring that return meant the shown server path could continue without confirming that random bytes were generated.

5. After the patch, server Initial handling calls fd_quic_conn_id_rand and returns FD_QUIC_PARSE_FAIL if it fails.

6. Client connection setup now similarly checks fd_quic_conn_id_rand for both local and peer connection IDs and returns NULL on failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/waltz/quic/fd_quic.c | 1389 | server Initial packet handling generates a new local QUIC connection ID and now fails closed if secure random generation fails |
| src/waltz/quic/fd_quic.c | 5021 | client connection setup generates local and peer connection IDs and now aborts if secure random generation fails |
| src/waltz/quic/fd_quic_conn_id.h | 1 | connection ID type/helper area where fd_quic_conn_id_rand is introduced to centralize secure connection ID generation |
| src/waltz/quic/crypto/fd_quic_crypto_suites.h | 201 | removes the exposed fd_quic_crypto_rand API from the crypto suite header, reducing duplicate RNG entry points |
| src/waltz/quic/crypto/fd_quic_crypto_suites.c | 598 | removes the fd_quic_crypto_rand wrapper around fd_rng_secure |

## Code Snippets

## Snippet 1

Context: `src/waltz/quic/crypto/fd_quic_crypto_suites.h:201` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
};

/* fd_quic_crypto_rand retrieves cryptographic quality random bytes
   into given memory region.  buf points to first byte of buffer in
   local address space.  buf_sz is the number of bytes to fill.  Current
   backend is getrandom(2) (>=256-bit security level on Linux).
   Return value in FD_QUIC_{SUCCESS,FAILURE}.  Reasons for failure
   include lack of entropy, in which case caller should wait and retry.
```
After
```c
};

/* fd_quic_crypto_ctx_init initializes the given QUIC crypto context
   using the TLS provider library.  Should be considered an expensive
```

## Snippet 2

Context: `src/waltz/quic/fd_quic.c:1389` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
with in the future (via dest conn ID). */

      fd_quic_conn_id_t new_conn_id = {8u,{0},{0}};

      fd_quic_crypto_rand( new_conn_id.conn_id, 8u );

      /* Save peer's conn ID, which we will use to address peer with. */
```
After
```c
with in the future (via dest conn ID). */

      fd_quic_conn_id_t new_conn_id;
      if( FD_UNLIKELY( !fd_quic_conn_id_rand( &new_conn_id ) ) ) {
        FD_LOG_DEBUG(( "fd_quic_conn_id_rand failed" ));
        return FD_QUIC_PARSE_FAIL;
      }
```

## Snippet 3

Context: `src/waltz/quic/fd_quic.c:5021` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
/* create conn ids for us and them
     client creates connection id for the peer, peer immediately replaces it */
  fd_quic_conn_id_t our_conn_id  = fd_quic_create_conn_id( quic );
  fd_quic_conn_id_t peer_conn_id = fd_quic_create_conn_id( quic );

  fd_quic_conn_t * conn = fd_quic_conn_create(
```
After
```c
/* create conn ids for us and them
     client creates connection id for the peer, peer immediately replaces it */
  fd_quic_conn_id_t our_conn_id;
  fd_quic_conn_id_t peer_conn_id;
  if( FD_UNLIKELY( !fd_quic_conn_id_rand( &peer_conn_id ) ||
                   !fd_quic_conn_id_rand( &our_conn_id  ) ) ) {
    FD_LOG_DEBUG(( "fd_rng_secure failed" ));
    return NULL;
```

## Snippet 4

Context: `src/waltz/quic/crypto/fd_quic_crypto_suites.c:598` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
uchar minor );

int
fd_quic_crypto_rand( uchar * buf,
                     ulong   buf_sz ) {
  /* TODO buffer */
  if( FD_UNLIKELY( fd_rng_secure( buf, buf_sz ) ) )
    return FD_QUIC_FAILED;
```
After
```c
uchar minor );

int
fd_quic_retry_token_encrypt(
```

# Fix Pattern

Replace unchecked random-byte calls and non-reporting ID creation paths with a purpose-specific connection ID random helper that returns success or failure, then fail closed at connection setup call sites.

## How It Was Fixed

The patch adds or switches to fd_quic_conn_id_rand for QUIC connection ID creation, checks the helper result in server and client connection setup paths, aborts on failure, and removes the older fd_quic_crypto_rand wrapper/API from the crypto suite files.

# Why It Matters

1. QUIC connection IDs are used to route later packets to the correct connection.

2. The changed paths require cryptographically secure randomness for connection ID generation.

3. Unchecked RNG failure can allow setup to proceed without proof that the ID was randomly populated.

4. The evidence does not prove practical exploitability or attacker-controlled RNG failure.

# Evidence Notes

Primary evidence is from src/waltz/quic/fd_quic.c around the server Initial path and client setup path. Supporting evidence shows fd_quic_crypto_rand was documented as a cryptographic random byte API with failure returns and was implemented as a wrapper around fd_rng_secure before removal. The claim should stay limited to RNG failure handling for QUIC connection ID generation. Protocol security invariant: QUIC connection IDs used for future packet routing should be generated only after successful secure random byte generation, and connection setup should fail closed if secure randomness cannot be obtained. Verification notes: The patch does not prove an attacker can cause fd_rng_secure or getrandom failure. The patch does not show that duplicate or all-zero connection IDs were observed in production. The patch does not establish packet decryption, authentication bypass, or key compromise. The patch does not support the heuristic serialization/state-representation classification. The patch does not prove a denial-of-service issue beyond local connection setup failure handling. Supported: unchecked fd_quic_crypto_rand return in the server Initial connection ID path. Supported: patched fail-closed handling with fd_quic_conn_id_rand in server and client setup paths. Supported: removal of fd_quic_crypto_rand wrapper/API from crypto suite files. Not supported: serialization or state representation bug. Not supported: access-control change, key compromise, authentication bypass, or confirmed exploit path. Partially supported: client-side prior behavior, because the old fd_quic_create_conn_id implementation is not included in the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unchecked-cryptographic-rng-failure`
Final impact type: `connection-id-randomness-integrity, fail-open-on-rng-failure`
Final tags: `cryptography, quic, rng, connection-id, fail-closed`

The supplied patch evidence supports retaining this as security hardening, not a proven exploitable security fix. The code changes replace unchecked cryptographic RNG use in QUIC connection ID generation with a helper that reports failure and causes connection setup or Initial handling to fail closed. That is security-sensitive because QUIC connection IDs depend on secure randomness, but the evidence does not prove attacker-triggered RNG failure, production impact, or concrete exploitability. The original serialization/state-representation framing is misleading and should be narrowed to RNG failure handling.

## Security Evidence

1. fd_quic_crypto_rand was documented as returning success or failure for cryptographic-quality random bytes.
2. Server Initial handling previously called fd_quic_crypto_rand for a new connection ID without checking the return value.
3. Patched server Initial handling calls fd_quic_conn_id_rand and returns FD_QUIC_PARSE_FAIL on failure.
4. Client connection setup now checks fd_quic_conn_id_rand for both peer and local connection IDs and returns NULL on failure.
5. The older fd_quic_crypto_rand wrapper/API is removed, consistent with centralizing secure RNG handling.

## Missing Evidence

1. No evidence that an attacker can cause fd_rng_secure or getrandom failure.
2. No evidence of observed duplicate, zero, predictable, or reused connection IDs in production.
3. Old fd_quic_create_conn_id implementation is not included, so the client-side prior behavior is only partially supported.
4. No evidence of authentication bypass, key compromise, packet decryption, or access-control impact.

## Claim Boundaries

1. Keep the claim limited to fail-closed hardening for QUIC connection ID random generation.
2. Do not classify this as serialization, state-representation, access-control, or resource-control.
3. Do not claim a confirmed vulnerability or practical exploit path from the provided patch alone.
4. Client-side impact is weaker than server-side impact because the old helper implementation is not shown.
