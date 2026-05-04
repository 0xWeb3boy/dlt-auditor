# Validation Card

## Metadata

- ID: `stellar-core-2015-05-04-stellar-core-storage-37668bf24`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-state-invariant`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- AllowTrustOpFrame gained a guard against revocation by non-revocable issuers.
- SetOptionsOpFrame gained a guard for authorization-related flags when issued credit exists.
- TrustFrame::hasIssued was added as the state predicate.

## What Could Have Invalidated It

- If the flag change only affects future trustlines and cannot touch existing balances, impact is lower.
- If the operation source is tightly controlled by offline governance, attacker capability may be operational rather than remote.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: The change protects issued-asset authorization semantics and user expectations, but evidence does not show direct fund theft or chain-wide compromise.

## False-Positive Cautions

- Do not flag explicit unsafe or migration modes without checking their operator opt-in semantics.
- Do not confuse trustline authorization with unrelated account option flags.
