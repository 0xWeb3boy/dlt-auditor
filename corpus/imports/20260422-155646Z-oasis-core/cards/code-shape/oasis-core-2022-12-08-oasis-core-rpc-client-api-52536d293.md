# Code-Shape Card

## Metadata

- ID: `oasis-core-2022-12-08-oasis-core-rpc-client-api-52536d293`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `quote-policy-synchronization`

## Code Shape Summary

- Short description of what the buggy code looked like: The pre-fix design appears to have lacked an explicit mechanism to keep key-manager quote-policy state synchronized inside the runtime, especially across epoch/redeploy-driven changes. The evidence supports a state-synchronization gap in attestation policy handling more clearly than a proven verification bypass.

## Search Motifs

- Motif 1: trust root or quote policy cached without refresh on change
- Motif 2: freshness inferred from success state instead of anchored evidence
- Motif 3: session or attestation state reused after peer-set or policy change

## Typical Asymmetry

- What was checked in one path but missing in another: Trust state was initialized once, but later policy, freshness, identity, or session changes were not revalidated before reuse.

## Patch Pattern

- What the fix changed structurally: The fix introduces quote-policy update delivery into the runtime, adds epoch-based refresh logic because quote policy may change on redeploy, and adds a runtime-side handler to receive the new policy state. This makes the quote policy available to the runtime along the same trust path as other key-manager policy updates.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
