---
case_id: case_20230929_7cbb71919
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: access-control
source_quality: high
date: 2023-09-29
source_refs:
  - git:7cbb71919ec9b8045c247957280e5b15d1e0cb85
  - "src/ballet/shred/fd_shred.h:257"
  - "src/ballet/shred/fd_shred.h:61"
  - "src/ballet/shred/fd_shred.h:191"
  - "src/ballet/shred/fd_shred.h:230"
bug_class: parser-bounds-hardening
impact_type:
  - input-validation-hardening
confidence: medium
tags:
  - blockchain-core
  - shred-parser
  - untrusted-input
  - bounds-check
  - size-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch improves Firedancer shred parsing and size accounting by passing the actual buffer length into fd_shred_parse, documenting a smaller minimum input size, distinguishing maximum shred size from actual shred size, and deriving payload size from a parsed fd_shred_t. This is plausibly security relevant because shreds are untrusted inputs, but the provided evidence does not establish a concrete vulnerability, exploit path, memory safety failure, consensus issue, or authentication bypass.

## Observed Patch Facts

1. In `src/ballet/shred/fd_shred.h`, the patch replaces `Returns an arbitrary value if the variant is invalid. */` with `Undefined behavior if the shred has not passed 'fd_shred_parse'. */`.

2. In `src/ballet/shred/fd_shred.h`, the patch replaces `/* FD_SHRED_SZ: The byte size of a shred.` with `/* FD_SHRED_MAX_SZ: The max byte size of a shred.`.

3. In `src/ballet/shred/fd_shred.h`, the patch replaces `The provided buffer must be at least FD_SHRED_SZ bytes long.` with `The provided buffer must be at least FD_SHRED_MIN_SZ bytes long.`.

4. In `src/ballet/shred/fd_shred.h`, the patch replaces `uchar shred_type = fd_shred_type( variant );` with `uchar type = fd_shred_type( variant );`.

## Project Context

The changed code sits primarily in `src/ballet/shred`, `src/ballet`, which anchors the finding in the `access-control` area of the project. Historical context from `src/ballet/shred/test_shred.c`, `src/ballet/shred/fd_shred.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ballet/shred/test_shred.c`, `src/ballet/shred/fd_shred.c`. The strongest project-level identifiers around this patch are `shred`, `variant`, `uchar`, and `shred_type`. Nearby tests or test-like files include `src/ballet/shred/fuzz_shred_parse.c`, `src/ballet/ed25519/fuzz_ed25519_verify.c`.

## Before/After Behavior

Before the patch, fd_shred_parse accepted only a buffer pointer and documented that callers must provide at least FD_SHRED_SZ bytes. Size helpers assumed fixed-size shreds and fd_shred_payload_sz computed payload length from a raw variant and FD_SHRED_SZ. After the patch, fd_shred_parse accepts buf and sz, performs an initial bounds check before reading the variant, the public comments distinguish FD_SHRED_MAX_SZ from smaller valid shreds, and fd_shred_payload_sz operates on a parsed fd_shred_t and uses parsed size fields.

# Root Cause

The prior parser API and size helpers encoded fixed-size assumptions for data that may be variable-sized. The evidence supports an API/design weakness around actual-length tracking, but does not prove that this weakness was reachable as a security bug.

## Walkthrough

1. Untrusted shred bytes are parsed through fd_shred_parse in the ballet shred subsystem.

2. The old parser signature accepted only uchar const *buf and relied on a documented FD_SHRED_SZ caller precondition.

3. The patch changes the parser signature to fd_shred_parse(buf, sz), so the implementation can reason about the actual input length.

4. The shown implementation stores sz as total_shred_sz and rejects buffers smaller than the minimum header size before accessing shred->variant.

5. The size model changes from treating FD_SHRED_SZ as the byte size of a shred to documenting FD_SHRED_MAX_SZ as a maximum, with comments noting that Merkle data shreds may be smaller.

6. fd_shred_payload_sz changes from accepting a variant byte and subtracting sizes from FD_SHRED_SZ to accepting a parsed fd_shred_t pointer.

7. For data shreds, payload size is derived from shred->data.size; for code shreds, it uses fd_shred_sz(shred), header size, and Merkle proof size.

