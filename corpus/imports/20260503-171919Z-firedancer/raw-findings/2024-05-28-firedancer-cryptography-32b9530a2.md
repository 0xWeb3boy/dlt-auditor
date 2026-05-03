---
case_id: case_20240528_32b9530a2
project: firedancer
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: medium
date: 2024-05-28
source_refs:
  - git:32b9530a2115b282b6bb8078b077b81c9cd9019e
  - "src/waltz/quic/fd_quic.c:504"
  - "src/waltz/quic/crypto/fd_quic_crypto_suites.c:616"
  - "src/waltz/quic/crypto/fd_quic_crypto_suites.c:696"
  - "src/waltz/quic/crypto/fd_quic_crypto_suites.c:650"
bug_class: retry-token-forgery
impact_type:
  - address-validation-bypass
  - token-spoofing
confidence: high
tags:
  - quic
  - cryptography
  - retry-token
  - token-authenticity
  - address-validation
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is a grounded security fix for QUIC Retry token spoofing. It adds a per-instance `retry_secret` to QUIC state initialization and threads that secret into Retry token encryption and decryption. The strongest supported claim is that Retry token validation previously lacked server-secret binding, allowing client-spoofable tokens according to the commit subject and surrounding code changes.

## Observed Patch Facts

1. In `src/waltz/quic/fd_quic.c`, the patch replaces `/* Initialize crypto */` with `/* use rng to generate secret bytes for future RETRY token generation */`.

2. In `src/waltz/quic/crypto/fd_quic_crypto_suites.c`, the patch replaces `uchar retry_token[static FD_QUIC_RETRY_TOKEN_SZ]` with `uchar retry_token[static FD_QUIC_RETRY_TOKEN_SZ] ) {`.

3. In `src/waltz/quic/crypto/fd_quic_crypto_suites.c`, the patch replaces `uchar * retry_token,` with `uchar const retry_secret[static FD_QUIC_RETRY_SECRET_SZ],`.

4. In `src/waltz/quic/crypto/fd_quic_crypto_suites.c`, the patch replaces `/* Since the key is derived from random bytes and only used once, we use a zero IV (n...` with `/* hash a portion of the entropy to generate the IV */`.

## Project Context

The changed code sits primarily in `src/waltz/quic`, `src/waltz`, `src/waltz/quic/crypto`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/waltz/quic/fd_quic_private.h`, `src/waltz/quic/fd_quic.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/waltz/quic/fd_quic_private.h`, `src/waltz/quic/fd_quic.h`. The strongest project-level identifiers around this patch are `uchar`, `retry_token`, `static`, and `length`. Nearby tests or test-like files include `src/waltz/quic/tests/test_quic_conformance.c`, `src/waltz/quic/tests/fuzz_quic_wire.c`.

## Before/After Behavior

Before the patch, `fd_quic_init` initialized the RNG but did not populate a Retry-token server secret. Retry token encryption generated HKDF key bytes into the beginning of `retry_token`, and decryption did not take a server-held secret parameter in the provided snippet. After the patch, `fd_quic_init` fills `state->retry_secret`, and Retry token encrypt/decrypt APIs take `retry_secret`. The encryption path also changes IV handling away from an all-zero IV, but the exact derivation is only partially shown.

# Root Cause

Retry token construction and validation were not sufficiently bound to private server-side state. The provided before snippets show key material being placed in the token itself and decryption lacking a per-instance secret input, so the token could be self-contained rather than server-authenticated.

## Walkthrough

1. QUIC state initialization previously created the RNG without initializing a Retry-token secret.

2. The patched initialization fills `state->retry_secret` with `FD_QUIC_RETRY_SECRET_SZ` bytes from the instance RNG.

3. Retry token encryption previously generated HKDF key bytes directly into the token buffer, with a removed comment stating those bytes formed the beginning of the token.

4. Retry token encryption now accepts `retry_secret` and checks the retry secret size against the HKDF key size.

5. Retry token decryption now also accepts `retry_secret`, making validation depend on server-held material.

6. The IV change away from a zero IV is security-relevant hardening in the same path, but the central fix is server-secret binding.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/waltz/quic/fd_quic.c | 504 | initializes per-instance retry_secret in QUIC state for future Retry token generation |
| src/waltz/quic/crypto/fd_quic_crypto_suites.c | 616 | Retry token encryption now accepts server retry_secret and enforces secret/key size relationship |
| src/waltz/quic/crypto/fd_quic_crypto_suites.c | 650 | Retry token encryption changes nonce/IV derivation away from constant zero IV |
| src/waltz/quic/crypto/fd_quic_crypto_suites.c | 696 | Retry token decryption now accepts server retry_secret for validation |

## Code Snippets

## Snippet 1

Context: `src/waltz/quic/fd_quic.c:504` (changes persisted or aggregate state handling)

Before
```c
fd_rng_new( state->_rng, 0UL, 0UL );

  /* Initialize crypto */
