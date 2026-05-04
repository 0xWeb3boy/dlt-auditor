---
case_id: case_20211215_aa99e9353b
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: replay-or-signature-validation
impact_type:
  - request-forgery-or-replay
confidence: medium
source_quality: medium
tags:
  - blockchain-core
  - transaction-processing
  - replay-or-signature-validation
  - request-forgery-or-replay
  - signature
date: 2021-12-15
source_refs:
  - git:aa99e9353b35b389aed5ab52dce62fb989802488
  - "runtime/moonbeam/src/lib.rs:752"
  - "runtime/moonriver/src/lib.rs:722"
  - "runtime/moonbeam/src/lib.rs:741"
  - "runtime/moonbase/src/lib.rs:783"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best characterized as likely security hardening for the crowdloan rewards runtime configuration. It adds signed origins for reward address association/change in Moonbeam and wires per-network `SignatureNetworkIdentifier` constants for Moonbeam, Moonriver, and Moonbase. The commit text explicitly mentions replay attack prevention, but the supplied diff does not prove an exploitable vulnerability or show the signature verification logic.

## Observed Patch Facts

1. In `runtime/moonbeam/src/lib.rs`, the patch replaces `// This will get accessible to users in future phases.` with `type RewardAddressAssociateOrigin = EnsureSigned<Self::AccountId>;`.

2. In `runtime/moonriver/src/lib.rs`, the patch adds `pub const SignatureNetworkIdentifier: &'static [u8] = b"moonriver-";`.

3. In `runtime/moonbeam/src/lib.rs`, the patch adds `pub const SignatureNetworkIdentifier: &'static [u8] = b"moonbeam-";`.

4. In `runtime/moonbase/src/lib.rs`, the patch adds `pub const SignatureNetworkIdentifier: &'static [u8] = b"moonbase-";`.

## Project Context

The changed code sits primarily in `runtime/moonbeam/src`, `runtime/moonbeam`, `runtime/moonriver/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/moonbase/src/precompiles.rs`, `runtime/moonriver/src/precompiles.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/moonbase/src/precompiles.rs`. The strongest project-level identifiers around this patch are `Self::AccountId`, `type`, `Perbill::from_percent`, and `const`. Nearby tests or test-like files include `runtime/moonbase/tests/common/mod.rs`, `runtime/moonriver/tests/common/mod.rs`.

## Before/After Behavior

Before the patch, the shown Moonbeam crowdloan rewards config had `RewardAddressChangeOrigin = EnsureRoot<Self::AccountId>` and no visible `RewardAddressAssociateOrigin` or `SignatureNetworkIdentifier` associated type. After the patch, Moonbeam sets both association and change origins to `EnsureSigned<Self::AccountId>` and wires `SignatureNetworkIdentifier`. The Moonbeam, Moonriver, and Moonbase runtime parameter blocks also gain distinct lowercase network prefixes: `moonbeam-`, `moonriver-`, and `moonbase-`.

# Root Cause

The supported root cause is missing or outdated runtime configuration for the crowdloan rewards pallet's signed-origin and network-identifier requirements. A stronger claim that signatures were actually replayable before the patch is not established by the provided snippets.

## Walkthrough

1. Moonbeam's `pallet_crowdloan_rewards::Config` adds `RewardAddressAssociateOrigin = EnsureSigned<Self::AccountId>`.

2. Moonbeam changes `RewardAddressChangeOrigin` from `EnsureRoot<Self::AccountId>` to `EnsureSigned<Self::AccountId>`.

3. Moonbeam wires `type SignatureNetworkIdentifier = SignatureNetworkIdentifier;` into the crowdloan rewards config.

4. Moonbeam defines `SignatureNetworkIdentifier` as `b"moonbeam-"`.

5. Moonriver defines `SignatureNetworkIdentifier` as `b"moonriver-"`.

6. Moonbase defines `SignatureNetworkIdentifier` as `b"moonbase-"`.

7. The commit subject and body connect these configuration changes to replay attack prevention, but the verifier and prior acceptance behavior are not included in the evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/moonbeam/src/lib.rs | 752 | Configures crowdloan reward address associate/change origins as signed and wires the signature network identifier into the Moonbeam runtime. |
| runtime/moonbeam/src/lib.rs | 741 | Defines the Moonbeam-specific signature domain prefix `moonbeam-`. |
| runtime/moonriver/src/lib.rs | 722 | Defines the Moonriver-specific signature domain prefix `moonriver-` for crowdloan reward signature checks. |
| runtime/moonbase/src/lib.rs | 783 | Defines the Moonbase-specific signature domain prefix `moonbase-` for crowdloan reward signature checks. |

## Code Snippets

## Snippet 1

Context: `runtime/moonbeam/src/lib.rs:752` (changes a sensitive control or state-update path)

Before
```rust
type RewardCurrency = Balances;
	type RelayChainAccountId = [u8; 32];
	// This will get accessible to users in future phases.
	type RewardAddressChangeOrigin = EnsureRoot<Self::AccountId>;
	type RewardAddressRelayVoteThreshold = RelaySignaturesThreshold;
	type VestingBlockNumber = cumulus_primitives_core::relay_chain::BlockNumber;
	type VestingBlockProvider =
```
After
```rust
type RewardCurrency = Balances;
	type RelayChainAccountId = [u8; 32];
	type RewardAddressAssociateOrigin = EnsureSigned<Self::AccountId>;
	type RewardAddressChangeOrigin = EnsureSigned<Self::AccountId>;
	type RewardAddressRelayVoteThreshold = RelaySignaturesThreshold;
	type SignatureNetworkIdentifier = SignatureNetworkIdentifier;
	type VestingBlockNumber = cumulus_primitives_core::relay_chain::BlockNumber;
	type VestingBlockProvider =
```

