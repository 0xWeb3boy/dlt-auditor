# Code-Shape Card

## Metadata

- ID: `rippled-2017-11-17-rippled-access-control-a4a43a4de`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `tls-sni-hostname-setup`

## Code Shape Summary

- The supplied evidence supports a TLS/SNI setup improvement, not a confirmed vulnerability fix. Reusable shape: check for trust-root-and-freshness-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact trust-root-and-freshness-validation check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Set the intended DNS hostname on verified outbound TLS sockets before connect/handshake so SNI can influence server certificate selection, while retaining hostname verification against the logical target name.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the trust-root-and-freshness-validation gate runs before the state-changing branch.

## Patch Pattern

- Set the intended DNS hostname on verified outbound TLS sockets before connect/handshake so SNI can influence server certificate selection, while retaining hostname verification against the logical target name.

## False Match Warnings

- No evidence that certificate verification was previously disabled or bypassed.
- No evidence that a wrong certificate was previously accepted.
