---
case_id: case_20230110_4fed3e0d2b
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-01-10
source_refs:
  - git:4fed3e0d2baaafe567e9d757203b6c7cacace82e
  - "precompiles/utils/src/data/mod.rs:79"
  - "precompiles/xcm-utils/src/mock.rs:77"
  - "precompiles/xcm-utils/src/lib.rs:61"
  - "precompiles/xcm-utils/src/mock.rs:307"
bug_class: smart-contract-xcm-execute-restriction
impact_type:
  - authorization-boundary
  - restricted-call-exposure
confidence: medium
tags:
  - blockchain-core
  - precompile
  - xcm
  - smart-contract-caller-restriction
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is narrower than the draft: the patch adds selector-level pre-checking around XCM execute selectors in the XCM utils precompile and adds helper/test support for that behavior. The commit text says not to allow execute from smart contracts, but the provided evidence does not prove that a released vulnerable path existed or show the full enforcement branch. This is potentially security-relevant hardening, not a confirmed vulnerability fix.

## Observed Patch Facts

1. In `precompiles/utils/src/data/mod.rs`, the patch replaces `/// Create a new input parser from a selector-initial input.` with `/// Read selector as u32`.

2. In `precompiles/xcm-utils/src/mock.rs`, the patch replaces `pub struct MockParentMultilocationToAccountConverter;` with `pub struct MockAccountToAccountKey20<Origin, AccountId>(PhantomData<(Origin, AccountI...`.

3. In `precompiles/xcm-utils/src/lib.rs`, the patch replaces `Runtime: pallet_evm::Config + frame_system::Config,` with `Runtime: pallet_evm::Config + frame_system::Config + pallet_xcm::Config,`.

4. In `precompiles/xcm-utils/src/mock.rs`, the patch replaces `pub struct DoNothingRouter;` with `// Simulates sending a XCM message`.

## Project Context

The changed code sits primarily in `precompiles/utils/src/data`, `precompiles/utils/src`, `precompiles/xcm-utils/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `precompiles/xcm-utils/src/tests.rs`, `precompiles/utils/src/data/xcm.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/xcm-utils/src/tests.rs`, `precompiles/utils/src/substrate.rs`. The strongest project-level identifiers around this patch are `frame_system::Config`, `Runtime`, `Config`, and `Origin`.

## Before/After Behavior

Before the patch, the supplied `XcmUtilsPrecompile` excerpt does not show a selector-level pre-check before public precompile methods. After the patch, the implementation has additional XCM/runtime dispatch bounds and a `#[precompile::pre_check]` that reads the raw ABI selector and compares it with `xcm_execute_selectors()`. A helper `read_u32_selector` was added to parse the first four input bytes with a length check. Mock origin conversion and sent-XCM capture support were also added for tests.

# Root Cause

The evidence supports a missing or newly introduced selector-level enforcement point for distinguishing XCM execute calls at the precompile boundary. It does not establish a broader authorization bypass, accounting drift, loss of funds, consensus issue, or even that the unguarded behavior existed in a released vulnerable version.

## Walkthrough

1. A caller enters the XCM utils precompile with ABI-encoded input.

2. The first four bytes identify the selected precompile function.

3. The patch adds a raw selector reader that checks input length before extracting those bytes as a big-endian `u32`.

4. The patch adds a precompile `pre_check` that compares the selector against `xcm_execute_selectors()`.

5. The commit message states the intended restriction as not allowing execute from smart contracts.

6. Mock conversion and sent-XCM capture changes support tests and should not be treated as the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/xcm-utils/src/lib.rs | 61 | Adds XCM utils precompile runtime bounds and a pre_check that inspects function selectors to block xcm_execute selectors from the disallowed caller path. |
| precompiles/utils/src/data/mod.rs | 79 | Adds raw u32 selector reading so precompile checks can identify execute functions before normal ABI decoding. |
| precompiles/xcm-utils/src/mock.rs | 77 | Adds mock origin-to-MultiLocation conversion support used to test account-origin behavior for XCM precompile paths. |
| precompiles/xcm-utils/src/mock.rs | 307 | Adds mock sent-XCM capture support for regression tests around XCM message dispatch. |

## Code Snippets

## Snippet 1

Context: `precompiles/utils/src/data/mod.rs:79` (updates aggregate accounting or lifecycle state)

Before
```rust
}

	/// Create a new input parser from a selector-initial input.
	pub fn new_skip_selector(input: &'a [u8]) -> MayRevert<Self> {
```
After
```rust
}

	/// Read selector as u32
	pub fn read_u32_selector(input: &'a [u8]) -> MayRevert<u32> {
		if input.len() < 4 {
			return Err(RevertReason::read_out_of_bounds("selector").into());
		}
```

## Snippet 2

Context: `precompiles/xcm-utils/src/mock.rs:77` (updates aggregate accounting or lifecycle state)

Before
```rust
);

pub struct MockParentMultilocationToAccountConverter;
impl Convert<MultiLocation, AccountId> for MockParentMultilocationToAccountConverter {
```
After
```rust
);

use frame_system::RawOrigin as SystemRawOrigin;
use xcm::latest::Junction;
pub struct MockAccountToAccountKey20<Origin, AccountId>(PhantomData<(Origin, AccountId)>);

impl<Origin: OriginTrait + Clone, AccountId: Into<H160>> Convert<Origin, MultiLocation>
	for MockAccountToAccountKey20<Origin, AccountId>
```

## Snippet 3