## Snippet 2

Context: `runtime/moonriver/src/lib.rs:722` (changes a sensitive control or state-update path)

Before
```rust
pub const MaxInitContributorsBatchSizes: u32 = 500;
	pub const RelaySignaturesThreshold: Perbill = Perbill::from_percent(100);
}
```
After
```rust
pub const MaxInitContributorsBatchSizes: u32 = 500;
	pub const RelaySignaturesThreshold: Perbill = Perbill::from_percent(100);
	pub const SignatureNetworkIdentifier:  &'static [u8] = b"moonriver-";

}
```

## Snippet 3

Context: `runtime/moonbeam/src/lib.rs:741` (changes a sensitive control or state-update path)

Before
```rust
pub const MaxInitContributorsBatchSizes: u32 = 500;
	pub const RelaySignaturesThreshold: Perbill = Perbill::from_percent(100);
}
```
After
```rust
pub const MaxInitContributorsBatchSizes: u32 = 500;
	pub const RelaySignaturesThreshold: Perbill = Perbill::from_percent(100);
	pub const SignatureNetworkIdentifier:  &'static [u8] = b"moonbeam-";
}
```

## Snippet 4

Context: `runtime/moonbase/src/lib.rs:783` (changes a sensitive control or state-update path)

Before
```rust
pub const MaxInitContributorsBatchSizes: u32 = 500;
	pub const RelaySignaturesThreshold: Perbill = Perbill::from_percent(100);
}
```
After
```rust
pub const MaxInitContributorsBatchSizes: u32 = 500;
	pub const RelaySignaturesThreshold: Perbill = Perbill::from_percent(100);
	pub const SignatureNetworkIdentifier:  &'static [u8] = b"moonbase-";

}
```

# Fix Pattern

Update runtime configuration to expose signed origins and runtime-specific signature domain identifiers to the reward authorization pallet.

## How It Was Fixed

The runtime configs were updated to require signed origins for Moonbeam reward address association/change paths and to define distinct `SignatureNetworkIdentifier` constants for Moonbeam, Moonriver, and Moonbase.

# Why It Matters

1. Network-specific signature identifiers can support domain separation between deployments.

2. Signed origins make the changed reward address operations user-authenticated at the runtime config boundary.

3. The evidence supports security hardening, not a confirmed exploit fix.

# Evidence Notes

Primary evidence is limited to runtime configuration snippets in `runtime/moonbeam/src/lib.rs`, `runtime/moonriver/src/lib.rs`, and `runtime/moonbase/src/lib.rs`, plus the commit message. The snippets do not include `pallet_crowdloan_rewards` signature construction or verification code. Related precompile snippets are contextual only and should not be treated as root cause evidence. Protocol security invariant: Crowdloan reward address association/change authorization should be tied to an authenticated origin, and any signature-based authorization should be scoped to the intended runtime network. The provided evidence shows runtime configuration for signed origins and per-network signature identifiers, but does not show the underlying verifier or a concrete prior replay acceptance path. Verification notes: The patch evidence does not show the implementation of signature verification inside `pallet_crowdloan_rewards`. No concrete exploit path or prior accepted replayed signature is proven by the provided diff. The origin change from root to signed may also reflect feature enablement/API adaptation, not purely a security fix. The related precompile contexts do not appear to be the primary business-logic path for this change. Inspect `pallet_crowdloan_rewards` signature verification to confirm how `SignatureNetworkIdentifier` is used. Check tests for replay or cross-network signature rejection cases. Do not claim confirmed replayability without evidence of the previous verifier behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The supplied evidence supports retaining this as security hardening, not a confirmed vulnerability fix. The patch wires distinct per-network signature identifiers and changes crowdloan reward address operations to signed origins, while the commit explicitly references replay attack prevention. However, the snippets do not show the signature verification implementation or prove that cross-network replay was accepted before the change.

## Security Evidence

1. Commit subject explicitly says replay attack prevention signature adaptation.
2. Runtime configs add network-specific SignatureNetworkIdentifier values for moonbeam, moonriver, and moonbase.
3. Moonbeam crowdloan rewards config adds signed origin for reward address association.
4. Moonbeam reward address change origin changes from root-only future-facing config to EnsureSigned, exposing authenticated user-origin behavior.

## Missing Evidence

1. No pallet_crowdloan_rewards signature construction or verification code is shown.
2. No test snippet demonstrates rejection of replayed or cross-network signatures.
3. No concrete pre-patch exploit path or accepted replay example is provided.
4. Origin change may also reflect feature enablement or API adaptation rather than a proven vulnerability fix.

## Claim Boundaries

1. Do not claim a confirmed exploitable replay vulnerability from the provided patch alone.
2. Supported claim is domain-separation and signed-origin hardening for crowdloan reward authorization.
3. Impact should remain conservative as potential request forgery or replay prevention.
4. The evidence is strongest for security-hardening, not security-fix.
