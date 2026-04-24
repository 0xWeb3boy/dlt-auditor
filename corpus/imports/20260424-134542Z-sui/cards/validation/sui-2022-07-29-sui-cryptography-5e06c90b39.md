# Validation Card

## Metadata

- ID: `sui-2022-07-29-sui-cryptography-5e06c90b39`
- Bug family: `authz_and_role_gates`
- Bug class: `epoch-authentication-invariant`

## What Confirmed The Issue

- Signed and certified epoch verification now checks `epoch != 0 && epoch - 1 == self.auth_sign_info.epoch`.
- The code comments state that epoch data must be verified by the previous epoch committee because it is signed by that committee.
- The changed data model removes the indirect next-epoch committee relationship and stores the committee for the epoch itself.
- Authority startup now initializes genesis authenticated epoch state and loads committee state from authenticated epoch data.

## What Could Have Invalidated It

- No concrete exploit path is shown.
- No evidence shows an attacker could bypass quorum signatures or forge authenticated epoch data.
- The storage indexing change named in the commit subject is not fully represented in the supplied hunks.
- The checkpoint variable rename does not independently support a security claim.

## Severity Guidance

- Expected impact band: consensus-integrity_or_state-integrity
- Expected severity band: high
- Rationale: Confirmed integrity or authorization impact on a consensus/state path generally warrants high severity unless a narrow deployment condition reduces reachability.

## False-Positive Cautions

- Classify as security-hardening, not security-fix.
- Do not claim proven signature forgery, consensus takeover, or exploitable state corruption.
- The supported claim is explicit tightening of epoch authentication invariants.
- The impact should be framed conservatively as consensus/state integrity hardening.
