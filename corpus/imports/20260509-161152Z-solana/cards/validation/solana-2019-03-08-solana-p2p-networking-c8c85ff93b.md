# Validation Card

## Metadata

- ID: `solana-2019-03-08-solana-p2p-networking-c8c85ff93b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `gossip-signature-integrity`

## What Confirmed The Issue

- ClusterInfo::new now calls insert_self instead of generic insert_info for the local node record.
- insert_self only inserts when self.id() == node_info.id.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: Medium
- Rationale: The issue was confirmed as a security fix, but the available evidence does not establish direct high-impact loss.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
