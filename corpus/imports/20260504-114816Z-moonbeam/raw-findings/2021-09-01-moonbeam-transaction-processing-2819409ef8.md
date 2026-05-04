---
case_id: case_20210901_2819409ef8
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2021-09-01
source_refs:
  - git:2819409ef84962ddcd56c90b75a7bc21b76cd581
  - "runtime/moonbase/src/lib.rs:259"
  - "runtime/moonbase/src/lib.rs:249"
  - "runtime/moonbeam/src/lib.rs:503"
  - "runtime/moonriver/src/lib.rs:346"
bug_class: fee-accounting-mismatch
impact_type:
  - fee-accounting
  - economic-accounting
tags:
  - blockchain-core
  - transaction-processing
  - evm
  - fee-accounting
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for inconsistent EVM transaction fee handling. The patch changes a Moonriver EVM fee hook from `OnChargeTransaction = ()` to `EVMCurrencyAdapter<Balances, DealWithFees<Runtime>>` and adds an EVM-facing `on_nonzero_unbalanced` handler that mirrors the existing Substrate fee split. The evidence supports a fee-accounting mismatch, but not stronger claims such as direct theft, balance inflation, treasury drain, or unlimited free transactions.

## Observed Patch Facts

1. In `runtime/moonbase/src/lib.rs`, the patch adds `// this is called from pallet_evm for Ethereum-based transactions`.

2. In `runtime/moonbase/src/lib.rs`, the patch adds `// this seems to be called for substrate-based transactions`.

3. In `runtime/moonbeam/src/lib.rs`, the patch replaces `pub const TreasuryId: PalletId = PalletId(*b"pc/trsry");` with `pub const TreasuryId: PalletId = PalletId(*b"py/trsry");`.

4. In `runtime/moonriver/src/lib.rs`, the patch replaces `type OnChargeTransaction = ();` with `type OnChargeTransaction = pallet_evm::EVMCurrencyAdapter<Balances, DealWithFees<Runt...`.

## Project Context

The changed code sits primarily in `runtime/moonbase/src`, `runtime/moonbase`, `runtime/moonbeam/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/moonriver/src/precompiles.rs`, `runtime/moonbeam/src/precompiles.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/moonriver/src/precompiles.rs`, `runtime/moonbeam/src/precompiles.rs`. The strongest project-level identifiers around this patch are `type`, `const`, `pallet_treasury::Module`, and `PalletId`. Nearby tests or test-like files include `runtime/moonriver/tests/integration_test.rs`, `runtime/moonriver/tests/common/mod.rs`.

## Before/After Behavior

Before the patch, the provided Moonriver runtime snippet configured `pallet_evm::Config::OnChargeTransaction` as `()`, while the shown Substrate fee path in `DealWithFees::on_unbalanceds` split fees 80/20 between burn and treasury. The provided before snippet does not show an EVM `on_nonzero_unbalanced` handler. After the patch, Moonriver EVM transaction charging is wired to `EVMCurrencyAdapter<Balances, DealWithFees<Runtime>>`, and Moonbase adds `on_nonzero_unbalanced(amount)` for EVM-originated nonzero imbalances using the same 80/20 split and treasury forwarding. A separate Moonbeam treasury `PalletId` change is related configuration context, not standalone proof of a vulnerability.

# Root Cause

The EVM transaction path was not shown to be wired to the same fee imbalance handling used by the Substrate transaction path. This left evidence of divergent fee accounting between EVM and Substrate transactions.

## Walkthrough

1. The existing `DealWithFees::on_unbalanceds` path takes Substrate transaction fees, splits the imbalance with `ration(80, 20)`, drops the burn portion, and sends the treasury share to `pallet_treasury::Module<R>::on_unbalanced`.

2. The Moonriver EVM configuration previously used `type OnChargeTransaction = ();` in the provided evidence.

3. The patch changes that configuration to `pallet_evm::EVMCurrencyAdapter<Balances, DealWithFees<Runtime>>`.

4. The patch adds `DealWithFees::on_nonzero_unbalanced(amount)` with comments tying it to `pallet_evm` Ethereum-based transactions.

5. The new handler applies the same 80/20 burn/treasury split as the Substrate fee path.

6. The Moonbeam `TreasuryId` update may affect treasury account derivation, but it should be treated as supporting configuration rather than the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/moonriver/src/lib.rs | 346 | Configures pallet_evm transaction charging to use Balances and DealWithFees instead of the unit no-op handler. |
| runtime/moonbase/src/lib.rs | 246 | Defines the existing Substrate transaction fee distribution baseline through DealWithFees::on_unbalanceds. |
| runtime/moonbase/src/lib.rs | 259 | Adds EVM-triggered nonzero imbalance handling so EVM fees are split between burn and treasury. |
| runtime/moonbeam/src/lib.rs | 503 | Updates the treasury PalletId used for fee destination/account derivation. |

## Code Snippets

## Snippet 1

Context: `runtime/moonbase/src/lib.rs:259` (updates aggregate accounting or lifecycle state)

Before
```rust
}
	}
}
```
After
```rust
}
	}

	// this is called from pallet_evm for Ethereum-based transactions
	// (technically, it calls on_unbalanced, which calls this when non-zero)
	fn on_nonzero_unbalanced(amount: NegativeImbalance<R>) {
		// Balances module automatically burns dropped Negative Imbalances by decreasing
		// total_supply accordingly
```

## Snippet 2

Context: `runtime/moonbase/src/lib.rs:249` (updates aggregate accounting or lifecycle state)

