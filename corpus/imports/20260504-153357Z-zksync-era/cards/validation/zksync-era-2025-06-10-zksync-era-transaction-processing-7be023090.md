# Validation Card

## Metadata

- ID: `zksync-era-2025-06-10-zksync-era-transaction-processing-7be023090`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: The default RPC handler previously forwarded caller-supplied unknown methods and params to `targetRpcUrl`.
- Evidence 2: The patched default handler returns `unauthorized(id)`, and the handler registry moves toward explicit allowed handlers.

## What Could Have Invalidated It

- Compensating control 1: The private RPC service is unreachable by untrusted callers.
- Compensating control 2: The upstream RPC target independently enforces an equivalent allowlist for all sensitive methods.

## Severity Guidance

- Expected impact band: access-control
- Expected severity band: high

## False-Positive Cautions

- Caution 1: Severity depends on which upstream methods are reachable and what privileges they expose.
- Caution 2: Claims about estimate-gas or state overrides require direct validation hunks, not just commit intent.
