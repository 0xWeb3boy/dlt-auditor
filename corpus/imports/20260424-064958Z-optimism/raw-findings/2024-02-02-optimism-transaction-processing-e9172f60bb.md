---
case_id: case_20240202_e9172f60bb
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2024-02-02
source_refs:
  - git:e9172f60bbce209c058b916b689ef9ab150647e1
  - "op-challenger/game/fault/contracts/vm_test.go:25"
  - "op-challenger/game/fault/preimages/large_test.go:115"
  - "op-challenger/game/fault/preimages/large_test.go:92"
  - "op-challenger/game/fault/preimages/large_test.go:132"
bug_class: preimage-representation-confusion
impact_type:
  - data-integrity
confidence: medium
tags:
  - blockchain-core
  - preimage-oracle
  - api-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a correctness/hardening change around how preimage bytes are represented in the challenger upload path, but it does not establish a concrete vulnerability. The visible before/after evidence is limited to tests and the commit message, which show movement away from using a length-prefixed buffer (`OracleData`) toward using raw bytes via `GetPreimageWithoutSize()` and a constructor API.

## Observed Patch Facts

1. In `op-challenger/game/fault/contracts/vm_test.go`, the patch replaces `tx, err := oracleContract.AddGlobalDataTx(&types.PreimageOracleData{` with `tx, err := oracleContract.AddGlobalDataTx(types.NewPreimageOracleData(common.Hash{}.B...`.

2. In `op-challenger/game/fault/preimages/large_test.go`, the patch replaces `contract.claimedSize = uint32(len(data.OracleData))` with `contract.claimedSize = uint32(len(data.GetPreimageWithoutSize()))`.

3. In `op-challenger/game/fault/preimages/large_test.go`, the patch replaces `contract.claimedSize = uint32(len(data.OracleData))` with `contract.claimedSize = uint32(len(data.GetPreimageWithoutSize()))`.

4. In `op-challenger/game/fault/preimages/large_test.go`, the patch replaces `contract.claimedSize = uint32(len(data.OracleData))` with `contract.claimedSize = uint32(len(data.GetPreimageWithoutSize()))`.

## Project Context

The changed code sits primarily in `op-challenger/game/fault/contracts`, `op-challenger/game/fault`, `op-challenger/game/fault/preimages`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-challenger/game/fault/contracts/oracle_test.go`, `op-challenger/game/fault/preimages/direct_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-challenger/game/fault/preimages/direct_test.go`, `op-challenger/game/fault/contracts/oracle_test.go`. The strongest project-level identifiers around this patch are `contract`, `data`, `require`, and `Background`. Nearby tests or test-like files include `op-challenger/game/fault/test/claim_builder.go`, `op-challenger/game/fault/test/game_builder.go`.

## Before/After Behavior

Before the patch, the provided tests expected `claimedSize` and uploaded data to come from `data.OracleData`, and one test constructed `PreimageOracleData` directly with that field. After the patch, those tests expect `claimedSize` and uploaded data to come from `data.GetPreimageWithoutSize()` and use `types.NewPreimageOracleData(...)` instead of direct field construction.

# Root Cause

The evidence suggests an API/representation mixup between an internal length-prefixed encoding and the raw preimage bytes expected by the upload path. That said, the actual implementation hunks are not shown, so the root cause is only supported at the level of intended behavior and API usage.

## Walkthrough

1. The commit message says to exclude the length prefix for large preimage uploads and to make `OracleData` private to avoid accidental use of length-prefixed data.

2. In `op-challenger/game/fault/preimages/large_test.go`, pre-patch expectations used `len(data.OracleData)` for `claimedSize`.

3. Those tests also previously expected uploaded data to equal `data.OracleData`.

4. After the patch, the same tests use `len(data.GetPreimageWithoutSize())` and expect uploaded data to equal `data.GetPreimageWithoutSize()`.

5. In `op-challenger/game/fault/contracts/vm_test.go`, direct struct construction using `OracleData` was replaced with `types.NewPreimageOracleData(...)`.

6. No implementation diff for `large.go`, `split.go`, or `types.go` is included here, so stronger claims about the exact fix mechanics remain inference.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-challenger/game/fault/preimages/large.go | 1 | large preimage uploader logic that must send raw bytes and matching claimed size to the oracle |
| op-challenger/game/fault/types/types.go | 1 | preimage data representation; patch hardens the API by privatizing the length-prefixed field |
| op-challenger/game/fault/preimages/split.go | 1 | chunk/split path implicated by the raw-vs-prefixed byte boundary for large uploads |
| op-challenger/game/fault/preimages/large_test.go | 92 | regression evidence that upload data and claimed size now use `GetPreimageWithoutSize()` instead of `OracleData` |
| op-challenger/game/fault/contracts/vm_test.go | 25 | binding-level evidence that callers now construct preimage payloads through the safe constructor |

## Code Snippets

## Snippet 1

Context: `op-challenger/game/fault/contracts/vm_test.go:25` (changes signature or replay validation logic)

Before
```go
oracleContract, err := vmContract.Oracle(context.Background())
	require.NoError(t, err)
	tx, err := oracleContract.AddGlobalDataTx(&types.PreimageOracleData{
		OracleData: make([]byte, 20),
	})
	require.NoError(t, err)
	// This test doesn't care about all the tx details, we just want to confirm the contract binding is using the
