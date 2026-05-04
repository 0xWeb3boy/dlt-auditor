---
case_id: case_20231023_3a0283f107
project: avalanchego
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2023-10-23
source_refs:
  - git:3a0283f10719477671b72f245eaa2c4a9a739e96
  - "plugin/evm/mempool.go:225"
  - "plugin/evm/mempool.go:149"
  - "plugin/evm/vm.go:1450"
  - "plugin/evm/mempool_atomic_gossiping_test.go:132"
bug_class: mempool-resource-validation
impact_type:
  - resource-exhaustion
tags:
  - infrastructure
  - transaction-processing
  - mempool
  - resource-validation
  - atomic-transactions
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch moves configured transaction verification into the non-forced mempool admission path and adds explicit signed-size and gas checks to `verifyTxAtTip`. The evidence supports resource-validation hardening of atomic mempool admission, but does not establish signature forgery, replay, authorization bypass, consensus failure, or a quantified denial-of-service exploit.

## Observed Patch Facts

1. In `plugin/evm/mempool.go`, the patch replaces `utxoSet := tx.InputUTXOs()` with `if !force && m.verify != nil {`.

2. In `plugin/evm/mempool.go`, the patch replaces `return m.addTx(tx, false)` with `err := m.addTx(tx, false)`.

3. In `plugin/evm/vm.go`, the patch replaces `// issueTx verifies [tx] as valid to be issued on top of the currently preferred block` with `// verifyTxAtTip verifies that [tx] is valid to be issued on top of the currently pre...`.

4. In `plugin/evm/mempool_atomic_gossiping_test.go`, the patch replaces `tx1 := createImportTx(t, vm, ids.ID{1}, params.AvalancheAtomicTxFee)` with `tx1, err := vm.newImportTx(vm.ctx.XChainID, testEthAddrs[0], initialBaseFee, []*secp2...`.

## Project Context

The changed code sits primarily in `plugin/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `plugin/evm/vm_test.go`, `plugin/evm/gossiper_eth_gossiping_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `plugin/evm/vm_test.go`, `plugin/evm/gossiper_eth_gossiping_test.go`. The strongest project-level identifiers around this patch are `mempool`, `local`, `txID`, and `remote`.

## Before/After Behavior

Before the patch, the supplied `Mempool.addTx` snippet proceeded from duplicate checks toward UTXO handling without showing a mempool-level verifier call, and `AddTx` directly returned `m.addTx(tx, false)`. Verification existed in the removed VM `issueTx(tx, local)` helper, but the evidence does not prove every mempool admission path necessarily went through it. After the patch, non-forced `addTx` calls `m.verify(tx)` when configured, failed remote `AddTx` admissions are recorded in `discardedTxs`, and `verifyTxAtTip` rejects atomic transactions above `targetAtomicTxsSize` or failing gas calculation.

# Root Cause

The supported root cause is a validation-boundary gap: atomic transaction verification and resource checks were not shown as enforced inside the shared mempool admission function itself. The patch makes that boundary explicit for non-forced admissions. Broader claims about replay, signer validation, or consensus-invalid blocks are not supported by the supplied evidence.

## Walkthrough

1. A transaction reaches `Mempool.AddTx`, which locks the mempool and calls `addTx(tx, false)`.

2. `addTx` skips transactions already issued, current, or already present in the heap.

3. The patched `addTx` invokes `m.verify(tx)` for non-forced admissions when a verifier exists.

4. The verifier path shown in `VM.verifyTxAtTip` now checks signed byte length against `targetAtomicTxsSize` and computes gas usage with `tx.GasUsed(true)`.

5. If a remote transaction fails admission through `AddTx`, the patched code stores it in `discardedTxs` and logs the failure.

6. Tests were adjusted around atomic mempool priority/drop behavior to use VM-created import transactions consistent with the new validation path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| plugin/evm/mempool.go | 214 | mempool admission now invokes configured transaction verification before accepting non-forced atomic transactions |
| plugin/evm/mempool.go | 147 | remote AddTx failures are recorded in discardedTxs so invalid remote transactions are not repeatedly requested |
| plugin/evm/vm.go | 1428 | verifyTxAtTip enforces preferred-tip validity plus atomic transaction signed-size and gas-use limits |
| plugin/evm/mempool_atomic_gossiping_test.go | 118 | test coverage for atomic mempool priority/drop behavior after admission validation changes |

## Code Snippets

## Snippet 1

Context: `plugin/evm/mempool.go:225` (changes signature or replay validation logic)

Before
```go
return nil
	}

	utxoSet := tx.InputUTXOs()
```
After
```go
return nil
	}
	if !force && m.verify != nil {
		if err := m.verify(tx); err != nil {
			return err
		}
	}
```

## Snippet 2

Context: `plugin/evm/mempool.go:149` (changes a sensitive control or state-update path)

Before
```go
defer m.lock.Unlock()

	return m.addTx(tx, false)
}
```
After
```go
defer m.lock.Unlock()

	err := m.addTx(tx, false)
	if err != nil {
		// unlike local txs, invalid remote txs are recorded as discarded
		// so that they won't be requested again
		txID := tx.ID()
		m.discardedTxs.Put(tx.ID(), tx)
```

## Snippet 3

Context: `plugin/evm/vm.go:1450` (changes signature or replay validation logic)

