---
case_id: case_20250919_3d4cbe567
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2025-09-19
source_refs:
  - git:3d4cbe567f064724f30afa70f3a07e7e7c36da99
  - "src/discof/send/fd_send_tile.c:449"
  - "src/discof/writer/fd_writer_tile.c:281"
bug_class: stack-buffer-overflow
impact_type:
  - memory-corruption
tags:
  - blockchain-core
  - transaction-processing
  - memory-safety
  - stack-buffer-overflow
  - fd-txn-parse
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Likely security fix for a stack-buffer-overflow risk in Firedancer's discof send/writer vote transaction path. The patch replaces stack fd_txn_t parser outputs with aligned FD_TXN_MAX_SZ byte buffers at two fd_txn_parse call sites. The evidence supports a caller-side output-buffer sizing bug, but does not prove remote exploitability, arbitrary code execution, or consensus divergence.

## Observed Patch Facts

1. In `src/discof/send/fd_send_tile.c`, the patch replaces `fd_txn_t txn;` with `uchar txn_mem[ FD_TXN_MAX_SZ ] __attribute__((aligned(alignof(fd_txn_t))));`.

2. In `src/discof/writer/fd_writer_tile.c`, the patch replaces `fd_txn_t txn;` with `uchar txn_mem[ FD_TXN_MAX_SZ ] __attribute__((aligned(alignof(fd_txn_t))));`.

## Project Context

The changed code sits primarily in `src/discof/send`, `src/discof`, `src/discof/writer`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/discof/send/fd_send_tile.h`, `src/discof/writer/fd_writer_tile.seccomppolicy` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/discof/resolv/fd_resolv_tile.c`, `src/discof/replay/test_rdisp.c`. The strongest project-level identifiers around this patch are `uchar`, `fd_txn_t`, `txn_mem`, and `signed_vote_txn`. Nearby tests or test-like files include `src/discof/backtest/fd_backtest_tile.c`, `src/discof/rpcserver/fuzz_json_lex.c`.

## Before/After Behavior

Before the patch, handle_vote_msg in src/discof/send/fd_send_tile.c and during_frag in src/discof/writer/fd_writer_tile.c declared fd_txn_t txn on the stack, passed &txn to fd_txn_parse, and then read parsed offsets through txn.field. After the patch, both callers allocate aligned uchar txn_mem[FD_TXN_MAX_SZ], cast it to fd_txn_t *, pass txn_mem to fd_txn_parse, and read parsed fields through txn->field.

# Root Cause

The affected callers gave fd_txn_parse storage sized as sizeof(fd_txn_t). The fix indicates fd_txn_parse may write metadata requiring a larger FD_TXN_MAX_SZ buffer, so the old calls could overwrite adjacent stack memory in these send/writer vote-handling paths.

## Walkthrough

1. handle_vote_msg receives a signed vote transaction and parses it before locating the signature and message inside signed_vote_txn.

2. The old send-side code allocated only fd_txn_t txn on the stack and passed &txn as fd_txn_parse output storage.

3. The patched send-side code allocates aligned uchar txn_mem[FD_TXN_MAX_SZ], casts it to fd_txn_t *, and passes txn_mem to fd_txn_parse.

4. during_frag handles a message from the send tile, derives payload from fd_txn_m_t, and parses that payload before copying the vote signature.

5. The old writer-side code also allocated only fd_txn_t txn on the stack and passed &txn to fd_txn_parse.

6. The patched writer-side code mirrors the larger aligned-buffer allocation and pointer-based field access.

7. The commit subject explicitly says the change fixes buffer overflows by fd_txn_parse, which matches the observed larger output-buffer allocation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/discof/send/fd_send_tile.c | 449 | handle_vote_msg parses a signed vote transaction before using parsed signature and message offsets for signing |
| src/discof/writer/fd_writer_tile.c | 281 | during_frag parses a transaction payload received from the send tile before copying the vote signature |

## Code Snippets

## Snippet 1

Context: `src/discof/send/fd_send_tile.c:449` (changes signature or replay validation logic)

Before
```c
ulong                vote_txn_sz ) {

  fd_txn_t txn;
  FD_TEST( fd_txn_parse( signed_vote_txn, vote_txn_sz, &txn, NULL ) );

  /* sign the txn */
  uchar * signature = signed_vote_txn + txn.signature_off;
  uchar const * message   = signed_vote_txn + txn.message_off;
```
After
```c
ulong                vote_txn_sz ) {

  uchar txn_mem[ FD_TXN_MAX_SZ ] __attribute__((aligned(alignof(fd_txn_t))));
  fd_txn_t * txn = (fd_txn_t *)txn_mem;
  FD_TEST( fd_txn_parse( signed_vote_txn, vote_txn_sz, txn_mem, NULL ) );

  /* sign the txn */
  uchar * signature = signed_vote_txn + txn->signature_off;
```

## Snippet 2

Context: `src/discof/writer/fd_writer_tile.c:281` (changes signature or replay validation logic)

