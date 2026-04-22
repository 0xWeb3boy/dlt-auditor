---
case_id: case_20190603_3f0716ecd
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: medium
source_quality: medium
date: 2019-06-03
source_refs:
  - git:3f0716ecdacc6e825478b8e05a1d8e98de851a81
  - "go/common/crypto/signature/signature.go:522"
  - "go/common/crypto/signature/signature.go:110"
  - "go/common/crypto/signature/signature.go:81"
  - "go/worker/keymanager/keymanager.go:464"
bug_class: non-production-credential-acceptance
impact_type:
  - policy-bypass
tags:
  - cryptography
  - signature-verification
  - test-keys
  - key-management
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a policy layer to shared signature verification so explicitly registered test public keys can be rejected by default. The evidence supports security hardening around acceptance of test-only credentials, but it does not by itself prove a concrete production exploit path.

## Observed Patch Facts

1. In `go/common/crypto/signature/signature.go`, the patch replaces `func digest(context, message []byte) ([]byte, error) {` with `// RegisterTestPublicKey registers a hardcoded test public key with the`.

2. In `go/common/crypto/signature/signature.go`, the patch adds `if _, isBlacklisted := blacklistedPublicKeys.Load(k.ToMapKey()); isBlacklisted {`.

3. In `go/common/crypto/signature/signature.go`, the patch adds `testPublicKeys sync.Map`.

4. In `go/worker/keymanager/keymanager.go`, the patch adds `signature.RegisterTestPublicKey(testPublicKey)`.

## Project Context

The changed code sits primarily in `go/common/crypto/signature`, `go/common/crypto`, `go/worker/keymanager`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `go/worker/keymanager/handler.go`, `go/worker/keymanager/grpc.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/txnscheduler/worker.go`, `go/worker/txnscheduler/grpc.go`. The strongest project-level identifiers around this patch are `RegisterTestPublicKey`, `testPublicKeys`, `blacklistedPublicKeys`, and `ToMapKey`. Nearby tests or test-like files include `go/worker/txnscheduler/tests/tester.go`, `go/worker/txnscheduler/algorithm/tests/tester.go`.

## Before/After Behavior

Before the patch, the shown `PublicKey.Verify` path only checked basic lengths before continuing to digest and signature verification, with no visible reject path for designated test keys. After the patch, the signature package can register test public keys, build a blacklist from them when test keys are not allowed, and `PublicKey.Verify` returns `false` for blacklisted keys before cryptographic verification. The keymanager module also registers its hardcoded test public key into this mechanism. The provided snippets do not show the call site that activates `BuildPublicKeyBlacklist`; that behavior is supported by the commit message, not by the shown diff alone.

# Root Cause

The shared verifier treated structurally valid keys with correct signatures as acceptable without a separate policy check for designated test-only keys. That meant acceptance depended only on cryptographic validity, not on whether a key was meant for non-production use.

## Walkthrough

1. `go/common/crypto/signature/signature.go` adds package-level `testPublicKeys` and `blacklistedPublicKeys` maps.

2. The same file adds `RegisterTestPublicKey`, which records a public key in the test-key set.

3. It also adds `BuildPublicKeyBlacklist(allowTestKeys bool)`, which copies registered test keys into the active blacklist when test keys are not allowed.

4. `PublicKey.Verify` now checks `blacklistedPublicKeys` and immediately returns `false` for a blacklisted key before digesting or verifying the signature.

5. `go/worker/keymanager/keymanager.go` registers its hardcoded `testPublicKey` through `signature.RegisterTestPublicKey(testPublicKey)`, bringing that specific key under the new policy.

6. The commit body states the intended result: unless `debug.allow_test_keys` is enabled, registered test keys fail signature verification even if the signature is correct.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/common/crypto/signature/signature.go | 101 | shared signature verification now rejects blacklisted/test public keys before cryptographic verification |
| go/common/crypto/signature/signature.go | 520 | registers test public keys and builds the runtime blacklist depending on `debug.allow_test_keys` |
| go/worker/keymanager/keymanager.go | 463 | registers a hardcoded keymanager test public key as a test-only credential |

## Code Snippets

## Snippet 1