```
After
```go
oracleContract, err := vmContract.Oracle(context.Background())
	require.NoError(t, err)
	tx, err := oracleContract.AddGlobalDataTx(types.NewPreimageOracleData(common.Hash{}.Bytes(), make([]byte, 20), 0))
	require.NoError(t, err)
	// This test doesn't care about all the tx details, we just want to confirm the contract binding is using the
```

## Snippet 2

Context: `op-challenger/game/fault/preimages/large_test.go:115` (changes a sensitive control or state-update path)

Before
```go
data := mockPreimageOracleData()
		contract.bytesProcessed = 5*MaxChunkSize + 1
		contract.claimedSize = uint32(len(data.OracleData))
		contract.timestamp = uint64(cl.Now().Unix())
		err := oracle.UploadPreimage(context.Background(), 0, &data)
		require.ErrorIs(t, err, ErrChallengePeriodNotOver)
		require.Equal(t, 0, contract.squeezeCalls)
		// Squeeze should be called once the challenge period has elapsed.
```
After
```go
data := mockPreimageOracleData()
		contract.bytesProcessed = 5*MaxChunkSize + 1
		contract.claimedSize = uint32(len(data.GetPreimageWithoutSize()))
		contract.timestamp = uint64(cl.Now().Unix())
		err := oracle.UploadPreimage(context.Background(), 0, data)
		require.ErrorIs(t, err, ErrChallengePeriodNotOver)
		require.Equal(t, 0, contract.squeezeCalls)
		// Squeeze should be called once the challenge period has elapsed.
```

## Snippet 3

Context: `op-challenger/game/fault/preimages/large_test.go:92` (changes a sensitive control or state-update path)

Before
```go
oracle, _, _, contract := newTestLargePreimageUploader(t)
		data := mockPreimageOracleData()
		contract.claimedSize = uint32(len(data.OracleData))
		err := oracle.UploadPreimage(context.Background(), 0, &data)
		require.NoError(t, err)
		require.Equal(t, 1, contract.initCalls)
		require.Equal(t, 6, contract.addCalls)
		require.Equal(t, data.OracleData, contract.addData)
```
After
```go
oracle, _, _, contract := newTestLargePreimageUploader(t)
		data := mockPreimageOracleData()
		contract.claimedSize = uint32(len(data.GetPreimageWithoutSize()))
		err := oracle.UploadPreimage(context.Background(), 0, data)
		require.NoError(t, err)
		require.Equal(t, 1, contract.initCalls)
		require.Equal(t, 6, contract.addCalls)
		require.Equal(t, data.GetPreimageWithoutSize(), contract.addData)
```

## Snippet 4

Context: `op-challenger/game/fault/preimages/large_test.go:132` (changes a sensitive control or state-update path)

Before
```go
contract.bytesProcessed = 5*MaxChunkSize + 1
		contract.timestamp = 123
		contract.claimedSize = uint32(len(data.OracleData))
		contract.squeezeCallFails = true
		err := oracle.UploadPreimage(context.Background(), 0, &data)
		require.ErrorIs(t, err, mockSqueezeCallError)
		require.Equal(t, 0, contract.squeezeCalls)
