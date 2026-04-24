# Validation Card

## Metadata

- ID: `zksync-2020-12-24-zksync-transaction-processing-ba3bb4b61`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`

## What Confirmed The Issue

- The code had an AuthTokenValidator available.
- The serving app had a commented-out .wrap(auth) marked for restoration.
- The patch activates the middleware wrapper.

## What Could Have Invalidated It

- Every sensitive endpoint is protected elsewhere before the handler runs.
- The service is strictly unreachable outside a single trusted process.

## Severity Guidance

- Expected impact band: `auth_bypass_service_integrity`
- Expected severity band: `high_or_medium`
- Rationale: This is a confirmed missing middleware installation on a sensitive service API, but exact blast radius depends on network exposure and endpoint capabilities.

## False-Positive Cautions

- If a reverse proxy or service mesh enforces equivalent auth, code-level missing middleware may be defense-in-depth.
- Logging/failure-handling changes in the same commit should not be treated as auth fixes.
