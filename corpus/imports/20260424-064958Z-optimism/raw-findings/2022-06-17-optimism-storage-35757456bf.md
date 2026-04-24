---
case_id: case_20220617_35757456bf
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2022-06-17
source_refs:
  - git:35757456bf9441beb9af93a7f368f3862ce581b0
  - "op-proposer/drivers/l2output/driver.go:158"
  - "op-proposer/drivers/l2output/driver.go:96"
  - "op-bindings/bindings/l2outputoracle.go:852"
  - "op-proposer/drivers/l2output/driver.go:172"
bug_class: oracle-output-key-mismatch
impact_type:
  - oracle-output-integrity
  - withdrawal-proof-integrity
confidence: medium
tags:
  - output-oracle
  - withdrawals
  - reorg-protection
  - block-number-canonicalization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a protocol-correctness change in the Bedrock L2 output oracle/proposer path: timestamp-based selection and validation were replaced with block-number-based selection and validation. That is plausibly security-relevant because downstream withdrawal/finality interfaces refer to `_l2BlockNumber`, but the provided diff does not prove an exploitable vulnerability or a concrete security failure.

## Observed Patch Facts

1. In `op-proposer/drivers/l2output/driver.go`, the patch replaces `// Fetch the next expected timestamp that we will submit along with the` with `numElements := new(big.Int).Sub(start, end).Uint64()`.

2. In `op-proposer/drivers/l2output/driver.go`, the patch replaces `// Determine the next uncommitted L2 block number. We do so by transforming` with `// Determine the last committed L2 Block Number`.

3. In `op-bindings/bindings/l2outputoracle.go`, the patch replaces `var _l2timestampRule []interface{}` with `var _l2BlockNumberRule []interface{}`.

4. In `op-proposer/drivers/l2output/driver.go`, the patch replaces `if l2Header.Time != timestamp.Uint64() {` with `if l2Header.Number.Cmp(nextCheckpointBlock) != 0 {`.

## Project Context

The changed code sits primarily in `op-proposer/drivers/l2output`, `op-proposer/drivers`, `op-bindings/bindings`, which anchors the finding in the `storage` area of the project. Historical context from `op-bindings/bindings/l1block.go`, `op-bindings/bindings/optimismportal.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-bindings/bindings/optimismportal.go`, `op-bindings/bindings/l2tol1messagepasser.go`. The strongest project-level identifiers around this patch are `timestamp`, `block`, `contract`, and `next`.

## Before/After Behavior

Before the patch, proposer code read oracle timestamp state, derived a block number from that timestamp, and validated a candidate output by comparing `l2Header.Time` to an expected timestamp. After the patch, it reads `LatestBlockNumber`, computes `nextCheckpointBlock := end - 1`, and validates by requiring `l2Header.Number` to equal that block number. Related generated bindings also expose deletion filtering keyed by `_l2BlockNumber` rather than timestamp-shaped filtering.

# Root Cause

The visible issue is inconsistent identity selection across the oracle/proposer path: some logic was anchored to timestamps and timestamp-derived block lookup instead of directly using the L2 block number. The evidence supports a keying mismatch or ambiguity, not a proven exploit mechanism.

## Walkthrough

1. `GetBlockRange` changed from timestamp-based positioning (`LatestBlockTimestamp` plus derived block computation) to direct `LatestBlockNumber` retrieval.

2. `CraftTx` now treats `end - 1` as the explicit checkpoint block to propose.

3. The proposer sanity check changed from timestamp equality to block-number equality on the fetched L2 header.

4. Generated oracle bindings show deletion/event handling in `_l2BlockNumber` terms, consistent with the same identity shift.

