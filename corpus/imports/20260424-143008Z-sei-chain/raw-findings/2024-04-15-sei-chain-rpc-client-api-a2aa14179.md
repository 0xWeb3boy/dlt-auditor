---
case_id: case_20240415_a2aa14179
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
  - git:a2aa1417909f14c78227ac7fa1873bc4d326a595
  - "x/evm/client/wasm/query.go:265"
  - "x/evm/client/wasm/query.go:384"
  - "x/evm/client/wasm/query.go:305"
  - "x/evm/client/wasm/query.go:197"
bug_class: missing-address-association-check
impact_type:
  - identity-binding
  - access-control-hardening
confidence: medium
tags:
  - evm
  - wasm
  - precompile
  - address-association
  - identity-binding
  - access-control
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch replaces defaulting address-conversion helpers with explicit EVM address lookups plus `found` checks in several `x/evm/client/wasm/query.go` ERC20/ERC721 helper paths. Unassociated Bech32 addresses now cause an error before ABI payload/query data is packed. This is plausibly security relevant as an identity-binding hardening or missing-check fix, but the supplied evidence does not prove that the previous behavior enabled unauthorized precompile execution, asset movement, or privilege escalation.

## Observed Patch Facts

1. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, owner)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(owner))`.

2. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, owner)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(owner))`.

3. In `x/evm/client/wasm/query.go`, the patch replaces `ownerEvmAddr := h.k.GetEVMAddressOrDefault(ctx, ownerAddr)` with `ownerEvmAddr, found := h.k.GetEVMAddress(ctx, ownerAddr)`.

4. In `x/evm/client/wasm/query.go`, the patch replaces `fromEvmAddr, err := h.k.GetEVMAddressFromBech32OrDefault(ctx, from)` with `fromEvmAddr, found := h.k.GetEVMAddress(ctx, sdk.MustAccAddressFromBech32(from))`.

## Project Context

The changed code sits primarily in `x/evm/client/wasm`, `x/evm/client`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `x/evm/client/wasm/query_test.go`, `x/evm/client/wasm/encoder.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/client/wasm/bindings/queries.go`, `x/evm/client/wasm/query_test.go`. The strongest project-level identifiers around this patch are `found`, `GetEVMAddress`, `GetEVMAddressFromBech32OrDefault`, and `owner`.

## Before/After Behavior

Before the patch, selected wasm EVM ERC20/ERC721 helper functions used `GetEVMAddressFromBech32OrDefault` or `GetEVMAddressOrDefault`, allowing address conversion to proceed without an explicit `found` check in the caller. After the patch, the handlers call `GetEVMAddress`, check whether a stored mapping exists, and return a not-associated error if it does not.

# Root Cause

The immediate cause was that wasm EVM helper code used defaulting address conversion for some Bech32 address parameters instead of requiring an explicit stored Cosmos-to-EVM mapping. The evidence does not show enough about the defaulting helpers or downstream execution path to prove a concrete vulnerability beyond missing association enforcement in these helper paths.

## Walkthrough

1. A wasm EVM ERC20 or ERC721 helper receives Bech32 address inputs such as `from`, `recipient`, `owner`, `spender`, or `operator`.

2. Before the patch, several paths converted those inputs using defaulting helpers like `GetEVMAddressFromBech32OrDefault` or `GetEVMAddressOrDefault`.

3. The caller code did not explicitly reject cases where no stored EVM address association existed.

4. The converted EVM addresses were then used for ABI packing of payload/query data.

5. After the patch, the same paths call `GetEVMAddress` with an SDK account address.

6. If the lookup returns `found == false`, the handler returns an association error and stops before ABI packing.

7. The provided diff demonstrates stricter address-association enforcement in these helper functions, not a fully demonstrated exploit chain.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/client/wasm/query.go | 194 | ERC721 transfer payload now requires both from and recipient Bech32 addresses to have stored EVM address associations before ABI packing. |
| x/evm/client/wasm/query.go | 262 | ERC20 transferFrom payload now requires owner and recipient to be associated before encoding EVM addresses. |
| x/evm/client/wasm/query.go | 301 | ERC20 allowance query now requires owner and spender to be associated instead of using default-derived EVM addresses. |
| x/evm/client/wasm/query.go | 381 | ERC721 isApprovedForAll query now requires owner and operator to be associated before encoding the call. |

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