8. Tests and a fuzz target are updated, which supports parser robustness work but does not by itself prove a vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ballet/shred/fd_shred.c | 1 | implements parsing and initial bounds checks for untrusted shred buffers |
| src/ballet/shred/fd_shred.h | 191 | defines parser contract, changing it to accept explicit buffer length |
| src/ballet/shred/fd_shred.h | 257 | derives payload size from a parsed shred instead of only the variant/fixed maximum size |
| src/ballet/shred/fd_shred.h | 61 | defines shred maximum/minimum size model used by parsing and validation |
| src/ballet/shred/test_shred.c | 1 | tests shred layout and parsing-related assumptions |
| src/ballet/shred/fuzz_shred_parse.c | 1 | fuzz target for untrusted shred parsing |

## Code Snippets

## Snippet 1

Context: `src/ballet/shred/fd_shred.h:257` (changes a sensitive control or state-update path)

Before
```c
/* fd_shred_payload_sz: Returns the payload size of a shred.
   Returns an arbitrary value if the variant is invalid. */
FD_FN_CONST static inline ulong
fd_shred_payload_sz( uchar variant ) {
  return FD_SHRED_SZ - fd_shred_header_sz( variant ) - fd_shred_merkle_sz( variant );
}
```
After
```c
/* fd_shred_payload_sz: Returns the payload size of a shred.
   Undefined behavior if the shred has not passed `fd_shred_parse`. */
FD_FN_PURE static inline ulong
fd_shred_payload_sz( fd_shred_t const * shred ) {
  if( FD_LIKELY( fd_shred_type( shred->variant ) & FD_SHRED_TYPEMASK_DATA ) ) {
    return shred->data.size - FD_SHRED_DATA_HEADER_SZ;
  } else {
```

## Snippet 2

Context: `src/ballet/shred/fd_shred.h:61` (changes bounds, limits, or capacity handling)

Before
```c
Consequentially, only the block producer is able to create valid shreds for any given block. */

#include "../fd_ballet_base.h"
#include "../../util/fd_util_base.h"

/* FD_SHRED_SZ: The byte size of a shred.
   This limit derives from the IPv6 MTU of 1280 bytes,
   minus 48 bytes for the UDP/IPv6 headers and another 4 bytes for good measure. */
```
After
```c
Consequentially, only the block producer is able to create valid shreds for any given block. */

#include "../fd_ballet.h"


/* FD_SHRED_MAX_SZ: The max byte size of a shred.
   This limit derives from the IPv6 MTU of 1280 bytes, minus 48 bytes
   for the UDP/IPv6 headers and another 4 bytes for good measure.  Most
```

## Snippet 3

Context: `src/ballet/shred/fd_shred.h:191` (changes bounds, limits, or capacity handling)

Before
```c
/* fd_shred_parse: Parses and validates an untrusted shred header.
   The provided buffer must be at least FD_SHRED_SZ bytes long.

   The returned pointer either equals the input pointer
   or is NULL if the given shred is malformed. */
FD_FN_PURE fd_shred_t const *
fd_shred_parse( uchar const * buf );
```
After
```c
/* fd_shred_parse: Parses and validates an untrusted shred header.
   The provided buffer must be at least FD_SHRED_MIN_SZ bytes long.

   The returned pointer either equals the input pointer
   or is NULL if the given shred is malformed. */
FD_FN_PURE fd_shred_t const *
fd_shred_parse( uchar const * buf,
```

## Snippet 4

Context: `src/ballet/shred/fd_shred.h:230` (changes persisted or aggregate state handling)

Before
```c
FD_FN_CONST static inline ulong
fd_shred_header_sz( uchar variant ) {
  uchar shred_type = fd_shred_type( variant );
  if( FD_LIKELY( shred_type==FD_SHRED_TYPE_MERKLE_DATA || shred_type==FD_SHRED_TYPE_LEGACY_DATA ) ) {
    return FD_SHRED_DATA_HEADER_SZ;
  }
  if( FD_LIKELY( shred_type==FD_SHRED_TYPE_MERKLE_CODE || shred_type==FD_SHRED_TYPE_LEGACY_CODE ) ) {
    return FD_SHRED_CODE_HEADER_SZ;
```
After
```c
FD_FN_CONST static inline ulong
fd_shred_header_sz( uchar variant ) {
  uchar type = fd_shred_type( variant );
  if( FD_LIKELY( (type==FD_SHRED_TYPE_MERKLE_DATA) | (type==FD_SHRED_TYPE_LEGACY_DATA) ) )
    return FD_SHRED_DATA_HEADER_SZ;
  if( FD_LIKELY( (type==FD_SHRED_TYPE_MERKLE_CODE) | (type==FD_SHRED_TYPE_LEGACY_CODE) ) )
    return FD_SHRED_CODE_HEADER_SZ;
  return 0;
```

