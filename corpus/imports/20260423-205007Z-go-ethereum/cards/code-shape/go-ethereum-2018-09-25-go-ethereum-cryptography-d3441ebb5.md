# Code-Shape Card

## Metadata

- ID: `go-ethereum-2018-09-25-go-ethereum-cryptography-d3441ebb5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-policy-hardening`

## Code Shape Summary

- The supported root cause is a permissive signer policy/API boundary: validation warnings and nonessential external API methods were allowed in the default signer interface. The evidence does not establish private key extraction, signature forgery, consensus failure, or a proven remote exploit path.

## Search Motifs

- Motif 1: rpc method missing exact checks for signer policy hardening
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Deny by default at the signer API boundary: turn validation warnings into blocking errors in normal mode, require explicit advanced mode for warning-only behavior, and reduce exposed external API capabilities

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Deny by default at the signer API boundary: turn validation warnings into blocking errors in normal mode, require explicit advanced mode for warning-only behavior, and reduce exposed external API capabilities.

## False Match Warnings

- Validate as signer/Clef hardening, not a proven cryptographic vulnerability fix.
- Do not claim private-key extraction, signature forgery, consensus impact, or remote compromise from this evidence.
