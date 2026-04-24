---
case_id: case_20260204_7671838c6
project: reth
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: consensus-safety
impact_type:
  - consensus-failure
confidence: medium
source_quality: high
tags:
  - infrastructure
  - transaction-processing
  - consensus-safety
  - consensus-failure
  - validator
  - consensus
date: 2026-02-04
source_refs:
  - git:7671838c61f0fc180a1363ecdb7be4a2934e842e
  - "crates/ethereum/evm/src/receipt.rs:16"
  - "crates/stateless/src/validation.rs:238"
  - "crates/ethereum/consensus/src/validation.rs:16"
  - "crates/ethereum/consensus/src/validation.rs:34"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to fix a protocol-validation bug in a consensus-critical path: Amsterdam/EIP-7778 changed gas-accounting semantics, and the affected code was not consistently preserving the distinction between header gas_used and receipt cumulative_gas_used. The evidence supports a likely security-relevant consensus fix, but not stronger claims such as demonstrated chain split or exploitability.

## Observed Patch Facts

1. In `crates/ethereum/evm/src/receipt.rs`, the patch replaces `tracing::debug!("Building receipt with cumulative gas used: {:?}", cumulative_gas_used);` with `// EIP-7778: when active, 'cumulative_gas_used' tracks gas before refunds (for block`.

2. In `crates/stateless/src/validation.rs`, the patch adds `Some(output.gas_used),`.

3. In `crates/ethereum/consensus/src/validation.rs`, the patch replaces `block: &RecoveredBlock<B>,` with `///`.

4. In `crates/ethereum/consensus/src/validation.rs`, the patch replaces `// Check if gas used matches the value set in header.` with `// EIP-7778: When Amsterdam is active, block header gas_used tracks gas before refunds,`.

## Project Context

The changed code sits primarily in `crates/ethereum/evm/src`, `crates/ethereum/evm`, `crates/stateless/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/ethereum/evm/src/build.rs`, `crates/ethereum/consensus/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/ethereum/evm/src/build.rs`, `crates/ethereum/consensus/src/lib.rs`. The strongest project-level identifiers around this patch are `cumulative_gas_used`, `tracing::debug`, `receipt`, and `refunds`. Nearby tests or test-like files include `crates/ethereum/evm/tests/execute.rs`.

## Before/After Behavior

Before the patch, the receipt builder used cumulative_gas_used directly and the stateless validation path passed None for the execution gas argument into post-execution validation. After the patch, receipt construction uses gas_spent when present for the receipt's cumulative_gas_used, consensus validation is documented to use execution gas_used for Amsterdam-era header checks, and stateless validation now passes Some(output.gas_used) into that validator.

# Root Cause

The root cause was inconsistent handling of two different gas-accounting values after EIP-7778/Amsterdam. Receipt construction and block validation were not clearly carrying and using the protocol-correct value for each purpose, creating a risk that header validation would compare against the wrong gas source.

## Walkthrough

1. In crates/ethereum/evm/src/receipt.rs, the patch adds comments explaining that under EIP-7778 the header-facing and receipt-facing gas values differ, then introduces receipt_gas = gas_spent.unwrap_or(cumulative_gas_used).

2. That same receipt code assigns the constructed receipt's cumulative_gas_used from receipt_gas, showing an explicit change in which value is emitted into receipts.

3. In crates/ethereum/consensus/src/validation.rs, the added documentation states that when Amsterdam is active, block header gas_used tracks gas before refunds while receipt cumulative_gas_used tracks gas after refunds.

4. The validation implementation comment then says the header must be checked using the execution result's gas_used semantics rather than the receipt-derived value.

5. In crates/stateless/src/validation.rs, the call to validate_block_post_execution changes from passing None to passing Some(output.gas_used), which is the concrete dataflow change needed for the corrected validation path.

