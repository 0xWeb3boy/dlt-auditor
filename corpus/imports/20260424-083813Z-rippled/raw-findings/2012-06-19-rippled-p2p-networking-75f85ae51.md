---
case_id: case_20120619_75f85ae51
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: medium
date: 2012-06-19
source_refs:
  - git:75f85ae519bbe5f82ea4beaffb1def13a7c9b757
  - "src/LedgerConsensus.cpp:815"
  - "src/LedgerConsensus.cpp:222"
  - "src/LedgerConsensus.cpp:194"
  - "src/LedgerConsensus.cpp:367"
bug_class: consensus-role-gating
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - blockchain-core
  - consensus
  - validator-logic
  - role-gating
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit `mValidating` and `mProposing` state in `LedgerConsensus` and gates proposal updates, initial proposal publication, and validation creation/relay on those flags. This is plausibly security-relevant because it touches consensus authority paths, but the supplied evidence does not prove a vulnerability, exploitability, peer acceptance impact, or the details of the referenced bug.

## Observed Patch Facts

1. In `src/LedgerConsensus.cpp`, the patch replaces `theApp->getValidations().addValidation(v);` with `if (mValidating)`.

2. In `src/LedgerConsensus.cpp`, the patch replaces `propose(std::vector<uint256>(), std::vector<uint256>());` with `if (mProposing)`.

3. In `src/LedgerConsensus.cpp`, the patch adds `if (theConfig.VALIDATION_SEED.isValid())`.

4. In `src/LedgerConsensus.cpp`, the patch adds `if (mProposing)`.

## Project Context

The changed code sits primarily in `src`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `src/Peer.cpp`, `src/NetworkOPs.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/Peer.cpp`, `src/NetworkOPs.cpp`. The strongest project-level identifiers around this patch are `boost::make_shared`, `std::vector`, `SerializedValidation::pointer`, and `boost`.

## Before/After Behavior

Before the patch, the shown consensus paths unconditionally created a seeded `LedgerProposal`, called `propose(...)`, updated local positions, and created/signed/relayed a `SerializedValidation`. After the patch, validating is enabled only when `theConfig.VALIDATION_SEED.isValid()`, proposing is additionally tied to `NetworkOPs::omFULL`, non-proposing nodes get a non-seeded proposal object, proposal actions run only under `mProposing`, and validation signing/relay runs only under `mValidating`.

# Root Cause

The provided evidence supports only that consensus participation, proposal behavior, and validation behavior were not visibly separated in the shown pre-patch code. The exact root cause of Arthur's reported bug is not described, and a security failure is not demonstrated.

## Walkthrough

1. The constructor now initializes `mValidating` and `mProposing` from validation seed availability and operating mode.

2. `takeInitialPosition` now creates a seeded proposal only for proposing nodes and otherwise creates a non-seeded proposal object.

3. The initial `propose(...)` call is now conditional on `mProposing`.

4. `stateEstablish` now updates local proposal positions only when proposing.

5. `accept` now creates, trusts, stores, signs, and relays validations only when `mValidating` is true.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/LedgerConsensus.cpp | 194 | initializes mValidating and mProposing based on validation seed and operating mode |
| src/LedgerConsensus.cpp | 222 | creates either keyed proposer position or non-proposing consensus position and only sends an initial proposal when proposing |
| src/LedgerConsensus.cpp | 367 | updates local proposal positions only for proposing nodes during consensus establishment |
| src/LedgerConsensus.cpp | 815 | creates, trusts, signs, stores, and relays ledger validations only when mValidating is true |

## Code Snippets

## Snippet 1

Context: `src/LedgerConsensus.cpp:815` (changes a sensitive control or state-update path)

Before
```cpp
#endif

	SerializedValidation::pointer v = boost::make_shared<SerializedValidation>
		(newLCLHash, mOurPosition->peekSeed(), true);
	v->setTrusted();
	theApp->getValidations().addValidation(v);
	std::vector<unsigned char> validation = v->getSigned();
	newcoin::TMValidation val;
```
After
```cpp
#endif

	if (mValidating)
	{
		SerializedValidation::pointer v = boost::make_shared<SerializedValidation>
			(newLCLHash, mOurPosition->peekSeed(), true);
		v->setTrusted();
		// FIXME: If not proposing, set not full
```

## Snippet 2

Context: `src/LedgerConsensus.cpp:222` (changes a sensitive control or state-update path)

Before
```cpp
}

	mOurPosition = boost::make_shared<LedgerProposal>
		(theConfig.VALIDATION_SEED, initialLedger->getParentHash(), txSet);
	mapComplete(txSet, initialSet, false);
	propose(std::vector<uint256>(), std::vector<uint256>());
}
```
After
```cpp
}

	if (mProposing)
		mOurPosition = boost::make_shared<LedgerProposal>
			(theConfig.VALIDATION_SEED, initialLedger->getParentHash(), txSet);
	else
		mOurPosition = boost::make_shared<LedgerProposal>(initialLedger->getParentHash(), txSet);
	mapComplete(txSet, initialSet, false);
```

