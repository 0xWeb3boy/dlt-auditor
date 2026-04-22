---
case_id: case_20190823_4333549d8
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: medium
source_quality: high
date: 2019-08-23
source_refs:
  - git:4333549d8dc37dfebf850f6980b3d7e0ac6d54c2
  - "go/common/sgx/ias/grpc.go:94"
  - "go/ekiden/cmd/ias/proxy.go:76"
  - "go/ekiden/cmd/ias/proxy.go:201"
  - "go/ekiden/cmd/ias/proxy.go:170"
bug_class: missing-authentication
impact_type:
  - unauthorized-request-processing
  - attestation-policy-bypass
tags:
  - authentication
  - attestation
  - rpc
  - sgx
  - ias
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The strongest supported reading is that this patch fixes a missing validation step in the IAS VerifyEvidence handler. Before the change, the handler decoded the request and then hit a TODO describing required authentication and enclave-policy checks without performing them. After the change, it calls an authenticator and rejects the request on failure. The proxy changes mostly support wiring and make a skip-auth development mode explicit.

## Observed Patch Facts

1. In `go/common/sgx/ias/grpc.go`, the patch replaces `// TODO: Authenticate/validate the verification request.` with `s.logger.Warn("malformed Evidence",`.

2. In `go/ekiden/cmd/ias/proxy.go`, the patch replaces `if !viper.GetBool(cfgDebugMock) {` with `endpoint, err := iasEndpointFromFlags()`.

3. In `go/ekiden/cmd/ias/proxy.go`, the patch replaces `endpoint, err := ias.NewIASEndpoint(cfg)` with `return ias.NewIASEndpoint(cfg)`.

4. In `go/ekiden/cmd/ias/proxy.go`, the patch replaces `return fmt.Errorf("ias: invalid signature type: %s", quoteSigType)` with `return nil, fmt.Errorf("ias: invalid signature type: %s", quoteSigType)`.

## Project Context

The changed code sits primarily in `go/common/sgx/ias`, `go/common/sgx`, `go/ekiden/cmd/ias`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `go/common/sgx/ias/ias.go`, `go/ekiden/cmd/ias/auth_genesis.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/common/sgx/ias/ias.go`, `go/ekiden/cmd/registry/entity/entity.go`. The strongest project-level identifiers around this patch are `logger`, `viper`, `endpoint`, and `signed`.

## Before/After Behavior

Before the patch, VerifyEvidence in go/common/sgx/ias/grpc.go accepted requests that were structurally valid enough to decode and open, then continued past comments saying authentication and quote validation still needed to happen. After the patch, the handler invokes s.authenticator.VerifyEvidence(...) immediately after decoding the evidence and returns an error if that check fails. In proxy.go, authenticator setup is separated and the skip-auth path is made explicit and warned about, but that support code is not the primary root cause.

# Root Cause

A security-sensitive RPC handler relied on comments describing required authorization and attestation-policy checks instead of enforcing those checks in code after parsing the request.

## Walkthrough

1. VerifyEvidence first unmarshals SignedEvidence from the protobuf request and rejects malformed input.

2. It then opens the signed payload into Evidence.

3. In the pre-patch code, execution reached a TODO that explicitly said the request still needed authentication and validation, including signer-key and quote-policy checks.

4. The patch adds s.authenticator.VerifyEvidence(signed.Signed.Signature.PublicKey, &ev) at that point.

5. If the authenticator rejects the request, the handler now logs a warning and returns an error instead of continuing.

6. Proxy-side changes factor endpoint/authenticator construction and expose a clearly logged debug skip-auth mode, which supports the new enforcement path but is not itself the main bug fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/common/sgx/ias/grpc.go | 85 | `VerifyEvidence` handler now authenticates the signer key and evidence before proceeding. |
| go/ekiden/cmd/ias/proxy.go | 160 | Builds IAS endpoint configuration and separates production auth material from debug/mock behavior. |
| go/ekiden/cmd/ias/proxy.go | 201 | Initializes and wires the gRPC authenticator, including explicit skip-auth development mode. |

## Code Snippets

## Snippet 1

Context: `go/common/sgx/ias/grpc.go:94` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
var ev Evidence
	if err := signed.Open(EvidenceSignatureContext, &ev); err != nil {
		return nil, err
	}

	// TODO: Authenticate/validate the verification request.
	//  * signed.Signature.PublicKey MUST be in the entity registry.
	//  * ev.Quote MUST be well-formed and for an approved MRENCLAVE.
```
After
```go
var ev Evidence
	if err := signed.Open(EvidenceSignatureContext, &ev); err != nil {
		s.logger.Warn("malformed Evidence",
			"err", err,
		)
		return nil, err
	}
```

## Snippet 2

Context: `go/ekiden/cmd/ias/proxy.go:76` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	if !viper.GetBool(cfgDebugMock) {
		if viper.GetString(cfgAuthCertFile) == "" {
			logger.Error("auth cert not configured")
			return
		}
		if viper.GetString(cfgAuthKeyFile) == "" {
```
After
```go
}

	endpoint, err := iasEndpointFromFlags()
	if err != nil {
		logger.Error("failed to initialize IAS endpoint",
			"err", err,
		)
		return
```

