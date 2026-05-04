---
case_id: case_20150601_a0bd68890
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2015-06-01
source_refs:
  - git:a0bd68890dd888c5c50d8882ad3339d4c068311f
  - "src/scp/SCPTests.cpp:131"
  - "src/scp/Node.cpp:65"
  - "src/scp/SCPTests.cpp:371"
  - "src/scp/SCPTests.cpp:428"
bug_class: consensus-vblocking-threshold-off-by-one
impact_type:
  - consensus-correctness
  - quorum-classification
confidence: medium
tags:
  - blockchain-core
  - consensus
  - scp
  - quorum
  - vblocking
  - off-by-one
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Commit a0bd68890 fixes a focused off-by-one error in SCP v-blocking classification. Node::isVBlocking changed its initial remaining-blocking count from N - T to N - T + 1, and SCP tests were updated around v-blocking/quorum behavior and downstream envelope counts. The evidence supports a consensus predicate correctness fix with likely security relevance, but it does not prove a concrete exploit or network-wide consensus failure.

## Observed Patch Facts

1. In `src/scp/SCPTests.cpp`, the patch replaces `TEST_CASE("protocol core4", "[scp]")` with `TEST_CASE("vblocking and quorum", "[scp]")`.

2. In `src/scp/Node.cpp`, the patch replaces `int leftTillBlock = (int) ((qset.validators.size() + qset.innerSets.size()) - qset.th...` with `int leftTillBlock = (int) ((1+qset.validators.size() + qset.innerSets.size()) - qset....`.

3. In `src/scp/SCPTests.cpp`, the patch replaces `REQUIRE(scp.mEnvs.size() == 3);` with `REQUIRE(scp.mEnvs.size() == 1);`.

4. In `src/scp/SCPTests.cpp`, the patch replaces `REQUIRE(scp.mEnvs.size() == 2);` with `REQUIRE(scp.mEnvs.size() == 1);`.

## Project Context

The changed code sits primarily in `src/scp`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/scp/SCP.h`, `src/scp/SCP.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/scp/SCP.h`, `src/scp/SCP.cpp`. The strongest project-level identifiers around this patch are `size`, `qset`, `const`, and `receiveEnvelope`.

## Before/After Behavior

Before the patch, Node::isVBlocking initialized leftTillBlock as validators plus innerSets minus threshold, which corresponds to N - T. After the patch, it initializes leftTillBlock as one plus validators plus innerSets minus threshold, corresponding to N - T + 1. Tests in SCPTests.cpp were retitled or added for v-blocking/quorum behavior and adjusted expected mEnvs counts after receiveEnvelope.

# Root Cause

An off-by-one error in the recursive SCP v-blocking predicate caused the implementation to use N - T where the mapper-provided quorum invariant requires N - T + 1.

## Walkthrough

1. Node.h declares isVBlocking beside hasQuorum, placing it in SCP quorum/blocking logic.

2. Node.cpp computes leftTillBlock at the start of Node::isVBlocking before iterating validators and inner quorum sets.

3. Before the fix, leftTillBlock omitted the +1 in the blocking threshold calculation.

4. The patch adds the +1, changing the required count from N - T to N - T + 1.

5. SCPTests.cpp adds or retitles v-blocking/quorum coverage and updates receiveEnvelope envelope-count expectations.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/scp/Node.cpp | 65 | Fixes the v-blocking threshold calculation for validators and inner quorum sets. |
| src/scp/Node.h | 19 | Declares the recursive hasQuorum/isVBlocking consensus predicates on Node. |
| src/scp/SCPTests.cpp | 131 | Adds or retitles tests around v-blocking and quorum behavior. |
| src/scp/SCPTests.cpp | 371 | Updates expected SCP envelope behavior after corrected blocking/quorum classification. |
| src/scp/SCPTests.cpp | 428 | Updates prepared-message expectations under the corrected v-blocking predicate. |

## Code Snippets

## Snippet 1

Context: `src/scp/SCPTests.cpp:131` (changes an authorization or privilege gate)

Before
```cpp
const Value X##Value = xdr::xdr_to_opaque(X##ValueHash);

