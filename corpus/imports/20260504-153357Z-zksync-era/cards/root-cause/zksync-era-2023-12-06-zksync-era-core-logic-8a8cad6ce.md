# Root-Cause Card

## Metadata

- ID: `zksync-era-2023-12-06-zksync-era-core-logic-8a8cad6ce`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `dependency-vulnerability-remediation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `dependency-advisory-gating`

## Violated Invariant

- Invariant: Security-sensitive services should not ship a dependency graph that includes a known vulnerable cryptographic package on an auth or storage path.

## Trust Boundary

- Boundary: Maintainer dependency selection crosses into the production object-store authentication dependency graph.

## Attack Surface

- Entrypoint type: Build-time dependency resolution.
- Sensitive sink: Cloud object-store authentication and cryptographic helper code pulled into runtime.

## Impact Pattern

- Primary impact: Timing-side-channel risk reduction for a known vulnerable transitive RSA dependency.
- Secondary impact: Advisory/deny-list compliance for production dependency graphs.

## Short Reusable Lesson

- Treat dependency advisories as security boundaries when the vulnerable crate is pulled through production auth, storage, crypto, or networking paths. Keep the claim at dependency-hardening level unless reachability and exploitability are proven.
