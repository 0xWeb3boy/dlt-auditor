---
case_id: case_20200123_d5cc58f88
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2020-01-23
source_refs:
  - git:d5cc58f88b11d1dbabb23a21727f7360ed683f1f
  - "go/consensus/tendermint/apps/registry/transactions.go:190"
  - "go/registry/api/api.go:404"
  - "go/registry/api/api.go:513"
  - "go/registry/api/api.go:658"
bug_class: insufficient-signature-verification
impact_type:
  - unauthorized-registration
confidence: medium
tags:
  - cryptography
  - signature-validation
  - proof-of-possession
  - node-registration
  - multisig
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes an authentication/integrity weakness in node registration by moving from a narrower signer model to explicit multisignature proof checks. The supplied hunks show that registration now requires the node identity key and the embedded consensus key to have signed the descriptor, rejects descriptors with unexpected signers, and binds the transaction signer to the node or authorized entity instead of a generic descriptor signer.

## Observed Patch Facts

1. In `go/consensus/tendermint/apps/registry/transactions.go`, the patch replaces `// Make sure the signer of the transaction matches the signer of the node.` with `// Make sure the signer of the transaction is the node identity key`.

2. In `go/registry/api/api.go`, the patch replaces `var expectedSigner signature.PublicKey` with `// Descriptors will always be signed by the node identity key.`.

3. In `go/registry/api/api.go`, the patch replaces `consensusAddressRequired := n.HasRoles(ConsensusAddressRequiredRoles)` with `if !sigNode.MultiSigned.IsSignedBy(n.Consensus.ID) {`.

4. In `go/registry/api/api.go`, the patch replaces `return &n, runtimes, nil` with `// Ensure that only the expected signatures are present, and nothing more.`.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/apps/registry`, `go/consensus/tendermint/apps`, `go/registry/api`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/registry/api/runtime.go`, `go/consensus/tendermint/apps/registry/registry.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/registry/api/runtime.go`, `go/consensus/tendermint/apps/registry/registry.go`. The strongest project-level identifiers around this patch are `sigNode`, `signer`, `entity`, and `transaction`. Nearby tests or test-like files include `go/registry/tests/tester.go`.

## Before/After Behavior

Before the patch, the shown code used a single-signer model (`expectedSigner`) and the transaction path compared `ctx.TxSigner()` to `sigNode.Signature.PublicKey`. The provided pre-change snippet does not show a requirement that the embedded consensus key also sign the descriptor. After the patch, validation requires `sigNode.MultiSigned.IsSignedBy(n.ID)`, requires `sigNode.MultiSigned.IsSignedBy(n.Consensus.ID)`, rejects unexpected signers with `IsOnlySignedBy(expectedSigners)`, and checks that the transaction signer is the node ID or the entity ID when the registration is entity-signed.

# Root Cause

Node registration validation was centered on a single accepted descriptor signer instead of requiring proof that specific security-relevant keys embedded in the descriptor had actually signed it, and the transaction authorization check was tied to the descriptor signer rather than directly to the authorized node/entity principal.

## Walkthrough

1. `registerNode` in `go/consensus/tendermint/apps/registry/transactions.go` stops comparing the transaction signer to `sigNode.Signature.PublicKey` and instead derives an authorized signer from the node ID or entity ID.

2. `VerifyRegisterNodeArgs` in `go/registry/api/api.go` changes from a single `expectedSigner` path to `expectedSigners` and explicitly requires the node identity key to have signed.

3. The same function now rejects a descriptor if `sigNode.MultiSigned.IsSignedBy(n.Consensus.ID)` is false after validating the consensus ID.

4. Near the end of validation, `sigNode.MultiSigned.IsOnlySignedBy(expectedSigners)` rejects descriptors that carry signatures outside the expected signer set.

5. The commit message states a broader proof-of-possession goal for descriptor keys, but the supplied code evidence directly demonstrates the node identity and consensus-key checks.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/registry/api/api.go | 357 | core RegisterNode argument validation; opens multisigned node descriptor and requires node identity participation in the signature set |
| go/registry/api/api.go | 507 | enforces proof-of-possession for the consensus key embedded in the node descriptor |
| go/registry/api/api.go | 652 | rejects descriptors carrying signatures outside the expected signer set |
| go/consensus/tendermint/apps/registry/transactions.go | 184 | state-changing registration path; binds transaction signer to node identity or authorized entity for entity-signed registrations |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/apps/registry/transactions.go:190` (changes signature or replay validation logic)

Before
```go
}

	// Make sure the signer of the transaction matches the signer of the node.
	// NOTE: If this is invoked during InitChain then there is no actual transaction
	//       and thus no transaction signer so we must skip this check.
	if !ctx.IsInitChain() && !sigNode.Signature.PublicKey.Equal(ctx.TxSigner()) {
		return registry.ErrIncorrectTxSigner
	}
