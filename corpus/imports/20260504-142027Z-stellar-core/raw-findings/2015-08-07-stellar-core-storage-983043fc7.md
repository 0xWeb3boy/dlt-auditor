---
case_id: case_20150807_983043fc7
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2015-08-07
source_refs:
  - git:983043fc7cd20b3e6738add89181eea273c012f1
  - "src/main/Config.cpp:66"
  - "src/main/Config.cpp:469"
  - "src/main/Config.h:85"
  - "src/main/Config.cpp:122"
bug_class: unsafe-consensus-configuration
impact_type:
  - consensus-integrity
  - byzantine-fault-tolerance
confidence: medium
tags:
  - blockchain-core
  - consensus
  - scp
  - quorum
  - configuration
  - validator
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Stellar SCP quorum configuration parsing and validation. It replaces a raw `THRESHOLD` value with bounded `THRESHOLD_PERCENT`, derives `qset.threshold` from the number of validators and inner sets, and adds `FAILURE_SAFETY` / `UNSAFE_QUORUM` configuration fields plus a visible validation check for `FAILURE_SAFETY == 0` without unsafe opt-in. The evidence supports security-relevant configuration hardening, but not a confirmed vulnerability fix.

## Observed Patch Facts

1. In `src/main/Config.cpp`, the patch replaces `if (item.first == "THRESHOLD")` with `int thresholdPercent = 67;`.

2. In `src/main/Config.cpp`, the patch adds `void`.

3. In `src/main/Config.h`, the patch replaces `uint32_t LEDGER_PROTOCOL_VERSION;` with `// This is the number of failures you want to be able to tolerate.`.

4. In `src/main/Config.cpp`, the patch replaces `(qset.validators.empty() && qset.innerSets.empty()))` with `qset.threshold = ceil( ((qset.validators.size() + qset.innerSets.size())*thresholdPer...`.

## Project Context

The changed code sits primarily in `src/main`, which anchors the finding in the `storage` area of the project. Historical context from `src/main/ApplicationImpl.cpp`, `src/main/test.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/main/ApplicationImpl.cpp`, `src/main/test.cpp`. The strongest project-level identifiers around this patch are `std::invalid_argument`, `qset`, `threshold`, and `item`. Nearby tests or test-like files include `src/main/fuzz.h`, `src/main/fuzz.cpp`.

## Before/After Behavior

Before the patch, `loadQset` parsed `THRESHOLD` and assigned a positive numeric value directly to `qset.threshold`. After the patch, it parses `THRESHOLD_PERCENT`, restricts it to 1..100, defaults it to 67, and computes `qset.threshold` from quorum-set cardinality. The patch also adds configuration fields for failure safety and unsafe quorum operation, and introduces a visible validation check rejecting `FAILURE_SAFETY == 0` unless `UNSAFE_QUORUM` is true.

# Root Cause

The configuration path allowed quorum thresholds to be expressed as detached absolute values, and the provided evidence shows limited added validation for unsafe quorum-related settings. The evidence does not show attacker control, remote exploitability, or a protocol implementation flaw independent of operator configuration.

## Walkthrough

1. `src/main/Config.cpp` previously recognized `THRESHOLD` and assigned the parsed value directly to `qset.threshold`.

2. The patch changes the input to `THRESHOLD_PERCENT` and rejects percentages outside 1..100.

3. The effective quorum threshold is calculated as `ceil(((validators + innerSets) * thresholdPercent) / 100.0)`.

4. `src/main/Config.h` adds `FAILURE_SAFETY` and `UNSAFE_QUORUM` fields with comments describing quorum safety intent.

5. `Config::validateConfig()` is added with a visible check that rejects `FAILURE_SAFETY == 0` unless unsafe quorum mode is explicitly enabled.

6. The provided trace shows application startup consumes `QUORUM_SET`, but does not by itself prove a vulnerability or exploit path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/main/Config.cpp | 66 | Parses quorum-set threshold configuration as THRESHOLD_PERCENT with default 67 and validates it is within 1..100. |
| src/main/Config.cpp | 122 | Derives qset.threshold from the number of validators and inner sets using the configured percentage. |
| src/main/Config.cpp | 469 | Adds Config::validateConfig startup sanity checks for unsafe quorum and failure-safety settings. |
| src/main/Config.h | 85 | Adds FAILURE_SAFETY and UNSAFE_QUORUM configuration fields documenting the intended Byzantine-failure tolerance invariant. |
| src/main/ApplicationImpl.cpp | 205 | Consumes the configured quorum set during application startup and rejects an unconfigured quorum threshold. |

## Code Snippets

## Snippet 1

Context: `src/main/Config.cpp:66` (changes an authorization or privilege gate)

Before
```cpp
}

    qset.threshold = 0;

    for (auto& item : *group)
    {
        if (item.first == "THRESHOLD")
        {
```
After
```cpp
}

    int thresholdPercent = 67;
    qset.threshold = 0;

    for (auto& item : *group)
    {
        if (item.first == "THRESHOLD_PERCENT")
```

## Snippet 2

Context: `src/main/Config.cpp:469` (changes an authorization or privilege gate)