```
After
```go
contract.bytesProcessed = 5*MaxChunkSize + 1
		contract.timestamp = 123
		contract.claimedSize = uint32(len(data.GetPreimageWithoutSize()))
		contract.squeezeCallFails = true
		err := oracle.UploadPreimage(context.Background(), 0, data)
		require.ErrorIs(t, err, mockSqueezeCallError)
		require.Equal(t, 0, contract.squeezeCalls)
```

# Fix Pattern

Hide ambiguous internal encodings behind a safer API and make callers use an accessor or constructor for the canonical payload.

## How It Was Fixed

Based on the supplied evidence, the change was fixed by switching expected upload inputs and size accounting from the length-prefixed representation to raw preimage bytes, and by steering callers away from direct access to the ambiguous field through a constructor-based API.

# Why It Matters

1. It reduces confusion between internal encoding and protocol-facing payload bytes.

2. It makes size accounting and uploaded content line up on the same byte representation.

3. It looks like hardening in a dispute-related path, but exploitability is not shown by the evidence provided.

# Evidence Notes

Direct evidence is limited to test diffs and the commit message. Those materials support a representation change from `OracleData` to `GetPreimageWithoutSize()` and a move to `NewPreimageOracleData(...)`. They do not directly show the production-code hunks, do not prove the old path was reachable in a harmful way, and do not establish a concrete security consequence such as bypass, corruption, or loss. Protocol security invariant: If large preimages are uploaded to the oracle, the uploaded bytes and the reported size should refer to the same canonical raw preimage bytes, not an internal length-prefixed representation. Verification notes: The patch does not prove a practical exploit path; it may be a correctness or liveness failure in the challenger. The evidence does not show whether the on-chain oracle accepted prefixed uploads and stored wrong data, or rejected them outright. The patch alone does not prove fund loss, finality break, or a successful dispute bypass. The exact implementation hunks in `large.go`, `split.go`, and `types.go` are inferred from tests and commit text rather than shown directly here. Production implementation changes were not provided directly. The evidence shows intended behavior changes, not a demonstrated exploit path. Security relevance is plausible because the path is dispute-related, but the vulnerability thesis is not established here. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `preimage-representation-confusion`
Final impact type: `data-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, preimage-oracle, api-hardening`

The supplied evidence supports keeping this as a security-hardening case, not a proven security fix. The commit text and test changes consistently show that large preimage uploads should use raw preimage bytes rather than a length-prefixed internal encoding, and that the ambiguous `OracleData` field is being hidden behind a safer constructor/API. In a dispute-game oracle path, that is a meaningful integrity hardening change, but the patch excerpts do not prove a concrete exploitable vulnerability, runtime acceptance of malformed data, or specific security impact beyond reducing a risky misuse condition.

## Security Evidence

1. Commit message explicitly says to exclude the length prefix for large preimage uploads and make `OracleData` private to avoid accidental misuse.
2. Tests change `claimedSize` from `len(data.OracleData)` to `len(data.GetPreimageWithoutSize())`, showing size accounting now uses canonical raw bytes.
3. Tests change uploaded payload expectations from `data.OracleData` to `data.GetPreimageWithoutSize()`, showing protocol-facing data no longer uses the prefixed form.
4. Caller construction changes from direct struct field access to `types.NewPreimageOracleData(...)`, which hardens the API against unsafe representation mixing.

## Missing Evidence

1. No production-code hunk is shown from `large.go`, `split.go`, `split.go`, or `types.go` to prove the exact runtime bug and fix path.
2. No evidence shows the old behavior caused accepted invalid uploads, failed dispute resolution, or another concrete exploitable outcome.
3. No demonstrated impact such as fund loss, consensus break, privilege bypass, or attacker-controlled trigger is provided.

## Claim Boundaries

1. Supported: the patch hardens a security-sensitive preimage/oracle upload path against representation confusion.
2. Supported: the change reduces the risk of callers using length-prefixed internal data where raw bytes are expected.
3. Not supported: a confirmed exploitable vulnerability or real-world attack path.
4. Not supported: specific economic, consensus, or availability impact from the old behavior.
