---
case_id: case_20240415_56ce9a974
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2024-04-15
source_refs:
  - git:56ce9a9741acdf61a6b83564ce0f7596c6e9ce6d
  - "x/evm/client/wasm/query.go:265"
  - "x/evm/client/wasm/query.go:384"
  - "x/evm/client/wasm/query.go:305"
  - "x/evm/client/wasm/query.go:197"
bug_class: identity-binding-hardening
impact_type:
  - identity-confusion
  - unauthorized-operation-prevention
confidence: medium
tags:
  - evm
  - wasm-query-api
  - precompile
  - address-association
  - identity-binding
  - fail-closed
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes several wasm EVM query payload builders to reject unassociated Bech32 accounts before ABI packing. This is security-relevant identity-binding hardening, but the provided evidence only shows query/payload-construction paths and does not establish a concrete vulnerability or exploit impact.

## Observed Patch Facts

1. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, owner)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(owner))`.

2. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, owner)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(owner))`.

3. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr := h.k.GetEVMAddressOrDefault(ctx, ownerAddr)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, ownerAddr)`.

4. In `x/evm/client/wasm/query.go`, the patch replaces `fromEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, from)` with `fromEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(from))`.

## Project Context

The changed code sits primarily in `x/evm/client/wasm`, `x/evm/client`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `x/evm/client/wasm/query_test.go`, `x/evm/client/wasm/encoder.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/client/wasm/bindings/queries.go`, `x/evm/client/wasm/query_test.go`. The strongest project-level identifiers around this patch are `found`, `GetEVMAddress`, `GetEVMAddressFromBech32OrDefault`, and `owner`.

## Before/After Behavior

Before the patch, affected handlers in `x/evm/client/wasm/query.go` used `GetEVMAddressFromBech32OrDefault` or `GetEVMAddressOrDefault`, allowing payload construction to proceed without a visible association check at those call sites. After the patch, the handlers call `GetEVMAddress` and return an `is not associated` error when no mapping is found.

# Root Cause

The affected payload builders used defaulting address-resolution helpers instead of requiring an explicit state-backed EVM address mapping. The evidence does not prove that this defaulting behavior was exploitable beyond allowing payload construction for unassociated accounts.

## Walkthrough

1. The changed handlers build ABI payloads for ERC20/ERC721-related wasm EVM queries.

2. They convert Bech32 account strings such as owner, recipient, spender, operator, or from into EVM addresses before packing the ABI call data.

3. Before the patch, those conversions used helpers that could return a default EVM address without a shown association check.

4. After the patch, each shown path looks up the EVM address mapping with `GetEVMAddress` and checks `found`.

5. If no mapping exists, the handler returns an error before ABI packing.

6. The supplied evidence does not show the full execution path or demonstrate asset theft, privilege escalation, consensus impact, or another concrete exploit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/client/wasm/query.go | 197 | ERC721 transfer payload construction now rejects unassociated from/recipient accounts instead of using default EVM addresses. |
| x/evm/client/wasm/query.go | 265 | ERC20 transferFrom payload construction now requires associated owner and recipient EVM mappings. |
| x/evm/client/wasm/query.go | 305 | ERC20 allowance query payload construction now requires associated owner and spender mappings. |
| x/evm/client/wasm/query.go | 384 | ERC721 isApprovedForAll payload construction now requires associated owner and operator mappings. |

## Code Snippets

## Snippet 1

Context: `x/evm/client/wasm/query.go:265` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return nil, err
	}
	ownerEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, owner)
	if err != nil {
		return nil, err
	}
	recipientEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, recipient)
	if err != nil {
```
After
```go
return nil, err
	}
	ownerEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(owner))
	if !found {
		return nil, fmt.Errorf("%s is not associated", owner)
	}
	recipientEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(recipient))
	if !found {
```

## Snippet 2

