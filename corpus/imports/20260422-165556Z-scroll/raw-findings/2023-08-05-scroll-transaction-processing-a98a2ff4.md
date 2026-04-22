---
case_id: case_20230805_a98a2ff4
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
impact_type:
  - request-forgery-or-replay
confidence: medium
source_quality: high
date: 2023-08-05
source_refs:
  - git:a98a2ff4b5f0c3749d54fef63faa1bbca09b5cc2
  - "coordinator/internal/controller/api/auth.go:32"
  - "coordinator/internal/logic/auth/login.go:21"
  - "coordinator/internal/config/config_test.go:88"
  - "coordinator/internal/config/config_test.go:47"
bug_class: authentication-challenge-replay-protection
tags:
  - authentication
  - replay-protection
  - challenge-binding
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best supported as an authentication replay fix in the coordinator login path. The visible code adds an explicit equality check between the Authorization bearer token and login.Message.Challenge, and changes replay tracking from storing login.Signature to storing login.Message.Challenge. That is grounded evidence of fixing nonce/challenge binding and replay consumption in login.

## Observed Patch Facts

1. In `coordinator/internal/controller/api/auth.go`, the patch replaces `// check the challenge is used, if used, return failure` with `// check login parameter's token is equal to bearer token, the Authorization must be...`.

2. In `coordinator/internal/logic/auth/login.go`, the patch replaces `func (l *LoginLogic) InsertChallengeString(ctx *gin.Context, signature string) error {` with `func (l *LoginLogic) InsertChallengeString(ctx *gin.Context, challenge string) error {`.

3. In `coordinator/internal/config/config_test.go`, the patch removes `t.Run("Default MaxVerifierWorkers", func(t *testing.T) {`.

4. In `coordinator/internal/config/config_test.go`, the patch replaces `config := fmt.Sprintf(configTemplate, defaultNumberOfSessionRetryAttempts, defaultNum...` with `_, err = tmpFile.WriteString(configTemplate)`.

## Project Context

The changed code sits primarily in `coordinator/internal/controller/api`, `coordinator/internal/controller`, `coordinator/internal/logic/auth`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `coordinator/internal/config/config.go`, `coordinator/internal/controller/api/submit_proof.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `coordinator/internal/orm/orm_test.go`, `coordinator/internal/logic/verifier/verifier_test.go`. The strongest project-level identifiers around this patch are `challenge`, `assert`, `tmpFile`, and `NoError`.

## Before/After Behavior

Before the patch, AuthController.Login called InsertChallengeString with login.Signature even though the nearby comment said it was checking whether the challenge had been used, and there was no shown check that the Authorization header matched login.Message.Challenge. After the patch, the handler rejects requests unless Authorization is exactly "Bearer " plus login.Message.Challenge, and it records login.Message.Challenge rather than login.Signature in the replay-tracking path.

# Root Cause

The shown login code used the signature field where the code comments and function naming indicate challenge replay tracking was intended, and it did not visibly enforce that the bearer token matched the submitted challenge. That mismatch weakens replay protection around the challenge value.

## Walkthrough

1. The login handler binds a request containing Message.Challenge and Signature.

2. In the pre-patch code, the replay-related call inserts login.Signature, despite the surrounding comment referring to challenge reuse.

3. The logic-layer helper also took a parameter named signature and passed it to challengeOrm.InsertChallenge, so the stored replay key followed the signature field.

4. The patch adds a controller-side check that Authorization must equal "Bearer " plus login.Message.Challenge.

5. The patch also changes the replay insertion call to use login.Message.Challenge, and the helper is renamed accordingly.

6. The config test edits shown separately do not add evidence for or against the auth finding.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| coordinator/internal/controller/api/auth.go | 29 | login endpoint for prover authentication |
| coordinator/internal/controller/api/auth.go | 32 | enforces Authorization bearer token equals submitted challenge before accepting login |
| coordinator/internal/logic/auth/login.go | 21 | records/checks used login nonce by challenge value for replay prevention |

## Code Snippets

## Snippet 1

Context: `coordinator/internal/controller/api/auth.go:32` (changes signature or replay validation logic)

Before
```go
return "", fmt.Errorf("missing the public_key, err:%w", err)
	}
	// check the challenge is used, if used, return failure
	if err := a.loginLogic.InsertChallengeString(c, login.Signature); err != nil {
		return "", fmt.Errorf("login insert challenge string failure:%w", err)
	}
