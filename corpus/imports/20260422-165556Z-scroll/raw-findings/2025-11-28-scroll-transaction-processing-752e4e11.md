---
case_id: case_20251128_752e4e11
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-11-28
source_refs:
  - git:752e4e1117d7040dd290632846f789b42afac9f2
  - "rollup/internal/controller/sender/sender.go:844"
  - "rollup/internal/controller/watcher/l1_watcher.go:85"
  - "rollup/internal/controller/relayer/l1_relayer.go:174"
  - "rollup/cmd/gas_oracle/app/app.go:67"
bug_class: insufficient-fee-bounds
impact_type:
  - availability
confidence: medium
tags:
  - blockchain-core
  - gas-oracle
  - fee-bounds
  - security-hardening
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is security-relevant in theme but not established as a vulnerability fix by the provided evidence. What is directly supported is that the code stopped computing blob base fee locally, switched to querying the L1 node for that value, and added configured caps before relaying fee updates. That is stronger evidence for fee-correctness and liveness hardening than for a confirmed exploitable overflow bug.

## Observed Patch Facts

1. In `rollup/internal/controller/sender/sender.go`, the patch replaces `blobBaseFee = misc.CalcBlobFee(*excess).Uint64()` with `// Leave it up to the L1 node to compute the correct blob base fee.`.

2. In `rollup/internal/controller/watcher/l1_watcher.go`, the patch replaces `blobBaseFee = misc.CalcBlobFee(*excess).Uint64()` with `// Leave it up to the L1 node to compute the correct blob base fee.`.

3. In `rollup/internal/controller/relayer/l1_relayer.go`, the patch replaces `data, err := r.l1GasOracleABI.Pack("setL1BaseFeeAndBlobBaseFee", new(big.Int).SetUint...` with `// Cap base fee update at the configured upper limit`.

4. In `rollup/cmd/gas_oracle/app/app.go`, the patch replaces `l1client, err := ethclient.Dial(cfg.L1Config.Endpoint)` with `// Init L1 connection`.

## Project Context

The changed code sits primarily in `rollup/internal/controller/sender`, `rollup/internal/controller`, `rollup/internal/controller/watcher`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rollup/internal/controller/sender/estimategas.go`, `rollup/internal/controller/sender/sender_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rollup/internal/controller/sender/estimategas.go`, `rollup/internal/controller/sender/sender_test.go`. The strongest project-level identifiers around this patch are `limit`, `blobBaseFee`, `base`, and `excess`.

## Before/After Behavior

Before the patch, sender and watcher code locally derived `blobBaseFee` from `misc.CalcBlobFee(*excess).Uint64()`, and the relayer path did not yet clamp `baseFee` or `blobBaseFee` before submitting gas-oracle updates. After the patch, those paths query `eth_blobBaseFee` from the L1 RPC node instead of computing locally, the relayer clamps both fee values to configured limits, and startup now fails if the fee-limit configuration is unset.

# Root Cause

The evidence supports a root cause of relying on local blob-fee derivation in code that must track L1 protocol behavior, combined with lack of explicit upper bounds in the downstream gas-oracle update path. The provided diff does not by itself prove a reachable arithmetic overflow exploit; it more clearly shows concern about protocol drift, oversized values, and operational safety.

## Walkthrough

1. `rollup/internal/controller/sender/sender.go` previously computed `blobBaseFee` locally with `misc.CalcBlobFee(*excess).Uint64()` when `ExcessBlobGas` was present.

2. `rollup/internal/controller/watcher/l1_watcher.go` used the same local computation pattern for ingested L1 headers.

3. Both paths were changed to call `eth_blobBaseFee` via a raw RPC client, and the added comments explicitly say the L1 node should compute the correct blob base fee because local calculation would require tracking future L1 configuration changes.

4. `rollup/cmd/gas_oracle/app/app.go` was updated to create a raw RPC client, which enables the new `eth_blobBaseFee` calls, and to abort startup if `l1_base_fee_limit` or `l1_blob_base_fee_limit` is zero.

5. `rollup/internal/controller/relayer/l1_relayer.go` now clamps `baseFee` and `blobBaseFee` to configured limits before packaging the gas-oracle update transaction and records over-limit events in metrics.

6. Taken together, the patch shows bounded, authoritative fee sourcing for the gas-oracle path, but the supplied evidence does not prove attacker-controlled exploitation or a concrete security impact beyond mispricing or stalled updates.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rollup/internal/controller/sender/sender.go | 844 | sender-side L1 fee retrieval for transaction fee estimation |
| rollup/internal/controller/watcher/l1_watcher.go | 85 | L1 header watcher ingestion of blob/base fee data |
| rollup/internal/controller/relayer/l1_relayer.go | 174 | gas-oracle relayer path that bounds and submits fee updates |
| rollup/cmd/gas_oracle/app/app.go | 67 | gas-oracle process initialization, raw RPC access, and fee-limit sanity checks |

## Code Snippets

## Snippet 1

Context: `rollup/internal/controller/sender/sender.go:844` (changes a sensitive control or state-update path)

Before
```go
var blobBaseFee uint64
	if excess := header.ExcessBlobGas; excess != nil {
		blobBaseFee = misc.CalcBlobFee(*excess).Uint64()
	}
	// header.Number.Uint64() returns the pendingBlockNumber, so we minus 1 to get the latestBlockNumber.
	return header.Number.Uint64() - 1, header.Time, baseFee, blobBaseFee, nil
