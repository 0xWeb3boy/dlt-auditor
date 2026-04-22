# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-06-03-oasis-core-rpc-client-api-3f0716ecd`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `non-production-credential-acceptance`

## Code Shape Summary

- Short description of what the buggy code looked like: The shared verifier treated structurally valid keys with correct signatures as acceptable without a separate policy check for designated test-only keys. That meant acceptance depended only on cryptographic validity, not on whether a key was meant for non-production use.

## Search Motifs

- Motif 1: trust root or quote policy cached without refresh on change
- Motif 2: freshness inferred from success state instead of anchored evidence
- Motif 3: session or attestation state reused after peer-set or policy change

## Typical Asymmetry

- What was checked in one path but missing in another: Trust state was initialized once, but later policy, freshness, identity, or session changes were not revalidated before reuse.

## Patch Pattern

- What the fix changed structurally: The fix introduced explicit registration of test public keys, a blacklist derived from that registration when test keys are disallowed, and an early blacklist check inside 'PublicKey.Verify'. A hardcoded keymanager test key is then registered so it is covered by the shared verification policy.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
