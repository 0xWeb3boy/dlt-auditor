---
case_id: case_20130226_bd3d28c2f
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
bug_class: consensus-safety
impact_type:
  - consensus-failure
confidence: medium
source_quality: high
tags:
  - blockchain-core
  - consensus
  - consensus-safety
  - consensus-failure
date: 2013-02-26
source_refs:
  - git:bd3d28c2fa57ee6f9f8d8e4c189de9b896c0950b
  - "src/cpp/ripple/NetworkOPs.cpp:880"
  - "src/cpp/ripple/NetworkOPs.cpp:631"
  - "src/cpp/ripple/NetworkOPs.cpp:673"
  - "src/cpp/ripple/NetworkOPs.h:259"
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant consensus correctness bug: a race during consensus startup could let the node begin consensus with the wrong last closed ledger. The supported evidence is limited to `NetworkOPs` startup flow and the commit subject; it does not establish practical exploitability or broader impact.

## Observed Patch Facts

1. In `src/cpp/ripple/NetworkOPs.cpp`, the patch replaces `if (mMode != omFULL)` with `if ((mMode == omFULL) || (mMode == omTRACKING))`.

2. In `src/cpp/ripple/NetworkOPs.cpp`, the patch replaces `// FIXME: Don't check unless last closed ledger is at least some seconds old` with `tryStartConsensus();`.

3. In `src/cpp/ripple/NetworkOPs.cpp`, the patch removes `if (mConsensus)`.

4. In `src/cpp/ripple/NetworkOPs.h`, the patch adds `void tryStartConsensus();`.

## Project Context

The changed code sits primarily in `src/cpp/ripple`, `src/cpp`, which anchors the finding in the `consensus` area of the project. Historical context from `src/cpp/ripple/LedgerConsensus.cpp`, `src/cpp/ripple/Peer.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/cpp/ripple/LedgerConsensus.cpp`, `src/cpp/ripple/Peer.cpp`. The strongest project-level identifiers around this patch are `networkClosed`, `std::vector`, `Peer::pointer`, and `mConsensus`. Nearby tests or test-like files include `src/cpp/websocketpp/examples/fuzzing_client/fuzzing_client.cpp`, `src/cpp/websocketpp/websocketpp.xcodeproj/xcuserdata/jcar.xcuserdatad/xcschemes/fuzzing_server.xcscheme`.

## Before/After Behavior

Before the patch, `haveConsensusObject()` and `checkState()` had separate consensus-startup logic involving peer state, last-closed-ledger checking, and `beginConsensus(...)`. After the patch, both paths route through `tryStartConsensus()`, which performs the last-closed-ledger check immediately before starting consensus when eligible.

# Root Cause

Consensus startup logic was duplicated across paths, creating a timing window where one path could start consensus using stale or incorrect last-closed-ledger state relative to peer/network observations.

## Walkthrough

1. `haveConsensusObject()` could be reached when no consensus object existed.

2. Before the patch, that path performed its own peer-vector collection, last-closed-ledger check, and direct `beginConsensus(...)` call.

3. `checkState()` also contained consensus startup logic, so startup decisions were split across timing-sensitive paths.

4. The commit subject states this produced a half-second race window where a proposal could cause consensus entry with the wrong last closed ledger.

5. The patch introduces `tryStartConsensus()` as the shared startup helper.

6. Both observed startup paths now call the helper, keeping last-closed-ledger checking closer to `beginConsensus(...)`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/cpp/ripple/NetworkOPs.cpp | 880 | Peer-triggered consensus-object creation now delegates to tryStartConsensus(), preserving the last-closed-ledger check before starting consensus. |
| src/cpp/ripple/NetworkOPs.cpp | 631 | Network state timer path now calls tryStartConsensus() before entering the active consensus timer flow. |
| src/cpp/ripple/NetworkOPs.cpp | 673 | Consensus startup boundary checks peer-reported last closed ledger and begins consensus with networkClosed/currentLedger when eligible. |
| src/cpp/ripple/NetworkOPs.h | 259 | Declares tryStartConsensus() as the shared consensus startup helper. |

## Code Snippets

## Snippet 1

Context: `src/cpp/ripple/NetworkOPs.cpp:880` (changes a consensus- or validator-sensitive branch)

Before
```cpp
if (mConsensus)
		return true;
	if (mMode != omFULL)
		return false;

	uint256 networkClosed;
	std::vector<Peer::pointer> peerList = theApp->getConnectionPool().getPeerVector();
	bool ledgerChange = checkLastClosedLedger(peerList, networkClosed);
```
After
```cpp
if (mConsensus)
		return true;

	if ((mMode == omFULL) || (mMode == omTRACKING))
	{
		tryStartConsensus();
	}
	else
```

## Snippet 2

Context: `src/cpp/ripple/NetworkOPs.cpp:631` (changes a sensitive control or state-update path)