Before
```go
}

// issueTx verifies [tx] as valid to be issued on top of the currently preferred block
// and then issues [tx] into the mempool if valid.
func (vm *VM) issueTx(tx *Tx, local bool) error {
	if err := vm.verifyTxAtTip(tx); err != nil {
		if !local {
			// unlike local txs, invalid remote txs are recorded as discarded
```
After
```go
}

// verifyTxAtTip verifies that [tx] is valid to be issued on top of the currently preferred block
func (vm *VM) verifyTxAtTip(tx *Tx) error {
	if txByteLen := len(tx.SignedBytes()); txByteLen > targetAtomicTxsSize {
		return fmt.Errorf("tx size (%d) exceeds total atomic txs size target (%d)", txByteLen, targetAtomicTxsSize)
	}
	gasUsed, err := tx.GasUsed(true)
```

## Snippet 4

Context: `plugin/evm/mempool_atomic_gossiping_test.go:132` (changes signature or replay validation logic)

Before
```go
mempool.maxSize = 1

	tx1 := createImportTx(t, vm, ids.ID{1}, params.AvalancheAtomicTxFee)
	assert.NoError(mempool.AddTx(tx1))
	assert.True(mempool.has(tx1.ID()))
	tx2 := createImportTx(t, vm, ids.ID{2}, params.AvalancheAtomicTxFee)
	assert.ErrorIs(mempool.AddTx(tx2), errInsufficientAtomicTxFee)
	assert.True(mempool.has(tx1.ID()))
```
After
```go
mempool.maxSize = 1

	tx1, err := vm.newImportTx(vm.ctx.XChainID, testEthAddrs[0], initialBaseFee, []*secp256k1.PrivateKey{testKeys[0]})
	if err != nil {
		t.Fatal(err)
	}
	assert.NoError(mempool.AddTx(tx1))
	assert.True(mempool.has(tx1.ID()))
```

# Fix Pattern

Place resource and validity checks at the shared mempool admission boundary, while keeping forced insertion as an explicit bypass path and caching rejected remote transactions to avoid repeated handling.

## How It Was Fixed

The VM-level `issueTx` helper was removed, `Mempool.addTx` was given a non-forced verifier call, `verifyTxAtTip` gained signed-size and gas validation, and `Mempool.AddTx` now records failed remote admissions in `discardedTxs` before returning the error.

# Why It Matters

1. Prevents normal atomic mempool admission from bypassing configured validation.

2. Rejects oversized or gas-invalid atomic transactions before acceptance.

3. Reduces repeated handling of remote transactions that already failed admission.

4. Evidence supports hardening, not a demonstrated exploit.

# Evidence Notes

Grounded evidence comes from `plugin/evm/mempool.go` `addTx` and `AddTx`, `plugin/evm/vm.go` `verifyTxAtTip`, and the atomic mempool tests. The commit message mentions size and gas limit checks for the atomic mempool. The evidence does not support the heuristic baseline's replay-or-signature-validation classification, nor claims of forged transactions, duplicated state transitions, or consensus-invalid block production. Protocol security invariant: Atomic transactions admitted through the normal EVM atomic mempool path should be validated against the currently preferred tip and should respect configured size and gas limits before acceptance or repeated gossip/request handling. Verification notes: No concrete exploit path is proven by the patch evidence. No signature forgery, replay, or authorization bypass is demonstrated. No consensus-invalid block production is shown. No unbounded memory, CPU, or network amplification impact is quantified. The removed issueTx helper may be partly an API cleanup; the security-relevant portion is the added mempool verification and resource checks. No command execution or file inspection was performed, per instruction. Classification is limited to the supplied snippets and commit metadata. Exploitability is not confirmed; this is best treated as likely security hardening. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `mempool-resource-validation`
Final impact type: `resource-exhaustion`
Final tags: `infrastructure, transaction-processing, mempool, resource-validation, atomic-transactions`

The supplied evidence supports retaining this as security hardening, not as a replay or signature-validation fix. The patch moves configured verification into the shared non-forced mempool admission path, adds atomic transaction signed-size and gas checks, and caches rejected remote transactions to avoid repeated handling. These are security-sensitive resource and validation-boundary improvements, but the evidence does not prove a concrete exploit, forgery, replay, consensus failure, or quantified denial-of-service impact.

## Security Evidence

1. Mempool.addTx now calls m.verify(tx) for non-forced admissions when configured.
2. verifyTxAtTip rejects transactions whose signed byte length exceeds targetAtomicTxsSize.
3. verifyTxAtTip computes gas usage as part of admission validation.
4. Remote AddTx failures are stored in discardedTxs so invalid remote transactions are not repeatedly requested.
5. Commit body explicitly mentions adding size and gas limit checks to the atomic mempool.

## Missing Evidence

1. No demonstrated attacker-controlled exploit path is shown.
2. No evidence proves signature forgery, replay, or authorization bypass.
3. No evidence shows consensus-invalid blocks could be produced before the patch.
4. No quantified memory, CPU, gas, or network amplification impact is provided.
5. No full before/after call graph proves all prior admission paths bypassed validation.

## Claim Boundaries

1. Classify as resource-validation hardening for atomic mempool admission.
2. Do not claim a confirmed vulnerability or concrete exploit.
3. Do not retain the replay-or-signature-validation classification.
4. Do not claim request forgery, replay, or database impact from the supplied evidence.
5. Security relevance is limited to stricter admission checks and reduced repeated handling of invalid remote transactions.