# Fix Pattern

Carry actual input length through parsing, validate minimum bounds before field access, separate maximum packet size from actual parsed size, and make payload-size helpers consume validated parsed objects.

## How It Was Fixed

The patch updates fd_shred_parse to take an explicit sz parameter, changes parser documentation from an FD_SHRED_SZ precondition to an FD_SHRED_MIN_SZ minimum, introduces FD_SHRED_MAX_SZ terminology, adds an initial bounds check in fd_shred_parse, and rewrites fd_shred_payload_sz to use a parsed fd_shred_t rather than a raw variant and fixed maximum size.

# Why It Matters

1. Shreds are parsed from untrusted input.

2. Variable-sized inputs need actual-length checks.

3. Fixed-size assumptions can become dangerous in parsers.

4. The evidence shows hardening, not a proven exploit fix.

# Evidence Notes

The access-control framing in the heuristic baseline is unsupported. The evidence supports the ballet shred parser and size-accounting subsystem, not authentication, replay, or authorization logic. The provided snippets show bounds and size-model improvements, but they do not show a concrete out-of-bounds read/write, remote crash, consensus divergence, or reachable exploit path. Because the vulnerability thesis is not established, this should not be kept as a confirmed security fix. Protocol security invariant: Untrusted shred buffers should be checked against the actual received length before fields such as the variant, header size, payload size, or Merkle proof size are interpreted. Downstream helpers should rely on parsed shred state rather than assuming every shred has a fixed maximum size. Verification notes: The patch does not prove an authentication bypass of block producer signatures. The patch does not show a concrete out-of-bounds read/write trigger from a caller path. The patch does not prove replay or consensus divergence by itself. The evidence does not establish remote exploitability, only that untrusted parsing and size validation were tightened. The access-control label in the heuristic baseline is not supported by the shown code paths. No concrete exploit trigger is shown in the supplied evidence. No caller path demonstrating unsafe short-buffer parsing is provided. No advisory, CVE, or explicit security commit message is provided. Fuzz/test updates support robustness work but are not sufficient to confirm a vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `parser-bounds-hardening`
Final impact type: `input-validation-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, shred-parser, untrusted-input, bounds-check, size-accounting`

The supplied evidence supports retaining this as security hardening, not as a confirmed security fix. The patch changes an untrusted shred parser to receive the actual buffer length, documents a smaller minimum parse size, adds an initial bounds check before interpreting fields, and changes payload sizing to depend on parsed shred state rather than a fixed maximum. That is security-relevant parser hardening, but the evidence does not prove a concrete exploitable bug, memory safety failure, consensus impact, or authentication/access-control issue.

## Security Evidence

1. fd_shred_parse is explicitly documented as parsing and validating an untrusted shred header.
2. The parser API changes from buf-only to buf plus sz, allowing validation against the actual input length.
3. The implementation excerpt shows an initial size check before accessing shred fields such as variant.
4. Size accounting changes from fixed FD_SHRED_SZ assumptions to maximum/actual shred sizing.
5. fd_shred_payload_sz now requires a parsed fd_shred_t, narrowing use to validated parsed state.

## Missing Evidence

1. No concrete vulnerable caller path is shown for short or malformed buffers.
2. No before-version implementation is provided showing an actual out-of-bounds read or write.
3. No crash, exploit, consensus divergence, or denial-of-service trigger is demonstrated.
4. No advisory, CVE, security note, or explicitly security-focused commit message is supplied.
5. The access-control and signature framing is not supported by the shown patch evidence.

## Claim Boundaries

1. Classify as parser/input bounds hardening, not a confirmed vulnerability fix.
2. Do not claim authentication bypass, access-control failure, replay issue, or signature verification weakness.
3. Do not claim proven remote exploitability from the supplied evidence alone.
4. Do not claim memory corruption beyond the general risk reduced by explicit length checks.
5. The supported impact is conservative input-validation hardening for untrusted shred parsing.