Before
```rust
pallet_treasury::Module<R>: OnUnbalanced<NegativeImbalance<R>>,
{
	fn on_unbalanceds<B>(mut fees_then_tips: impl Iterator<Item = NegativeImbalance<R>>) {
		if let Some(fees) = fees_then_tips.next() {
```
After
```rust
pallet_treasury::Module<R>: OnUnbalanced<NegativeImbalance<R>>,
{
	// this seems to be called for substrate-based transactions
	fn on_unbalanceds<B>(mut fees_then_tips: impl Iterator<Item = NegativeImbalance<R>>) {
		if let Some(fees) = fees_then_tips.next() {
```

## Snippet 3

Context: `runtime/moonbeam/src/lib.rs:503` (updates aggregate accounting or lifecycle state)

Before
```rust
pub const ProposalBondMinimum: Balance = 1 * currency::GLMR;
	pub const SpendPeriod: BlockNumber = 6 * DAYS;
	pub const TreasuryId: PalletId = PalletId(*b"pc/trsry");
	pub const MaxApprovals: u32 = 100;
}
```
After
```rust
pub const ProposalBondMinimum: Balance = 1 * currency::GLMR;
	pub const SpendPeriod: BlockNumber = 6 * DAYS;
	pub const TreasuryId: PalletId = PalletId(*b"py/trsry");
	pub const MaxApprovals: u32 = 100;
}
```

## Snippet 4

Context: `runtime/moonriver/src/lib.rs:346` (updates aggregate accounting or lifecycle state)

Before
```rust
type Precompiles = MoonriverPrecompiles<Self>;
	type ChainId = EthereumChainId;
	type OnChargeTransaction = ();
	type BlockGasLimit = BlockGasLimit;
	type FindAuthor = AuthorInherent;
```
After
```rust
type Precompiles = MoonriverPrecompiles<Self>;
	type ChainId = EthereumChainId;
	type OnChargeTransaction = pallet_evm::EVMCurrencyAdapter<Balances, DealWithFees<Runtime>>;
	type BlockGasLimit = BlockGasLimit;
	type FindAuthor = AuthorInherent;
```

# Fix Pattern

Route all transaction fee imbalances through a shared fee-accounting policy and implement the callback variant used by the EVM path.

## How It Was Fixed

The EVM runtime configuration was changed to use `EVMCurrencyAdapter<Balances, DealWithFees<Runtime>>`, and `DealWithFees` gained an `on_nonzero_unbalanced` implementation for EVM-originated imbalances that mirrors the existing Substrate 80/20 burn-and-treasury distribution. The treasury `PalletId` was also updated in Moonbeam.

# Why It Matters

1. Keeps EVM and Substrate transactions aligned under the same fee policy.

2. Reduces risk of inconsistent fee charging or fee distribution across transaction types.

3. Supports protocol economic accounting consistency.

4. Does not establish direct theft, balance inflation, treasury drain, or exact monetary impact from the supplied evidence.

# Evidence Notes

Grounded evidence comes from `runtime/moonriver/src/lib.rs:346`, where `OnChargeTransaction` changes from `()` to `pallet_evm::EVMCurrencyAdapter<Balances, DealWithFees<Runtime>>`, and `runtime/moonbase/src/lib.rs:246`/`:259`, where the EVM nonzero imbalance handler is added to mirror the existing Substrate fee split. `runtime/moonbeam/src/lib.rs:503` changes the treasury `PalletId`; this is relevant to treasury routing but is not sufficient by itself to prove a security issue. Confidence is medium because the provided evidence supports a fee-accounting mismatch but does not fully prove production exploitability or impact. Protocol security invariant: Ethereum-style transactions and Substrate transactions should enter equivalent runtime fee-accounting machinery so fee imbalances are charged and distributed under the same burn/treasury policy. Verification notes: The patch does not prove that users could execute unlimited free EVM transactions in production. The patch does not prove direct theft, balance inflation, or treasury drain. The patch does not show the exact monetary impact or affected networks beyond the touched runtimes. The TreasuryId change alone is not enough to establish a security bug. No access-control or signature-verification failure is shown. No proof of direct theft is provided. No proof of balance inflation is provided. No proof of treasury drain is provided. No exact monetary impact is shown. No access-control or signature-verification issue is shown. Security classification rests on protocol fee-accounting impact, not on a demonstrated exploit. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `fee-accounting-mismatch`
Final impact type: `fee-accounting, economic-accounting`
Final tags: `blockchain-core, transaction-processing, evm, fee-accounting, security-hardening`

The evidence supports retaining this as security hardening, not a proven security fix. The patch wires Moonriver EVM transaction charging from a unit no-op to EVMCurrencyAdapter using the shared DealWithFees policy, and adds an EVM-facing imbalance handler that applies the same burn/treasury split as Substrate transactions. That is security-sensitive economic accounting in a blockchain runtime, but the supplied evidence does not prove exploitability, free transactions, theft, inflation, or a concrete production impact.

## Security Evidence

1. EVM runtime configuration changes OnChargeTransaction from () to EVMCurrencyAdapter<Balances, DealWithFees<Runtime>>.
2. A new on_nonzero_unbalanced handler is explicitly documented as being called from pallet_evm for Ethereum-based transactions.
3. The new EVM imbalance path applies the same 80/20 burn and treasury fee split used by the existing Substrate fee path.
4. Commit subject states EVM transactions must deal with fees the same way as Substrate transactions.

## Missing Evidence

1. No proof that EVM transactions were actually free or undercharged in production.
2. No demonstrated exploit path, attacker workflow, or monetary impact is provided.
3. No evidence of direct theft, balance inflation, treasury drain, or consensus failure.
4. Treasury PalletId change is configuration evidence but does not independently prove a security issue.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix from the supplied patch alone.
2. Supported claim is inconsistent or incomplete EVM fee accounting relative to Substrate transactions.
3. Do not claim unlimited free EVM transactions without additional evidence.
4. Do not claim direct loss of funds, inflation, or treasury compromise.
