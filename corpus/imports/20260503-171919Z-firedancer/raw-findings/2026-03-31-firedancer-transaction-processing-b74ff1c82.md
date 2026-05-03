---
case_id: case_20260331_b74ff1c82
project: firedancer
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-03-31
source_refs:
  - git:b74ff1c8216773c14d94449ed80b72eead88caba
  - "src/waltz/h2/test_h2_conn.c:268"
  - "src/waltz/h2/fd_h2_conn.c:679"
  - "src/waltz/h2/test_h2_conn.c:621"
  - "src/disco/bundle/test_bundle_common.c:73"
bug_class: resource-capacity-invariant-violation
impact_type:
  - availability
  - denial-of-service
confidence: medium
tags:
  - http2
  - availability
  - denial-of-service
  - resource-control
  - deadlock
  - protocol-parser
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Firedancer's Waltz HTTP/2 receive path against an availability deadlock when a non-DATA frame's header plus payload is larger than the rx buffer capacity. The evidence supports a real correctness issue in the frame receive state machine under an invalid buffer/frame-size relationship, but the commit states current production buffers already satisfy the invariant. The supplied evidence does not establish a currently exploitable security vulnerability.

## Observed Patch Facts

1. In `src/waltz/h2/test_h2_conn.c`, the patch replaces `test_h2_invalid_max_frame_size( void ) {` with `static uint test_conn_final_cnt;`.

2. In `src/waltz/h2/fd_h2_conn.c`, the patch replaces `conn->rx_suppress = rbuf_rx->lo_off + tot_sz;` with `if( FD_UNLIKELY( tot_sz>rbuf_rx->bufsz ) ) {`.

3. In `src/waltz/h2/test_h2_conn.c`, the patch adds `test_h2_buffer_guard();`.

4. In `src/disco/bundle/test_bundle_common.c`, the patch replaces `state->grpc_buf_max = 4096UL;` with `state->grpc_buf_max = 16384UL + sizeof(fd_h2_frame_hdr_t);`.

## Project Context

The changed code sits primarily in `src/waltz/h2`, `src/waltz`, `src/disco/bundle`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/waltz/h2/fd_h2_conn.h`, `src/disco/bundle/fd_bundle_tile_private.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/waltz/h2/fd_h2_conn.h`, `src/disco/bundle/fd_bundle_tile_private.h`. The strongest project-level identifiers around this patch are `state`, `grpc_buf_max`, `static`, and `tot_sz`. Nearby tests or test-like files include `src/waltz/h2/fuzz_h2_actor.c`, `src/waltz/h2/fuzz_h2.c`.

## Before/After Behavior

Before the patch, `fd_h2_rx1` computed `tot_sz = sizeof(fd_h2_frame_hdr_t) + frame_sz` and, if the complete non-DATA frame was not yet buffered, could set `conn->rx_suppress = rbuf_rx->lo_off + tot_sz` without first proving `tot_sz` was no larger than `rbuf_rx->bufsz`. If an accepted frame was larger than the rx buffer capacity, the connection could wait for an impossible buffered byte count. After the patch, `fd_h2_rx1` checks `tot_sz > rbuf_rx->bufsz`, raises `FD_H2_ERR_INTERNAL`, and returns before entering suppression. Supporting test/fuzz setup sizes and clamps buffer-related values so the frame-size/buffer-capacity invariant is explicit.

# Root Cause

The root cause was an implicit and unenforced resource-capacity invariant in the HTTP/2 all-or-nothing non-DATA frame consumption path. The code assumed accepted frame size plus header could fit in the receive buffer; when that assumption was false, it could suppress receive processing until a buffer state that could never occur.

## Walkthrough

1. A non-DATA HTTP/2 frame reaches `fd_h2_rx1`.

2. The receive path computes the total frame size as header size plus payload size.

3. The all-or-nothing path requires the complete frame before consumption proceeds.

4. Before the fix, the code could set `rx_suppress` to wait for `lo_off + tot_sz` when the full frame was not currently buffered.

5. If `tot_sz` exceeded `rbuf_rx->bufsz`, the receive buffer could never satisfy that target.

6. The patch adds a guard that detects this impossible condition before setting `rx_suppress`.

7. On violation, the connection raises `FD_H2_ERR_INTERNAL` and returns.

8. Tests and fuzz setup were adjusted to make the buffer/max-frame-size relationship explicit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/waltz/h2/fd_h2_conn.c | 679 | runtime guard in H2 receive path rejects frames that can never fit in rx buffer instead of setting rx_suppress indefinitely |
| src/disco/bundle/test_bundle_common.c | 73 | test/fuzz gRPC client setup sizes rx buffer and clamps max_frame_size to preserve frame-size versus buffer-capacity invariant |
| src/waltz/h2/test_h2_conn.c | 268 | test callback state used by new buffer guard coverage to observe connection-final error handling |
| src/waltz/h2/test_h2_conn.c | 621 | adds H2 buffer guard unit test into the connection test suite |

## Code Snippets

## Snippet 1

Context: `src/waltz/h2/test_h2_conn.c:268` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
}

static void
test_h2_invalid_max_frame_size( void ) {
```
After
```c
}

static uint test_conn_final_cnt;
static uint test_conn_final_err;

static void
test_cb_conn_final( fd_h2_conn_t * conn,
                    uint           h2_err,
```

