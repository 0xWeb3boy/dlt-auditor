# Validation Card

## Metadata

- ID: `snarkos-2020-08-15-snarkos-transaction-processing-8b5ad567b`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `confirmed` and kept in the security corpus.
- The patch pattern matches the missing property: Move record methods to protected RPC wrappers and call validate_auth(meta) before parsing params or invoking record logic.
- Root-cause evidence from the finding: Record RPC logic was present on the public RPC implementation path instead of being consistently routed through protected wrappers that enforce validate_auth(meta). 1. rpc/src/rpc_trait.rs identifies RpcFunctions as the public RPC endpoint surface. 2. The before evidence for rpc/src/rpc_impl.rs shows a record handling section under impl RpcFunctions for RpcImpl, including decrypt_record. 3. The patch evidence shows that record handling section removed from the displayed public implementation are

## What Could Have Invalidated It

- Node config binds RPC to localhost with mandatory auth proxy.
- The endpoint is never registered in production.

## Severity Guidance

- Expected impact band: `privileged-disclosure`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls unauthorized record RPC access; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- Read-only public record metadata may be intentionally unauthenticated
- External RPC auth can compensate if it is mandatory
- Do not infer private-key compromise from record API movement alone