Before
```c
fd_txn_m_t * txnm    = fd_type_pun( fd_chunk_to_laddr( in_ctx->mem, chunk ) );
    uchar *      payload = ((uchar *)txnm) + sizeof(fd_txn_m_t);
    fd_txn_t txn;
    if( FD_UNLIKELY( !fd_txn_parse( payload, txnm->payload_sz, &txn, NULL ) ) ) {
      FD_LOG_CRIT(( "Could not parse txn from send tile" ));
    }
    uchar * signature = payload + txn.signature_off;
    memcpy( ctx->vote_msg, signature, 64UL );
```
After
```c
fd_txn_m_t * txnm    = fd_type_pun( fd_chunk_to_laddr( in_ctx->mem, chunk ) );
    uchar *      payload = ((uchar *)txnm) + sizeof(fd_txn_m_t);
    uchar        txn_mem[ FD_TXN_MAX_SZ ] __attribute__((aligned(alignof(fd_txn_t))));
    fd_txn_t *   txn = (fd_txn_t *)txn_mem;
    if( FD_UNLIKELY( !fd_txn_parse( payload, txnm->payload_sz, txn_mem, NULL ) ) ) {
      FD_LOG_CRIT(( "Could not parse txn from send tile" ));
    }
    uchar * signature = payload + txn->signature_off;
```

# Fix Pattern

Replace undersized stack parser-output objects with correctly sized, aligned byte buffers, then access parsed metadata through a fd_txn_t pointer backed by that larger buffer.

## How It Was Fixed

Both fd_txn_parse callers replaced fd_txn_t txn with uchar txn_mem[FD_TXN_MAX_SZ] aligned to alignof(fd_txn_t). Each caller casts the buffer to fd_txn_t *, passes txn_mem to fd_txn_parse, and updates field reads from txn.field to txn->field. No provided evidence shows fd_txn_parse itself changed.

# Why It Matters

1. Prevents fd_txn_parse from writing past a too-small stack fd_txn_t buffer in these paths.

2. Protects parsed signature and message offset handling from adjacent stack corruption.

3. Touches validator vote transaction handling in send and writer tiles.

4. Evidence does not prove remote exploitability, code execution, or consensus divergence.

# Evidence Notes

Primary evidence is the focused diff in src/discof/send/fd_send_tile.c:handle_vote_msg and src/discof/writer/fd_writer_tile.c:during_frag, plus the commit subject "send, writer: fix buffer overflows by fd_txn_parse". The stronger claim that the parser's required output buffer is formally documented is not directly shown in the provided evidence, so it should be framed as inferred from the fix shape and commit subject. Protocol security invariant: Transaction parsing in the send/writer vote path must provide fd_txn_parse with output storage large enough for the parser's worst-case metadata, not merely a stack fd_txn_t object, before parsed offsets are used for signing or vote-message handling. Verification notes: No proof that an unauthenticated remote attacker can directly control the overflowing transaction in these paths No proof of arbitrary code execution from the stack overwrite No proof of consensus safety violation or ledger divergence No evidence that fd_txn_parse itself was changed, only its callers' output buffer allocation No concrete malformed transaction example is provided Supported: two fd_txn_parse call sites changed from stack fd_txn_t output to aligned FD_TXN_MAX_SZ storage. Supported: commit subject identifies buffer overflows by fd_txn_parse. Not shown: malformed transaction proof of concept. Not shown: attacker control path, arbitrary code execution, or consensus safety impact. Not shown: changes to fd_txn_parse itself. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `stack-buffer-overflow`
Final impact type: `memory-corruption`
Final tags: `blockchain-core, transaction-processing, memory-safety, stack-buffer-overflow, fd-txn-parse`

The supplied patch and commit subject directly support a memory-safety fix: two fd_txn_parse callers stopped passing a stack fd_txn_t object and instead provide an aligned FD_TXN_MAX_SZ buffer. The evidence is strong for a caller-side stack buffer overflow fix in transaction/vote handling code, but not for the original liveness-focused classification or for claims about remote exploitability, code execution, replay, or consensus divergence.

## Security Evidence

1. Commit subject explicitly says "fix buffer overflows by fd_txn_parse".
2. Both changed call sites replace stack fd_txn_t output storage with aligned uchar txn_mem[FD_TXN_MAX_SZ].
3. Both call sites pass the larger txn_mem buffer to fd_txn_parse and then read fields through a fd_txn_t pointer.
4. Affected code parses signed vote transactions or send-tile transaction payloads before signature handling.

## Missing Evidence

1. No fd_txn_parse contract or documentation is provided to prove the exact required output size.
2. No malformed transaction proof of concept is provided.
3. No evidence shows attacker control over these exact inputs.
4. No crash, overwrite target, code execution, or consensus divergence demonstration is provided.

## Claim Boundaries

1. Supported claim: this fixes undersized output storage passed to fd_txn_parse at two call sites.
2. Supported claim: the risk is stack buffer overflow or memory corruption.
3. Unsupported claim: arbitrary code execution is proven.
4. Unsupported claim: consensus failure, replay vulnerability, or liveness failure is proven.
5. Unsupported claim: the issue is remotely exploitable from the supplied evidence alone.
