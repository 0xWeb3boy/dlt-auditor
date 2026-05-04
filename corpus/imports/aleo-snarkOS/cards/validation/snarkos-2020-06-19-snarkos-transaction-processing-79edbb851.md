# Validation Card

## Metadata

- ID: `snarkos-2020-06-19-snarkos-transaction-processing-79edbb851`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-attack-surface-reduction`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Remove the methods from the exported RPC trait/implementation surface pending a real protected wrapper or authentication scheme.
- Root-cause evidence from the finding: Not established as a vulnerability. The grounded issue is that methods associated with transaction construction and record access were present on the JSON-RPC trait while a nearby comment indicated password guarding was still unfinished. The evidence does not prove that this created an exploitable access-control flaw. 1. `RpcImpl` is registered with the JSON-RPC handler through `to_delegate()`, so trait-declared RPC methods are part of the served RPC interface. 2. Before the patch, `rpc/src/rpc_trait.

## What Could Have Invalidated It

- External authentication gates the entire RPC server.
- Removed methods were disabled or unreachable in production builds.

## Severity Guidance

- Expected impact band: `access-surface-hardening`
- Expected severity band: `low`
- Rationale: Low severity is appropriate when the affected boundary is reachable and the sink controls unnecessary privileged API exposure; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- Private-loopback-only RPC deployments reduce exploitability
- Methods that only return public chain data may not be sensitive
- A reverse proxy or RPC auth layer may already enforce access