Context: `precompiles/xcm-utils/src/lib.rs:61` (updates aggregate accounting or lifecycle state)

Before
```rust
impl<Runtime, XcmConfig> XcmUtilsPrecompile<Runtime, XcmConfig>
where
	Runtime: pallet_evm::Config + frame_system::Config,
	XcmOriginOf<XcmConfig>: OriginTrait,
	XcmAccountIdOf<XcmConfig>: Into<H160>,
	XcmConfig: xcm_executor::Config,
{
	#[precompile::public("multilocationToAddress((uint8,bytes[]))")]
```
After
```rust
impl<Runtime, XcmConfig> XcmUtilsPrecompile<Runtime, XcmConfig>
where
	Runtime: pallet_evm::Config + frame_system::Config + pallet_xcm::Config,
	XcmOriginOf<XcmConfig>: OriginTrait,
	XcmAccountIdOf<XcmConfig>: Into<H160>,
	XcmConfig: xcm_executor::Config,
	SystemCallOf<Runtime>: Dispatchable<PostInfo = PostDispatchInfo> + Decode + GetDispatchInfo,
	<<Runtime as frame_system::Config>::RuntimeCall as Dispatchable>::RuntimeOrigin:
```

## Snippet 4

Context: `precompiles/xcm-utils/src/mock.rs:307` (updates aggregate accounting or lifecycle state)

Before
```rust
}

pub struct DoNothingRouter;
impl SendXcm for DoNothingRouter {
	fn send_xcm(_dest: impl Into<MultiLocation>, _msg: Xcm<()>) -> SendResult {
		Ok(())
	}
```
After
```rust
}

use sp_std::cell::RefCell;
use xcm::latest::opaque;
// Simulates sending a XCM message
thread_local! {
	pub static SENT_XCM: RefCell<Vec<(MultiLocation, opaque::Xcm)>> = RefCell::new(Vec::new());
}
```

# Fix Pattern

Add an early precompile-boundary selector check for a restricted function family, supported by a small bounds-checked selector parsing helper and regression-test scaffolding.

## How It Was Fixed

`precompiles/utils/src/data/mod.rs` adds `read_u32_selector` for safe raw selector parsing. `precompiles/xcm-utils/src/lib.rs` adds runtime bounds and a `#[precompile::pre_check]` hook that checks whether the input selector belongs to XCM execute selectors. Test support in `mock.rs` adds origin conversion and sent-XCM capture so tests can exercise XCM precompile behavior.

# Why It Matters

1. May preserve an intended boundary between smart contracts and XCM execute.

2. Moves restricted-call classification earlier in precompile handling.

3. Evidence supports only a narrow execute-selector restriction.

4. No supplied evidence proves exploitability or impact.

# Evidence Notes

Grounded evidence: `precompiles/xcm-utils/src/lib.rs` adds `#[precompile::pre_check]`, reads a selector, and checks `xcm_execute_selectors()`; `precompiles/utils/src/data/mod.rs` adds a bounds-checked raw selector reader; commit text includes `dont allow execute from SC`. Unsupported claims removed: accounting/state drift, phantom state, balances/counters, general XCM authorization bypass, confirmed exploitability, or production impact. The supplied snippet does not include the full rejection code after the `contains(&selector)` check. Protocol security invariant: XCM execute calls exposed through the XCM utils precompile appear intended to be restricted from smart-contract caller paths, but the supplied evidence does not fully establish the before-state behavior, the complete rejection logic, or an exploitable vulnerability. Verification notes: The patch does not prove an externally exploitable vulnerability existed in a released version. The patch does not show loss of funds, privilege escalation beyond the XCM execute call boundary, or consensus failure. Mock and test changes are not themselves production security controls. The evidence supports a smart-contract caller restriction for xcm_execute, not a general XCM authorization bypass. No commands or external inspection were performed, per instruction. Classification is limited to the provided excerpts and commit metadata. Keep out of the security corpus because the vulnerability thesis is not established by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `smart-contract-xcm-execute-restriction`
Final impact type: `authorization-boundary, restricted-call-exposure`
Final confidence: `medium`
Final tags: `blockchain-core, precompile, xcm, smart-contract-caller-restriction, security-hardening`

The supplied evidence supports a narrow security-hardening classification: the patch adds a precompile pre-check that identifies XCM execute selectors, and the commit text explicitly says not to allow execute from smart contracts. This is a security-sensitive caller-boundary restriction, but the evidence does not prove a concrete exploitable vulnerability, production exposure, or the full rejection branch, so it should not be treated as a confirmed security fix.

## Security Evidence

1. Commit body states: dont allow execute from SC.
2. Commit body mentions documentation and tests showing xcm execute is not callable by smart contracts.
3. XcmUtilsPrecompile adds a #[precompile::pre_check] hook.
4. The pre-check reads the raw ABI selector and compares it against xcm_execute_selectors().
5. A bounds-checked read_u32_selector helper was added to support early selector inspection.

## Missing Evidence

1. The supplied snippet does not show the complete rejection logic after the selector match.
2. No evidence proves that a released version allowed exploitable smart-contract-triggered XCM execute.
3. No concrete impact such as fund loss, privilege escalation result, or consensus failure is shown.
4. Mock and test scaffolding do not by themselves establish production vulnerability.

## Claim Boundaries

1. Classify only as hardening of the XCM utils precompile smart-contract caller boundary.
2. Do not claim accounting or state drift.
3. Do not claim a general XCM authorization bypass.
4. Do not claim confirmed exploitability or production impact from the provided evidence.
