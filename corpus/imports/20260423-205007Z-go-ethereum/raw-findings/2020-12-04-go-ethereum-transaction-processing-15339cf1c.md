---
case_id: case_20201204_15339cf1c
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2020-12-04
source_refs:
  - git:15339cf1c9af2b1242c2574869fa7afca1096cdf
  - "cmd/geth/testdata/vcheck/data2.json:1"
  - "cmd/geth/testdata/vcheck/data.json:1"
  - "cmd/geth/version_check.go:1"
  - "cmd/geth/version_check_test.go:1"
bug_class: signed-vulnerability-advisory-check
impact_type:
  - advisory-integrity
  - vulnerability-detection
confidence: medium
tags:
  - vulnerability-check
  - signed-advisory-feed
  - signature-verification
  - cli-hardening
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The commit adds a cmd/geth vulnerability-check mechanism with signed advisory-feed verification and tests. The evidence supports classifying this as security hardening for advisory authenticity and version-based warning behavior, not as a direct fix for the CorruptedDAG mining flaw or any transaction-processing bug.

## Observed Patch Facts

1. In `cmd/geth/testdata/vcheck/data2.json`, the patch adds `"name": "CorruptedDAG",`.

2. In `cmd/geth/testdata/vcheck/data.json`, the patch adds `"name": "CorruptedDAG",`.

3. In `cmd/geth/version_check.go`, the patch adds `// Copyright 2020 The go-ethereum Authors`.

4. In `cmd/geth/version_check_test.go`, the patch adds `// Copyright 2020 The go-ethereum Authors`.

## Project Context

The changed code sits primarily in `cmd/geth/testdata/vcheck`, `cmd/geth/testdata`, `cmd/geth`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `cmd/geth/usage.go`, `cmd/geth/misccmd.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cmd/geth/usage.go`, `cmd/geth/main.go`. The strongest project-level identifiers around this patch are `ethereum`, `nodes`, `mining`, and `License`.

## Before/After Behavior

Before the commit, the provided evidence shows no existing vulnerability-check implementation or signed advisory-feed fixtures. After the commit, cmd/geth gains version_check.go and tests, CLI integration files are touched, advisory JSON fixtures include the CorruptedDAG metadata, and minisign/signify key and signature fixtures are added for signed-feed verification behavior.

# Root Cause

The supported root issue is a missing advisory-check path that can authenticate vulnerability feed contents before using them for local version warnings. The evidence does not establish that an exploitable feed-spoofing vulnerability existed before the patch, nor that this commit fixes the underlying CorruptedDAG index-overflow mining issue.

## Walkthrough

1. The commit subject and body state that cmd/geth implements a vulnerability check and uses minisign to verify the vulnerability feed.

2. New files include cmd/geth/version_check.go and cmd/geth/version_check_test.go, indicating a new implementation and test path for version/advisory checking.

3. Test advisory JSON files include a CorruptedDAG advisory with introduced, fixed, and published metadata plus links to the prior security release and fix.

4. The added testdata includes minisign/signify public keys, secret keys, and detached signatures, supporting tests around signed-feed verification.

5. The commit body also states support for multiple public signing files, file:// URLs, CVE fields, and better key ID printing on signature failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| cmd/geth/version_check.go | 1 | new implementation for vulnerability feed retrieval, version matching, and signed-feed verification |
| cmd/geth/misccmd.go | 1 | cmd/geth integration point for invoking miscellaneous CLI functionality including the vulnerability check |
| cmd/geth/main.go | 1 | geth command entrypoint where the checker may be wired into CLI startup or commands |
| cmd/geth/testdata/vcheck/data.json | 1 | test vulnerability feed containing CorruptedDAG advisory metadata |
| cmd/geth/testdata/vcheck/data2.json | 1 | alternate test vulnerability feed for version-check behavior |
| cmd/geth/version_check_test.go | 1 | tests for vulnerability check and signature-verification behavior |

## Code Snippets

## Snippet 1

Context: `cmd/geth/testdata/vcheck/data2.json:1` (changes a consensus- or validator-sensitive branch)

Before
```text
(no before snippet captured)
```
After
```text
[
  {
    "name": "CorruptedDAG",
    "uid": "GETH-2020-01",
    "summary": "Mining nodes will generate erroneous PoW on epochs > `385`.",
    "description": "A mining flaw could cause miners to erroneously calculate PoW, due to an index overflow, if DAG size is exceeding the maximum 32 bit unsigned value.\n\nThis occurred on the ETC chain on 2020-11-06. This is likely to trigger for ETH mainnet around block `11550000`/epoch `385`, slated to occur early January 2021.\n\nThis issue is relevant only for miners, non-mining nodes are unaffected, since non-mining nodes use a smaller verification cache instead of a full DAG.",
    "links": [
      "https://github.com/ethereum/go-ethereum/pull/21793",
```

## Snippet 2

Context: `cmd/geth/testdata/vcheck/data.json:1` (changes a consensus- or validator-sensitive branch)