6. Taken together, the shown changes support a consensus-correctness fix: receipt encoding keeps one gas meaning, while block-header validation uses a different one.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/ethereum/evm/src/receipt.rs | 16 | builds transaction receipts and restores the protocol-required post-refund `cumulative_gas_used` value under EIP-7778 |
| crates/ethereum/consensus/src/validation.rs | 23 | validates post-execution block header gas usage and switches Amsterdam-era header checks to the execution result's `gas_used` semantics |
| crates/stateless/src/validation.rs | 238 | passes execution `gas_used` into consensus validation so stateless block validation uses the correct header-accounting source |

## Code Snippets

## Snippet 1

Context: `crates/ethereum/evm/src/receipt.rs:16` (changes a sensitive control or state-update path)

Before
```rust
fn build_receipt<E: Evm>(&self, ctx: ReceiptBuilderCtx<'_, TxType, E>) -> Self::Receipt {
        let ReceiptBuilderCtx { tx_type, result, cumulative_gas_used, gas_spent, .. } = ctx;
        tracing::debug!("Building receipt with cumulative gas used: {:?}", cumulative_gas_used);
        tracing::debug!("Gas spent in receipt builder: {:?}", gas_spent);
        Receipt {
            tx_type,
```
After
```rust
fn build_receipt<E: Evm>(&self, ctx: ReceiptBuilderCtx<'_, TxType, E>) -> Self::Receipt {
        let ReceiptBuilderCtx { tx_type, result, cumulative_gas_used, gas_spent, .. } = ctx;
        // EIP-7778: when active, `cumulative_gas_used` tracks gas before refunds (for block
        // accounting), but receipts must use gas after refunds (unchanged). `gas_spent` holds the
        // after-refund cumulative gas when EIP-7778 is active.
        let receipt_gas = gas_spent.unwrap_or(cumulative_gas_used);
        Receipt {
            tx_type,
```

## Snippet 2

Context: `crates/stateless/src/validation.rs:238` (changes a sensitive control or state-update path)

Before
```rust
&output.requests,
        None,
        None,
    )
    .map_err(StatelessValidationError::ConsensusValidationFailed)?;
```
After
```rust
&output.requests,
        None,
        Some(output.gas_used),
    )
    .map_err(StatelessValidationError::ConsensusValidationFailed)?;
```

## Snippet 3

Context: `crates/ethereum/consensus/src/validation.rs:16` (changes a sensitive control or state-update path)

Before
```rust
/// If `receipt_root_bloom` is provided, the pre-computed receipt root and logs bloom are used
/// instead of computing them from the receipts.
pub fn validate_block_post_execution<B, R, ChainSpec>(
    block: &RecoveredBlock<B>,
```
After
```rust
/// If `receipt_root_bloom` is provided, the pre-computed receipt root and logs bloom are used
/// instead of computing them from the receipts.
///
/// `gas_spent` is the gas_used value from the block execution result. When EIP-7778
/// (Amsterdam) is active, block header gas_used tracks gas before refunds while receipt
/// cumulative_gas_used tracks gas after refunds. In that case, the header must be validated
/// against the execution result's gas_used rather than the receipt value.
pub fn validate_block_post_execution<B, R, ChainSpec>(
```

## Snippet 4

Context: `crates/ethereum/consensus/src/validation.rs:34` (changes a sensitive control or state-update path)

Before
```rust
ChainSpec: EthereumHardforks,
{
    // Check if gas used matches the value set in header.
    let cumulative_gas_used =
        if chain_spec.is_amsterdam_active_at_timestamp(block.header().timestamp()) {
```
After
```rust
ChainSpec: EthereumHardforks,
{
    // EIP-7778: When Amsterdam is active, block header gas_used tracks gas before refunds,
    // but receipt cumulative_gas_used still tracks gas after refunds. Use the execution
    // result's gas_used which always matches the header semantics.
    let cumulative_gas_used =
        if chain_spec.is_amsterdam_active_at_timestamp(block.header().timestamp()) {
```

# Fix Pattern

Separate protocol meanings that were previously conflated, then thread the correct value through each validation boundary instead of reusing a nearby but semantically different field.

