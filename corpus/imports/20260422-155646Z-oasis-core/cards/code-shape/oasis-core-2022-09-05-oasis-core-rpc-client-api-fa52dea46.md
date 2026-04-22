# Code-Shape Card

## Metadata

- ID: `oasis-core-2022-09-05-oasis-core-rpc-client-api-fa52dea46`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `freshness-verification`

## Code Shape Summary

- Short description of what the buggy code looked like: Not established by the provided evidence. The observable change is that the runtime-host path previously lacked an end-to-end way to submit a freshness-related transaction and receive a consensus inclusion proof back through the API layers. The excerpts do not show whether stale TEE evidence was previously accepted, where verification happened, or whether this is a new feature versus a fix for an exploitable bug.

## Search Motifs

- Motif 1: trust root or quote policy cached without refresh on change
- Motif 2: freshness inferred from success state instead of anchored evidence
- Motif 3: session or attestation state reused after peer-set or policy change

## Typical Asymmetry

- What was checked in one path but missing in another: Trust state was initialized once, but later policy, freshness, identity, or session changes were not revalidated before reuse.

## Patch Pattern

- What the fix changed structurally: The patch introduces a 'ProveFreshness' host handler that submits a dedicated registry transaction and receives a proof of inclusion. Supporting APIs were added so the proof can be produced by the backend and returned over gRPC instead of collapsing the operation to success-or-error only. The supplied excerpts do not show the consuming verifier logic.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
