---
case_id: case_20240415_78eb1d663
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: medium
source_quality: high
date: 2024-04-15
source_refs:
  - git:78eb1d663346ca557292cbc4d3891278deacf456
  - "x/evm/client/wasm/query.go:265"
  - "x/evm/client/wasm/query.go:384"
  - "x/evm/client/wasm/query.go:305"
  - "x/evm/client/wasm/query.go:197"
bug_class: missing-address-association-check
impact_type:
  - identity-binding
  - access-control
tags:
  - evm
  - wasm-query
  - precompile
  - address-association
  - access-control
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes several wasm EVM query handlers so they reject unassociated Cosmos/Bech32 addresses before ABI-packing ERC20/ERC721 payloads. The strongest supported finding is a missing strict address-association check in payload construction, not a proven token-theft or consensus-impact vulnerability.

## Observed Patch Facts

1. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, owner)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(owner))`.

2. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, owner)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(owner))`.

3. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr := h.k.GetEVMAddressOrDefault(ctx, ownerAddr)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, ownerAddr)`.

4. In `x/evm/client/wasm/query.go`, the patch replaces `fromEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, from)` with `fromEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(from))`.

## Project Context

The changed code sits primarily in `x/evm/client/wasm`, `x/evm/client`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `x/evm/client/wasm/query_test.go`, `x/evm/client/wasm/encoder.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/client/wasm/bindings/queries.go`, `x/evm/client/wasm/query_test.go`. The strongest project-level identifiers around this patch are `found`, `GetEVMAddress`, `GetEVMAddressFromBech32OrDefault`, and `owner`.

## Before/After Behavior

Before the patch, handlers in x/evm/client/wasm/query.go used GetEVMAddressFromBech32OrDefault or GetEVMAddressOrDefault, allowing payload construction to continue with a default or derived EVM address when no explicit mapping was found. After the patch, the handlers call GetEVMAddress, require found == true, and return an unassociated-address error before packing the call data.

# Root Cause

The affected query handlers did not require an explicit Cosmos-to-EVM address mapping before using participant addresses in ERC20/ERC721 payload construction. They relied on default-address lookup helpers, which weakened the association requirement for those precompile-facing payload paths.

## Walkthrough

1. A wasm EVM query handler receives a request for an ERC20 or ERC721 payload/query helper.

2. The request includes participant addresses such as owner, spender, recipient, operator, or transfer sender.

3. Before the patch, those addresses could be resolved with defaulting helpers when no explicit EVM association existed.

4. The handler then used the resolved EVM address in ABI-packed call data.

5. After the patch, each relevant Cosmos address is looked up with GetEVMAddress.

6. If no stored association is found, the handler returns an error and does not build the payload.

7. Only explicitly associated accounts are used in these changed payload-generation paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/client/wasm/query.go | 194 | ERC721 transfer payload generation now rejects unassociated from and recipient accounts before packing precompile call data. |
| x/evm/client/wasm/query.go | 262 | ERC20 transferFrom payload generation now rejects unassociated owner and recipient accounts before packing precompile call data. |
| x/evm/client/wasm/query.go | 301 | ERC20 allowance query payload generation now rejects unassociated owner and spender accounts instead of using default EVM addresses. |
| x/evm/client/wasm/query.go | 381 | ERC721 approval-for-all query payload generation now rejects unassociated owner and operator accounts before constructing the call. |

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

Replace default-or-derived EVM address resolution with strict lookup plus an explicit found check before constructing precompile-related ABI payloads.

## How It Was Fixed

In x/evm/client/wasm/query.go, the patch updates ERC721 transfer payload generation, ERC20 transferFrom payload generation, ERC20 allowance payload generation, and ERC721 approval-for-all payload/query generation. Each changed path removes GetEVMAddressFromBech32OrDefault or GetEVMAddressOrDefault and rejects the request when GetEVMAddress does not find an association.

# Why It Matters

1. Maintains explicit account-to-EVM identity binding in the changed wasm query paths.

2. Prevents these helpers from silently accepting unassociated addresses through default EVM address resolution.

3. The provided evidence supports precompile-facing payload construction impact, but not arbitrary asset theft or consensus failure.

4. Regression coverage is relevant for ERC20/ERC721 participant address handling.

# Evidence Notes

Primary evidence is limited to x/evm/client/wasm/query.go snippets at the ERC721 transfer, ERC20 transferFrom, ERC20 allowance, and ERC721 isApprovedForAll handlers. The repeated replacement of default address helpers with GetEVMAddress plus found checks directly supports a missing-address-association-check finding. The broader claim that unassociated EOAs could fully use all precompiles is suggested by the commit subject and file list, but is not fully demonstrated by the provided code snippets. The heuristic serialization/state-representation finding is unsupported by the observed diff. Protocol security invariant: Wasm EVM query paths that construct ERC20/ERC721 precompile-style call payloads should not use a Cosmos/Bech32 account as an EVM address participant unless that account has an explicit stored EVM address association. Verification notes: The patch does not prove arbitrary token theft or unauthorized transfer execution by itself. The patch does not show the full precompile execution path, only the wasm/query payload construction side in the provided evidence. The patch does not prove consensus divergence or validator-level impact. The patch does not establish exploitability for every precompile listed in the commit files. The patch does not show whether default EVM address derivation was externally reachable in all affected flows. Do not claim arbitrary token theft from the provided evidence. Do not claim consensus or validator impact from the provided evidence. Do not generalize to every precompile touched by the commit without matching diff evidence. Security classification is likely rather than confirmed because the snippets show payload construction checks, not the full execution path or exploit scenario. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-address-association-check`
Final impact type: `identity-binding, access-control`
Final tags: `evm, wasm-query, precompile, address-association, access-control`

The supplied patch evidence supports security hardening: multiple EVM wasm query/payload handlers stop using default-or-derived EVM address resolution and now require an explicit stored Cosmos-to-EVM address association before constructing ERC20/ERC721 precompile-related payloads. The evidence does not prove a concrete exploitable token theft, consensus issue, or full precompile execution bypass, so security-fix is too strong and the original serialization/state-representation framing is misleading.

## Security Evidence

1. Commit subject explicitly says unassociated EOA addresses are disallowed from using precompiles.
2. Changed handlers replace GetEVMAddressFromBech32OrDefault or GetEVMAddressOrDefault with GetEVMAddress plus found checks.
3. Unassociated owner, recipient, spender, operator, and transfer sender addresses now return errors before ABI payload construction.
4. The affected code is in EVM wasm query paths for ERC20/ERC721 precompile-style operations.

## Missing Evidence

1. No full execution-path evidence showing that these payload helpers directly allowed unauthorized precompile execution.
2. No exploit scenario or demonstrated asset theft is provided.
3. No evidence supports consensus divergence or validator-level impact.
4. The snippets do not prove the issue affected every precompile touched by the commit.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Limit the claim to strict address-association enforcement in EVM wasm precompile payload/query paths.
3. Do not claim arbitrary token theft or unauthorized transfer execution from this evidence alone.
4. Do not retain the original serialization-or-state-representation bug class.