Replace default-or-derived address conversion with explicit lookup and negative-path rejection before constructing EVM call payloads or query data.

## How It Was Fixed

`HandleERC721TransferPayload`, `HandleERC20TransferFromPayload`, `HandleERC20Allowance`, and `HandleERC721IsApprovedForAll` were changed to call `GetEVMAddress` and reject missing mappings. The patch removes caller reliance on `GetEVMAddressFromBech32OrDefault` or `GetEVMAddressOrDefault` in the shown paths.

# Why It Matters

1. Prevents these helpers from silently converting unassociated Bech32 addresses into EVM address parameters.

2. Strengthens Cosmos-to-EVM identity binding for selected wasm EVM ERC20/ERC721 helper calls.

3. May prevent unintended precompile or token-call payload construction for unassociated accounts.

4. Evidence does not establish asset theft, privilege escalation, consensus impact, or full unauthorized execution.

# Evidence Notes

Grounded evidence comes from `x/evm/client/wasm/query.go` changes at ERC721 transfer payload, ERC20 transferFrom payload, ERC20 allowance, and ERC721 isApprovedForAll handlers. The before snippets show defaulting helpers; the after snippets show `GetEVMAddress` and `!found` errors. Related context shows these are wasm EVM query/helper interfaces. The evidence does not show the implementation of the defaulting helpers, the full precompile execution path, or tests proving an exploitable security failure. Protocol security invariant: Cosmos/Bech32 addresses should only be converted to EVM addresses for wasm EVM ERC20/ERC721 helper calls when an explicit stored address association exists. The provided evidence shows this invariant being enforced in selected wasm query/payload helpers, but does not establish the full exploitability or execution path. Verification notes: The patch evidence does not prove successful asset theft or privilege escalation by itself. The patch evidence does not show the full transaction execution path for every precompile touched in the commit file list. The patch evidence does not establish consensus failure or validator-level impact. The patch evidence supports an address-association enforcement fix, not a serialization or canonical-state-object fix. Confirmed by provided snippets: defaulting helpers were replaced by explicit lookup plus `found` checks. Commit subject supports security relevance but is not enough by itself to prove vulnerability impact. No provided evidence demonstrates unauthorized state change, asset loss, privilege escalation, or consensus failure. Classified as unclear rather than confirmed security-fix because the vulnerability thesis is plausible but incomplete. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-address-association-check`
Final impact type: `identity-binding, access-control-hardening`
Final confidence: `medium`
Final tags: `evm, wasm, precompile, address-association, identity-binding, access-control, security-hardening`

The supplied patch evidence supports retaining this as security hardening. Multiple wasm EVM ERC20/ERC721 helper paths stopped using default address-conversion helpers and now require an explicit stored Cosmos-to-EVM address association before packing precompile call data. The evidence does not prove a concrete exploit, asset theft, or unauthorized state transition, so it should not be upgraded to a confirmed security-fix. The original serialization/state-representation framing is misleading; the supported issue is missing address-association enforcement.

## Security Evidence

1. Commit subject explicitly says unassociated EOA addresses are disallowed from using precompiles.
2. ERC20 transferFrom payload generation now rejects owner and recipient addresses without stored EVM associations.
3. ERC721 transfer payload generation now rejects from and recipient addresses without stored EVM associations.
4. ERC20 allowance and ERC721 approval queries now reject unassociated owner/spender/operator addresses.
5. The changed code constructs EVM/precompile call payloads for token-related operations, a security-sensitive identity boundary.

## Missing Evidence

1. No supplied evidence shows the implementation or exact behavior of the removed defaulting helpers.
2. No supplied test or trace demonstrates unauthorized precompile execution before the patch.
3. No supplied evidence proves asset loss, privilege escalation, or consensus impact.
4. The evidence is limited mainly to helper/query payload construction, not the full execution path.

## Claim Boundaries

1. Classify as security-hardening, not a proven exploitable security-fix.
2. Supported claim is stricter Cosmos-to-EVM address association enforcement for selected wasm EVM helper paths.
3. Do not claim confirmed theft, authorization bypass in execution, or validator/consensus compromise.
4. Do not retain the original serialization-or-state-representation bug class as the final framing.
