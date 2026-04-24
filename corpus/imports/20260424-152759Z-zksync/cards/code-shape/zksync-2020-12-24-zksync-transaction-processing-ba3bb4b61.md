# Code-Shape Card

## Metadata

- ID: `zksync-2020-12-24-zksync-transaction-processing-ba3bb4b61`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`

## Code Shape Summary

- The patch restores Actix authentication middleware by changing a commented-out wrap(auth) into an active route wrapper. The reusable shape is security middleware constructed in code but not attached to the application that serves privileged endpoints.

## Search Motifs

- commented restore-auth marker next to .wrap(auth)
- AuthTokenValidator exists but middleware is not installed
- route/app builder gains authentication wrapper around prover/admin endpoints

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Attach the existing authentication middleware to the service route/app builder so every sensitive request passes token validation before handler execution.

## False Match Warnings

- If a reverse proxy or service mesh enforces equivalent auth, code-level missing middleware may be defense-in-depth.
- Logging/failure-handling changes in the same commit should not be treated as auth fixes.
- Public read-only endpoints need different severity than privileged coordination endpoints.
