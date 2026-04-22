# Code-Shape Card

## Metadata

- ID: `oasis-core-2023-04-12-oasis-core-cryptography-97f265501`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-secret-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The supported evidence points to weaker pre-patch state selection and scoping in the rotation path: the code depended on a single fetched master-secret candidate, and the shown proposal helper API was less explicitly bound to runtime and generation. That supports a narrow thesis of validation/scoping hardening, but not a proven exploitable vulnerability.

## Search Motifs

- Motif 1: trust root or quote policy cached without refresh on change
- Motif 2: freshness inferred from success state instead of anchored evidence
- Motif 3: session or attestation state reused after peer-set or policy change

## Typical Asymmetry

- What was checked in one path but missing in another: Trust state was initialized once, but later policy, freshness, identity, or session changes were not revalidated before reuse.

## Patch Pattern

- What the fix changed structurally: The patch swaps one-shot secret fetches for provider-backed iteration so non-matching replicated candidates can be skipped, constrains startup ephemeral-secret import to a recent bounded range, and makes proposal persistence explicitly runtime/generation-scoped in the shown tests. These changes harden integrity and robustness of the rotation flow, but the supplied evidence does not prove a full attack scenario.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
