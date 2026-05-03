---
case_id: case_20251202_52a2cbfda
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
source_quality: medium
date: 2025-12-02
source_refs:
  - git:52a2cbfdae26503d47def686168901350ad4b312
  - "src/discof/genesis/fd_genesis_client.c:169"
  - "src/app/shared_dev/rpc_client/fd_rpc_client.c:195"
  - "src/discof/genesis/Local.mk:3"
  - "src/tango/tempo/test_tempo.c:87"
bug_class: content-length-integer-overflow
impact_type:
  - out-of-bounds-read
confidence: medium
tags:
  - rpc
  - genesis-client
  - content-length
  - integer-overflow
  - out-of-bounds-read
  - input-validation
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

This is a confirmed security fix for Content-Length parsing in the genesis and RPC client paths. Both parsers previously accepted any numeric value returned by strtoul as long as at least one digit was parsed. The patch adds an explicit content_length > UINT_MAX rejection in both functions. The commit body identifies the issue as an OOB read vulnerability caused by crafted Content-Length headers.

## Observed Patch Facts

1. In `src/discof/genesis/fd_genesis_client.c`, the patch adds `if( FD_UNLIKELY( content_length>UINT_MAX ) ) return ULONG_MAX; /* prevent overflow */`.

2. In `src/app/shared_dev/rpc_client/fd_rpc_client.c`, the patch adds `if( FD_UNLIKELY( content_length>UINT_MAX ) ) return ULONG_MAX; /* prevent overflow */`.

3. In `src/discof/genesis/Local.mk`, the patch adds `ifdef FD_HAS_HOSTED`.

4. In `src/tango/tempo/test_tempo.c`, the patch replaces `//FD_TEST( !fd_tempo_async_min( 0L, 1UL, 1.f ) );` with `FD_TEST( !fd_tempo_async_min( 0L, 1UL, 1.f ) );`.

## Project Context

The changed code sits primarily in `src/discof/genesis`, `src/discof`, `src/app/shared_dev/rpc_client`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/tango/tempo/fd_tempo.h`, `src/tango/tempo/fd_tempo.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/tango/test_frag_tx.c`, `src/tango/tempo/fd_tempo.h`. The strongest project-level identifiers around this patch are `fd_tempo_async_min`, `content_length`, `headers`, and `value`. Nearby tests or test-like files include `src/discof/genesis/fuzz_genesis_client.c`, `src/discof/backtest/fd_backtest_rocksdb.c`.

## Before/After Behavior

Before the patch, rpc_phr_content_length() and fd_rpc_phr_content_length() parsed Content-Length with strtoul() and only rejected values where no digits were consumed. Numeric values greater than UINT_MAX were returned as valid ulong lengths. After the patch, both functions return ULONG_MAX for content_length > UINT_MAX, using the existing invalid-length path before the value can be accepted. The Local.mk change adds hosted fuzz coverage for fd_genesis_client. The tempo test changes are unrelated to the Content-Length issue.

# Root Cause

The root cause was missing upper-bound validation after parsing an untrusted Content-Length value into ulong. Values larger than UINT_MAX could be accepted by the parser. The patch comment says this prevents overflow, and the commit body says the crafted-header condition caused an OOB read. The supplied evidence does not show the downstream read site.

## Walkthrough

1. The genesis client and RPC client scan parsed HTTP headers for Content-Length.

2. When the header is found, the value is parsed with strtoul(headers[i].value, &end, 10).

3. Before the patch, the visible validation only rejected values where no digits were parsed.

4. A numeric Content-Length greater than UINT_MAX could still pass that validation.

5. The parser would return that oversized value as a usable content length.

6. The commit body states that crafted Content-Length input caused an OOB read in fd_rpc_client and fd_genesis_client.

7. After the patch, both parsers reject content_length > UINT_MAX by returning ULONG_MAX.

8. The added fuzz target is supporting test coverage, not the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/discof/genesis/fd_genesis_client.c | 169 | genesis client Content-Length parser rejects values above UINT_MAX before returning a usable body length |
| src/app/shared_dev/rpc_client/fd_rpc_client.c | 195 | RPC client Content-Length parser rejects values above UINT_MAX before returning a usable body length |
| src/discof/genesis/Local.mk | 3 | adds hosted fuzz target coverage for fd_genesis_client |
| src/tango/tempo/test_tempo.c | 87 | unrelated tempo unit-test reenablement, not part of the Content-Length security path |

## Code Snippets

## Snippet 1

Context: `src/discof/genesis/fd_genesis_client.c:169` (changes a sensitive control or state-update path)

Before
```c
char * end;
    ulong content_length = strtoul( headers[i].value, &end, 10 );
    if( FD_UNLIKELY( end==headers[i].value ) ) return ULONG_MAX;
    return content_length;
```
After
```c
char * end;
    ulong content_length = strtoul( headers[i].value, &end, 10 );
    if( FD_UNLIKELY( content_length>UINT_MAX ) ) return ULONG_MAX; /* prevent overflow */
    if( FD_UNLIKELY( end==headers[i].value ) ) return ULONG_MAX;
    return content_length;
```

## Snippet 2

Context: `src/app/shared_dev/rpc_client/fd_rpc_client.c:195` (changes a sensitive control or state-update path)

Before
```c
char * end;
    ulong content_length = strtoul( headers[i].value, &end, 10 );
    if( FD_UNLIKELY( end==headers[i].value ) ) return ULONG_MAX;
    return content_length;
```
After
```c
char * end;
    ulong content_length = strtoul( headers[i].value, &end, 10 );
    if( FD_UNLIKELY( content_length>UINT_MAX ) ) return ULONG_MAX; /* prevent overflow */
    if( FD_UNLIKELY( end==headers[i].value ) ) return ULONG_MAX;
    return content_length;
