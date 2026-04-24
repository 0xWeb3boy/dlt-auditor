# Validation Card

## Metadata

- ID: `reth-2023-08-29-reth-p2p-networking-03afe376b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `listener-filter-bypass`

## What Confirmed The Issue

- on_new_transaction now checks listener.kind.is_propagate_only() together with !event.transaction.propagate before sending.
- The added comment explicitly says these restricted listeners include network-style consumers.

## What Could Have Invalidated It

- No proof that non-propagable transactions were actually broadcast to remote peers
- No proof of attacker control over the affected listener path or a practical exploit chain

## Severity Guidance

- Expected impact band: network_policy_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that non-propagable transactions were actually broadcast to remote peers
- No proof of attacker control over the affected listener path or a practical exploit chain
