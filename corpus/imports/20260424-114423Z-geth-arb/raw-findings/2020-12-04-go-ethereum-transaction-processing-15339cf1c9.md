---
case_id: case_20201204_15339cf1c9
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2020-12-04
source_refs:
  - git:15339cf1c9af2b1242c2574869fa7afca1096cdf
  - "cmd/geth/testdata/vcheck/data2.json:1"
  - "cmd/geth/testdata/vcheck/data.json:1"
  - "cmd/geth/version_check.go:1"
  - "cmd/geth/version_check_test.go:1"
bug_class: advisory-feed-authentication
impact_type:
  - integrity
tags:
  - vulnerability-check
  - advisory-feed
  - signature-verification
  - feed-integrity
  - cmd-geth
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The commit adds a cmd/geth vulnerability/version-check mechanism with signed advisory-feed validation. The evidence supports security hardening around advisory-feed authenticity, not a direct fix for the CorruptedDAG mining flaw and not a transaction-processing or consensus vulnerability fix.

## Observed Patch Facts

1. In `cmd/geth/testdata/vcheck/data2.json`, the patch adds `"name": "CorruptedDAG",`.

2. In `cmd/geth/testdata/vcheck/data.json`, the patch adds `"name": "CorruptedDAG",`.

3. In `cmd/geth/version_check.go`, the patch adds `// Copyright 2020 The go-ethereum Authors`.

4. In `cmd/geth/version_check_test.go`, the patch adds `// Copyright 2020 The go-ethereum Authors`.

## Project Context

The changed code sits primarily in `cmd/geth/testdata/vcheck`, `cmd/geth/testdata`, `cmd/geth`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `cmd/geth/usage.go`, `cmd/geth/misccmd.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cmd/geth/usage.go`, `cmd/geth/main.go`. The strongest project-level identifiers around this patch are `ethereum`, `nodes`, `mining`, and `License`.

## Before/After Behavior

Before the commit, the provided evidence shows no existing cmd/geth vulnerability-check implementation or advisory-feed fixtures in the extracted before state. After the commit, version-check code and tests are added, command-side files are touched, and test fixtures include signed advisory JSON describing the historical CorruptedDAG issue. The commit body states that minisign/signify verification, multiple public keys, file:// feed support, CVE fields, and signature-failure diagnostics were added.

# Root Cause

No exploitable root cause is established from the supplied snippets. The security-relevant design concern is that a vulnerability advisory mechanism must not rely on unauthenticated metadata; the commit appears to add signature verification as part of introducing that mechanism.

## Walkthrough

1. cmd/geth/version_check.go and cmd/geth/version_check_test.go are added, but the visible snippets only show file headers.

2. The commit body explicitly describes implementing a vulnerability check and verifying the vulnerability feed with minisign.

3. Test fixtures under cmd/geth/testdata/vcheck add advisory JSON, signature files, and signing keys.

4. The advisory fixture references CorruptedDAG as feed content, including affected and fixed version metadata.

5. The supplied evidence does not show changes to mining, consensus, transaction validation, or mempool behavior.

6. The supported finding is advisory-feed integrity hardening for a new vulnerability-check feature.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| cmd/geth/version_check.go | 1 | implements vulnerability/version check logic and signed-feed validation |
| cmd/geth/main.go | 1 | wires the vulnerability check into geth command startup or CLI flow |
| cmd/geth/misccmd.go | 1 | exposes or supports the command-side vulnerability checking path |
| cmd/geth/testdata/vcheck/data.json | 1 | test advisory feed fixture containing a historical vulnerability entry |
| cmd/geth/testdata/vcheck/data2.json | 1 | alternate test advisory feed fixture |
| cmd/geth/version_check_test.go | 1 | tests parsing and signature verification behavior for vulnerability checks |

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

Add cryptographic authentication for externally supplied vulnerability advisory metadata and test the signed-feed handling with representative fixtures and keys.

## How It Was Fixed

The patch introduces cmd/geth vulnerability-check support, adds advisory-feed fixtures, and, according to the commit body and mapper, validates feed signatures with minisign/signify and supports multiple trusted public keys.

# Why It Matters

1. Helps prevent unauthenticated advisory metadata from being treated as authoritative.

2. Keeps vulnerability/version reporting tied to trusted signing keys.

3. Avoids conflating a referenced historical advisory with a direct fix for that vulnerability.

# Evidence Notes

The strongest evidence is the commit body and the added vcheck fixture files. The provided code excerpts for version_check.go and version_check_test.go only show headers, so detailed implementation behavior is not directly visible. Claims about transaction processing, consensus, validator logic, or fixing CorruptedDAG are unsupported by the supplied evidence. Protocol security invariant: No consensus, transaction-processing, mempool, validator, or network protocol invariant is shown. The grounded security invariant is local: geth's vulnerability advisory metadata should be authenticated before the vulnerability/version-check mechanism treats it as authoritative. Verification notes: Does not prove a remotely exploitable geth node vulnerability in this commit. Does not prove a transaction-processing or mempool validation bug. Does not fix the CorruptedDAG mining flaw; it references that issue as advisory feed data. Does not show consensus or validator logic changes despite heuristic flags. Does not prove that users were previously accepting a malicious feed, only that feed authentication was added for this mechanism. No direct vulnerable code path is shown in the supplied snippets. No proof is provided that users previously accepted malicious feeds. No protocol-level behavior change is established. Security-hardening classification is based mainly on commit text and added signed-feed fixtures. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `advisory-feed-authentication`
Final impact type: `integrity`
Final tags: `vulnerability-check, advisory-feed, signature-verification, feed-integrity, cmd-geth`

The supplied evidence supports retaining this as security hardening, not as a direct security bug fix. The commit explicitly adds a vulnerability check and minisign/signify verification for a vulnerability feed, with public keys, signatures, and tests. However, the visible code snippets do not show the actual verification implementation or any prior vulnerable behavior, and the CorruptedDAG content appears to be advisory fixture data rather than the bug fixed by this commit. The original transaction-processing, consensus, and liveness framing is misleading.

## Security Evidence

1. Commit body says cmd/geth implements a vulnerability check.
2. Commit body says minisign is used to verify the vulnerability feed.
3. Commit body mentions multiple public files/keys, signature tests, and signature failure diagnostics.
4. Changed files include vulnerability-check test fixtures, signature files, and public/private signing key fixtures.
5. Added advisory fixture data references a known GETH security advisory.

## Missing Evidence

1. Visible snippets from version_check.go and version_check_test.go only show license headers, not verification logic.
2. No before-state shows an unauthenticated feed being trusted by existing production code.
3. No code evidence shows a transaction-processing, consensus, validator, or mining logic fix in this commit.
4. No exploit path or concrete vulnerability in the newly added checker is demonstrated.

## Claim Boundaries

1. Validate only advisory-feed authenticity hardening for the new cmd/geth vulnerability-check mechanism.
2. Do not classify this as a fix for CorruptedDAG itself; the advisory appears to be test/feed content.
3. Do not claim transaction-processing, consensus, validator, or liveness impact from the supplied patch evidence.
4. Do not claim a concrete exploitable vulnerability was fixed without implementation snippets showing the vulnerable behavior and remediation.
