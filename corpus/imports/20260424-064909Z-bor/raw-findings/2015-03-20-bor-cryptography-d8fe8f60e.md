---
case_id: case_20150320_d8fe8f60e
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
bug_class: input-validation
impact_type:
  - correctness-or-hardening
confidence: low
source_quality: high
tags:
  - infrastructure
  - cryptography
  - input-validation
  - correctness-or-hardening
date: 2015-03-20
source_refs:
  - git:d8fe8f60e84f599a92783bd690b8d3477cf5a595
  - "Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c:40"
  - "Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c:55"
  - "Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c:217"
  - "Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c:158"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch in vendored Ethash code replaces several assertion-based assumptions with explicit runtime checks and failure returns in size lookup, cache generation, DAG generation, and hashing helpers. That is a real robustness improvement, but the provided evidence does not establish a concrete vulnerability, exploit path, or security impact beyond safer handling of invalid parameters.

## Observed Patch Facts

1. In `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c`, the patch replaces `size_t ethash_get_datasize(const uint32_t block_number) {` with `uint64_t ethash_get_datasize(const uint32_t block_number) {`.

2. In `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c`, the patch replaces `void static ethash_compute_cache_nodes(` with `int static ethash_compute_cache_nodes(`.

3. In `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c`, the patch replaces `assert((params->full_size % MIX_WORDS) == 0);` with `if ((params->full_size % MIX_WORDS) != 0)`.

4. In `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c`, the patch replaces `void ethash_compute_full_data(` with `return 1;`.

## Project Context

The changed code sits primarily in `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash`, `Godeps/_workspace/src/github.com/ethereum/ethash/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/ethash.h`, `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/ethash.h`, `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash-cl/ethash_cl_miner.cpp`. The strongest project-level identifiers around this patch are `const`, `params`, `block_number`, and `sizeof`.

## Before/After Behavior

Before the patch, these helpers used `assert(...)` for epoch bounds and size/alignment assumptions and returned sizes or proceeded with computation under those assumptions. After the patch, the code returns `0` or failure for out-of-range epoch values and invalid `cache_size`/`full_size` layouts, and some helper signatures were changed from `void` to `int` so failure can propagate.

# Root Cause

Critical Ethash helper routines depended on assertion-only checks for bounds and alignment instead of explicit runtime validation and error propagation.

## Walkthrough

1. `ethash_get_datasize()` changed from an asserted table bound to an explicit `if (...) return 0;` check before indexing `dag_sizes`.

2. `ethash_get_cachesize()` received the same explicit bound check before indexing `cache_sizes`.

3. `ethash_compute_cache_nodes()` changed from `void` to `int` and now returns failure when `cache_size` is not node-aligned.

4. `ethash_compute_full_data()` changed from `void` to `int` and now rejects invalid `full_size` alignment instead of asserting.

5. `ethash_hash()` now returns failure when `params->full_size` violates the expected layout constraint before continuing.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c | 40 | epoch-to-DAG-size lookup now bounds-checks the fixed size table |
| Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c | 49 | epoch-to-cache-size lookup now bounds-checks the fixed size table |
| Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c | 55 | cache-node generation now rejects misaligned cache sizes instead of asserting |
| Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c | 158 | full DAG generation now rejects invalid full-size alignment and propagates failure |
| Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c | 217 | core Ethash hash routine now rejects invalid full-size layout before processing |

## Code Snippets

## Snippet 1

Context: `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c:40` (changes a consensus- or validator-sensitive branch)

Before
```c
#endif // WITH_CRYPTOPP

size_t ethash_get_datasize(const uint32_t block_number) {
    assert(block_number / EPOCH_LENGTH < 2048);
    return dag_sizes[block_number / EPOCH_LENGTH];
}

size_t ethash_get_cachesize(const uint32_t block_number) {
```
After
```c
#endif // WITH_CRYPTOPP

uint64_t ethash_get_datasize(const uint32_t block_number) {
    if (block_number / EPOCH_LENGTH >= 2048)
        return 0;
    return dag_sizes[block_number / EPOCH_LENGTH];
}
```

## Snippet 2

Context: `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c:55` (changes the branch that decides whether execution stops or continues)

Before
```c
// https://bitslog.files.wordpress.com/2013/12/memohash-v0-3.pdf
// SeqMemoHash(s, R, N)
void static ethash_compute_cache_nodes(
        node *const nodes,
        ethash_params const *params,
        const uint8_t seed[32]) {
    assert((params->cache_size % sizeof(node)) == 0);
    uint32_t const num_nodes = (uint32_t) (params->cache_size / sizeof(node));
```
After
```c
// https://bitslog.files.wordpress.com/2013/12/memohash-v0-3.pdf
// SeqMemoHash(s, R, N)
int static ethash_compute_cache_nodes(
        node *const nodes,
        ethash_params const *params,
        const uint8_t seed[32]) {

    if ((params->cache_size % sizeof(node)) != 0)
```