Before
```cpp
return;
	}

	// FIXME: Don't check unless last closed ledger is at least some seconds old
	// If full or tracking, check only at wobble time!
	uint256 networkClosed;
	bool ledgerChange = checkLastClosedLedger(peerList, networkClosed);
	if(networkClosed.isZero())
```
After
```cpp
return;
	}
	tryStartConsensus();
	if (mConsensus)
		mConsensus->timerEntry();
}

void NetworkOPs::tryStartConsensus()
```

## Snippet 3

Context: `src/cpp/ripple/NetworkOPs.cpp:673` (changes a sensitive control or state-update path)

Before
```cpp
if ((!mConsensus) && (mMode != omDISCONNECTED))
		beginConsensus(networkClosed, mLedgerMaster->getCurrentLedger());
	if (mConsensus)
		mConsensus->timerEntry();
}
```
After
```cpp
if ((!mConsensus) && (mMode != omDISCONNECTED))
		beginConsensus(networkClosed, mLedgerMaster->getCurrentLedger());
}
```

## Snippet 4

Context: `src/cpp/ripple/NetworkOPs.h:259` (changes a sensitive control or state-update path)

Before
```c
bool checkLastClosedLedger(const std::vector<Peer::pointer>&, uint256& networkClosed);
	int beginConsensus(const uint256& networkClosed, Ledger::ref closingLedger);
	void endConsensus(bool correctLCL);
	void setStandAlone()				{ setMode(omFULL); }
```
After
```c
bool checkLastClosedLedger(const std::vector<Peer::pointer>&, uint256& networkClosed);
	int beginConsensus(const uint256& networkClosed, Ledger::ref closingLedger);
	void tryStartConsensus();
	void endConsensus(bool correctLCL);
	void setStandAlone()				{ setMode(omFULL); }
```

# Fix Pattern

Centralize timing-sensitive consensus startup behind a shared helper that rechecks network last-closed-ledger state immediately before starting consensus.

## How It Was Fixed

`NetworkOPs::tryStartConsensus()` was added and declared in `NetworkOPs.h`. `haveConsensusObject()` now calls it for `omFULL` or `omTRACKING` instead of duplicating startup logic, and `checkState()` also calls it before driving the consensus timer.

# Why It Matters

1. Consensus safety depends on all participants building on the correct previous ledger.

2. Starting consensus from the wrong last closed ledger can destabilize ledger agreement.

3. The evidence supports a consensus-state race, not theft, signature bypass, RCE, or proven denial of service.

# Evidence Notes

Grounded evidence comes from the changed `NetworkOPs.cpp` startup paths, the new `tryStartConsensus()` declaration, and the commit subject. Claims about reliable remote exploitation, direct fund loss, or impacts outside consensus startup are not supported by the supplied input. Protocol security invariant: A node should enter consensus only after selecting a last closed ledger that has just been checked against current peer/network state; proposal- or peer-triggered startup must not race or bypass that selection. Verification notes: The patch does not prove transaction theft, signature bypass, or direct fund loss. The evidence does not show whether an untrusted peer alone can reliably trigger the race. The impact is limited to consensus startup state shown here, not the full LedgerConsensus algorithm. No denial-of-service or remote code execution claim is supported by the patch. No tests or runtime traces are provided. Adversarial triggerability by an untrusted peer is plausible from the proposal/peer-action wording but not proven by the supplied code excerpts. Confidence is medium because the failure mode is explicit in the commit subject, while impact and exploitability remain bounded by limited evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied evidence supports retaining this as a security-relevant consensus fix. The commit explicitly describes a race window where a proposal could cause consensus to start with the wrong last closed ledger, and the patch changes consensus startup flow to centralize last-closed-ledger checking immediately before beginConsensus(). The evidence does not prove exploitability, fund loss, or a network-wide consensus break, so the existing medium-confidence, bounded consensus-safety framing is appropriate.

## Security Evidence

1. Commit subject identifies a race window affecting consensus entry with the wrong last closed ledger.
2. Patch modifies NetworkOPs consensus startup logic, including haveConsensusObject(), checkState(), and beginConsensus() flow.
3. New tryStartConsensus() centralizes checkLastClosedLedger() before starting consensus.
4. The affected subsystem is blockchain consensus, where incorrect last-closed-ledger selection is security-sensitive.

## Missing Evidence

1. No proof that an untrusted peer can reliably trigger the race.
2. No tests, traces, or incident notes demonstrating practical exploitation.
3. No evidence of direct fund loss, signature bypass, RCE, or denial of service.
4. No full protocol analysis showing network-wide consensus failure.

## Claim Boundaries

1. Keep the claim limited to a consensus startup race involving last-closed-ledger selection.
2. Do not claim proven theft, remote code execution, or authentication bypass.
3. Do not claim reliable adversarial exploitability from the supplied patch alone.
4. Do not generalize beyond the NetworkOPs consensus startup paths shown in the evidence.
