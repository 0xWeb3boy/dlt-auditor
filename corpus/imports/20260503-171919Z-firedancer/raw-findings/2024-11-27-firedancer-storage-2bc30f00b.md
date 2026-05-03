---
case_id: case_20241127_2bc30f00b
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2024-11-27
source_refs:
  - git:2bc30f00b6bee4a7055ec16d29846d6decb728d6
  - "src/flamenco/runtime/program/fd_precompiles.c:351"
  - "src/ballet/secp256r1/test_secp256r1.c:226"
  - "src/ballet/secp256r1/fd_secp256r1_s2n.c:145"
  - "src/ballet/secp256r1/fd_secp256r1_s2n.c:25"
bug_class: crypto-precompile-input-validation-hardening
impact_type:
  - malformed-input-acceptance
  - signature-verification-integrity
confidence: medium
tags:
  - blockchain-core
  - cryptography
  - precompile
  - secp256r1
  - input-validation
  - signature-verification
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is plausibly security-relevant because it touches Firedancer's secp256r1 precompile verification path and low-level secp256r1 deserialization. The provided evidence supports a correctness fix for malformed precompile input handling, scalar byte copying, and compressed public-key y-coordinate selection. However, it does not establish an end-to-end vulnerability such as invalid signature acceptance, authentication bypass, consensus divergence, or asset loss, so this should not be retained as a confirmed security fix.

## Observed Patch Facts

1. In `src/flamenco/runtime/program/fd_precompiles.c`, the patch removes `if( FD_UNLIKELY( data_sz == 2 && data[0] == 0 ) ) {`.

2. In `src/ballet/secp256r1/test_secp256r1.c`, the patch replaces `// test correctness (r,s)` with `uchar _msg[ 10 ] = { 0 }; uchar * msg = _msg;`.

3. In `src/ballet/secp256r1/fd_secp256r1_s2n.c`, the patch replaces `bignum_neg_p256( neg_y->limbs, r->y->limbs );` with `bignum_demont_p256( demont_y->limbs, r->y->limbs );`.

4. In `src/ballet/secp256r1/fd_secp256r1_s2n.c`, the patch replaces `memcpy( r, in, 32 );` with `memcpy( r->buf, in, 32 );`.

## Project Context

The changed code sits primarily in `src/flamenco/runtime/program`, `src/flamenco/runtime`, `src/ballet/secp256r1`, which anchors the finding in the `storage` area of the project. Historical context from `src/flamenco/runtime/program/fd_vote_program.c`, `src/flamenco/runtime/program/fd_system_program_nonce.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ballet/ed25519/fd_x25519.c`, `src/flamenco/runtime/program/fd_vote_program.c`. The strongest project-level identifiers around this patch are `limbs`, `uchar`, `cond`, and `ulong`. Nearby tests or test-like files include `src/flamenco/runtime/tests/fd_exec_instr_test.c`, `src/ballet/bmtree/fuzz_bmtree.c`.

## Before/After Behavior

Before the patch, fd_precompile_secp256r1_verify had a special case that returned FD_EXECUTOR_INSTR_SUCCESS for data_sz == 2 and data[0] == 0 inside the data_sz < DATA_START branch. After the patch, undersized data consistently returns FD_EXECUTOR_PRECOMPILE_ERR_INSTR_DATA_SIZE. Before the patch, fd_secp256r1_scalar_frombytes_positive copied input bytes with memcpy( r, in, 32 ); after the patch it copies to r->buf. Before the patch, fd_secp256r1_point_frombytes chose between y and -y using a negated Montgomery-domain value and numeric comparison; after the patch it demontgomerizes y, checks affine parity against sgn == 3U, and conditionally negates. Tests were reworked around explicit message buffers and sizes.

# Root Cause

The evidence points to incorrect or inconsistent handling in secp256r1 verification support code: an undersized zero-signature precompile input could return success, scalar bytes were copied through the scalar object pointer rather than explicitly into its buffer, and compressed public-key deserialization selected the y-coordinate using an ordering-based method instead of the encoded parity bit. The security impact of these behaviors is not demonstrated by the supplied evidence.

## Walkthrough

1. The runtime precompile reads instruction data and data_sz in fd_precompile_secp256r1_verify.

2. The patched size check removes a special success case for data_sz == 2 and data[0] == 0 when data_sz is below DATA_START.

3. After the patch, that undersized input path reports FD_EXECUTOR_PRECOMPILE_ERR_INSTR_DATA_SIZE.

4. Signature verification uses secp256r1 scalar deserialization in fd_secp256r1_scalar_frombytes_positive.