5. The traced `OptimismPortal` interface already accepts `_l2BlockNumber`, which suggests surrounding consumers are block-oriented even though the pre-patch proposer path was partly timestamp-oriented.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-proposer/drivers/l2output/driver.go | 88 | Proposer range selection now starts from the latest committed L2 block number instead of deriving position from an oracle timestamp. |
| op-proposer/drivers/l2output/driver.go | 141 | Checkpoint construction is tied to an explicit `nextCheckpointBlock`, which is the output being proposed. |
| op-proposer/drivers/l2output/driver.go | 172 | Submission path now rejects mismatches on L2 block number rather than only checking timestamp equality. |
| op-bindings/bindings/l2outputoracle.go | 844 | Oracle event/binding surface reflects L2 output deletion keyed by L2 block number, indicating the oracle identity model changed. |
| op-bindings/bindings/optimismportal.go | 32 | Downstream withdrawal finalization interface consumes `_l2BlockNumber`, showing the oracle key feeds the withdrawal proof path. |

## Code Snippets

## Snippet 1

Context: `op-proposer/drivers/l2output/driver.go:158` (updates aggregate accounting or lifecycle state)

Before
```go
}

	// Fetch the next expected timestamp that we will submit along with the
	// L2Output.
	callOpts := &bind.CallOpts{
		Pending: false,
		Context: ctx,
	}
```
After
```go
}

	numElements := new(big.Int).Sub(start, end).Uint64()
	d.l.Info(name+" checkpoint constructed", "start", start, "end", end,
		"nonce", nonce, "blocks_committed", numElements, "checkpoint_block", nextCheckpointBlock)

	l1Header, err := d.cfg.L1Client.HeaderByNumber(ctx, nil)
	if err != nil {
```

## Snippet 2

Context: `op-proposer/drivers/l2output/driver.go:96` (updates aggregate accounting or lifecycle state)

Before
```go
}

	// Determine the next uncommitted L2 block number. We do so by transforming
	// the timestamp of the latest committed L2 block into its block number and
	// adding one.
	l2ooTimestamp, err := d.l2ooContract.LatestBlockTimestamp(callOpts)
	if err != nil {
		d.l.Error(name+" unable to get latest block timestamp", "err", err)
```
After
```go
}

	// Determine the last committed L2 Block Number
	start, err := d.l2ooContract.LatestBlockNumber(callOpts)
	if err != nil {
		d.l.Error(name+" unable to get latest block number", "err", err)
		return nil, nil, err
	}
```

## Snippet 3

Context: `op-bindings/bindings/l2outputoracle.go:852` (updates aggregate accounting or lifecycle state)

Before
```go
_l1TimestampRule = append(_l1TimestampRule, _l1TimestampItem)
	}
	var _l2timestampRule []interface{}
	for _, _l2timestampItem := range _l2timestamp {
		_l2timestampRule = append(_l2timestampRule, _l2timestampItem)
	}

	logs, sub, err := _L2OutputOracle.contract.FilterLogs(opts, "l2OutputAppended", _l2OutputRule, _l1TimestampRule, _l2timestampRule)
```
After
```go
_l1TimestampRule = append(_l1TimestampRule, _l1TimestampItem)
	}
	var _l2BlockNumberRule []interface{}
	for _, _l2BlockNumberItem := range _l2BlockNumber {
		_l2BlockNumberRule = append(_l2BlockNumberRule, _l2BlockNumberItem)
	}

	logs, sub, err := _L2OutputOracle.contract.FilterLogs(opts, "L2OutputDeleted", _l2OutputRule, _l1TimestampRule, _l2BlockNumberRule)
```

## Snippet 4

Context: `op-proposer/drivers/l2output/driver.go:172` (updates aggregate accounting or lifecycle state)

Before
```go
}

	if l2Header.Time != timestamp.Uint64() {
		return nil, fmt.Errorf("invalid timestamp: next timestamp is %v, timestamp of block is %v", timestamp, l2Header.Time)
	}
```
After
```go
}

	if l2Header.Number.Cmp(nextCheckpointBlock) != 0 {
		return nil, fmt.Errorf("invalid blockNumber: next blockNumber is %v, blockNumber of block is %v", nextCheckpointBlock, l2Header.Number)
	}
```

# Fix Pattern

Replace derived or secondary identifiers with a single canonical identifier across producer and consumer paths.

## How It Was Fixed