TEST_CASE("protocol core4", "[scp]")
{
```
After
```cpp
const Value X##Value = xdr::xdr_to_opaque(X##ValueHash);

TEST_CASE("vblocking and quorum", "[scp]")
{
    class TestNode : public Node
    {
    public:
        TestNode() : Node(uint256(), nullptr)
```

## Snippet 2

Context: `src/scp/Node.cpp:65` (changes an authorization or privilege gate)

Before
```cpp
Node::isVBlocking(SCPQuorumSet const& qset, std::vector<uint256> const& nodeSet)
{
    int leftTillBlock = (int) ((qset.validators.size() + qset.innerSets.size()) - qset.threshold);

    for(auto const &validator : qset.validators)
```
After
```cpp
Node::isVBlocking(SCPQuorumSet const& qset, std::vector<uint256> const& nodeSet)
{
    int leftTillBlock = (int) ((1+qset.validators.size() + qset.innerSets.size()) - qset.threshold);

    for(auto const &validator : qset.validators)
```

## Snippet 3

Context: `src/scp/SCPTests.cpp:371` (changes the branch that decides whether execution stops or continues)

Before
```cpp
scp.receiveEnvelope(prepared1);
        REQUIRE(scp.mEnvs.size() == 3);
        REQUIRE(scp.mHeardFromQuorums[0].size() == 0);
        scp.receiveEnvelope(prepared2);
```
After
```cpp
scp.receiveEnvelope(prepared1);
        REQUIRE(scp.mEnvs.size() == 1);
        REQUIRE(scp.mHeardFromQuorums[0].size() == 0);
        scp.receiveEnvelope(prepared2);
```

## Snippet 4

Context: `src/scp/SCPTests.cpp:428` (changes the branch that decides whether execution stops or continues)

Before
```cpp
scp.receiveEnvelope(prepared1);
        REQUIRE(scp.mEnvs.size() == 2);

        scp.receiveEnvelope(prepared2);
```
After
```cpp
scp.receiveEnvelope(prepared1);
        REQUIRE(scp.mEnvs.size() == 1);

        scp.receiveEnvelope(prepared2);
```

# Fix Pattern

Correct threshold arithmetic in a consensus predicate and update focused SCP tests that cover quorum, v-blocking, and downstream envelope behavior.

## How It Was Fixed

The implementation fix is a one-line arithmetic change in src/scp/Node.cpp. leftTillBlock now uses 1 + validators.size() + innerSets.size() - threshold. Test expectations in src/scp/SCPTests.cpp were updated to match the corrected classification behavior.

# Why It Matters

1. isVBlocking is part of SCP consensus quorum/blocking logic.

2. An off-by-one in this predicate can misclassify blocking sets.

3. The patch aligns implementation with the mapper-stated N - T + 1 invariant.

4. The evidence does not establish a concrete remote exploit path.

5. The patch does not involve cryptographic primitives or access-control checks.

# Evidence Notes

The strongest evidence is the src/scp/Node.cpp change from (validators.size() + innerSets.size()) - threshold to (1 + validators.size() + innerSets.size()) - threshold in Node::isVBlocking. Node.h shows this is a recursive Node predicate alongside hasQuorum. SCPTests.cpp changes provide supporting test evidence for v-blocking/quorum behavior and changed envelope counts. Claims about cryptography, signature verification, access control, or a demonstrated network-wide consensus failure are not supported by the provided evidence. Protocol security invariant: In SCP quorum logic, v-blocking classification must require enough validators or recursively blocking inner sets to intersect quorum slices. The provided mapper states that for a quorum set with total entries N and threshold T, the blocking count is N - T + 1; the patch changes isVBlocking to use that count. Verification notes: The patch does not prove a remote exploit path by itself. The patch does not show signature verification or cryptographic primitive changes. The patch does not establish a concrete safety violation scenario, only a consensus predicate correction. The observed test expectation changes do not by themselves prove network-wide consensus failure. Verified from provided diff excerpts only. No commands, file inspection, or external context used. Security relevance is inferred from the SCP consensus predicate role and mapper-stated invariant. Exploitability remains unproven in the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-vblocking-threshold-off-by-one`
Final impact type: `consensus-correctness, quorum-classification`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, scp, quorum, vblocking, off-by-one`

The supplied patch evidence supports a focused correction to SCP v-blocking quorum logic: Node::isVBlocking changes its threshold arithmetic from N - T to N - T + 1, with tests updated around v-blocking/quorum behavior and downstream envelope counts. Because this predicate is part of blockchain consensus logic, the change is security-relevant hardening/correctness of a security-sensitive invariant. However, the evidence does not prove a concrete exploit, remote attack path, signature issue, cryptographic primitive flaw, or demonstrated network-wide consensus failure, so security-fix would be too strong.

## Security Evidence

1. Node::isVBlocking is a recursive SCP quorum/blocking predicate declared alongside hasQuorum.
2. The implementation changes the v-blocking threshold calculation by adding +1 to validators plus inner sets minus threshold.
3. Tests are renamed or added around vblocking and quorum behavior.
4. SCP receiveEnvelope expectations change after the corrected quorum/blocking classification.

## Missing Evidence

1. No advisory, CVE, exploit scenario, or vulnerability disclosure is provided.
2. No proof that the old calculation allowed consensus safety failure, liveness failure, or validator manipulation in practice.
3. No evidence of cryptographic primitive, signature verification, authentication, or access-control changes.
4. No commit body explains security impact beyond the short subject fix isVBlocking.

## Claim Boundaries

1. Treat as consensus security hardening, not a proven exploitable security fix.
2. Do not classify under cryptography or signature validation based on the provided patch.
3. Do not claim remote exploitability or network-wide consensus failure from this evidence alone.
4. The supported bug class is an off-by-one threshold correction in SCP v-blocking logic.