5. The scalar copy destination changes from r to r->buf before byte swapping and range checking.

6. Compressed public-key deserialization computes y and then selects between y and -y.

7. The previous selection used negation, numeric comparison, and muxing tied to sgn.

8. The new selection uses affine y parity compared with whether the compressed prefix is 3, then conditionally negates.

9. The accompanying tests were updated, but the provided excerpt does not show a concrete exploit regression or end-to-end failing transaction case.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/flamenco/runtime/program/fd_precompiles.c | 351 | secp256r1 precompile instruction-data size validation and zero-signature handling |
| src/ballet/secp256r1/fd_secp256r1_s2n.c | 25 | positive scalar deserialization for signature components |
| src/ballet/secp256r1/fd_secp256r1_s2n.c | 145 | compressed public key point deserialization and y-coordinate parity selection |
| src/ballet/secp256r1/test_secp256r1.c | 226 | regression and correctness coverage for secp256r1 verification behavior |

## Code Snippets

## Snippet 1

Context: `src/flamenco/runtime/program/fd_precompiles.c:351` (changes a sensitive control or state-update path)

Before
```c
/* ... */
  if( FD_UNLIKELY( data_sz < DATA_START ) ) {
    if( FD_UNLIKELY( data_sz == 2 && data[0] == 0 ) ) {
      return FD_EXECUTOR_INSTR_SUCCESS;
    }
    txn_ctx->custom_err = FD_EXECUTOR_PRECOMPILE_ERR_INSTR_DATA_SIZE;
    return FD_EXECUTOR_INSTR_ERR_CUSTOM_ERR;
```
After
```c
/* ... */
  if( FD_UNLIKELY( data_sz < DATA_START ) ) {
    txn_ctx->custom_err = FD_EXECUTOR_PRECOMPILE_ERR_INSTR_DATA_SIZE;
    return FD_EXECUTOR_INSTR_ERR_CUSTOM_ERR;
```

## Snippet 2

Context: `src/ballet/secp256r1/test_secp256r1.c:226` (changes a sensitive control or state-update path)

Before
```c
test_secp256r1_verify( FD_FN_UNUSED fd_rng_t * rng ) {

  // test correctness (r,s)
  uchar * msg = (uchar *)"hello";
  uchar _sig[ 64 ] = { 0 }; uchar * sig = _sig;
  fd_hex_decode( sig, "a940d67c9560a47c5dafb45ab1f39eb68c8fac9b51fc8c4e30b1f0e63e4967d3586569a56364c3b03eefd421aa7fc750f6fa187210c3206c55602f96e0ecaa4d", 64 );
  uchar _pub[ 33 ] = { 0 }; uchar * pub = _pub;
  fd_hex_decode( pub, "02d8c82b3791c8b51cfe44aa50226217159596ca26e6075aaf8bf8be2d351b96ae", 33 );
```
After
```c
test_secp256r1_verify( FD_FN_UNUSED fd_rng_t * rng ) {

  uchar _msg[ 10 ] = { 0 }; uchar * msg = _msg;
  ulong msg_sz;
  uchar _sig[ 64 ] = { 0 }; uchar * sig = _sig;
  uchar _pub[ 33 ] = { 0 }; uchar * pub = _pub;
  fd_sha256_t sha[1];
```

## Snippet 3

Context: `src/ballet/secp256r1/fd_secp256r1_s2n.c:145` (changes a sensitive control or state-update path)

Before
```c
/* choose y or -y */
  bignum_neg_p256( neg_y->limbs, r->y->limbs );
  ulong cond = fd_uint256_cmp( neg_y, r->y ) == (sgn == 2 ? -1 : 1);
  bignum_mux_4( cond, r->y->limbs, r->y->limbs, neg_y->limbs );

  fd_secp256r1_fp_set( r->z, fd_secp256r1_const_one_mont );
```
After
```c
/* choose y or -y */
  bignum_demont_p256( demont_y->limbs, r->y->limbs );
  ulong cond = (demont_y->limbs[0] % 2) != (sgn == 3U);
  bignum_optneg_p256( r->y->limbs, cond, r->y->limbs );

  fd_secp256r1_fp_set( r->z, fd_secp256r1_const_one_mont );
```

## Snippet 4

Context: `src/ballet/secp256r1/fd_secp256r1_s2n.c:25` (changes a sensitive control or state-update path)

