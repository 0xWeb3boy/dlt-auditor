---
case_id: case_20260429_4c4abcf43
project: firedancer
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2026-04-29
source_refs:
  - git:4c4abcf430d4d9393dc693e7d7f6a81f917ddc79
  - "src/waltz/http/fd_http_server.c:65"
  - "src/discof/restore/utils/fd_sshttp.c:592"
  - "src/discof/restore/fd_snapct_tile.c:1329"
  - "src/discof/restore/fd_snapct_tile.c:1401"
bug_class: http-content-length-input-validation
impact_type:
  - availability-hardening
  - snapshot-restore-integrity-hardening
confidence: medium
tags:
  - infrastructure
  - http
  - content-length
  - input-validation
  - snapshot-restore
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens snapshot restore HTTP Content-Length handling by replacing permissive strtoul parsing with fd_http_parse_content_len, rejecting malformed or zero values, canceling invalid HTTP responses, and marking zero snapshot size metadata as malformed. The evidence supports input-validation and robustness hardening, but not a confirmed vulnerability.

## Observed Patch Facts

1. In `src/waltz/http/fd_http_server.c`, the patch replaces `case FD_HTTP_SERVER_CONNECTION_CLOSE_OK: return "OK-Connection was closed normally";` with `case FD_HTTP_SERVER_CONNECTION_CLOSE_OK: return "OK-Connection was closed normally";`.

2. In `src/discof/restore/utils/fd_sshttp.c`, the patch replaces `http->content_len = strtoul( headers[i].value, NULL, 10 );` with `ulong val = 0UL;`.

3. In `src/discof/restore/fd_snapct_tile.c`, the patch replaces `if( full ) ctx->metrics.full.bytes_total = meta->total_sz;` with `if( FD_UNLIKELY( meta->total_sz==0UL ) ) {`.

4. In `src/discof/restore/fd_snapct_tile.c`, the patch replaces `if( full ) FD_TEST( ctx->metrics.full.bytes_total !=0UL );` with `if( FD_UNLIKELY( full && ctx->metrics.full.bytes_total==0UL ) ) {`.

## Project Context

The changed code sits primarily in `src/waltz/http`, `src/waltz`, `src/discof/restore/utils`, which anchors the finding in the `storage` area of the project. Historical context from `src/discof/restore/fd_snapwm_tile.c`, `src/discof/restore/fd_snaplv_tile.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/discof/restore/fd_snapwm_tile.c`, `src/discof/restore/fd_snaplv_tile.c`. The strongest project-level identifiers around this patch are `case`, `full`, `malformed`, and `bytes_total`. Nearby tests or test-like files include `src/waltz/http/fuzz_picohttpparser.c`, `src/waltz/http/fuzz_httpserver.c`.

## Before/After Behavior

Before the patch, fd_sshttp.c parsed Content-Length with strtoul and assigned the result directly to http->content_len. Snapshot control code then accepted meta->total_sz into bytes_total, while later data-fragment handling relied on FD_TEST assertions that bytes_total was nonzero. After the patch, Content-Length parse failure or zero length cancels the HTTP request; zero snapshot metadata marks the restore context malformed; and zero bytes_total during data handling is treated as malformed runtime state instead of only an assertion failure.

# Root Cause

The supported root cause is insufficient validation of HTTP Content-Length-derived snapshot size state before it was used for restore accounting. Claims about memory corruption, consensus compromise, or malicious unauthenticated control are not established by the supplied evidence.

## Walkthrough

1. The restore HTTP response path scans headers for content-length in src/discof/restore/utils/fd_sshttp.c.

2. The old code used strtoul(headers[i].value, NULL, 10) and stored the result as http->content_len.

3. The new code calls fd_http_parse_content_len with the explicit header value length.

4. If parsing fails or the parsed value is zero, the patched code logs a warning, cancels the request, and returns FD_SSHTTP_ADVANCE_ERROR.

5. Snapshot metadata handling in src/discof/restore/fd_snapct_tile.c now rejects meta->total_sz==0UL before recording bytes_total.

6. Snapshot data-fragment handling now marks zero full or incremental bytes_total as malformed and returns.