## Snippet 3

Context: `src/LedgerConsensus.cpp:194` (changes a sensitive control or state-update path)

Before
```cpp
Log(lsDEBUG) << "Creating consensus object";
	Log(lsTRACE) << "LCL:" << previousLedger->getHash().GetHex() <<", ct=" << closeTime;
}
```
After
```cpp
Log(lsDEBUG) << "Creating consensus object";
	Log(lsTRACE) << "LCL:" << previousLedger->getHash().GetHex() <<", ct=" << closeTime;
	if (theConfig.VALIDATION_SEED.isValid())
	{
		mValidating = true;
		mProposing = theApp->getOPs().getOperatingMode() == NetworkOPs::omFULL;
	}
	else mProposing = mValidating = false;
```

## Snippet 4

Context: `src/LedgerConsensus.cpp:367` (changes a sensitive control or state-update path)

Before
```cpp
int LedgerConsensus::stateEstablish(int secondsSinceClose)
{ // we are establishing consensus
	updateOurPositions(secondsSinceClose);
	if (secondsSinceClose > LEDGER_MAX_CONVERGE)
	{
```
After
```cpp
int LedgerConsensus::stateEstablish(int secondsSinceClose)
{ // we are establishing consensus
	if (mProposing)
		updateOurPositions(secondsSinceClose);
	if (secondsSinceClose > LEDGER_MAX_CONVERGE)
	{
```

# Fix Pattern

Introduce explicit local role flags and guard authority-bearing consensus actions with those flags.

## How It Was Fixed

The patch initializes role state in `LedgerConsensus::LedgerConsensus`, adds a non-seeded `LedgerProposal` construction path for non-proposing nodes, and wraps proposal and validation operations in `if (mProposing)` or `if (mValidating)` checks.

# Why It Matters

1. Clarifies the distinction between consensus participation and proposer/validator behavior.

2. Prevents the shown node-local validation relay path from running when `mValidating` is false.

3. Prevents the shown proposal update/publication paths from running when `mProposing` is false.

4. Does not, by itself, prove a security vulnerability or exploit path.

# Evidence Notes

The mapper and draft are grounded on the changed `LedgerConsensus.cpp` hunks, but their security conclusion is stronger than the evidence supports. The patch touches consensus role handling and may be security relevant, yet there is no supplied evidence of forged validations, remote attacker control, peer acceptance behavior, consensus safety impact, or the actual contents of Arthur's bug report. No tests or issue details were provided. Protocol security invariant: The patch suggests a role-separation invariant: nodes may enter consensus without necessarily proposing or validating, and proposal/validation actions should be gated on local proposer/validator state. The provided evidence does not establish that this invariant was violated in a security-exploitable way. Verification notes: The patch does not prove that invalid or non-validator nodes could successfully forge trusted validations. The patch does not prove remote exploitability or a consensus safety break by itself. The patch does not show peer acceptance rules for proposals or validations. The exact bug Arthur reported is not described in the provided commit body or evidence. No test evidence is provided to demonstrate the pre-patch failure mode. No external verification was performed because only the provided input may be used. No test evidence was supplied. Peer-side validation or proposal acceptance rules were not included. The referenced bug report is not included, so the vulnerability thesis remains unproven. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-role-gating`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, validator-logic, role-gating, security-hardening`

The patch does not prove a concrete exploitable vulnerability, but it clearly hardens consensus authority behavior by separating validating and proposing roles and gating validation signing/relay plus proposal publication/update paths on those roles. Because validations and proposals are security-sensitive consensus artifacts, the evidence supports retaining this as security hardening rather than a confirmed security fix.

## Security Evidence

1. Validation creation, trusted marking, signing, storage, and relay are now executed only when mValidating is true.
2. mValidating is enabled only when the configured validation seed is valid.
3. Proposal creation with validation seed, initial propose calls, and proposal updates are gated on mProposing.
4. mProposing is tied to both a valid validation seed and FULL operating mode.
5. The changed paths are in LedgerConsensus consensus and validator logic.

## Missing Evidence

1. No Arthur bug report details are provided.
2. No peer-side acceptance or rejection rules for validations/proposals are shown.
3. No proof of remote attacker control or exploitability is included.
4. No tests demonstrate the pre-patch failure mode or security impact.
5. No evidence shows forged or unauthorized validations were accepted by the network.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Do not claim confirmed consensus compromise or state corruption.
3. Do not claim remote exploitability from the supplied patch alone.
4. Do not claim invalid nodes could forge accepted validations without peer validation evidence.
5. The supported claim is limited to role-based gating of security-sensitive consensus actions.
