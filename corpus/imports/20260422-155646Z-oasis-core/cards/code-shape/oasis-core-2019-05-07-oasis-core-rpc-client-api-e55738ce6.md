# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-05-07-oasis-core-rpc-client-api-e55738ce6`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `key-scope-isolation`

## Code Shape Summary

- Short description of what the buggy code looked like: Not established by the provided evidence. At most, the patch appears to tighten an incompletely integrated keymanager/runtime design by routing signing through a shared interface and reducing handler scope, but the snippets do not prove the original flaw beyond that.

## Search Motifs

- Motif 1: trust root or quote policy cached without refresh on change
- Motif 2: freshness inferred from success state instead of anchored evidence
- Motif 3: session or attestation state reused after peer-set or policy change

## Typical Asymmetry

- What was checked in one path but missing in another: Trust state was initialized once, but later policy, freshness, identity, or session changes were not revalidated before reuse.

## Patch Pattern

- What the fix changed structurally: From the supplied evidence, the concrete code-level fix is limited to two visible changes: exposing 'RAK' through the common 'Signer' trait and replacing the shown generic storage path in the keymanager host handler with runtime-scoped local storage access. The broader hardening claims in the commit description should be treated as stated intent rather than fully validated from the snippets alone.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