## Snippet 3

Context: `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c:217` (changes the branch that decides whether execution stops or continues)

Before
```c
const uint64_t nonce) {

    assert((params->full_size % MIX_WORDS) == 0);

    // pack hash and nonce together into first 40 bytes of s_mix
    assert(sizeof(node) * 8 == 512);
    node s_mix[MIX_NODES + 1];
    memcpy(s_mix[0].bytes, header_hash, 32);
```
After
```c
const uint64_t nonce) {

    if ((params->full_size % MIX_WORDS) != 0)
        return 0;

    // pack hash and nonce together into first 40 bytes of s_mix
    node s_mix[MIX_NODES + 1];
    memcpy(s_mix[0].bytes, header_hash, 32);
```

## Snippet 4

Context: `Godeps/_workspace/src/github.com/ethereum/ethash/src/libethash/internal.c:158` (changes the branch that decides whether execution stops or continues)

Before
```c
SHA3_512(ret->bytes, ret->bytes, sizeof(node));
}

void ethash_compute_full_data(
        void *mem,
        ethash_params const *params,
        ethash_cache const *cache) {
```
After
```c
SHA3_512(ret->bytes, ret->bytes, sizeof(node));
    return 1;
}

int ethash_compute_full_data(
        void *mem,
        ethash_params const *params,
```

# Fix Pattern

Replace assertion-only invariant enforcement with explicit runtime validation and propagated error returns.

## How It Was Fixed

The patch adds guard checks for epoch-table bounds and Ethash size/alignment constraints, returns `0` on invalid inputs, and updates helper return types so callers can observe failure instead of depending on assertions.

# Why It Matters

1. Prevents unchecked indexing past fixed size tables for invalid epoch values.

2. Rejects malformed size/layout inputs before continuing computation.

3. Improves fail-closed behavior in low-level Ethash helpers.

4. Does not, by itself, prove an exploitable security bug.

# Evidence Notes

The evidence directly supports only a defensive coding change in `src/libethash/internal.c`: `assert(...)` checks became `if (...) return 0;`, and several functions now return status values. Supporting context from `ethash.h` shows related size fields are `uint64_t`. The draft's stronger security framing is not fully supported because the provided material does not show how invalid parameters are reached, whether this was exploitable in practice, or whether valid-input behavior was security-sensitive in the affected integration. Protocol security invariant: Ethash size lookup and computation helpers should reject out-of-range epoch indexes and misaligned cache/full-size parameters at runtime instead of relying on assertions or unchecked table indexing. Verification notes: The patch does not prove that remote or untrusted inputs can directly reach these invalid parameter states in deployed bor builds. It does not prove prior memory corruption; the visible change is from assert-based assumptions to explicit failure handling. It does not show that consensus results for valid Ethash inputs changed. It does not establish a demonstrated exploit path beyond possible crash, abort, or undefined behavior on malformed inputs. No concrete exploit scenario is shown in the provided evidence. No test diff or regression case in the input demonstrates a previously reachable failure. The patch is best supported as robustness hardening; security relevance remains unproven from this record alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The patch clearly replaces assertion-only assumptions with explicit runtime bounds and alignment checks in low-level Ethash helpers, and it propagates failure instead of proceeding or relying on debug-only assertions. That is meaningful hardening in a security-sensitive hashing/consensus path, especially because the old code could index fixed tables or continue computation on invalid parameters when assertions were not effective. The evidence does not, however, prove attacker-controlled reachability, a concrete exploit, or a previously demonstrated vulnerability, so this is best classified as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. `ethash_get_datasize` and `ethash_get_cachesize` now reject epochs `>= 2048` instead of relying on `assert` before fixed-table indexing.
2. `ethash_compute_cache_nodes` now returns failure when `cache_size` is misaligned instead of assuming the invariant holds.
3. `ethash_compute_full_data` now validates `full_size` layout and returns failure instead of asserting.
4. `ethash_hash` now rejects invalid `full_size` values before processing.
5. Several helper return types changed from `void` to `int`, enabling explicit failure propagation in cryptographic/validator code.

## Missing Evidence

1. No proof that untrusted or remote input can drive invalid `block_number`, `cache_size`, or `full_size` values in the deployed product.
2. No commit message, test, or advisory links the change to a reported security issue, exploit, or CVE.
3. No evidence shows prior memory corruption, data disclosure, or consensus compromise under real reachability conditions.

## Claim Boundaries

1. Supported: the patch hardens Ethash helpers against malformed or out-of-range parameters.
2. Supported: the old code depended on assertion-only checks and could perform unchecked table access or invalid processing when those assumptions failed.
3. Not supported: a confirmed exploitable vulnerability or concrete attack path.
4. Not supported: any behavior change for valid Ethash inputs or a demonstrated consensus bug.
