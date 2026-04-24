# Validation Card

## Metadata

- ID: `rippled-2013-01-18-rippled-access-control-bda80d414`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says the RPC admin access security model changed.
- Evidence 2: WebSocket RPC no longer dispatches all non-public requests as RPCHandler::ADMIN and instead calls iAdminGet.

## What Could Have Invalidated It

- Compensating control 1: No iAdminGet implementation is supplied to confirm exact credential or policy behavior.
- Compensating control 2: No evidence shows whether the affected RPC listeners were reachable by untrusted attackers.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: privilege-misuse
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No iAdminGet implementation is supplied to confirm exact credential or policy behavior.
- Caution 2: No evidence shows whether the affected RPC listeners were reachable by untrusted attackers.
