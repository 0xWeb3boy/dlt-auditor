# Code-Shape Card

## Metadata

- ID: `scroll-2023-08-05-scroll-transaction-processing-a98a2ff4`
- Bug family: `authz_and_role_gates`
- Bug class: `authentication-challenge-replay-protection`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch is best supported as an authentication replay fix in the coordinator login path. The visible code adds an explicit equality check between the Authorization bearer token and login.Message.Challenge, and changes replay tracking from storing login.Signature to storing login.Message.Challenge. That is grounded evidence of fixing nonce/challenge binding and replay consumption in login.

## Search Motifs

- Motif 1: replay cache keyed by signature instead of canonical nonce or challenge
- Motif 2: bearer token accepted without equality check against the signed challenge field
- Motif 3: challenge-response login path consumes the wrong identifier when marking requests as used

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Bind the presented token to the signed challenge and store or invalidate the canonical challenge value rather than a derived signature field when consuming login requests.

## False Match Warnings

- Warning 1: If the challenge is already single-use, bound to the session token, and consumed on the canonical nonce value, a similar login flow is usually safe.
- Warning 2: Signature-format refactors near the login path are not enough by themselves; the key issue is whether replay tracking and token binding use the same challenge.
- Warning 3: The evidence supports replay hardening, not a proven forged-signature or privilege-escalation exploit beyond session reuse.
