---
case_id: case_20240717_ebef6c368
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: core-logic
confidence: medium
source_quality: high
date: 2024-07-17
source_refs:
  - git:ebef6c3687087685ae7422c2f56ae7c2f6ae0405
  - "src/util/BinaryFuseFilter.cpp:25"
  - "lib/binaryfusefilter.h:31"
  - "lib/binaryfusefilter.h:368"
  - "lib/binaryfusefilter.h:293"
bug_class: hash-collision-dos-hardening
impact_type:
  - denial-of-service
tags:
  - dos-protection
  - hash-collision
  - siphash
  - bounded-retry
  - binary-fuse-filter
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best classified as likely DoS hardening for BinaryFuseFilter. It replaces Murmur/mix-split-style hashing with SipHash24 keyed by the filter seed in population and lookup paths, and changes population retry behavior from unbounded to capped at 10 attempts. The evidence supports security hardening, but does not prove a concrete exploitable production DoS path.

## Observed Patch Facts

1. In `src/util/BinaryFuseFilter.cpp`, the patch replaces `for (size_t i = 0;; ++i)` with `// If too many hash collisions occur, population will fail. Retry with`.

2. In `lib/binaryfusefilter.h`, the patch replaces `binary_fuse_murmur64(uint64_t h)` with `sip_hash24(uint64_t key, binary_fuse_seed_t const& seed)`.

3. In `lib/binaryfusefilter.h`, the patch replaces `uint64_t hash = binary_fuse_murmur64(keys[i] + _seed);` with `uint64_t hash = sip_hash24(keys[i], _seed);`.

4. In `lib/binaryfusefilter.h`, the patch replaces `uint64_t hash = binary_fuse_mix_split(key, _seed);` with `uint64_t hash = sip_hash24(key, _seed);`.

## Project Context

