---
case_id: case_20120901_3bd054748
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: high
source_quality: medium
date: 2012-09-01
source_refs:
  - git:3bd054748e0d7ae0eac1e113aa1c95325e039996
  - "src/NetworkOPs.cpp:608"
bug_class: consensus-proposal-duplicate-suppression-bypass
impact_type:
  - consensus-message-suppression
  - denial-of-service
tags:
  - blockchain-core
  - consensus
  - duplicate-suppression
  - malformed-message
  - message-identity
  - denial-of-service
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes duplicate suppression in `NetworkOPs::recvPropose`. Before the change, the preliminary duplicate key used only proposal sequence, current ledger ID, and public key. After the change, it includes proposal hash, proposal sequence, close time, public key, and signature. This matches the commit subject's stated vulnerability: a malformed proposal could fail validation while still being similar enough to suppress the real proposal as a duplicate.

## Observed Patch Facts

1. In `src/NetworkOPs.cpp`, the patch replaces `Serializer s(128);` with `Serializer s(256);`.

## Project Context

The changed code sits primarily in `src`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/Serializer.h`, `src/Serializer.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/Serializer.h`, `src/Serializer.cpp`. The strongest project-level identifiers around this patch are `add32`, `Serializer`, `addRaw`, and `preliminary`.

## Before/After Behavior

Before: `recvPropose` serialized `proposeSeq`, `getCurrentLedgerID()`, and `pubKey` and used `s.getSHA512Half()` with `theApp->isNew(...)` for duplicate suppression. After: the duplicate key serializes `proposeHash`, `proposeSeq`, `closeTime`, `pubKey`, and `signature`, making suppression depend on more of the received proposal's identity.

# Root Cause

The duplicate-suppression key for received ledger proposals was under-specified. It allowed an invalid or malformed proposal sharing the narrow keyed fields to consume the duplicate entry for a distinct valid proposal.

## Walkthrough

1. `NetworkOPs::recvPropose` receives proposal fields including `proposeSeq`, `proposeHash`, `closeTime`, `pubKey`, and `signature`.

2. The function computes a preliminary hash used to suppress duplicate proposals.

3. Before the fix, that hash used only `proposeSeq`, `getCurrentLedgerID()`, and `pubKey`.

4. The commit subject states that a malformed proposal could fail validity checks but still suppress the real proposal as a duplicate.

5. The patch expands the serialized duplicate key to include `proposeHash`, `closeTime`, and `signature`, while retaining `proposeSeq` and `pubKey`.

6. The duplicate check is therefore tied more closely to the actual received proposal rather than a narrower participant/context key.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/NetworkOPs.cpp | 608 | Builds the preliminary hash used to decide whether an incoming ledger proposal has already been seen and should be suppressed as a duplicate. |

## Code Snippets

## Snippet 1

Context: `src/NetworkOPs.cpp:608` (changes signature or replay validation logic)

Before
```cpp
// Get a preliminary hash to use to suppress duplicates
	Serializer s(128);
	s.add32(proposeSeq);
	s.add32(getCurrentLedgerID());
	s.addRaw(pubKey);
	if (!theApp->isNew(s.getSHA512Half()))
		return false;
```
After
```cpp
// Get a preliminary hash to use to suppress duplicates
	Serializer s(256);
	s.add256(proposeHash);
	s.add32(proposeSeq);
	s.add32(closeTime);
	s.addRaw(pubKey);
	s.addRaw(signature);
```

# Fix Pattern

Build replay-sensitive or duplicate-suppression keys from the full message identity needed to distinguish valid protocol messages from malformed variants, before allowing a message to suppress later processing.

## How It Was Fixed

In `src/NetworkOPs.cpp`, the patch changes the serializer from `Serializer s(128)` to `Serializer s(256)`, removes `getCurrentLedgerID()` from the preliminary duplicate key, and adds `proposeHash`, `closeTime`, and `signature` to the fields hashed for duplicate suppression.

# Why It Matters

1. Malformed proposals should not be able to suppress distinct valid proposals.

2. Consensus proposal handling depends on accurate message identity.

3. The evidence supports duplicate-suppression confusion, not signature forgery or arbitrary consensus control.

# Evidence Notes

Primary evidence is the focused diff in `src/NetworkOPs.cpp` around `NetworkOPs::recvPropose` and the explicit commit subject describing the vulnerability. The code evidence shows the duplicate-suppression hash changing from `proposeSeq`, current ledger ID, and `pubKey` to `proposeHash`, `proposeSeq`, `closeTime`, `pubKey`, and `signature`. Claims about cryptographic primitive failure, signature forgery, ledger compromise, or arbitrary consensus control are not supported. Protocol security invariant: Incoming ledger proposal duplicate suppression must key on the security-relevant identity of the received proposal so that a malformed proposal cannot mark a distinct valid proposal as already seen. Verification notes: The patch does not prove signature forgery or cryptographic primitive failure. The patch does not by itself prove successful ledger compromise. The evidence supports malformed proposal suppression of valid proposals, not arbitrary consensus control. No related tests are shown in the provided context. No related tests are shown in the supplied evidence. The vulnerability classification relies on both the explicit commit subject and the matching duplicate-key change. Helper or traced serializer files are supporting context only, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `consensus-proposal-duplicate-suppression-bypass`
Final impact type: `consensus-message-suppression, denial-of-service`
Final tags: `blockchain-core, consensus, duplicate-suppression, malformed-message, message-identity, denial-of-service`

The supplied evidence supports keeping this as a security fix. The commit subject explicitly describes a vulnerability where a malformed ledger proposal could suppress the real proposal as a duplicate, and the patch directly changes the duplicate-suppression key in `NetworkOPs::recvPropose` to include proposal hash, close time, public key, and signature. The strongest validated class is consensus/message duplicate-suppression confusion, not cryptographic primitive failure.

## Security Evidence

1. Commit subject explicitly calls the issue a vulnerability.
2. Subject describes attacker-observable proposal replay/mutation leading to suppression of the real proposal.
3. Patch changes the preliminary duplicate hash used before returning false for already-seen proposals.
4. Before key used only proposal sequence, current ledger ID, and public key.
5. After key includes proposal hash, proposal sequence, close time, public key, and signature.

## Missing Evidence

1. No tests are supplied showing the malformed-proposal scenario.
2. No surrounding validity-check code is supplied to prove the exact ordering of duplicate suppression versus validation.
3. No evidence proves ledger compromise, signature forgery, or arbitrary consensus control.

## Claim Boundaries

1. Validated only as malformed ledger proposal duplicate-suppression bypass.
2. Do not classify as cryptographic primitive weakness or signature verification bypass.
3. Impact should be limited to suppression/interference with consensus proposal handling.
4. The evidence supports a security fix because the commit message and patch behavior align.