Before
```cpp
}
}
}
```
After
```cpp
}
}

void 
Config::validateConfig()
{
    if(FAILURE_SAFETY == 0 && UNSAFE_QUORUM == false)
    {
```

## Snippet 3

Context: `src/main/Config.h:85` (changes a sensitive control or state-update path)

Before
```c
bool BREAK_ASIO_LOOP_FOR_FAST_TESTS;

    uint32_t LEDGER_PROTOCOL_VERSION;
    uint32_t OVERLAY_PROTOCOL_VERSION;
```
After
```c
bool BREAK_ASIO_LOOP_FOR_FAST_TESTS;

    // This is the number of failures you want to be able to tolerate.
    // You will need at least 3f+1 nodes in your quorum set.
    // If you don't have enough in your quorum set to tolerate the level you 
    //  set here stellar-core won't run.
    uint32_t FAILURE_SAFETY;
```

## Snippet 4

Context: `src/main/Config.cpp:122` (changes an authorization or privilege gate)

Before
```cpp
}
    }
    if (qset.threshold == 0 ||
        (qset.validators.empty() && qset.innerSets.empty()))
```
After
```cpp
}
    }

    qset.threshold = ceil( ((qset.validators.size() + qset.innerSets.size())*thresholdPercent) / 100.0);

    LOG(INFO) << qset.threshold;

    if (qset.threshold == 0 ||
```

# Fix Pattern

Convert raw consensus configuration into bounded, derived values and add startup-style sanity checks for unsafe operator-selected settings.

## How It Was Fixed

The patch bounds the quorum threshold percentage, derives the numeric threshold from the configured quorum-set size, adds explicit configuration knobs for failure safety and unsafe quorum operation, and adds validation logic for at least one unsafe setting combination.

# Why It Matters

1. Reduces risk of accidental unsafe SCP quorum setup.

2. Makes unsafe quorum operation more explicit.

3. Keeps threshold values tied to quorum-set size.

4. Does not establish attacker exploitability from the provided evidence.

# Evidence Notes

Grounded evidence comes from `src/main/Config.cpp` changes to `loadQset`, the derived `qset.threshold` calculation, the added `Config::validateConfig()` snippet, `src/main/Config.h` fields, and traced startup use of `QUORUM_SET`. Unsupported claims removed: storage/state-corruption classification, privilege-check bypass, remote exploitability, attacker-controlled config modification, and a fully proven Byzantine-failure invariant beyond the visible checks. Protocol security invariant: A node's SCP quorum configuration should avoid trivially unsafe threshold settings unless the operator explicitly opts into unsafe operation. The provided evidence supports bounds-checking and derived quorum threshold calculation, but does not fully establish a concrete vulnerability or exploit path. Verification notes: The patch does not prove remote exploitability. The patch does not show an attacker can modify another node's config. The patch does not prove a consensus algorithm implementation flaw independent of configuration. The evidence does not support classifying this as storage state corruption. The evidence supports startup hardening against unsafe SCP configuration, not a demonstrated privilege-check bypass. No evidence proves remote attacker control of the affected configuration. No evidence proves a consensus algorithm flaw independent of configuration. The patch is security-relevant hardening, but the vulnerability thesis is not established enough to keep as a confirmed security-fix corpus item. The provided excerpt does not show the full `validateConfig()` body or its call site. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unsafe-consensus-configuration`
Final impact type: `consensus-integrity, byzantine-fault-tolerance`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, scp, quorum, configuration, validator, security-hardening`

The patch evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. It tightens Stellar SCP quorum setup by replacing raw absolute thresholds with bounded percentage-based thresholds, deriving the effective threshold from quorum-set size, and rejecting an explicitly unsafe failure-safety configuration unless an unsafe opt-in is set. The original storage/state-corruption/database framing is not supported by the supplied evidence.

## Security Evidence

1. SCP quorum threshold configuration changes from raw THRESHOLD to bounded THRESHOLD_PERCENT.
2. THRESHOLD_PERCENT is constrained to 1..100 before deriving qset.threshold.
3. qset.threshold is computed from validator and inner-set count, tying threshold to quorum-set size.
4. Config adds FAILURE_SAFETY and UNSAFE_QUORUM fields with comments about Byzantine failure tolerance.
5. validateConfig rejects FAILURE_SAFETY == 0 unless UNSAFE_QUORUM is explicitly true.
6. The thrown error string labels the rejected configuration as SCP unsafe.

## Missing Evidence

1. No evidence that an attacker can modify another node's configuration.
2. No concrete exploit path or demonstrated consensus failure is shown.
3. No evidence supports storage, database, or state-corruption classification.
4. The provided snippets do not prove a protocol implementation flaw independent of operator configuration.

## Claim Boundaries

1. Classify as security hardening for unsafe SCP quorum configuration checks.
2. Do not classify as a confirmed exploitable security fix.
3. Do not claim remote attacker control or privilege bypass.
4. Do not retain the storage/state-corruption/database framing.
5. Impact should be limited to consensus/quorum safety and Byzantine-fault-tolerance configuration.