```
After
```go
return "", fmt.Errorf("missing the public_key, err:%w", err)
	}

	// check login parameter's token is equal to bearer token, the Authorization must be existed
	// if not exist, the jwt token will intercept it
	brearToken := c.GetHeader("Authorization")
	if brearToken != "Bearer "+login.Message.Challenge {
		return "", fmt.Errorf("check challenge failure for the not equal challenge string")
```

## Snippet 2

Context: `coordinator/internal/logic/auth/login.go:21` (changes signature or replay validation logic)

Before
```go
// InsertChallengeString insert and check the challenge string is existed
func (l *LoginLogic) InsertChallengeString(ctx *gin.Context, signature string) error {
	return l.challengeOrm.InsertChallenge(ctx, signature)
}
```
After
```go
// InsertChallengeString insert and check the challenge string is existed
func (l *LoginLogic) InsertChallengeString(ctx *gin.Context, challenge string) error {
	return l.challengeOrm.InsertChallenge(ctx, challenge)
}
```

## Snippet 3

Context: `coordinator/internal/config/config_test.go:88` (changes the branch that decides whether execution stops or continues)

Before
```go
assert.Error(t, err)
	})

	t.Run("Default MaxVerifierWorkers", func(t *testing.T) {
		tmpFile, err := os.CreateTemp("", "example")
		assert.NoError(t, err)
		defer func() {
			assert.NoError(t, tmpFile.Close())
```
After
```go
assert.Error(t, err)
	})
}
```

## Snippet 4

Context: `coordinator/internal/config/config_test.go:47` (changes a sensitive control or state-update path)

Before
```go
assert.NoError(t, os.Remove(tmpFile.Name()))
		}()
		config := fmt.Sprintf(configTemplate, defaultNumberOfSessionRetryAttempts, defaultNumberOfVerifierWorkers)
		_, err = tmpFile.WriteString(config)
		assert.NoError(t, err)
```
After
```go
assert.NoError(t, os.Remove(tmpFile.Name()))
		}()
		_, err = tmpFile.WriteString(configTemplate)
		assert.NoError(t, err)
```

# Fix Pattern

Bind duplicated authentication inputs to each other at the controller boundary, and key replay prevention on the actual nonce/challenge field rather than on an adjacent artifact.

## How It Was Fixed

The fix adds a direct comparison between the Authorization header and login.Message.Challenge in the login controller, then switches the replay-consumption path to store the challenge value itself. The corresponding logic helper was updated from a signature parameter to a challenge parameter so the replay store tracks the same field the protocol is treating as the one-time token.

# Why It Matters

1. Replay protection is only meaningful if it consumes the field that is meant to be single-use.

2. If the request body challenge and bearer token are not explicitly bound, mismatched values can pass deeper into the login path.

3. The patch supports a narrow replay/binding conclusion, not a broader claim that signature verification was generally broken.

# Evidence Notes

Primary evidence is limited but direct: auth.go adds an Authorization-versus-challenge equality check and changes InsertChallengeString from login.Signature to login.Message.Challenge; login.go updates the helper to accept and forward challenge instead of signature. The commit subject explicitly says "fix login replay attack," which matches the code shape. Claims about challenge issuance, expiry behavior, JWT middleware semantics, or a separate signature-validation flaw are not established by the provided diff and are intentionally excluded. Protocol security invariant: In the login flow, the challenge value appears to be the replay-sensitive authentication token. The request should only be accepted when the challenge presented in the request body is bound to the request's Authorization bearer token, and replay tracking should consume that challenge value itself rather than a different field such as the signature. Verification notes: The patch does not prove the exact exploit preconditions beyond replay or rebinding of a previously issued challenge. The evidence does not show whether signature verification itself was broken; the visible fix is about nonce binding and replay tracking. The patch does not establish how challenges are generated, expired, or authenticated elsewhere in the system. The config test changes do not demonstrate an additional security issue. The auth finding is grounded in the shown before/after code, not just the commit subject. Confidence is medium rather than high because the full login flow, challenge generation, and downstream verification are not shown. The config_test.go changes are ancillary test maintenance based on the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authentication-challenge-replay-protection`
Final tags: `authentication, replay-protection, challenge-binding`

The patch is clearly security-relevant in the login path, but the visible evidence is stronger for hardening than for a fully proven exploitable vulnerability. The code adds explicit binding between the bearer token and the submitted challenge, and it changes replay tracking to consume the challenge value instead of the signature. That supports retaining the case in a security corpus, but the provided diff does not conclusively prove the exact pre-patch exploit conditions or justify the broader original "signature validation" framing.

## Security Evidence

1. `AuthController.Login` now rejects requests unless `Authorization` equals `Bearer ` plus `login.Message.Challenge`.
2. The replay-consumption call changed from `InsertChallengeString(c, login.Signature)` to `InsertChallengeString(c, login.Message.Challenge)`.
3. `LoginLogic.InsertChallengeString` was updated to take and forward a `challenge` value, matching the replay-oriented comment and ORM call.
4. The changed code is in the authentication/login controller and logic, which is a security-sensitive path.

## Missing Evidence

1. The full login flow is not shown, including signature verification and how challenges are issued or validated elsewhere.
2. The patch does not prove a concrete exploit path or show an end-to-end replay succeeding before the change.
3. The evidence does not establish whether the signature format was deterministic or otherwise insufficient for replay prevention on its own.
4. Ancillary config test edits do not add support for the security claim.

## Claim Boundaries

1. This supports a narrow claim about tightening challenge binding and replay protection in login.
2. This does not establish a general signature-validation vulnerability across the subsystem.
3. This does not prove a concrete authentication bypass beyond increased replay or rebinding risk.
4. The evidence should not be stretched to broader transaction-processing or database-security claims.