```

## Snippet 3

Context: `src/discof/genesis/Local.mk:3` (changes a sensitive control or state-update path)

Before
```text
ifdef FD_HAS_BZIP2
$(call add-objs,fd_genesi_tile fd_genesis_client,fd_discof)
endif
endif
```
After
```text
ifdef FD_HAS_BZIP2
$(call add-objs,fd_genesi_tile fd_genesis_client,fd_discof)
ifdef FD_HAS_HOSTED
$(call make-fuzz-test,fuzz_genesis_client,fuzz_genesis_client,fd_discof fd_waltz fd_ballet fd_util)
endif
endif
endif
```

## Snippet 4

Context: `src/tango/tempo/test_tempo.c:87` (changes a sensitive control or state-update path)

Before
```c
FD_TEST( fd_tempo_lazy_default( ULONG_MAX   )==2147483647L );

//FD_TEST( !fd_tempo_async_min(   0L,     1UL, 1.f ) );
//FD_TEST( !fd_tempo_async_min(   1L,     0UL, 1.f ) );
//FD_TEST( !fd_tempo_async_min(   1L,     1UL, 0.f ) );
//FD_TEST( !fd_tempo_async_min( 100L, 10000UL, 1.f ) );
  FD_TEST( fd_ulong_is_pow2( fd_tempo_async_min( 100000L, 1UL, 1.f ) ) );
```
After
```c
FD_TEST( fd_tempo_lazy_default( ULONG_MAX   )==2147483647L );

  FD_TEST( !fd_tempo_async_min(   0L,     1UL, 1.f ) );
  FD_TEST( !fd_tempo_async_min(   1L,     0UL, 1.f ) );
  FD_TEST( !fd_tempo_async_min(   1L,     1UL, 0.f ) );
  FD_TEST( !fd_tempo_async_min( 100L, 10000UL, 1.f ) );
  FD_TEST( fd_ulong_is_pow2( fd_tempo_async_min( 100000L, 1UL, 1.f ) ) );
```

# Fix Pattern

Validate untrusted length fields immediately after parsing and reject values outside the supported downstream integer range before returning or using them.

## How It Was Fixed

The patch adds the same guard to both affected parser functions: if content_length is greater than UINT_MAX, return ULONG_MAX. This appears in src/discof/genesis/fd_genesis_client.c and src/app/shared_dev/rpc_client/fd_rpc_client.c. Existing rejection for nonnumeric values remains in place. src/discof/genesis/Local.mk also adds a hosted fuzz target for fuzz_genesis_client.

# Why It Matters

1. Prevents oversized Content-Length values from being accepted as valid body lengths.

2. Addresses the commit-stated OOB read condition for crafted Content-Length headers.

3. Applies the same boundary check to both affected client parser paths.

4. Does not establish write impact, code execution, authentication impact, or consensus impact from the provided evidence.

# Evidence Notes

The strongest evidence is the identical added content_length > UINT_MAX guard in src/discof/genesis/fd_genesis_client.c and src/app/shared_dev/rpc_client/fd_rpc_client.c, plus the inline prevent overflow comment and commit body explicitly naming an OOB read vulnerability. The downstream OOB read location is not shown. The fuzzer addition supports regression coverage. The tempo test hunk is unrelated. Protocol security invariant: Content-Length values parsed from HTTP headers must be rejected if they exceed the integer range supported by downstream body handling. The grounded invariant shown by the patch is that both genesis and RPC client parsers must treat values greater than UINT_MAX as invalid before returning a usable length. Verification notes: The exact downstream OOB read site is not shown in the provided patch evidence. Remote exploitability is not proven beyond handling of crafted Content-Length input. No write primitive, code execution, authentication bypass, or consensus impact is shown. The fd_tempo_async_min test changes are not evidence of this security fix. The fuzzer addition alone would be non-security without the parser range checks and commit body. Confirmed by provided diff snippets only; no repository inspection was performed. Exact downstream OOB read site is not established by the supplied evidence. Remote exploitability and impact beyond OOB read are not proven. Helper/fuzzer changes are support code rather than the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `content-length-integer-overflow`
Final impact type: `out-of-bounds-read`
Final confidence: `medium`
Final tags: `rpc, genesis-client, content-length, integer-overflow, out-of-bounds-read, input-validation`

The supplied evidence supports keeping this as a security-fix case. The commit body explicitly describes an OOB read vulnerability from crafted Content-Length headers, and the patch adds identical upper-bound validation to two Content-Length parsers before returning the parsed value. The exact downstream OOB read site is not shown, so the corpus metadata should stay conservative and avoid claiming broader exploit impact.

## Security Evidence

1. Commit body states this fixes an OOB read vulnerability triggered by crafted Content-Length headers.
2. Both fd_genesis_client and fd_rpc_client parsed Content-Length with strtoul and previously accepted values greater than UINT_MAX.
3. The patch rejects content_length > UINT_MAX and comments that this prevents overflow.
4. The fixed value comes from HTTP header input and is returned as a usable content length.

## Missing Evidence

1. No downstream buffer access or read site is shown in the supplied patch evidence.
2. No proof of remote exploitability beyond crafted header handling is provided.
3. No evidence supports write impact, code execution, authentication bypass, or consensus impact.
4. The tempo test changes are unrelated to the Content-Length issue.

## Claim Boundaries

1. Classify only the Content-Length parser range check as the security fix.
2. Impact should be limited to OOB read / overflow prevention based on the supplied evidence.
3. The fuzzer addition is supporting evidence, not independently a security fix.
4. Do not infer broader blockchain consensus or privilege impact from this patch.