## Snippet 2

Context: `src/waltz/h2/fd_h2_conn.c:679` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
/* Consume all or nothing */
  ulong const tot_sz = sizeof(fd_h2_frame_hdr_t) + frame_sz;
  if( FD_UNLIKELY( tot_sz>fd_h2_rbuf_used_sz( rbuf_rx ) ) ) {
    conn->rx_suppress = rbuf_rx->lo_off + tot_sz;
```
After
```c
/* Consume all or nothing */
  ulong const tot_sz = sizeof(fd_h2_frame_hdr_t) + frame_sz;
  if( FD_UNLIKELY( tot_sz>rbuf_rx->bufsz ) ) {
    /* Frame will never fit in the buffer */
    fd_h2_conn_error( conn, FD_H2_ERR_INTERNAL );
    return;
  }
  if( FD_UNLIKELY( tot_sz>fd_h2_rbuf_used_sz( rbuf_rx ) ) ) {
```

## Snippet 3

Context: `src/waltz/h2/test_h2_conn.c:621` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
test_h2_invalid_max_frame_size();
  test_h2_ping_tx();
}
```
After
```c
test_h2_invalid_max_frame_size();
  test_h2_ping_tx();
  test_h2_buffer_guard();
}
```

## Snippet 4

Context: `src/disco/bundle/test_bundle_common.c:73` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
state->tcp_sock        = -1;
  state->grpc_buf_max    = 4096UL;
  state->grpc_client_mem = fd_wksp_alloc_laddr( wksp, fd_grpc_client_align(), fd_grpc_client_footprint( state->grpc_buf_max ), 1UL );
  state->grpc_client     = fd_grpc_client_new( state->grpc_client_mem, &fd_bundle_client_grpc_callbacks, state->grpc_metrics, state, state->grpc_buf_max, 1UL );
  fd_h2_conn_t * h2_conn = fd_grpc_client_h2_conn( state->grpc_client );
  h2_conn->flags = 0;
```
After
```c
state->tcp_sock        = -1;
  state->grpc_buf_max    = 16384UL + sizeof(fd_h2_frame_hdr_t);
  state->grpc_client_mem = fd_wksp_alloc_laddr( wksp, fd_grpc_client_align(), fd_grpc_client_footprint( state->grpc_buf_max ), 1UL );
  state->grpc_client     = fd_grpc_client_new( state->grpc_client_mem, &fd_bundle_client_grpc_callbacks, state->grpc_metrics, state, state->grpc_buf_max, 1UL );
  fd_h2_conn_t * h2_conn = fd_grpc_client_h2_conn( state->grpc_client );
  h2_conn->flags = 0;
  /* Clamp max_frame_size to buffer capacity so oversized frames are
```

# Fix Pattern

Check resource-capacity invariants before entering a wait or suppression state. Reject impossible frame-buffer relationships immediately, and align test/fuzz configuration with the same invariant.

## How It Was Fixed

`src/waltz/h2/fd_h2_conn.c` adds a `tot_sz > rbuf_rx->bufsz` guard before the existing suppression logic. `src/disco/bundle/test_bundle_common.c` increases the test/fuzz gRPC buffer size, clamps `self_settings.max_frame_size` to the buffer payload capacity, and asserts the invariant. `src/waltz/h2/test_h2_conn.c` adds buffer-guard test coverage and callback state for observing connection-final errors.

# Why It Matters

1. Prevents a receive-path deadlock under an invalid frame-size/buffer-capacity configuration.

2. Makes an implicit HTTP/2 receive-buffer invariant explicit.

3. Fails closed with a connection error instead of waiting for an impossible buffer state.

4. Security impact is not established for current production settings based on the provided evidence.

# Evidence Notes

The strongest evidence is the `fd_h2_rx1` change in `src/waltz/h2/fd_h2_conn.c:679`, which adds the `tot_sz > rbuf_rx->bufsz` guard. Supporting evidence appears in `src/disco/bundle/test_bundle_common.c:73`, where test/fuzz buffer sizing and `max_frame_size` clamping are made explicit, and in `src/waltz/h2/test_h2_conn.c`, where buffer-guard test coverage is added. Claims about serialization, transaction-processing state, memory corruption, or confirmed production exploitability are unsupported by the provided evidence. Protocol security invariant: HTTP/2 all-or-nothing frame receive handling must not enter a suppressed receive state waiting for a complete frame that cannot fit in the configured rx buffer. Either the configured maximum accepted frame size plus the frame header must fit in the rx buffer, or the connection must fail closed. Verification notes: The patch does not prove current production configurations were vulnerable; the commit states production buffers are currently sized safely. The patch does not show memory corruption or bounds overwrite; the failure mode evidenced is an availability deadlock. The patch does not prove remote exploitability beyond the condition where accepted frame size can exceed rx buffer capacity. The bundle fixture and fuzzer changes support regression coverage but do not by themselves establish a live security bug. Grounded as an HTTP/2 receive-path availability hardening change. The patch does not show memory corruption or bounds overwrite. The commit states production buffers are currently sized safely. Remote exploitability is not established unless a deployment accepts frames larger than its rx buffer capacity. Helper and test/fuzz changes support the runtime guard but are not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-capacity-invariant-violation`
Final impact type: `availability, denial-of-service`
Final confidence: `medium`
Final tags: `http2, availability, denial-of-service, resource-control, deadlock, protocol-parser, hardening`

The evidence supports retaining this as security hardening, not as a confirmed security fix. The patch adds an explicit HTTP/2 receive-buffer capacity guard before entering a suppression/wait state that could otherwise wait forever for a frame that can never fit. The commit itself states current production configurations already satisfy the invariant, so the evidence does not prove a presently exploitable vulnerability, but it does clearly tighten network protocol handling against an availability deadlock under unsafe future or test/fuzz configurations.

## Security Evidence

1. Runtime HTTP/2 receive path now checks total frame size against rx buffer capacity before waiting for complete frame data.
2. Oversized impossible-to-buffer frames now trigger FD_H2_ERR_INTERNAL instead of setting rx_suppress indefinitely.
3. Commit message explicitly describes a potential deadlock in the H2 all-or-nothing frame consumption path.
4. Test/fuzz setup was changed to enforce and assert the max_frame_size versus buffer-capacity invariant.
5. New unit coverage was added for buffer guard edge cases.

## Missing Evidence

1. No evidence that current production deployments were vulnerable; commit says production buffers are currently sized properly.
2. No proof of remote exploitability unless a deployment can accept frames larger than its rx buffer capacity.
3. No evidence of memory corruption, privilege escalation, consensus failure, or transaction-state divergence.
4. No demonstrated attacker-controlled path beyond the general HTTP/2 frame receive path.

## Claim Boundaries

1. Classify as HTTP/2 availability hardening, not a confirmed live vulnerability.
2. Impact should be limited to deadlock or denial of service under invalid buffer/frame-size configuration.
3. Do not retain original serialization-or-state-representation or client-view-divergence framing.
4. Do not claim production exploitability from the supplied patch evidence alone.