Before
```c
fd_secp256r1_scalar_frombytes_positive( fd_secp256r1_scalar_t * r,
                                        uchar const             in[ 32 ] ) {
  memcpy( r, in, 32 );
  fd_uint256_bswap( r, r );
  if( FD_LIKELY( fd_uint256_cmp( r, fd_secp256r1_const_n_m1_half )<=0 ) ) {
```
After
```c
fd_secp256r1_scalar_frombytes_positive( fd_secp256r1_scalar_t * r,
                                        uchar const             in[ 32 ] ) {
  memcpy( r->buf, in, 32 );
  fd_uint256_bswap( r, r );
  if( FD_LIKELY( fd_uint256_cmp( r, fd_secp256r1_const_n_m1_half )<=0 ) ) {
```

# Fix Pattern

Correctness tightening in a cryptographic precompile path: remove an undersized-input success shortcut, make scalar deserialization write to the intended buffer field, and select compressed public-key y-coordinate using affine parity from the encoded prefix.

## How It Was Fixed

The patch removed the zero-signature success shortcut from the undersized-data branch, changed scalar deserialization to copy into r->buf, replaced ordering-based compressed-point y selection with parity-based selection after demontgomery conversion, and updated secp256r1 verification tests.

# Why It Matters

1. The changed code is on a signature verification path.

2. Malformed precompile input returning success can be security-relevant in a runtime.

3. Compressed public-key decoding must follow the encoded parity rule for correctness.

4. The evidence does not prove invalid signatures were accepted.

5. No concrete exploit path or consensus impact is shown.

# Evidence Notes

Primary evidence is limited to commit 2bc30f00b6bee4a7055ec16d29846d6decb728d6 and snippets from fd_precompiles.c, fd_secp256r1_s2n.c, and test_secp256r1.c. The commit subject says secp256k1, while the supplied code evidence is secp256r1. Related vote, nonce, BPF serialization, and x25519 snippets do not support the vulnerability thesis and should not be treated as affected paths. Claims about storage, funds at risk, consensus divergence, or proven signature bypass are unsupported. Protocol security invariant: The secp256r1 precompile should apply its instruction-data layout checks and cryptographic decoding rules consistently before returning verification success, including handling undersized input, scalar deserialization, and compressed public-key y-coordinate selection according to the encoded format. Verification notes: No concrete exploit path is proven by the patch evidence. No proof is shown that invalid signatures were accepted end-to-end. No consensus divergence or funds-at-risk scenario is demonstrated. The commit subject says secp256k1, but the provided files and code paths are secp256r1. Related vote, nonce, BPF serialization, and x25519 contexts do not appear to be the primary affected business-logic path. No end-to-end invalid-signature acceptance is shown. No transaction-level exploit scenario is shown. No protocol reference is provided proving the zero-signature case must fail. Tests indicate regression coverage, but the supplied snippets do not show the full expected outcomes. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `crypto-precompile-input-validation-hardening`
Final impact type: `malformed-input-acceptance, signature-verification-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, cryptography, precompile, secp256r1, input-validation, signature-verification, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not a confirmed security fix. The changes are in an exposed blockchain runtime precompile and low-level secp256r1 verification/deserialization code, and they remove a path where undersized precompile data could return instruction success while also correcting cryptographic parsing behavior. However, the evidence does not prove an exploitable invalid-signature acceptance, consensus divergence, authorization bypass, or asset-loss scenario, so the corpus entry should be framed conservatively as hardening.

## Security Evidence

1. The runtime secp256r1 precompile previously returned success for data_sz == 2 and data[0] == 0 inside an undersized-data branch; the patch now reports an instruction data size error.
2. The patched code is on a signature verification precompile path exposed to transaction instruction data.
3. Compressed public-key deserialization was changed from ordering-based y selection to parity-based selection after demontgomery conversion, matching security-sensitive crypto decoding semantics.
4. Scalar deserialization now copies into r->buf instead of the scalar object pointer, tightening parsing behavior in signature component handling.
5. Tests were updated alongside the implementation changes, indicating regression coverage for the secp256r1 behavior.

## Missing Evidence

1. No end-to-end transaction or exploit proof shows that invalid signatures were accepted before the patch.
2. No demonstrated consensus divergence, funds-at-risk, privilege bypass, or authentication bypass is provided.
3. No protocol reference is supplied proving the removed zero-signature success case was exploitable rather than merely nonconforming.
4. The commit subject says secp256k1 while the code evidence is secp256r1, creating some metadata ambiguity.

## Claim Boundaries

1. Treat this as security hardening of a crypto precompile, not a confirmed exploitable vulnerability.
2. Do not claim asset loss, consensus failure, or invalid-signature acceptance from the supplied evidence alone.
3. Do not retain the original storage subsystem framing; the supported area is cryptographic precompile verification.
4. The supported impact is malformed input acceptance and signature verification integrity risk, not a proven attack outcome.
