# Code-Shape Card

## Metadata

- ID: `rippled-2018-08-10-rippled-access-control-38c3a46a3`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The patch is a confirmed security fix for rippled RPC transaction signing. It adds a default access-control gate to sign, sign_for, and the submit path used for sign-and-submit behavior, rejecting non-admin callers unless signing support is explicitly enabled in configuration. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact authorization check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Add a handler-boundary authorization and explicit-configuration gate before invoking server-side transaction signing or sign-and-submit helpers.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Add a handler-boundary authorization and explicit-configuration gate before invoking server-side transaction signing or sign-and-submit helpers.

## False Match Warnings

- No evidence proves actual seed theft, interception, or transaction forgery occurred.
- No evidence proves all deployments exposed these commands remotely or unauthenticated.