7. The fd_http_server.c close-reason string edits appear cosmetic in the supplied evidence and are not part of the security claim.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/discof/restore/utils/fd_sshttp.c | 592 | Parses HTTP response Content-Length from snapshot source; now rejects malformed or zero values and cancels the request. |
| src/discof/restore/fd_snapct_tile.c | 1329 | Consumes snapshot metadata total_sz; now marks zero Content-Length metadata malformed before recording bytes_total. |
| src/discof/restore/fd_snapct_tile.c | 1401 | Handles snapshot data fragments; now treats zero bytes_total as malformed instead of relying on FD_TEST assertions. |
| src/waltz/http/fd_http_server.c | 65 | Connection close reason string cleanup; no direct security invariant shown in this hunk. |

## Code Snippets

## Snippet 1

Context: `src/waltz/http/fd_http_server.c:65` (changes a sensitive control or state-update path)

Before
```c
fd_http_server_connection_close_reason_str( int reason ) {
  switch( reason ) {
    case FD_HTTP_SERVER_CONNECTION_CLOSE_OK:                           return "OK-Connection was closed normally";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_EVICTED:                      return "EVICTED-Connection was evicted to make room for a new one";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_TOO_SLOW:                     return "TOO_SLOW-Client was too slow and did not read the reponse in time";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_EXPECTED_EOF:                 return "EXPECTED_EOF-Client continued to send data when we expected no more";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_PEER_RESET:                   return "PEER_RESET-Connection was reset by peer";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_LARGE_REQUEST:                return "LARGE_REQUEST-Request body was too large";
```
After
```c
fd_http_server_connection_close_reason_str( int reason ) {
  switch( reason ) {
    case FD_HTTP_SERVER_CONNECTION_CLOSE_OK:                            return "OK-Connection was closed normally";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_EVICTED:                       return "EVICTED-Connection was evicted to make room for a new one";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_TOO_SLOW:                      return "TOO_SLOW-Client was too slow and did not read the response in time";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_EXPECTED_EOF:                  return "EXPECTED_EOF-Client continued to send data when we expected no more";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_PEER_RESET:                    return "PEER_RESET-Connection was reset by peer";
    case FD_HTTP_SERVER_CONNECTION_CLOSE_LARGE_REQUEST:                 return "LARGE_REQUEST-Request body was too large";
```

## Snippet 2

Context: `src/discof/restore/utils/fd_sshttp.c:592` (changes a sensitive control or state-update path)

Before
```c
if( FD_LIKELY( strncasecmp( headers[i].name, "content-length", 14UL ) ) ) continue;

    http->content_len = strtoul( headers[i].value, NULL, 10 );
    break;
  }
```
After
```c
if( FD_LIKELY( strncasecmp( headers[i].name, "content-length", 14UL ) ) ) continue;

    ulong val = 0UL;
    if( FD_UNLIKELY( fd_http_parse_content_len( headers[i].value, (ulong)headers[i].value_len, &val ) || val==0UL ) ) {
      FD_LOG_WARNING(( "invalid content-length in response from " FD_IP4_ADDR_FMT ":%hu", FD_IP4_ADDR_FMT_ARGS( http->addr.addr ), fd_ushort_bswap( http->addr.port ) ));
      fd_sshttp_cancel( http );
      return FD_SSHTTP_ADVANCE_ERROR;
    }
```

## Snippet 3

Context: `src/discof/restore/fd_snapct_tile.c:1329` (changes persisted or aggregate state handling)

Before
```c
fd_ssctrl_meta_t const * meta = fd_chunk_to_laddr_const( ctx->snapld_in_mem, chunk );

    if( full ) ctx->metrics.full.bytes_total        = meta->total_sz;
    else       ctx->metrics.incremental.bytes_total = meta->total_sz;
```
After
```c
fd_ssctrl_meta_t const * meta = fd_chunk_to_laddr_const( ctx->snapld_in_mem, chunk );

    if( FD_UNLIKELY( meta->total_sz==0UL ) ) {
      FD_LOG_WARNING(( "received zero Content-Length metadata for %s snapshot, marking malformed", full ? "full" : "incremental" ));
      ctx->malformed = 1;
      return;
    }
```

## Snippet 4

Context: `src/discof/restore/fd_snapct_tile.c:1401` (changes persisted or aggregate state handling)

