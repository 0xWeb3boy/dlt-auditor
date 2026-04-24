---
case_id: case_20201204_15339cf1c
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2020-12-04
source_refs:
  - git:15339cf1c9af2b1242c2574869fa7afca1096cdf
  - "cmd/geth/testdata/vcheck/data2.json:1"
  - "cmd/geth/testdata/vcheck/data.json:1"
  - "cmd/geth/version_check.go:1"
  - "cmd/geth/version_check_test.go:1"
bug_class: unsigned-advisory-feed
impact_type:
  - integrity
confidence: medium
tags:
  - signature-verification
  - security-metadata
  - cli-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports that this commit adds a `cmd/geth` vulnerability/version check and includes signed advisory-feed handling with Minisign/Signify test material. It does not support a stronger claim that the commit fixes a proven exploitable vulnerability in existing code. The `CorruptedDAG` content in the JSON files is advisory data consumed by the checker, not the bug being fixed here.

## Observed Patch Facts

1. In `cmd/geth/testdata/vcheck/data2.json`, the patch adds `"name": "CorruptedDAG",`.

2. In `cmd/geth/testdata/vcheck/data.json`, the patch adds `"name": "CorruptedDAG",`.

3. In `cmd/geth/version_check.go`, the patch adds `// Copyright 2020 The go-ethereum Authors`.

4. In `cmd/geth/version_check_test.go`, the patch adds `// Copyright 2020 The go-ethereum Authors`.

## Project Context

The changed code sits primarily in `cmd/geth/testdata/vcheck`, `cmd/geth/testdata`, `cmd/geth`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `cmd/geth/usage.go`, `cmd/geth/misccmd.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cmd/geth/usage.go`, `cmd/geth/main.go`. The strongest project-level identifiers around this patch are `ethereum`, `nodes`, `mining`, and `License`.

## Before/After Behavior

Before the patch, the provided evidence does not show an existing `cmd/geth` vulnerability-check implementation or any prior unsigned advisory-feed path. After the patch, the tree includes `cmd/geth/version_check.go`, `cmd/geth/version_check_test.go`, advisory JSON fixtures, detached signature fixtures, and public-key fixtures, and the commit message says the checker verifies the feed with Minisign, supports multiple public-key files, and supports `file://` URLs.

# Root Cause

Not established by the provided evidence. At most, the commit shows that advisory-feed authenticity was implemented or strengthened in the new checker. The evidence does not prove that older code accepted unauthenticated advisory data or that a concrete security bug existed before this commit.

## Walkthrough

1. The commit subject and body describe a new `cmd/geth` vulnerability check and explicitly mention verifying the vulnerability feed with Minisign.

2. New files include `cmd/geth/version_check.go` and `cmd/geth/version_check_test.go`, which supports that a checker and tests were added in this area.

3. New testdata includes advisory JSON plus detached signatures and public keys, which supports that signed advisory content is part of the intended behavior.

4. The JSON fixture content describes `CorruptedDAG`, but that is evidence of advisory payload contents, not evidence that this commit fixes the mining flaw itself.

5. The provided snippets from `version_check.go` and the test file only show file headers, so detailed behavioral claims about old vs. new runtime handling are not directly proven from code excerpts.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| cmd/geth/version_check.go | 1 | Implements vulnerability/version feed handling and signature verification logic for advisory data. |
| cmd/geth/version_check_test.go | 1 | Exercises feed parsing and Minisign/Signify verification behavior. |
| cmd/geth/testdata/vcheck/data.json | 1 | Fixture advisory payload used as signed vulnerability-feed input. |
| cmd/geth/testdata/vcheck/data2.json | 1 | Additional fixture advisory payload covering vulnerability metadata such as UID/CVE/version ranges. |

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

Add signature verification and trusted-key material around externally supplied security metadata as part of an advisory-check feature, with tests and support code for signer/key handling.

## How It Was Fixed

The patch appears to introduce a vulnerability/version checker in `cmd/geth`, add signed advisory fixtures and trusted public keys for testing, and wire the checker to verify advisory data with Minisign/Signify-related support. It also adds support features called out in the commit message such as multiple public-key files and `file://` URLs.

# Why It Matters

1. Authenticated advisory data is safer than unauthenticated advisory data if the CLI consumes external security metadata.

2. The evidence separates advisory reporting from the underlying mining flaw described in the fixture payloads.

3. Tests, detached signatures, and public keys suggest deliberate integrity checks rather than a direct runtime bug fix in mining or consensus code.

# Evidence Notes

The strongest grounded evidence is the commit message plus the added file set under `cmd/geth` and `cmd/geth/testdata/vcheck`. The visible JSON snippets prove the checker's fixtures carry vulnerability metadata about `CorruptedDAG`. They do not prove the mining defect is fixed here. The visible excerpts from `version_check.go` and `version_check_test.go` are only license headers, so claims about exact code behavior beyond the commit message and filenames should be treated cautiously. The evidence does not establish a prior exploitable unsigned-feed state in released code. Protocol security invariant: If `geth` consumes external vulnerability/version advisory data, that metadata should be authenticated with trusted signing keys before it influences user-visible security status. The provided evidence only shows this invariant being implemented around a new or newly added checker; it does not establish a previously vulnerable production path. Verification notes: The patch does not fix the underlying CorruptedDAG mining defect; it adds detection/reporting for known vulnerabilities. The evidence does not prove prior real-world exploitability of an unsigned advisory feed. The evidence does not support claims about transaction-processing, consensus, or validator-path bugs. The patch shows authenticity checks for advisory metadata, not confidentiality or privilege-boundary changes. Review the actual diff in `cmd/geth/version_check.go` to determine whether signature verification was added to an existing path or introduced with a brand-new feature. Do not classify this as a confirmed security fix for `CorruptedDAG`; the fixture data only shows what the checker reports. If stronger classification is needed, require code evidence that an earlier implementation consumed advisory data without authentication. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unsigned-advisory-feed`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `signature-verification, security-metadata, cli-hardening`

The supplied evidence does not show a direct fix for the underlying CorruptedDAG vulnerability, but it does support that this commit adds or strengthens authentication for externally supplied vulnerability metadata in `cmd/geth` by verifying the advisory feed with Minisign/Signify and trusted public keys. That is security-relevant hardening of a security-sensitive update/advisory path, not a proven exploitable bug fix in consensus or transaction processing.

## Security Evidence

1. Commit body explicitly says the vulnerability feed is verified with Minisign.
2. New files include `version_check.go`, tests, signature fixtures, and public-key fixtures, consistent with signed-feed verification.
3. Commit body mentions support for multiple public-key files and improved signature-failure reporting, which indicates trust-validation behavior.
4. The added JSON files are advisory feed fixtures, showing the feature consumes security metadata rather than fixing the referenced mining flaw itself.

## Missing Evidence

1. No behavioral code excerpt from `version_check.go` shows exactly how verification is enforced.
2. No evidence shows a pre-existing production path that accepted unsigned or untrusted advisory data.
3. No evidence shows exploitation, impact, or a concrete vulnerability in existing runtime logic.

## Claim Boundaries

1. Do not classify this as a fix for the CorruptedDAG mining flaw described in the fixture data.
2. Do not claim consensus, transaction-processing, or validator-path security impact from the provided patch evidence.
3. The strongest supported claim is hardening of advisory-feed authenticity checks in a new or newly expanded vulnerability-check feature.
