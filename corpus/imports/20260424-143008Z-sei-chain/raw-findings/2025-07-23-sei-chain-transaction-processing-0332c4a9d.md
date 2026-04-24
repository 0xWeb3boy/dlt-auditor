---
case_id: case_20250723_0332c4a9d
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-07-23
source_refs:
  - git:0332c4a9d7fd9d367cacf5b6fc66e5b5e02b5e31
  - "x/evm/types/tx.pb.go:3957"
  - "precompiles/solo/solo.go:139"
  - "x/evm/keeper/evm.go:82"
  - "precompiles/solo/solo.go:166"
bug_class: entrypoint-scope-enforcement
impact_type:
  - authorization-scope
  - cross-runtime-access-control
confidence: medium
tags:
  - evm
  - precompile
  - claim-flow
  - access-control
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is security hardening in the Sei EVM Solo precompile. The strongest evidence is that the generic Claim entrypoint previously discarded the concrete validated claim message and then transferred all balances from the sender, while the patch keeps the message and rejects MsgClaimSpecific. The patch also blocks CosmWasm-originated calls to the Solo precompile and adds native-denom handling for ClaimSpecific. The evidence supports a likely claim-scope hardening, but not a proven exploit, theft scenario, replay issue, panic, or consensus failure.

## Observed Patch Facts

1. In `x/evm/types/tx.pb.go`, the patch replaces `default:` with `case 3:`.

2. In `precompiles/solo/solo.go`, the patch replaces `_, sender, err := p.validate(ctx, caller, args, readOnly)` with `claimMsg, sender, err := p.validate(ctx, caller, args, readOnly)`.

3. In `x/evm/keeper/evm.go`, the patch adds `if to != nil && to.Cmp(common.HexToAddress(solo.SoloAddress)) == 0 {`.

4. In `precompiles/solo/solo.go`, the patch replaces `contractAddr, err := sdk.AccAddressFromBech32(asset.GetContractAddress())` with `if asset.IsNative() {`.

## Project Context

The changed code sits primarily in `x/evm/types`, `x/evm`, `precompiles/solo`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/types/types.pb.go`, `x/evm/types/receipt.pb.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/artifacts/native/native.go`, `x/evm/artifacts/erc721/cwerc721.wasm`. The strongest project-level identifiers around this patch are `sender`, `caller`, `asset`, and `iNdEx`. Nearby tests or test-like files include `x/evm/integration_test.go`, `x/evm/blocktest/config.go`.

## Before/After Behavior

Before the patch, Claim called validate, discarded the returned claim message, and then sent all balances from sender to the caller's Sei address. After the patch, Claim retains claimMsg and rejects values implementing claimSpecificMsg with an explicit error. Before the patch, ClaimSpecific's visible path attempted contract-address handling for assets; after the patch, it handles native assets by denom and transfers only that denom balance. Before the patch, CallEVM had no visible guard against calls to solo.SoloAddress; after the patch, it rejects such calls. Before the patch, Asset.Unmarshal did not visibly decode field 3; after the patch, it decodes Denom.

# Root Cause

The generic Solo Claim entrypoint did not enforce that the validated message was appropriate for the generic all-balances claim flow. By discarding the concrete claim message returned by validate, the code lacked an explicit guard against MsgClaimSpecific reaching a path that transfers all balances. The provided evidence does not prove the surrounding signature or authorization rules, so the root cause should be framed as missing entrypoint/type-scope enforcement rather than confirmed unauthorized fund theft.

## Walkthrough

1. A caller reaches the Solo precompile Claim entrypoint with arguments that are validated into a claim message and sender address.

2. In the pre-patch Claim code, the validated message object is discarded, so the entrypoint does not visibly distinguish generic claims from MsgClaimSpecific.

3. The pre-patch Claim path then sends all balances from sender to the caller's Sei address.

4. The patched Claim path retains claimMsg and rejects claimSpecificMsg before any all-balances transfer.

5. The ClaimSpecific path validates that the message is specific-asset scoped and iterates requested assets.

6. The patch adds native-asset handling by denom in ClaimSpecific, so native denom claims can follow asset-specific transfer semantics.

7. The protobuf Asset unmarshal path now decodes Denom, supporting the native-asset path.

8. CallEVM now rejects calls targeting the Solo precompile address, narrowing a cross-runtime call path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/solo/solo.go | 139 | Claim entrypoint now rejects MsgClaimSpecific so a specific-asset claim cannot be handled by the all-balances Claim flow. |
| precompiles/solo/solo.go | 157 | ClaimSpecific entrypoint validates MsgClaimSpecific and applies asset-by-asset transfer semantics. |
| precompiles/solo/solo.go | 166 | ClaimSpecific now handles native assets by denom when transferring the sender balance to the caller's Sei address. |
| x/evm/keeper/evm.go | 82 | CallEVM now blocks CosmWasm-originated calls targeting the Solo precompile address. |
| x/evm/types/tx.pb.go | 3957 | Asset protobuf unmarshalling now decodes the Denom field used by native asset-specific claims. |

## Code Snippets

## Snippet 1

Context: `x/evm/types/tx.pb.go:3957` (changes a sensitive control or state-update path)

Before
```go
m.ContractAddress = string(dAtA[iNdEx:postIndex])
			iNdEx = postIndex
		default:
			iNdEx = preIndex
