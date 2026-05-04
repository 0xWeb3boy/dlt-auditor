# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-02-07-stacks-core-p2p-networking-8778d4f74a`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-role-enforcement`

## Code Shape Summary

- The patch adds a coordinator check before signer command execution. This is plausibly security relevant because it prevents non-coordinator signers from processing commands, but the supplied evidence does not establish an exploit path, attacker control over commands, or a concrete protocol-security impact.

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