Before
```c
}

  if( full ) FD_TEST( ctx->metrics.full.bytes_total       !=0UL );
  else       FD_TEST( ctx->metrics.incremental.bytes_total!=0UL );

  if( full ) ctx->metrics.full.bytes_read        += sz;
```
After
```c
}

  if( FD_UNLIKELY( full  && ctx->metrics.full.bytes_total==0UL ) ) {
    if( !ctx->malformed ) {
      ctx->malformed = 1;
      FD_LOG_WARNING(( "received data frag for full snapshot with zero bytes_total" ));
    }
    return;
```

# Fix Pattern

Replace permissive numeric parsing with strict bounded parsing, reject invalid zero-size state at ingestion, and convert assumptions about externally received size metadata into explicit runtime error handling.

## How It Was Fixed

The patch uses fd_http_parse_content_len instead of strtoul for Content-Length, rejects parse errors and zero values, cancels invalid HTTP responses, and adds zero-size checks in snapshot metadata and data-fragment paths that mark the restore context malformed before continuing.

# Why It Matters

1. Prevents malformed or zero Content-Length values from silently becoming snapshot restore size state.

2. Moves validation closer to the HTTP response boundary.

3. Avoids relying on assertions for zero bytes_total conditions during restore processing.

4. Security relevance is plausible, but the evidence does not prove an exploitable vulnerability.

# Evidence Notes

Grounded evidence is limited to Content-Length parsing and zero-size handling in src/discof/restore/utils/fd_sshttp.c and src/discof/restore/fd_snapct_tile.c. The supplied diff does not show memory corruption, authorization impact, consensus failure, snapshot integrity bypass, or that an attacker can control the HTTP response source. The server close-reason changes are cleanup only. Protocol security invariant: Snapshot restore HTTP handling should parse Content-Length strictly and should not allow a zero length to become required snapshot size/accounting state. The provided evidence shows this invariant being enforced, but does not establish exploitability or attacker control of the response source. Verification notes: No proof of memory corruption is shown by the patch evidence. No proof of consensus compromise or snapshot integrity bypass is shown. No proof that an unauthenticated attacker can control the HTTP response source is shown. The fd_http_server close-reason string changes appear cosmetic and are not security-relevant on their own. The evidence supports hardening against malformed Content-Length/state handling, not a confirmed exploitable vulnerability. Classified as hardening-relevant but not a validated security fix. Downgraded security_verdict from likely to unclear due lack of exploitability evidence. Set keep_in_security_corpus to false under the rule for security-relevant but unestablished vulnerability theses. Preserved snapshot-restore-http and content-length-validation because those are directly supported by the patch. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `http-content-length-input-validation`
Final impact type: `availability-hardening, snapshot-restore-integrity-hardening`
Final confidence: `medium`
Final tags: `infrastructure, http, content-length, input-validation, snapshot-restore, hardening`

The supplied patch clearly tightens parsing and validation of HTTP Content-Length values used by snapshot restore state. It replaces permissive strtoul parsing with a bounded parser, rejects parse failures and zero values, cancels invalid HTTP responses, and treats zero snapshot size state as malformed at runtime. The evidence supports security hardening of an externally influenced HTTP/snapshot restore boundary, but does not prove a concrete exploitable vulnerability, memory corruption, consensus impact, or attacker control sufficient for a security-fix classification.

## Security Evidence

1. Commit subject explicitly says the Content-Length parser was hardened.
2. HTTP response Content-Length parsing changed from strtoul to fd_http_parse_content_len with explicit value length.
3. Malformed or zero Content-Length now cancels the HTTP request and returns an error.
4. Zero snapshot total size metadata now marks the restore context malformed instead of being accepted into bytes_total.
5. Zero bytes_total during data-fragment handling is now handled as malformed runtime state rather than only via FD_TEST assertions.

## Missing Evidence

1. No proof that an unauthenticated or remote attacker can control the snapshot HTTP response source.
2. No demonstrated memory corruption, out-of-bounds access, or integer overflow from the old parser.
3. No demonstrated consensus failure, snapshot integrity bypass, or persistent state corruption.
4. No tests or advisory text showing a concrete exploit scenario.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Limit the bug class to Content-Length input validation in snapshot restore HTTP handling.
3. Do not claim memory safety impact from the provided patch alone.
4. Do not claim consensus compromise or database corruption from the provided evidence.
5. Treat fd_http_server.c close-reason string edits as cosmetic unless supported by other evidence.