The patch aligned proposer range selection, transaction construction, and validation around explicit L2 block numbers instead of timestamp-derived lookup. Supporting bindings and interfaces were updated accordingly so oracle lifecycle operations and consumers speak in block-number terms.

# Why It Matters

1. Mismatched identifiers across components can select the wrong protocol object.

2. Reorg-sensitive paths are easier to reason about when keyed by explicit block number.

3. Using one canonical key reduces cross-component ambiguity.

# Evidence Notes

Direct evidence is limited to proposer code and generated bindings. It clearly shows a timestamp-to-block-number refactor in `op-proposer/drivers/l2output/driver.go` and block-number-oriented binding updates in `op-bindings/bindings/l2outputoracle.go`. The commit text mentions reorg protection and oracle interface changes, but the provided excerpts do not show the full contract-side bug, any failing pre-patch scenario, or proof of unauthorized withdrawal/finality impact. Protocol security invariant: If oracle outputs are consumed by block-specific proof or finality logic, all components must refer to the same canonical output identity for a given L2 block. The provided evidence shows an alignment from timestamp-derived lookup toward explicit L2 block numbers, but does not by itself establish a demonstrated security break. Verification notes: The patch does not by itself prove arbitrary theft or unauthorized withdrawal finalization occurred. It is not proven from this diff alone that timestamps were attacker-controlled or non-unique in normal operation. The exact pre-patch failure mode inside `L2OutputOracle.sol` is only partially visible from the provided evidence. Some touched files are bindings, specs, or tests and do not independently establish exploitability. The exact pre-patch failure mode inside `L2OutputOracle.sol` is not shown in the provided excerpts. No concrete exploit path is demonstrated from the supplied diff alone. Security relevance is plausible but not established strongly enough to keep as a confirmed or likely vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `oracle-output-key-mismatch`
Final impact type: `oracle-output-integrity, withdrawal-proof-integrity`
Final confidence: `medium`
Final tags: `output-oracle, withdrawals, reorg-protection, block-number-canonicalization`

The patch evidence supports a security-sensitive hardening change in the L2 output oracle/proposer path: it replaces timestamp-derived selection and validation with explicit L2 block-number keying, and the surrounding project context shows those outputs feed withdrawal finalization through `_l2BlockNumber`. That makes the change more than ordinary cleanup or reliability work. However, the supplied diff does not prove a concrete exploitable vulnerability, attacker control, or a demonstrated unauthorized withdrawal/finality break, so it is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. The proposer changed from using `LatestBlockTimestamp` and derived block lookup to directly using `LatestBlockNumber` for output selection.
2. `CraftTx` now validates the fetched L2 header by exact block number equality instead of only timestamp equality.
3. Commit metadata explicitly mentions `oracle reorg protection` and `withdrawals logic`, both security-sensitive protocol areas.
4. Project context shows `OptimismPortal.finalizeWithdrawalTransaction` consumes `_l2BlockNumber`, tying oracle key correctness to withdrawal proof/finality behavior.
5. Bindings and oracle-facing interfaces were updated to speak in `_l2BlockNumber` terms, indicating canonicalization of a security-relevant identifier across components.

## Missing Evidence

1. No contract-side excerpt shows the exact pre-patch faulty acceptance condition in `L2OutputOracle.sol`.
2. No concrete exploit scenario or failing unauthorized-withdrawal path is demonstrated in the provided patch snippets.
3. No evidence proves timestamps were attacker-influenced, ambiguous in practice, or sufficient to cause acceptance of the wrong output.
4. The provided excerpts do not show the added tests, so the exact regression/security property being enforced is only implied.

## Claim Boundaries

1. Supported claim: the patch hardens a security-sensitive oracle/withdrawal path by canonicalizing output identity to L2 block number.
2. Supported claim: the change improves reorg-sensitive correctness and reduces identifier ambiguity across proposer/oracle consumers.
3. Not supported: a proven exploitable vulnerability, theft, or finalized unauthorized withdrawal before the patch.
4. Not supported: strong economic-impact claims such as direct loss or distortion from the supplied evidence alone.