## Snippet 3

Context: `go/ekiden/cmd/ias/proxy.go:201` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	endpoint, err := ias.NewIASEndpoint(cfg)
	if err != nil {
		return err
	}

	ias.NewGRPCServer(env.grpcSrv.Server(), endpoint)
```
After
```go
}

	return ias.NewIASEndpoint(cfg)
}

func grpcAuthenticatorFromFlags() (ias.GRPCAuthenticator, error) {
	if viper.GetBool(cfgDebugSkipAuth) {
		logger.Warn("IAS gRPC authentication disabled, proxy is open")
```

## Snippet 4

Context: `go/ekiden/cmd/ias/proxy.go:170` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
cfg.QuoteSignatureType = ias.SignatureLinkable
	default:
		return fmt.Errorf("ias: invalid signature type: %s", quoteSigType)
	}
```
After
```go
cfg.QuoteSignatureType = ias.SignatureLinkable
	default:
		return nil, fmt.Errorf("ias: invalid signature type: %s", quoteSigType)
	}
```

# Fix Pattern

Insert an explicit authorization/policy check in the request handler immediately after structural decoding, and isolate any intentional bypass behind an explicit debug-only configuration path.

## How It Was Fixed

The fix adds a mandatory authenticator call in the VerifyEvidence handler using the request signer key and decoded evidence, and aborts the RPC when that validation fails. Related proxy changes centralize endpoint/authenticator creation and make the development skip-auth mode explicit rather than leaving enforcement absent in the normal handler path.

# Why It Matters

1. Structurally valid evidence was not enough to guarantee the request met the intended trust policy.

2. The trust decision moved from a TODO comment into executed code that can reject invalid requests.

3. The debug bypass is now explicit and logged instead of being indistinguishable from missing enforcement.

# Evidence Notes

Direct evidence is strongest in go/common/sgx/ias/grpc.go: the old code contains a TODO stating that authentication and validation still must happen, and the new code adds s.authenticator.VerifyEvidence(...) with an error return on failure. go/ekiden/cmd/ias/proxy.go supports this by adding explicit authenticator construction and a warned cfgDebugSkipAuth branch. The commit subject mentions MRSIGNER/MRENCLAVE, but the provided diff does not show those exact comparisons, so that detail should be treated as inferred rather than directly proven here. Protocol security invariant: The IAS VerifyEvidence RPC must not accept a request solely because its SignedEvidence blob parses; it must also enforce the configured attestation policy for the caller and decoded evidence before proceeding. Verification notes: The patch shows missing request authentication/policy enforcement, but does not by itself prove a practical remote exploit path in a deployed configuration. The exact `MRSIGNER`/`MRENCLAVE` matching logic is inferred from the commit subject and comments; the full authenticator implementation is not shown here. The diff does not demonstrate quote forgery, cryptographic breakage, or replay bypass beyond acceptance of unauthorized or policy-invalid evidence. The presence of a debug skip-auth option does not prove production systems exposed that mode. Directly shown: missing handler-side validation was replaced with a real authenticator call. Directly shown: failure of that authenticator now causes the RPC to return an error. Not shown: the internal logic of s.authenticator.VerifyEvidence, so exact policy details are not visible in this evidence. Not shown: proof that any production deployment enabled the debug skip-auth mode. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `missing-authentication`
Final impact type: `unauthorized-request-processing, attestation-policy-bypass`
Final tags: `authentication, attestation, rpc, sgx, ias`

This belongs in a security corpus, but the original phase-3 labeling is misleading. The patch evidence does not support a serialization or state-representation issue; it directly shows a security-sensitive RPC handler moving from a TODO for authentication and enclave-policy validation to an enforced authenticator check that rejects the request on failure. That is strong evidence of a real security fix for missing request/authz-style validation on attestation evidence, even though the exact internal policy logic and deploy-time exposure are not fully shown.

## Security Evidence

1. Pre-patch `VerifyEvidence` contained a TODO stating the request still needed authentication and quote/MRENCLAVE validation.
2. Post-patch `VerifyEvidence` calls `s.authenticator.VerifyEvidence(...)` immediately after decoding the evidence.
3. The handler now returns an error when authenticator validation fails, changing acceptance behavior rather than only logging or refactoring.
4. Proxy-side changes add explicit authenticator wiring and a warned `debugSkipAuth` mode that says the proxy is open, reinforcing that authentication is now expected by default.

## Missing Evidence

1. The implementation of `s.authenticator.VerifyEvidence` is not shown, so the exact MRSIGNER/MRENCLAVE checks are not directly visible.
2. The patch does not prove a demonstrated exploit or confirm how widely the vulnerable path was exposed in production.
3. No provided test evidence shows concrete before/after acceptance of unauthorized evidence.

## Claim Boundaries

1. Supported: the handler previously lacked an executed authentication/validation step after parsing signed evidence.
2. Supported: the patch makes failed authenticator validation reject the RPC request.
3. Not directly shown: the precise attestation-policy rules enforced inside the authenticator.
4. Not directly shown: any broader impact beyond acceptance of unauthorized or policy-invalid `VerifyEvidence` requests.