Context: `x/evm/client/wasm/query.go:384` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return nil, err
	}
	ownerEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, owner)
	if err != nil {
		return nil, err
	}
	operatorEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, operator)
	if err != nil {
```
After
```go
return nil, err
	}
	ownerEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(owner))
	if !found {
		return nil, fmt.Errorf("%s is not associated", owner)
	}
	operatorEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(operator))
	if !found {
```

## Snippet 3

Context: `x/evm/client/wasm/query.go:305` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return nil, err
	}
	ownerEvmAddr := h.k.GetEVMAddressOrDefault(ctx, ownerAddr)

	// Get the evm address of spender
	spenderEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, spender)
	if err != nil {
		return nil, err
```
After
```go
return nil, err
	}
	ownerEvmAddr, found := h.k.GetEVMAddress(ctx, ownerAddr)
	if !found {
		return nil, fmt.Errorf("owner %s is not associated", ownerAddr.String())
	}

	// Get the evm address of spender
```

## Snippet 4

Context: `x/evm/client/wasm/query.go:197` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return nil, err
	}
	fromEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, from)
	if err != nil {
		return nil, err
	}
	toEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, recipient)
	if err != nil {
```
After
```go
return nil, err
	}
	fromEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(from))
	if !found {
		return nil, fmt.Errorf("%s is not associated", from)
	}
	toEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(recipient))
	if !found {
```

# Fix Pattern

Replace default-derived address resolution with explicit state-backed lookup and fail closed when no association exists.

## How It Was Fixed

`HandleERC721TransferPayload`, `HandleERC20TransferFromPayload`, `HandleERC20Allowance`, and `HandleERC721IsApprovedForAll` now call `GetEVMAddress(ctx, sdk.AccAddress)` and check the returned `found` value. Missing associations now produce errors instead of ABI payloads using default-derived EVM addresses.

# Why It Matters

1. Enforces explicit address association in the shown payload builders.

2. Prevents silent use of default-derived EVM identities in these paths.

3. May reduce identity-confusion risk around precompile-related call data.

4. Impact beyond payload construction is not established by the provided evidence.

# Evidence Notes

Primary evidence is limited to snippets from `x/evm/client/wasm/query.go` around lines 197, 265, 305, and 384. The commit subject supports the intended policy change, but the provided code evidence does not show the complete runtime precompile authorization path or prove exploitability. Claims about theft, consensus failure, or broad precompile access control would be unsupported. Protocol security invariant: Accounts used as EVM identities in these wasm EVM query payload builders should have an explicit EVM address association recorded in state rather than relying on a default-derived EVM address. Verification notes: The patch evidence does not prove that funds or NFTs could be stolen. The patch evidence does not show a consensus split or validator-level failure. The patch evidence does not prove exploitability beyond unintended use of default-derived EVM identities. The provided snippets focus on wasm query payload builders, not the full runtime execution path for every precompile. Confirmed by provided diff snippets: defaulting helpers were replaced with `GetEVMAddress` plus `found` checks. Tests are mentioned and some related tests show mapped addresses before successful payload construction, but no negative test evidence is included in the supplied snippets. Security relevance is plausible, but vulnerability classification remains unproven from the provided evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `identity-binding-hardening`
Final impact type: `identity-confusion, unauthorized-operation-prevention`
Final confidence: `medium`
Final tags: `evm, wasm-query-api, precompile, address-association, identity-binding, fail-closed`

The supplied patch evidence supports a conservative security-hardening classification. Multiple wasm EVM payload builders for ERC20/ERC721 operations changed from default-derived address resolution to explicit state-backed EVM address lookup, returning an error when the Bech32 account is not associated. This tightens identity binding in security-sensitive asset and approval-related paths, but the evidence does not prove a concrete exploitable vulnerability or full runtime precompile authorization failure.

## Security Evidence

1. Commit subject explicitly says unassociated EOA addresses are disallowed from using precompiles.
2. Affected handlers build ERC20/ERC721 transfer, transferFrom, allowance, and approval-related ABI payloads.
3. Defaulting helpers such as GetEVMAddressFromBech32OrDefault and GetEVMAddressOrDefault were replaced with GetEVMAddress plus found checks.
4. Missing address associations now fail closed with is-not-associated errors before ABI packing.

## Missing Evidence

1. No supplied evidence shows an end-to-end exploit path.
2. No supplied evidence proves funds, NFTs, approvals, or privileges could actually be taken or misused.
3. No full precompile execution or authorization path is shown.
4. No negative regression test snippets are provided for unassociated addresses.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Limit claims to rejecting unassociated addresses in the shown wasm EVM query payload builders.
3. Do not claim asset theft, consensus impact, or validator compromise from the supplied evidence.
4. Do not generalize to every precompile path beyond the changed functions shown.