Context: `go/common/crypto/signature/signature.go:522` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func digest(context, message []byte) ([]byte, error) {
	if len(context) != ContextSize {
```
After
```go
}

// RegisterTestPublicKey registers a hardcoded test public key with the
// internal public key blacklist.
func RegisterTestPublicKey(pk PublicKey) {
	testPublicKeys.Store(pk.ToMapKey(), true)
}
```

## Snippet 2

Context: `go/common/crypto/signature/signature.go:110` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return false
	}

	data, err := digest(context, message)
```
After
```go
return false
	}
	if _, isBlacklisted := blacklistedPublicKeys.Load(k.ToMapKey()); isBlacklisted {
		return false
	}

	data, err := digest(context, message)
```

## Snippet 3

Context: `go/common/crypto/signature/signature.go:81` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
_ encoding.BinaryUnmarshaler = (*RawSignature)(nil)
	_ encoding.BinaryUnmarshaler = (*PrivateKey)(nil)
)
```
After
```go
_ encoding.BinaryUnmarshaler = (*RawSignature)(nil)
	_ encoding.BinaryUnmarshaler = (*PrivateKey)(nil)

	testPublicKeys        sync.Map
	blacklistedPublicKeys sync.Map
)
```

## Snippet 4

Context: `go/worker/keymanager/keymanager.go:464` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
emptyRoot.Empty()
	_ = testPublicKey.UnmarshalHex("9d41a874b80e39a40c9644e964f0e4f967100c91654bfd7666435fe906af060f")
}
```
After
```go
emptyRoot.Empty()
	_ = testPublicKey.UnmarshalHex("9d41a874b80e39a40c9644e964f0e4f967100c91654bfd7666435fe906af060f")
	signature.RegisterTestPublicKey(testPublicKey)
}
```

# Fix Pattern

Add a centralized deny policy in the shared verifier for explicitly registered non-production keys.

## How It Was Fixed

The fix introduced explicit registration of test public keys, a blacklist derived from that registration when test keys are disallowed, and an early blacklist check inside `PublicKey.Verify`. A hardcoded keymanager test key is then registered so it is covered by the shared verification policy.

# Why It Matters

1. Known test keys can no longer pass the shared verifier by default.

2. The policy is enforced in common verification code instead of relying on individual callers.

3. The evidence supports protection for explicitly registered test keys, not a broader cryptographic flaw.

# Evidence Notes

Direct evidence shows new test-key registration state, a blacklist check in `PublicKey.Verify`, and registration of a hardcoded keymanager test key. The commit message explicitly says registered test keys should fail verification unless `debug.allow_test_keys` is set. The provided excerpts do not show the caller that invokes `BuildPublicKeyBlacklist`, do not identify all protocol paths that use this verifier, and do not prove that the matching private key was exploitable in production. Protocol security invariant: When test keys are disallowed, public keys explicitly designated as test-only must not pass the shared signature verification path, even if the signature is otherwise valid. Verification notes: The patch does not prove that an attacker could use the corresponding private test key on a live network. It does not show which exact protocol messages or identities were reachable through this verification path. It does not indicate a break in the signature algorithm itself; the change is policy enforcement around accepted keys. It does not prove impact beyond the registered test-key set, even though the verification function is shared. The shared verifier behavior change is directly visible in the provided diff. Activation of the blacklist depends on a call path not shown in the supplied snippets. No supplied evidence proves live-network exploitability or impact beyond registered test keys. A touched test file is listed in commit metadata, but no test diff was provided here. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `non-production-credential-acceptance`
Final impact type: `policy-bypass`
Final tags: `cryptography, signature-verification, test-keys, key-management`

The patch clearly hardens a security-sensitive verification path by making explicitly registered test public keys fail signature verification unless a debug allowance is enabled. The code evidence shows a new blacklist mechanism, an enforcement check in shared signature verification, and registration of a hardcoded test key. That supports retaining this as security hardening. However, the supplied patch does not prove a concrete exploitable production vulnerability, does not show all activation call paths, and does not establish actual unauthorized access in the wild, so this should not be elevated to a confirmed security-fix case.

## Security Evidence

1. Shared signature verification now rejects blacklisted public keys before cryptographic verification proceeds.
2. The patch introduces explicit tracking of test public keys and a blacklist derived from them.
3. A hardcoded keymanager test public key is registered into the new deny mechanism.
4. The commit message states that registered test keys should fail verification unless `debug.allow_test_keys` is enabled.

## Missing Evidence

1. No supplied diff shows where `BuildPublicKeyBlacklist` is invoked in production paths.
2. No evidence proves the corresponding private test key was usable by attackers on a live network.
3. No provided patch snippet shows which externally reachable protocol messages depended on this verifier.
4. No test diff is included here to demonstrate the intended security invariant end to end.

## Claim Boundaries

1. This supports hardening around rejection of designated test-only keys, not a flaw in the signature algorithm itself.
2. The evidence supports policy enforcement in shared verification code, not a proven authentication bypass exploit.
3. Impact should be limited to acceptance of registered test keys; broader protocol compromise is not shown.
4. The original phase-3 metadata about serialization/state representation and rpc-client-api is not supported by the supplied patch evidence.