Before
```text
(no before snippet captured)
```
After
```text
[
  {
    "name": "CorruptedDAG",
    "uid": "GETH-2020-01",
    "summary": "Mining nodes will generate erroneous PoW on epochs > `385`.",
    "description": "A mining flaw could cause miners to erroneously calculate PoW, due to an index overflow, if DAG size is exceeding the maximum 32 bit unsigned value.\n\nThis occurred on the ETC chain on 2020-11-06. This is likely to trigger for ETH mainnet around block `11550000`/epoch `385`, slated to occur early January 2021.\n\nThis issue is relevant only for miners, non-mining nodes are unaffected, since non-mining nodes use a smaller verification cache instead of a full DAG.",
    "links": [
      "https://github.com/ethereum/go-ethereum/pull/21793",
```

## Snippet 3

Context: `cmd/geth/version_check.go:1` (changes signature or replay validation logic)

Before
```go
(no before snippet captured)
```
After
```go
// Copyright 2020 The go-ethereum Authors
// This file is part of go-ethereum.
//
// go-ethereum is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
```

## Snippet 4

Context: `cmd/geth/version_check_test.go:1` (changes a sensitive control or state-update path)

Before
```go
(no before snippet captured)
```
After
```go
// Copyright 2020 The go-ethereum Authors
// This file is part of go-ethereum.
//
// go-ethereum is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
```

# Fix Pattern

Introduce an authenticated vulnerability advisory-feed checker: load advisory metadata, verify detached signatures against trusted signing keys, parse affected/fixed version ranges, and warn only when the local version matches trusted advisory data.

## How It Was Fixed

The patch adds the cmd/geth version-check implementation, wires it into geth command files, adds signed advisory feed fixtures, adds minisign/signify verification test material, and adds tests around the new vulnerability-check behavior. The CorruptedDAG advisory is used as feed content, but the mining bug itself was not fixed by this commit.

# Why It Matters

1. Reduces the risk of unauthenticated advisory data driving vulnerability warnings.

2. Lets users be warned when their local geth version matches signed metadata for a known vulnerable release.

3. Keeps the security impact scoped to advisory authenticity and version checking.

4. Does not demonstrate a consensus, mempool, transaction-processing, crash, or RCE fix.

# Evidence Notes

The draft correctly rejects the heuristic claim about transaction-processing panic hardening. Supported evidence comes mainly from the commit body, file list, advisory test JSON, and signature/key fixture names. The provided code excerpts for version_check.go and version_check_test.go show only license headers, so detailed implementation behavior should be treated as inferred from file names and commit text rather than directly proven by code hunks. Protocol security invariant: The geth vulnerability checker should rely only on advisory feed data authenticated by trusted signing keys before using that data to warn about locally vulnerable versions. Verification notes: Does not prove this commit fixes the CorruptedDAG mining/index-overflow vulnerability itself. Does not prove a prior vulnerability-feed spoofing exploit existed in released geth versions. Does not support classifying this as transaction-processing, mempool, or consensus-validation hardening. Does not prove remote code execution, node crash, or chain consensus failure from the vulnerability checker path. Test advisory data references a real prior issue, but this patch is the advisory-check mechanism around it. No direct code body for version_check.go was provided beyond the license header. No evidence shows this commit repairing the CorruptedDAG mining/index-overflow vulnerability itself. No evidence proves a previously exploitable vulnerability-feed spoofing flaw in released geth versions. Classification is security-hardening rather than vulnerability-fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signed-vulnerability-advisory-check`
Final impact type: `advisory-integrity, vulnerability-detection`
Final confidence: `medium`
Final tags: `vulnerability-check, signed-advisory-feed, signature-verification, cli-hardening, security-hardening`

The evidence supports retaining this as security hardening, not as a direct vulnerability fix. The commit explicitly adds a cmd/geth vulnerability check and minisign/signify-style verification for a vulnerability feed, with signed feed fixtures and trusted public-key material. However, the supplied code excerpts do not show the implementation body, and the CorruptedDAG advisory in testdata refers to a prior mining flaw rather than a bug fixed by this commit.

## Security Evidence

1. Commit subject states cmd/geth implements a vulnerability check.
2. Commit body states minisign is used to verify the vulnerability feed.
3. File list includes version_check.go, version_check_test.go, public keys, secret keys, detached signatures, and vulnerability-feed testdata.
4. Advisory JSON fixture contains a real security advisory identifier, affected/fixed versions, publication date, and links to a prior security release.

## Missing Evidence

1. No implementation body for version_check.go is provided beyond the license header.
2. No code excerpt demonstrates exactly how signature verification is enforced before using feed contents.
3. No evidence shows this commit fixes the underlying CorruptedDAG mining/index-overflow flaw.
4. No evidence proves a previously exploitable feed-spoofing vulnerability existed in released geth versions.

## Claim Boundaries

1. Classify as security-hardening for authenticated vulnerability advisory checking only.
2. Do not classify as a transaction-processing, mempool, or consensus-validation fix.
3. Do not claim this commit fixes CorruptedDAG itself.
4. Do not claim concrete exploitability such as RCE, chain split, node crash, or remote consensus failure from the supplied evidence.