```
After
```go
}

	// Make sure the signer of the transaction is the node identity key
	// or the entity (iff the registration is entity signed).
	// NOTE: If this is invoked during InitChain then there is no actual transaction
	//       and thus no transaction signer so we must skip this check.
	if !ctx.IsInitChain() {
		expectedTxSigner := newNode.ID
```

## Snippet 2

Context: `go/registry/api/api.go:404` (changes signature or replay validation logic)

Before
```go
}

	var expectedSigner signature.PublicKey
	if inEntityNodeList {
		expectedSigner = n.ID
	} else if entity.AllowEntitySignedNodes {
		expectedSigner = entity.ID
	} else {
```
After
```go
}

	// Descriptors will always be signed by the node identity key.
	var expectedSigners []signature.PublicKey
	if !sigNode.MultiSigned.IsSignedBy(n.ID) {
		logger.Error("RegisterNode: registration not signed by node identity",
			"signed_node", sigNode,
			"node", n,
```

## Snippet 3

Context: `go/registry/api/api.go:513` (changes a consensus- or validator-sensitive branch)

Before
```go
return nil, nil, fmt.Errorf("%w: invalid consensus ID", ErrInvalidArgument)
	}
	consensusAddressRequired := n.HasRoles(ConsensusAddressRequiredRoles)
	if err := verifyAddresses(params, consensusAddressRequired, n.Consensus.Addresses); err != nil {
```
After
```go
return nil, nil, fmt.Errorf("%w: invalid consensus ID", ErrInvalidArgument)
	}
	if !sigNode.MultiSigned.IsSignedBy(n.Consensus.ID) {
		logger.Error("RegisterNode: not signed by consensus ID",
			"signed_node", sigNode,
			"node", n,
		)
		return nil, nil, fmt.Errorf("%w: registration not signed by consensus ID", ErrInvalidArgument)
```

## Snippet 4

Context: `go/registry/api/api.go:658` (changes signature or replay validation logic)

Before
```go
}

	return &n, runtimes, nil
}

// VerifyNodeRuntimeEnclaveIDs verifies TEE-specific attributes of the node's runtime.
func VerifyNodeRuntimeEnclaveIDs(logger *logging.Logger, rt *node.Runtime, regRt *Runtime, ts time.Time) error {
```
After
```go
}

	// Ensure that only the expected signatures are present, and nothing more.
	if !sigNode.MultiSigned.IsOnlySignedBy(expectedSigners) {
		logger.Error("RegisterNode: unexpected number of signatures",
			"signed_node", sigNode,
			"node", n,
		)
```

# Fix Pattern

Replace single-signer acceptance with explicit multisignature proof checks for required embedded keys, and separately bind the state-changing transaction to the authorized submitting principal.

## How It Was Fixed

The fix introduces multisigned descriptor verification in the node registration path. The shown code now requires signatures from the node identity key and consensus key, accumulates the allowed signer set, rejects descriptors with unexpected signers, and authorizes the transaction based on the node or authorized entity instead of the descriptor's generic signer field.

# Why It Matters

1. A node descriptor can no longer pass the shown checks with only one acceptable signer while omitting the consensus key's participation.

2. Registry state is more tightly bound to actual control of the keys advertised in the descriptor.

3. Transaction submission authority is narrowed to the node or authorized entity, reducing signer ambiguity.

# Evidence Notes

Direct evidence is limited to `go/registry/api/api.go` and `go/consensus/tendermint/apps/registry/transactions.go`. Those hunks clearly show new multisignature checks for the node identity key, the consensus key, exact-signer-set enforcement, and a stricter transaction-signer check. The commit message mentions p2p and TLS certificate keys as well, but those checks are not directly shown in the provided snippets, so they should be treated as commit-level context rather than demonstrated diff evidence. Protocol security invariant: Node registration must not accept a descriptor unless the authorized registration principal submits it and the descriptor carries signatures from the required keys it embeds. In the provided evidence, that is directly shown for the node identity key and the consensus key, with rejection of unexpected extra signers. Verification notes: The patch shows stronger descriptor authentication, but it does not by itself prove a publicly exploitable attack path. The provided evidence does not establish whether prior abuse required entity-level authorization or could be performed by a broader attacker set. The diff shows signature-binding changes, not a demonstrated replay flaw or confidentiality impact. The exact p2p/TLS verification lines are described in the commit message but are not all present in the provided hunks. Security relevance is established by direct changes to authentication/signature validation in the node registration path. The exact broader signer set beyond node identity and consensus key is not fully proven from the supplied hunks. No concrete exploit chain is shown, but the pre/post behavior directly evidences a fixed proof-of-possession gap. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-signature-verification`
Final impact type: `unauthorized-registration`
Final confidence: `medium`
Final tags: `cryptography, signature-validation, proof-of-possession, node-registration, multisig`

The supplied patch evidence shows a clear tightening of authentication and proof-of-possession checks in the node registration path: descriptors must now carry signatures from specific embedded keys, unexpected signers are rejected, and the transaction signer is bound to the node or authorized entity. That is security-relevant and fits a security-hardening entry. However, the patch alone does not confidently prove a concrete exploitable vulnerability, replay condition, or the full broader scope claimed in the generated finding.

## Security Evidence

1. Registration validation now requires the node identity key to have signed the descriptor.
2. Registration validation now requires the embedded consensus key to have signed the descriptor.
3. The code rejects descriptors signed by keys outside the expected signer set.
4. The transaction signer check is tightened to the node ID or authorized entity instead of a generic descriptor signer.
5. The commit message explicitly frames the change as proof of possession for descriptor keys.

## Missing Evidence

1. No concrete exploit path or attacker workflow is shown in the provided patch.
2. The provided hunks do not directly show the p2p and TLS certificate signature checks mentioned in the commit message.
3. The evidence does not prove a replay bug specifically.
4. The patch does not establish how broadly the pre-change behavior was exploitable in practice.

## Claim Boundaries

1. Supported claim: node registration authentication/proof-of-possession checks were strengthened.
2. Supported claim: prior validation was less strict about which keys had to sign a descriptor.
3. Not supported from the patch alone: a confirmed replay vulnerability.
4. Not supported from the patch alone: full proof that p2p and TLS key enforcement was added, beyond commit-message context.
5. Not supported from the patch alone: a demonstrated externally exploitable security incident.
