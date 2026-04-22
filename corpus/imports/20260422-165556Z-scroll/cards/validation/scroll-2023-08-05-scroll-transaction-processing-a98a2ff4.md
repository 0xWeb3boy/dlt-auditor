# Validation Card

## Metadata

- ID: `scroll-2023-08-05-scroll-transaction-processing-a98a2ff4`
- Bug family: `authz_and_role_gates`
- Bug class: `authentication-challenge-replay-protection`

## What Confirmed The Issue

- Evidence 1: In `coordinator/internal/controller/api/auth.go`, the patch replaces `// check the challenge is used, if used, return failure` with `// check login parameter's token is equal to bearer token, the Authorization must be...`.
- Evidence 2: In `coordinator/internal/logic/auth/login.go`, the patch replaces `func (l *LoginLogic) InsertChallengeString(ctx *gin.Context, signature string) error {` with `func (l *LoginLogic) InsertChallengeString(ctx *gin.Context, challenge string) error {`.
- Evidence 3: In `coordinator/internal/config/config_test.go`, the patch removes `t.Run("Default MaxVerifierWorkers", func(t *testing.T) {`.

## What Could Have Invalidated It

- Compensating control 1: If the challenge is already single-use, bound to the session token, and consumed on the canonical nonce value, a similar login flow is usually safe.
- Compensating control 2: Signature-format refactors near the login path are not enough by themselves; the key issue is whether replay tracking and token binding use the same challenge.
- Compensating control 3: The evidence supports replay hardening, not a proven forged-signature or privilege-escalation exploit beyond session reuse.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: If the challenge is already single-use, bound to the session token, and consumed on the canonical nonce value, a similar login flow is usually safe.
- Caution 2: Signature-format refactors near the login path are not enough by themselves; the key issue is whether replay tracking and token binding use the same challenge.
- Caution 3: The evidence supports replay hardening, not a proven forged-signature or privilege-escalation exploit beyond session reuse.
