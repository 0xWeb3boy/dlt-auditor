# Code-Shape Card

## Metadata

- ID: `oasis-core-2022-04-20-oasis-core-rpc-client-api-40afd4203`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `trust-root-verification`

## Code Shape Summary

- Short description of what the buggy code looked like: The availability state machine did not include completion of runtime trust synchronization as a prerequisite for registration or advertised availability.

## Search Motifs

- Motif 1: trust root or quote policy cached without refresh on change
- Motif 2: freshness inferred from success state instead of anchored evidence
- Motif 3: session or attestation state reused after peer-set or policy change

## Typical Asymmetry

- What was checked in one path but missing in another: Trust state was initialized once, but later policy, freshness, identity, or session changes were not revalidated before reuse.

## Patch Pattern

- What the fix changed structurally: The change introduces 'runtimeTrustSynced' into the availability condition, resets that state on runtime start, initiates trust synchronization, and cancels outstanding sync work on stop or failure. Supporting mock code was updated to accept 'RuntimeConsensusSyncRequest'.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
