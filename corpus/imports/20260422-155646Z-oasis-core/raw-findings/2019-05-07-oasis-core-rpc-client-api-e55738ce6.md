---
case_id: case_20190507_e55738ce6
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2019-05-07
source_refs:
  - git:e55738ce601ce7c63624308b37cb4ac3652106eb
  - "runtime/src/rak.rs:283"
  - "runtime/src/rak.rs:271"
  - "go/keymanager/keymanager.go:106"
  - "go/keymanager/handler.go:19"
bug_class: key-scope-isolation
impact_type:
  - cross-scope-data-access
  - authenticated-response-integrity
confidence: medium
tags:
  - keymanager
  - runtime-isolation
  - local-storage
  - signing
  - attestation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is security-relevant in theme, but the provided evidence does not establish a specific pre-patch vulnerability. The grounded code changes show `RAK` signing being exposed through the shared `Signer` trait and the keymanager host handler being narrowed from generic storage access to runtime-scoped local storage access. The stronger claims about master-secret generation, per-contract derivation, and runtime-ID namespacing come primarily from the commit message, not from the shown code.

## Observed Patch Facts

1. In `runtime/src/rak.rs`, the patch adds `impl Signer for RAK {`.

2. In `runtime/src/rak.rs`, the patch replaces `/// Generate a RAK signature with the private key over the context and message.` with `/// Verify a provided RAK binding.`.

3. In `go/keymanager/keymanager.go`, the patch replaces `func (k *KeyManager) loadStateRoot() error {` with `func (k *KeyManager) worker() {`.

4. In `go/keymanager/handler.go`, the patch replaces `storage storage.Backend` with `// Local storage.`.

## Project Context

The changed code sits primarily in `runtime/src`, `go/keymanager`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `runtime/src/types.rs`, `runtime/src/dispatcher.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/types.rs`, `runtime/src/dispatcher.rs`. The strongest project-level identifiers around this patch are `inner`, `message`, `with`, and `sign`.

## Before/After Behavior

Before the change, the shown Rust code had an inherent `RAK::sign` method and the Go host handler included a generic `storage.Backend` path handling `HostStorageGetRequest`. After the change, the same signing logic is exposed via `impl Signer for RAK`, and the shown handler excerpt uses `localStorage.Get(h.runtimeID, key)` for `HostLocalStorageGetRequest`. The excerpts do not prove how these paths were used end to end or whether the old behavior was exploitable.

# Root Cause

Not established by the provided evidence. At most, the patch appears to tighten an incompletely integrated keymanager/runtime design by routing signing through a shared interface and reducing handler scope, but the snippets do not prove the original flaw beyond that.

## Walkthrough

1. `runtime/src/rak.rs` previously showed signing as an inherent `RAK::sign(&[u8; 8], ...)` method guarded by `inner.private_key`.

2. The patched `runtime/src/rak.rs` shows equivalent signing logic moved under `impl Signer for RAK`, with a `&[u8]` context type.

3. Nearby `verify_binding` code remains present in the same file, so signing and attestation-related logic are colocated, but the snippets do not show the full call path.

4. `runtime/src/dispatcher.rs` imports both `Signer` and `RAK`, which is consistent with trait-based integration, but an import alone does not prove actual response-signing behavior.

5. `go/keymanager/handler.go` removes the visible generic `storage.Backend` field from the shown struct and serves `HostLocalStorageGetRequest` through `localStorage.Get(h.runtimeID, key)`, indicating narrower storage access in the excerpt.

6. The commit message states stronger goals such as master-secret loading, per-contract derivation, and runtime-ID namespacing, but those details are not demonstrated in the provided diff snippets.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/rak.rs | 254 | RAK binding verification and enclave identity check for authenticated use of the runtime attestation key |
| runtime/src/rak.rs | 274 | RAK `Signer` implementation enabling protocol responses to be signed with the enclave-held private key |
| runtime/src/dispatcher.rs | 10 | runtime RPC/dispatch path that consumes the `Signer`/RAK capability for outbound authenticated messages |
| go/keymanager/handler.go | 18 | keymanager host request handler scoped by `runtimeID` and local storage, relevant to runtime-level key namespace isolation |
| go/keymanager/keymanager.go | 105 | keymanager service state/lifecycle path tied to persisted root state for key material management |

## Code Snippets

## Snippet 1

Context: `runtime/src/rak.rs:283` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}
}
```
After
```rust
}
}

