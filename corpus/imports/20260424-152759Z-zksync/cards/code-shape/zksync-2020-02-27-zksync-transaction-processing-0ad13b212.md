# Code-Shape Card

## Metadata

- ID: `zksync-2020-02-27-zksync-transaction-processing-0ad13b212`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-message-domain-separation-hardening`

## Code Shape Summary

- The patch changes ChangePubKey Ethereum authorization from opaque raw bytes to a protocol-specific registration message. The reusable pattern is account-control signatures whose prompts or signed payloads lack clear action/domain semantics.

## Search Motifs

- get_eth_signed_data changed from raw bytes to readable registration text
- ChangePubKey authorization message includes protocol/action/new pubkey context
- wallet signing path moves away from opaque byte arrays

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Replace opaque account-control authorization bytes with a canonical, protocol-specific, human-readable message that binds the intended registration action.

## False Match Warnings

- Readable text alone is not a full cryptographic domain separator if verifier semantics are unchanged.
- Do not claim exploitability without evidence the old message could be reused.
- UI/prompt wording changes outside an authorization sink are weaker.