## How It Was Fixed

The fix makes the distinction explicit in code and call flow. Receipts now use gas_spent when available so receipt cumulative gas remains aligned with receipt semantics, while post-execution validation uses execution-result gas_used for Amsterdam-era header checks. The stateless path was updated to supply that execution gas value into consensus validation.

# Why It Matters

1. Consensus validation depends on exact protocol semantics, not approximate field reuse.

2. Using receipt gas semantics for header checks can cause incorrect accept/reject decisions.

3. The patch aligns the stateless validation path with the same gas-accounting rule.

4. The evidence supports protocol-safety impact, but not stronger claims like proven exploitation or observed chain split.

# Evidence Notes

The strongest evidence is the coordinated change across receipt building, consensus validation comments/docs, and stateless validation plumbing. The supplied snippets explicitly describe the semantic split between pre-refund header gas accounting and post-refund receipt gas accounting, and show that the stateless validator previously did not pass execution gas_used into post-execution validation. No exploit, incident, or full test diff is provided, so claims should stay at protocol-validation risk rather than demonstrated real-world impact. Protocol security invariant: After EIP-7778/Amsterdam, block validation must keep two gas-accounting meanings separate: block-header gas_used must be checked against execution-result gas_used, while receipt cumulative_gas_used must remain the receipt-format value. Validation and receipt construction must not treat those values as interchangeable. Verification notes: The patch does not prove an attacker could reliably exploit this beyond triggering protocol-invalid acceptance or rejection behavior. The patch does not show that a chain split or consensus divergence happened in production. The patch does not establish memory-safety, cryptographic, or authentication impact. The patch does not prove receipt-root corruption independently of the gas-accounting mismatch, even though receipt encoding is affected. The provided evidence shows a real behavioral fix, not just comment cleanup. The evidence is sufficient to support a likely consensus-safety issue. The evidence does not establish production exploitation, chain split occurrence, or attacker prerequisites. No quoted test diff was provided, so validation coverage cannot be assessed from the input alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The patch clearly corrects behavior in consensus-critical receipt and block-validation paths for Amsterdam/EIP-7778 gas semantics. The supplied code shows that the implementation was previously conflating header-facing gas accounting with receipt-facing gas accounting, and that validation now uses execution-result gas for header checks while receipts retain their own semantics. In a blockchain client, that is security-sensitive consensus logic, so the case belongs in a security corpus as hardening. However, the patch alone does not prove a concrete exploitable vulnerability, real-world chain split, or invalid-block acceptance scenario strongly enough to keep the stronger "security-fix" label.

## Security Evidence

1. Consensus validation code now explicitly distinguishes header `gas_used` semantics from receipt `cumulative_gas_used` semantics under Amsterdam/EIP-7778.
2. `crates/stateless/src/validation.rs` changed from passing `None` to `Some(output.gas_used)` into post-execution validation, showing a real logic fix rather than comment-only cleanup.
3. `crates/ethereum/evm/src/receipt.rs` now uses `gas_spent.unwrap_or(cumulative_gas_used)` so receipts preserve after-refund gas semantics when EIP-7778 is active.
4. The touched paths are receipt construction and block post-execution validation, which are consensus-sensitive code paths in an Ethereum client.

## Missing Evidence

1. No failing test, reproducer, or execution trace is provided showing concrete invalid acceptance or rejection before the fix.
2. No advisory, commit text, or patch evidence states attacker exploitability or an observed chain split.
3. The excerpt does not prove whether the bug could be triggered by adversarial blocks in practice versus causing compatibility issues at fork activation.

## Claim Boundaries

1. Supported claim: this is a security-sensitive consensus-validation correction around gas-accounting semantics.
2. Supported claim: the patch reduces risk of protocol-validation mismatch in Amsterdam/EIP-7778 handling.
3. Not supported from the patch alone: proven exploit, production incident, or demonstrated consensus split.
4. Not supported from the patch alone: broader impacts such as receipt-root corruption, memory safety, or authentication failure.