impl Signer for RAK {
    /// Generate a RAK signature with the private key over the context and message.
    fn sign(&self, context: &[u8], message: &[u8]) -> Fallible<Signature> {
        let inner = self.inner.read().unwrap();
        match inner.private_key {
```

## Snippet 2

Context: `runtime/src/rak.rs:271` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    /// Generate a RAK signature with the private key over the context and message.
    pub fn sign(&self, context: &[u8; 8], message: &[u8]) -> Fallible<Signature> {
        let inner = self.inner.read().unwrap();
        match inner.private_key {
            Some(ref key) => Ok(key.sign(context, message)?),
            None => Err(RAKError::NotConfigured.into()),
```
After
```rust
}

    /// Verify a provided RAK binding.
    pub fn verify_binding(avr: &avr::AuthenticatedAVR, rak: &PublicKey) -> Fallible<()> {
```

## Snippet 3

Context: `go/keymanager/keymanager.go:106` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (k *KeyManager) loadStateRoot() error {
	r, err := ioutil.ReadFile(k.stateRootPath)
	if err != nil {
		// If the file does not exist, start with an empty root.
		if os.IsNotExist(err) {
			k.stateRoot.Empty()
```
After
```go
}

func (k *KeyManager) worker() {
	// Wait for the gRPC server and worker to terminate.
```

## Snippet 4

Context: `go/keymanager/handler.go:19` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
runtimeID signature.PublicKey

	storage      storage.Backend
	localStorage *host.LocalStorage
}

func (h *hostHandler) Handle(ctx context.Context, body *protocol.Body) (*protocol.Body, error) {
	// Storage.
```
After
```go
runtimeID signature.PublicKey

	localStorage *host.LocalStorage
}

func (h *hostHandler) Handle(ctx context.Context, body *protocol.Body) (*protocol.Body, error) {
	// Local storage.
	if body.HostLocalStorageGetRequest != nil {
```

# Fix Pattern

Integrate signing through the shared signer abstraction and narrow keymanager storage access to runtime-scoped local storage; additional derivation and namespacing hardening is asserted by the commit message but not directly shown here.

## How It Was Fixed

From the supplied evidence, the concrete code-level fix is limited to two visible changes: exposing `RAK` through the common `Signer` trait and replacing the shown generic storage path in the keymanager host handler with runtime-scoped local storage access. The broader hardening claims in the commit description should be treated as stated intent rather than fully validated from the snippets alone.

# Why It Matters

1. Narrower storage access can reduce accidental cross-scope data exposure.

2. Using a shared signer interface can make authenticated signing easier to apply consistently.

3. The evidence suggests hardening of key-handling boundaries.

4. The excerpts do not prove a concrete pre-patch exploit or breakage.

# Evidence Notes

The strongest code evidence is in `runtime/src/rak.rs` and `go/keymanager/handler.go`. `runtime/src/rak.rs` shows an API/integration change for signing, not a new verification rule by itself. `go/keymanager/handler.go` supports a claim of reduced storage surface, but not a full proof of cross-runtime isolation. The commit message contains the strongest security framing, so claims about master secrets, per-contract KDF behavior, and runtime-ID namespacing should be treated as partially supported intent rather than established fact from the shown diff. Protocol security invariant: Key-management responses and stored key material should be scoped to the intended runtime or contract and authenticated through the runtime attestation key when exposed over shared runtime paths. The provided snippets suggest movement toward that model, but they do not establish the full protocol or a concrete violated invariant before the patch. Verification notes: The excerpts do not prove a practical key-extraction or remote-code-execution exploit before the patch. The exact signed response format and verification path are not shown in the provided diff snippets. Cross-runtime or cross-contract key collisions are suggested by the commit message, but reachability in deployed configurations is not proven here. Part of the change may be initial secure feature enablement rather than a narrowly scoped bug fix. No test excerpt demonstrates a failing pre-patch security case. No provided snippet shows the full response-signing call chain end to end. No provided snippet shows the actual master-secret or per-contract derivation logic. The evidence supports security relevance, but not a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `key-scope-isolation`
Final impact type: `cross-scope-data-access, authenticated-response-integrity`
Final confidence: `medium`
Final tags: `keymanager, runtime-isolation, local-storage, signing, attestation`

The supplied patch evidence supports a security-hardening reading, not a confirmed vulnerability fix. The strongest grounded change is in the keymanager host handler, where generic storage access is replaced by runtime-scoped local storage lookup using `h.runtimeID`, which clearly narrows access to sensitive key material. The RAK changes also show signing being wired through a shared `Signer` interface in an attestation-sensitive area, consistent with authenticated-response hardening. However, the excerpts do not prove a concrete exploitable pre-patch flaw, so this should be retained only as a conservative hardening case.

## Security Evidence

1. `go/keymanager/handler.go` removes the visible generic `storage.Backend` path and serves `HostLocalStorageGetRequest` via `localStorage.Get(h.runtimeID, key)`.
2. The handler change introduces explicit runtime scoping for storage access, which is a security-sensitive boundary for key management.
3. `runtime/src/rak.rs` adds `impl Signer for RAK`, connecting response signing to the runtime attestation key path.
4. The RAK code sits next to binding verification logic, reinforcing that the modified path is security-sensitive rather than routine refactoring.
5. The commit message explicitly frames the change as secure key derivation and runtime namespacing, which matches the direction of the shown code even if not fully proven by it.

## Missing Evidence

1. No provided diff shows the full pre-patch storage path end to end or demonstrates that cross-runtime access was previously reachable.
2. No excerpt shows the master-secret generation or per-contract derivation logic mentioned in the commit body.
3. No test snippet demonstrates a failing pre-patch security case or a reproduced exploit scenario.
4. No evidence shows how `impl Signer for RAK` changed actual caller behavior on the wire.

## Claim Boundaries

1. Do not claim a confirmed exploitable vulnerability from the patch alone.
2. Do not keep the original `serialization-or-state-representation` bug class; the evidence points more narrowly to key scoping and authenticated signing.
3. It is supported to say the patch tightens runtime-scoped key access and authenticated response handling.
4. It is not supported to assert proven key leakage, cross-contract compromise, or a specific attacker model from the supplied snippets.