The changed code sits primarily in `src/util`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/util/BinaryFuseFilter.h`, `lib/catch.hpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/util/BinaryFuseFilter.h`, `src/util/RandomEvictionCache.h`. The strongest project-level identifiers around this patch are `uint64_t`, `hash`, `_seed`, and `filterSeed`. Nearby tests or test-like files include `src/util/test/MetricTests.cpp`, `src/util/test/BinaryFuseTests.cpp`.

## Before/After Behavior

Before the patch, BinaryFuseFilter population used binary_fuse_murmur64(keys[i] + _seed), contain() used binary_fuse_mix_split(key, _seed), and construction retried population with an unbounded loop. After the patch, population and contain() use sip_hash24(..., _seed), LedgerKey inputs are hashed with SipHash24 using mInputSeed, and population retries are bounded to 10 attempts with comments tying failure to excessive hash collisions.

# Root Cause

The prior BinaryFuseFilter implementation used predictable non-SipHash mixing in collision-sensitive filter operations and allowed unbounded retry after population failure. The provided evidence supports this as insufficient DoS resistance, but not a demonstrated exploit by itself.

## Walkthrough

1. BinaryFuseFilter builds a filter from LedgerKey-derived inputs.

2. Before the change, population segment assignment used binary_fuse_murmur64(keys[i] + _seed).

3. Before the change, contain() used binary_fuse_mix_split(key, _seed) before deriving fingerprints and hash positions.

4. The constructor retried population in an unbounded for loop.

5. The patch adds sip_hash24(uint64_t key, binary_fuse_seed_t const& seed).

6. Population and contain() now use sip_hash24 with the filter seed.

7. Construction retries are capped at 10 attempts and tracked with a populated flag.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/util/BinaryFuseFilter.cpp | 19 | Hashes LedgerKey inputs with SipHash24 before building the filter. |
| src/util/BinaryFuseFilter.cpp | 25 | Bounds filter population retries after collision-related failures. |
| lib/binaryfusefilter.h | 31 | Introduces SipHash24 helper keyed by binary_fuse_seed_t. |
| lib/binaryfusefilter.h | 293 | Uses SipHash24 in contain() membership checks. |
| lib/binaryfusefilter.h | 368 | Uses SipHash24 during filter population segment assignment. |

## Code Snippets

## Snippet 1

Context: `src/util/BinaryFuseFilter.cpp:25` (changes a sensitive control or state-update path)

Before
```cpp
}

    for (size_t i = 0;; ++i)
    {
        //     auto filterSeed = mInputSeed;
        //     filterSeed[0] += i;
        //     if (mFilter.populate(hashes, filterSeed))
        //     {
```
After
```cpp
}

    // If too many hash collisions occur, population will fail. Retry with
    // a different seed. This is unlikely to happen once, and is statically
    // impossible to happen 10 times.
    bool populated = false;
    for (size_t i = 0; i < 10; ++i)
    {
```

## Snippet 2

Context: `lib/binaryfusefilter.h:31` (changes a sensitive control or state-update path)

Before
```c
***/
static inline uint64_t
binary_fuse_murmur64(uint64_t h)
{
    h ^= h >> 33;
    h *= UINT64_C(0xff51afd7ed558ccd);
    h ^= h >> 33;
    h *= UINT64_C(0xc4ceb9fe1a85ec53);
```
After
```c
***/
static inline uint64_t
sip_hash24(uint64_t key, binary_fuse_seed_t const& seed)
{
    SipHash24 hasher(seed.data());
    hasher.update(reinterpret_cast<unsigned char*>(&key), sizeof(key));
    return hasher.digest();
}
```

## Snippet 3

Context: `lib/binaryfusefilter.h:368` (changes signature or replay validation logic)

Before
```c
for (uint32_t i = 0; i < size; i++)
            {
                uint64_t hash = binary_fuse_murmur64(keys[i] + _seed);
                uint64_t segment_index = hash >> (64 - blockBits);
                while (reverseOrder[startPos[segment_index]] != 0)
```
After
```c
for (uint32_t i = 0; i < size; i++)
            {
                uint64_t hash = sip_hash24(keys[i], _seed);
                uint64_t segment_index = hash >> (64 - blockBits);
                while (reverseOrder[startPos[segment_index]] != 0)
```

## Snippet 4

Context: `lib/binaryfusefilter.h:293` (changes signature or replay validation logic)

Before
```c
{
        ZoneScoped;
        uint64_t hash = binary_fuse_mix_split(key, _seed);
        T f = binary_fuse_fingerprint(hash);
        binary_hashes_t hashes = hash_batch(hash);
```
After
```c
{
        ZoneScoped;
        uint64_t hash = sip_hash24(key, _seed);
        T f = binary_fuse_fingerprint(hash);
        binary_hashes_t hashes = hash_batch(hash);
```

# Fix Pattern

Replace predictable hashing in collision-sensitive data-structure paths with keyed SipHash24, and bound retry loops that handle collision-related construction failures.

## How It Was Fixed

The patch introduces a SipHash24 helper in lib/binaryfusefilter.h, switches BinaryFuseFilter population and contain() hashing to that helper, hashes LedgerKey inputs with SipHash24 in src/util/BinaryFuseFilter.cpp, and caps population retries at 10 attempts. Tests were updated, but their assertions are not included in the provided input.

# Why It Matters

1. Collision-heavy inputs can cause excessive work in hash-based structures.

2. Keyed hashing reduces predictability for chosen-input collision attempts.

3. Bounded retries prevent repeated population failure from becoming unbounded work.

4. The patch supports DoS hardening, not confidentiality, authentication, or asset-loss claims.

# Evidence Notes

The strongest evidence is the commit subject, "Siphash24 in BinaryFuseFilter for DOS protection", plus code changes in lib/binaryfusefilter.h replacing Murmur/mix-split hashing with SipHash24 and src/util/BinaryFuseFilter.cpp bounding collision-related retries. Remote reachability, production exploitability, and test assertions are not provided, so the finding should remain hardening/likely rather than confirmed vulnerability fix. Protocol security invariant: Collision-sensitive BinaryFuseFilter construction and lookup should use keyed, unpredictable hashing and bounded retry behavior so chosen or pathological inputs cannot force excessive collision handling work. Verification notes: Remote exploitability is not proven by the patch alone. The patch does not prove that the prior unbounded loop was practically reachable in production. No confidentiality, authentication, or key-recovery issue is shown. No consensus safety failure or asset-loss path is demonstrated. Tests are referenced but their exact assertions are not provided in the input. Confirmed by provided diff excerpts only. No external exploit path is shown. No test assertions are available in the input. No confidentiality, authentication, consensus, or asset-loss impact is supported. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `hash-collision-dos-hardening`
Final impact type: `denial-of-service`
Final tags: `dos-protection, hash-collision, siphash, bounded-retry, binary-fuse-filter`

The supplied evidence supports retaining this as security hardening. The commit subject explicitly says the SipHash24 change is for DoS protection, and the patch replaces predictable Murmur/mix-split hashing in BinaryFuseFilter population and lookup with keyed SipHash24 while also bounding a collision-related retry loop. The evidence does not prove a concrete exploitable production vulnerability, so security-hardening is more appropriate than security-fix.

## Security Evidence

1. Commit subject states: Siphash24 in BinaryFuseFilter for DOS protection.
2. Population hashing changes from binary_fuse_murmur64(keys[i] + _seed) to sip_hash24(keys[i], _seed).
3. Lookup hashing changes from binary_fuse_mix_split(key, _seed) to sip_hash24(key, _seed).
4. Constructor retry loop changes from unbounded to capped at 10 attempts with comments tying failure to excessive hash collisions.
5. LedgerKey inputs are hashed with SipHash24 using mInputSeed before filter construction.

## Missing Evidence

1. No exploit scenario or attacker-controlled input path is shown.
2. No production reachability analysis is provided.
3. No test assertions are included in the supplied input.
4. No evidence shows the prior unbounded loop was practically triggerable in deployed conditions.

## Claim Boundaries

1. Supports DoS hardening against hash-collision or pathological-input behavior.
2. Does not support confidentiality, authentication, key-recovery, consensus-safety, or asset-loss claims.
3. Does not prove a confirmed vulnerability fix from patch evidence alone.
4. Classification should remain likely security-hardening, not confirmed security-fix.
