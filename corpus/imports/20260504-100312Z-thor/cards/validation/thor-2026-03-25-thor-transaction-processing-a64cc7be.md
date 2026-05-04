# Validation Card

## Metadata

- ID: `thor-2026-03-25-thor-transaction-processing-a64cc7be`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-rlp-list-decoding`

## What Confirmed The Issue

- reserved.DecodeRLP now rejects lists longer than MaxUnusedReservedFields+1.
- Clauses.DecodeRLP counts list items and enforces MaxClausesPerTx before decoding Clause objects.
- Phase 4 kept the finding as likely `security-hardening`, not as a confirmed vulnerability.

## What Could Have Invalidated It

- A strict transaction byte-size cap already bounds worst-case list count to a safe value.
- The oversized lists cannot be submitted through any network or RPC path.

## Severity Guidance

- Expected impact band: medium node-local availability hardening
- Expected severity band: `medium_or_low`
- Rationale: Unbounded transaction decode work can affect any node that parses submitted transactions. The finding is validated as hardening because concrete exploitability and limits elsewhere are not proven.

## False-Positive Cautions

- No issue if outer transaction size limits make the list count harmless.
- No issue if the decoder already streams and rejects after a small bounded count.
- Do not treat test helper additions alone as evidence without a production decode guard.
