# Code-Shape Card

## Metadata

- ID: `oasis-core-2022-04-20-oasis-core-rpc-client-api-a02e1e95f`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `improper-trust-verification-gating`

## Code Shape Summary

- Short description of what the buggy code looked like: The pre-patch executor readiness logic did not gate registration/availability on completion of runtime trust sync, so a runtime could be treated as available before its trust-root synchronization finished.

## Search Motifs

- Motif 1: trust root or quote policy cached without refresh on change
- Motif 2: freshness inferred from success state instead of anchored evidence
- Motif 3: session or attestation state reused after peer-set or policy change

## Typical Asymmetry

- What was checked in one path but missing in another: Trust state was initialized once, but later policy, freshness, identity, or session changes were not revalidated before reuse.

## Patch Pattern

- What the fix changed structurally: The executor now starts runtime trust sync during runtime startup, requires 'runtimeTrustSynced' before advertising availability, and cancels outstanding sync work when the runtime stops or fails. Mock runtime support was extended so the new consensus-sync request path can succeed in non-production coverage.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