```
After
```go
m.ContractAddress = string(dAtA[iNdEx:postIndex])
			iNdEx = postIndex
		case 3:
			if wireType != 2 {
				return fmt.Errorf("proto: wrong wireType = %d for field Denom", wireType)
			}
			var stringLen uint64
			for shift := uint(0); ; shift += 7 {
```

## Snippet 2

Context: `precompiles/solo/solo.go:139` (changes a sensitive control or state-update path)

Before
```go
func (p PrecompileExecutor) Claim(ctx sdk.Context, caller common.Address, method *abi.Method, args []interface{}, readOnly bool) (ret []byte, remainingGas uint64, err error) {
	_, sender, err := p.validate(ctx, caller, args, readOnly)
	if err != nil {
		return nil, 0, err
	}
	if err := p.bankKeeper.SendCoins(ctx, sender,
		p.evmKeeper.GetSeiAddressOrDefault(ctx, caller), p.bankKeeper.GetAllBalances(ctx, sender)); err != nil {
```
After
```go
func (p PrecompileExecutor) Claim(ctx sdk.Context, caller common.Address, method *abi.Method, args []interface{}, readOnly bool) (ret []byte, remainingGas uint64, err error) {
	claimMsg, sender, err := p.validate(ctx, caller, args, readOnly)
	if err != nil {
		return nil, 0, err
	}
	_, ok := claimMsg.(claimSpecificMsg)
	if ok {
```

## Snippet 3

Context: `x/evm/keeper/evm.go:82` (changes a sensitive control or state-update path)

Before
```go
return nil, fmt.Errorf("%w: code size %v, limit %v", core.ErrMaxInitCodeSizeExceeded, len(data), params.MaxInitCodeSize)
	}
	value := utils.Big0
	if val != nil {
```
After
```go
return nil, fmt.Errorf("%w: code size %v, limit %v", core.ErrMaxInitCodeSizeExceeded, len(data), params.MaxInitCodeSize)
	}
	if to != nil && to.Cmp(common.HexToAddress(solo.SoloAddress)) == 0 {
		return nil, errors.New("cannot call Solo precompile via CosmWasm")
	}
	value := utils.Big0
	if val != nil {
```

## Snippet 4

Context: `precompiles/solo/solo.go:166` (changes persisted or aggregate state handling)

Before
```go
callerSeiAddr := p.evmKeeper.GetSeiAddressOrDefault(ctx, caller)
	for _, asset := range claimSpecificMsg.GetIAssets() {
		contractAddr, err := sdk.AccAddressFromBech32(asset.GetContractAddress())
		if err != nil {
```
After
```go
callerSeiAddr := p.evmKeeper.GetSeiAddressOrDefault(ctx, caller)
	for _, asset := range claimSpecificMsg.GetIAssets() {
		if asset.IsNative() {
			denom := asset.GetDenom()
			balance := p.bankKeeper.GetBalance(ctx, sender, denom)
			if !balance.IsZero() {
				if err := p.bankKeeper.SendCoins(ctx, sender, callerSeiAddr, sdk.NewCoins(balance)); err != nil {
					return nil, 0, err
```

# Fix Pattern

Enforce message type and call-boundary checks at precompile entrypoints before value transfer, and ensure serialized asset fields needed for scoped execution are decoded.

## How It Was Fixed

Claim was changed to capture claimMsg from validate and reject claimSpecificMsg. ClaimSpecific was extended to handle native assets by checking IsNative, reading Denom, getting the sender's balance for that denom, and sending only that denom balance. Asset unmarshalling was updated to decode Denom. CallEVM was changed to reject calls whose destination is solo.SoloAddress.

# Why It Matters

1. Specific-asset claim messages should not be processed by a generic all-balances claim path.

2. The fix aligns the validated message type with the selected precompile entrypoint before transfer.

3. Native denom claims need explicit decoding and handling to preserve scoped asset semantics.

4. The CosmWasm guard reduces exposure of the Solo precompile across runtime boundaries.

5. The evidence supports hardening, not a confirmed exploit chain.

# Evidence Notes

Grounded evidence comes from precompiles/solo/solo.go Claim retaining claimMsg and rejecting claimSpecificMsg, ClaimSpecific adding native denom transfer handling, x/evm/keeper/evm.go rejecting calls to solo.SoloAddress, and x/evm/types/tx.pb.go decoding Asset.Denom. The commit message says 'Harden solo precompile' and mentions disallowing MsgClaimSpecific in Claim and adding a check for calls from CW. The provided snippets do not show the full validate/signature rules, exact nonce increment logic, exploit preconditions, or tests proving unauthorized transfer. Protocol security invariant: Solo claim execution should preserve the authorization scope represented by the validated claim message and the selected precompile entrypoint: a specific-asset claim message should not be accepted by the generic all-balances Claim path, and cross-runtime access to the Solo precompile should be limited to intended call paths. Verification notes: The patch does not prove unauthorized third-party theft without the surrounding validate/signature rules. The patch does not prove consensus failure or node crash from the protobuf change alone. The evidence does not show the exact nonce increment logic, so replay impact is not independently validated here. The CosmWasm restriction indicates a trust-boundary hardening, but the provided context does not prove a complete exploit through CW calls. Native asset handling may be correctness or feature completion unless tied to an authorization bypass by surrounding code. Do not classify this as a panic, liveness, or protobuf parsing vulnerability based on the provided evidence. Do not claim confirmed theft or replay impact; the necessary authorization and nonce context is not shown. Treat protobuf changes as support for native asset handling, not the root cause by themselves. Treat the CosmWasm block as boundary hardening unless a complete CW exploit path is shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `entrypoint-scope-enforcement`
Final impact type: `authorization-scope, cross-runtime-access-control`
Final confidence: `medium`
Final tags: `evm, precompile, claim-flow, access-control, security-hardening`

The supplied patch evidence supports retaining this as security hardening, but not as a confirmed exploit fix. The strongest signals are explicit rejection of MsgClaimSpecific in the generic Claim path before an all-balances transfer, and blocking CosmWasm-originated calls to the Solo precompile. The original liveness-focused classification is not supported by the evidence; the validated issue is narrower entrypoint/message-scope and runtime-boundary hardening.

## Security Evidence

1. Claim now preserves the validated claimMsg and rejects claimSpecificMsg before executing the generic all-balances transfer path.
2. CallEVM now rejects calls targeting solo.SoloAddress with an explicit CosmWasm boundary error.
3. ClaimSpecific now handles native assets by denom, aligning specific-asset claim handling with scoped transfer semantics.
4. The commit message explicitly says Harden solo precompile and mentions disallowing MsgClaimSpecific in Claim plus adding a check for calls from CW.

## Missing Evidence

1. No full validate/signature logic is shown, so unauthorized transfer is not proven.
2. No exploit path through CosmWasm calls is demonstrated.
3. Nonce increment evidence is mentioned in commit metadata but not included in the supplied snippets.
4. No test output or before/after failing security test is provided.
5. The protobuf Denom decoding change may be correctness support rather than independently security relevant.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed security-fix.
2. Do not claim proven fund theft, replay, consensus failure, panic, or liveness impact from the supplied evidence.
3. Treat the CosmWasm restriction as trust-boundary narrowing unless a complete exploit chain is shown.
4. Treat native denom handling and protobuf decoding as supporting scoped claim semantics, not as the standalone vulnerability.
