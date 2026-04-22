# Code-Shape Card

## Metadata

- ID: `oasis-core-2023-01-26-oasis-core-cryptography-8ffc81e94`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `insufficient-peer-identity-verification`

## Code Shape Summary

- Short description of what the buggy code looked like: Explicit-member routing needed additional identity-binding state across the host/session boundary. The provided evidence shows that this state was previously not exposed in the relevant APIs, so explicit peer selection could not be tied as directly to session identity verification as it is after the patch.

## Search Motifs

- Motif 1: trust root or quote policy cached without refresh on change
- Motif 2: freshness inferred from success state instead of anchored evidence
- Motif 3: session or attestation state reused after peer-set or policy change

## Typical Asymmetry

- What was checked in one path but missing in another: Trust state was initialized once, but later policy, freshness, identity, or session changes were not revalidated before reuse.

## Patch Pattern

- What the fix changed structurally: The patch threads the selected key manager node through the host RPC response, exposes remote-node identity from the session, and adds builder/client state used for remote identity verification. Per the commit message, Noise sessions then verify the selected member against consensus-derived trusted RAK material.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
