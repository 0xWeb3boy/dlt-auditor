# Validation Card

## Metadata

- ID: `rippled-2018-08-10-rippled-access-control-38c3a46a3`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: Commit message explicitly describes security implications of divulging account seeds to the server and possible clear-text or command-line exposure.
- Evidence 2: doSign, doSignFor, and sign-and-submit doSubmit paths now check context.role != Role::ADMIN && !context.app.config().canSign() before signing behavior.

## What Could Have Invalidated It

- Compensating control 1: No evidence proves actual seed theft, interception, or transaction forgery occurred.
- Compensating control 2: No evidence proves all deployments exposed these commands remotely or unauthenticated.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: privilege-misuse
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No evidence proves actual seed theft, interception, or transaction forgery occurred.
- Caution 2: No evidence proves all deployments exposed these commands remotely or unauthenticated.
