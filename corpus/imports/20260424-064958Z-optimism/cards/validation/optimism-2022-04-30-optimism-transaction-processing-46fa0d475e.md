# Validation Card

## Metadata

- ID: `optimism-2022-04-30-optimism-transaction-processing-46fa0d475e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-message-validation-hardening`

## What Confirmed The Issue

- Generic pubsub.NewGossipSub is replaced by rollup-aware p2p.NewGossipSub(..., &cfg.Rollup).
- Startup now explicitly calls p2p.JoinGossip(..., &cfg.Rollup, n.blocks) before feeding blocks into the node.
- rollup.Config adds L2ChainID and P2PSequencerAddress with comments tying them to chain-unique P2P signatures and signer identity.
- OpNode.Start reads from c.blocks, showing gossip messages reach runtime handling of unsafe L2 blocks.

## What Could Have Invalidated It

- No diff for p2p.NewGossipSub or p2p.JoinGossip shows the exact validation logic.
- No test excerpt shows rejection of spoofed, unauthenticated, or cross-chain gossip blocks.
- No patch evidence proves that pre-patch nodes actually accepted invalid blocks.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No diff for p2p.NewGossipSub or p2p.JoinGossip shows the exact validation logic.
- No test excerpt shows rejection of spoofed, unauthenticated, or cross-chain gossip blocks.
- No patch evidence proves that pre-patch nodes actually accepted invalid blocks.