```
After
```c
fd_rng_new( state->_rng, 0UL, 0UL );

  /* use rng to generate secret bytes for future RETRY token generation */
  fd_rng_t * rng = fd_rng_join( state->_rng );
  for( ulong j = 0; j < FD_QUIC_RETRY_SECRET_SZ; ++j ) {
    state->retry_secret[j] = fd_rng_uchar( rng );
  }
  fd_rng_leave( rng );
```

## Snippet 2

Context: `src/waltz/quic/crypto/fd_quic_crypto_suites.c:616` (changes a sensitive control or state-update path)

Before
```c
uint                ip_addr,
    ushort              udp_port,
    uchar               retry_token[static FD_QUIC_RETRY_TOKEN_SZ]
) {
  /* Generate pseudorandom bytes to use as the key for the AEAD HKDF. Note these bytes form the
     beginning of the retry token. */
  uchar * hkdf_key = retry_token;
  int     rc       = fd_quic_crypto_rand( retry_token, FD_QUIC_RETRY_TOKEN_HKDF_KEY_SZ );
```
After
```c
uint                ip_addr,
    ushort              udp_port,
    uchar               retry_token[static FD_QUIC_RETRY_TOKEN_SZ] ) {

  /* currently we use a server retry secret the same length as the key size */
  if( FD_UNLIKELY( FD_QUIC_RETRY_SECRET_SZ != FD_QUIC_RETRY_TOKEN_HKDF_KEY_SZ ) ) {
    FD_LOG_ERR(( "FD_QUIC_RETRY_SECRET_SZ must equal FD_QUIC_RETRY_TOKEN_HKDF_KEY_SZ" ));
  }
```

## Snippet 3

Context: `src/waltz/quic/crypto/fd_quic_crypto_suites.c:696` (changes a sensitive control or state-update path)

Before
```c
int fd_quic_retry_token_decrypt(
    uchar *             retry_token,
    fd_quic_conn_id_t * retry_src_conn_id,
    uint                ip_addr,
    ushort              udp_port,
    fd_quic_conn_id_t * orig_dst_conn_id,
    ulong *             now
```
After
```c
int fd_quic_retry_token_decrypt(
    uchar const         retry_secret[static FD_QUIC_RETRY_SECRET_SZ],
    uchar               retry_token[static FD_QUIC_RETRY_TOKEN_SZ],
    fd_quic_conn_id_t * retry_src_conn_id,
    uint                ip_addr,
    ushort              udp_port,
    fd_quic_conn_id_t * orig_dst_conn_id,
```

## Snippet 4

Context: `src/waltz/quic/crypto/fd_quic_crypto_suites.c:650` (changes a sensitive control or state-update path)

Before
```c
);

  /* Since the key is derived from random bytes and only used once, we use a zero IV (nonce).
     Note the IV length is by default 12 bytes (which is the recommended length for AES-GCM). */
  uchar iv[FD_QUIC_NONCE_SZ] = { 0 };

  /* The AAD is the client IPv4 address, UDP port, and retry source connection id. */
```
After
```c
);

  /* hash a portion of the entropy to generate the IV */
  /* use of a constant IV is strongly discouraged */
  union {
    uchar   iv[FD_QUIC_NONCE_SZ];

    /* ensures alignment and size */
```

# Fix Pattern

Bind client-returned validation tokens to server-held secret material. Initialize the secret per instance and require both token creation and validation to use it.

## How It Was Fixed

The patch initializes `state->retry_secret` during `fd_quic_init`, changes Retry token encryption and decryption signatures to accept that secret, adds a size consistency check, and updates IV handling in the token encryption path.

# Why It Matters

1. Clients should not be able to mint Retry tokens that pass server validation.

2. A token should not carry all material needed to authenticate itself.

3. The supported impact is Retry token spoofing or address-validation bypass.

4. The evidence does not support broader claims about TLS or QUIC packet encryption compromise.

# Evidence Notes

Evidence supports a QUIC Retry token authenticity issue. The commit subject explicitly says the fix ensures Retry tokens include a per-instance secret so clients cannot spoof the token. Code snippets show `state->retry_secret` added during initialization, `retry_secret` added to encrypt/decrypt APIs, prior HKDF key material generated into the token, and prior zero-IV handling changed. The evidence does not show a full exploit trace, deployment exposure, RNG quality analysis, or stronger authorization impact beyond Retry token spoofing/address-validation bypass. Protocol security invariant: QUIC Retry tokens must not be forgeable by clients. Validation should depend on server-held secret material and the relevant Retry/address-validation context, rather than on material carried entirely inside the client-returned token. Verification notes: The patch does not prove compromise of QUIC packet encryption or TLS handshake authentication. The evidence does not show a full end-to-end exploit trace, only that the token construction lacked server-secret binding before the fix. The impact should be bounded to Retry token spoofing/address-validation bypass unless other code paths consume these tokens for stronger authorization. The evidence does not establish whether deployed instances used Retry tokens in all configurations. The RNG quality and true per-instance uniqueness are not fully established from the provided snippets alone. Confirmed by commit subject and focused cryptographic token-path changes. No end-to-end exploit is provided in the input. No evidence supports the heuristic liveness-failure classification. IV hardening is secondary and only partially evidenced by the provided snippets. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `retry-token-forgery`
Final impact type: `address-validation-bypass, token-spoofing`
Final confidence: `high`
Final tags: `quic, cryptography, retry-token, token-authenticity, address-validation`

The supplied evidence strongly supports a security fix: the commit subject explicitly describes preventing client spoofing of QUIC Retry tokens, and the patch changes token generation and validation to depend on a per-instance server secret instead of apparently placing HKDF key material in the client-returned token. The original liveness classification is misleading; the supported issue is Retry token authenticity and address-validation bypass.

## Security Evidence

1. Commit subject states Retry tokens now include a per-instance secret so clients cannot spoof the token.
2. QUIC initialization now generates and stores state->retry_secret for future Retry token generation.
3. Retry token encryption now accepts retry_secret and enforces its size relationship to the HKDF key size.
4. Retry token decryption now accepts retry_secret, making validation depend on server-held material.
5. Before snippet says pseudorandom HKDF key bytes formed the beginning of the retry_token, supporting the self-contained token concern.
6. The same cryptographic token path also removes a constant zero IV, which is security-relevant hardening.

## Missing Evidence

1. No full exploit trace or proof-of-concept is provided.
2. No evidence shows which deployments or configurations enabled Retry tokens.
3. No broader compromise of QUIC packet encryption or TLS authentication is shown.
4. The exact complete new IV derivation and full token format are only partially shown.

## Claim Boundaries

1. Valid claim: clients could spoof or self-mint Retry tokens because validation lacked server-secret binding.
2. Valid claim: impact is bounded to QUIC Retry token authenticity and address-validation behavior.
3. Do not classify this as a liveness failure based on the supplied evidence.
4. Do not claim TLS compromise, packet encryption compromise, or general authentication bypass beyond Retry token validation.
