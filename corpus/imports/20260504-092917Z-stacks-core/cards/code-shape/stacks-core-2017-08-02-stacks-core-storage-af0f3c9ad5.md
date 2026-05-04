# Code-Shape Card

## Metadata

- ID: `stacks-core-2017-08-02-stacks-core-storage-af0f3c9ad5`
- Bug family: `authz_and_role_gates`
- Bug class: `address-bound-authorization-hardening`

## Code Shape Summary

- The patch is security relevant but the vulnerability thesis is not established by the supplied evidence. The grounded evidence shows subdomain code moving from pubkey-oriented handling toward Bitcoin-address-based ownership, address-bound mutable-data lookup, and scriptSig-style verification. However, the full update acceptance path, validation outcome, and attacker capability are not shown, so this should not be treated as a confirmed vulnerability fix.

## Search Motifs

- Motif 1: owner address or role checked after lookup rather than before mutation
- Motif 2: identity material converted without binding it to the authorized principal
- Motif 3: state update helper accepts caller-controlled identity fields

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Bind the mutable operation to an authenticated owner or role check before the state update path can proceed.

## False Match Warnings

- The caller may already be authenticated by an outer dispatcher.
- The changed path may be read-only or test-only rather than a privileged mutation.
