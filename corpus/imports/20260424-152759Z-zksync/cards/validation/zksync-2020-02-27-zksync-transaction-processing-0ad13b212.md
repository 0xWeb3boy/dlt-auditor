# Validation Card

## Metadata

- ID: `zksync-2020-02-27-zksync-transaction-processing-0ad13b212`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-message-domain-separation-hardening`

## What Confirmed The Issue

- The authorization payload changes from opaque bytes to a readable zkSync registration message.
- The changed path is ChangePubKey Ethereum authorization.
- Validation kept the case as likely hardening, not confirmed replay.

## What Could Have Invalidated It

- The message is only displayed and not the payload actually verified.
- A stronger typed-data domain already made the old opaque payload non-reusable.

## Severity Guidance

- Expected impact band: `authorization_hardening`
- Expected severity band: `medium_or_low`
- Rationale: Better authorization messaging reduces replay/blind-signing risk, but validation did not prove a concrete forgery or exploit path.

## False-Positive Cautions

- Readable text alone is not a full cryptographic domain separator if verifier semantics are unchanged.
- Do not claim exploitability without evidence the old message could be reused.