```
After
```go
var blobBaseFee uint64
	if excess := header.ExcessBlobGas; excess != nil {
		// Leave it up to the L1 node to compute the correct blob base fee.
		// Previously we would compute it locally using `CalcBlobFee`, but
		// that approach requires syncing any future L1 configuration changes.
		// Note: The fetched blob base fee might not correspond to the block
		// that we fetched in the previous step, but this is acceptable.
		var blobBaseFeeHex hexutil.Big
```

## Snippet 2

Context: `rollup/internal/controller/watcher/l1_watcher.go:85` (changes a sensitive control or state-update path)

Before
```go
var blobBaseFee uint64
	if excess := block.ExcessBlobGas; excess != nil {
		blobBaseFee = misc.CalcBlobFee(*excess).Uint64()
	}
```
After
```go
var blobBaseFee uint64
	if excess := block.ExcessBlobGas; excess != nil {
		// Leave it up to the L1 node to compute the correct blob base fee.
		// Previously we would compute it locally using `CalcBlobFee`, but
		// that approach requires syncing any future L1 configuration changes.
		// Note: The fetched blob base fee might not correspond to the block
		// that we fetched in the previous step, but this is acceptable.
		var blobBaseFeeHex hexutil.Big
```

## Snippet 3

Context: `rollup/internal/controller/relayer/l1_relayer.go:174` (changes bounds, limits, or capacity handling)

Before
```go
return
			}
			data, err := r.l1GasOracleABI.Pack("setL1BaseFeeAndBlobBaseFee", new(big.Int).SetUint64(baseFee), new(big.Int).SetUint64(blobBaseFee))
			if err != nil {
```
After
```go
return
			}
			// Cap base fee update at the configured upper limit
			if limit := r.cfg.GasOracleConfig.L1BaseFeeLimit; baseFee > limit {
				log.Error("L1 base fee exceed max limit, set to max limit", "baseFee", baseFee, "maxLimit", limit)
				r.metrics.rollupL1RelayerGasPriceOracleFeeOverLimitTotal.Inc()
				baseFee = limit
			}
```

## Snippet 4

Context: `rollup/cmd/gas_oracle/app/app.go:67` (changes persisted or aggregate state handling)

Before
```go
observability.Server(ctx, db)

	l1client, err := ethclient.Dial(cfg.L1Config.Endpoint)
	if err != nil {
		log.Crit("failed to connect l1 geth", "config file", cfgFile, "error", err)
	}

	l1watcher := watcher.NewL1WatcherClient(ctx.Context, l1client, cfg.L1Config.StartHeight, db, registry)
```
After
```go
observability.Server(ctx, db)

	// Init L1 connection
	l1RpcClient, err := rpc.Dial(cfg.L1Config.Endpoint)
	if err != nil {
		log.Crit("failed to dial raw RPC client to L1 endpoint", "endpoint", cfg.L1Config.Endpoint, "error", err)
	}
	l1client := ethclient.NewClient(l1RpcClient)
```

# Fix Pattern

Replace local protocol-sensitive value derivation with an authoritative RPC source, then add explicit configuration-backed bounds before relaying those values.

## How It Was Fixed

The fix moves blob base fee sourcing from local computation to `eth_blobBaseFee` on the L1 node, adds max-limit clamps for both base fee and blob base fee in the relayer, and enforces at startup that the limit configuration exists. This addresses correctness and containment in the fee update pipeline.

# Why It Matters

1. Reduces risk that rollup code diverges from L1 fee rules.

2. Prevents extreme fee values from flowing unbounded into oracle updates.

3. Improves operational safety if fee inputs are unexpectedly large.

4. Supports availability and pricing correctness more clearly than exploit mitigation.

5. Does not, from the provided evidence alone, prove fund loss or consensus impact.

# Evidence Notes

The strongest grounded evidence is the removal of local `CalcBlobFee(...).Uint64()` calls in sender and watcher, the new `eth_blobBaseFee` RPC calls, the added fee caps in `l1_relayer.go`, and the startup sanity check for non-zero limits in `app.go`. The draft's stronger overflow framing is only partially supported: the commit subject mentions overflow, but the diff itself more directly shows authoritative sourcing and bounds enforcement than a demonstrated exploitable overflow condition. The mapper's `l1-gas-oracle` subsystem is reasonable, but `numeric-overflow` is too strong given the available code evidence. Protocol security invariant: Fee data propagated from L1 into the rollup gas-oracle path should come from an authoritative source and remain within configured bounds before being published on-chain. The provided evidence supports correctness and availability hardening for that invariant, but does not establish a broader security break. Verification notes: The patch does not prove an attacker could force an honest L1 node to return overflowing blob-fee values. The patch does not prove fund loss, privilege escalation, or consensus breakage. The evidence does not show that pre-fix behavior was reachable under current mainnet parameters rather than future protocol/config drift. The patch supports availability and economic-correctness hardening, but exploitability beyond mispricing or stalled updates is not shown. Tests were updated according to the commit metadata, but no specific failing exploit scenario is provided in the supplied evidence. The patch comments explicitly justify the change in terms of future L1 configuration changes, which supports correctness-drift hardening. No provided evidence shows an attacker causing an honest L1 node to emit an overflowing blob fee. No provided evidence shows privilege escalation, fund theft, or consensus breakage before the fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-fee-bounds`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `blockchain-core, gas-oracle, fee-bounds, security-hardening, availability`

The patch supports retaining this as a security-hardening case, not a confirmed security bug fix. The code changes harden a security-sensitive gas-oracle/relayer path by replacing local blob-fee derivation with an authoritative L1 RPC result, adding explicit upper bounds for base-fee values before on-chain propagation, and refusing to start without configured limits. That materially reduces risk from incorrect or oversized fee inputs affecting rollup operations, but the provided patch does not by itself prove a concrete exploitable overflow, attacker control, fund loss, or consensus compromise.

## Security Evidence

1. Local `CalcBlobFee(...).Uint64()` derivation was removed from sender and watcher paths in favor of `eth_blobBaseFee` from the L1 node.
2. The relayer now caps both `baseFee` and `blobBaseFee` before packing and submitting gas-oracle updates.
3. Startup now fails if fee-limit configuration is unset, preventing unbounded operation.
4. The changed code sits on the gas-oracle/relayer path that publishes fee data into rollup behavior.
5. Comments explicitly describe avoiding local protocol-drift and handling values that should not overflow `uint64`.

## Missing Evidence

1. No proof that pre-fix overflow was reachable from honest chain data under real protocol parameters.
2. No exploit or attacker-controlled input path is shown in the supplied evidence.
3. No evidence of fund theft, privilege escalation, or consensus failure before the patch.
4. No test excerpt demonstrates a concrete security failure scenario rather than correctness or liveness regression.

## Claim Boundaries

1. Supported claim: the commit hardens fee sourcing and bounds checking in a security-sensitive rollup gas-oracle path.
2. Supported claim: the change reduces risk of incorrect or oversized fee values propagating on-chain.
3. Not supported: a confirmed exploitable numeric-overflow vulnerability.
4. Not supported: direct evidence of asset loss, chain takeover, or consensus break from the pre-fix code.
