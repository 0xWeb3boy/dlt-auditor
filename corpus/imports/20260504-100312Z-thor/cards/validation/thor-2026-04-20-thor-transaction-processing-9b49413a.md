# Validation Card

## Metadata

- ID: `thor-2026-04-20-thor-transaction-processing-9b49413a`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-chain-id-validation`

## What Confirmed The Issue

- Txpool now checks EthChainID against p.ethChainID after INTERSTELLAR.
- Consensus now rejects pre-fork EthTyped1559 and post-fork mismatched EthChainID.
- Tests verify configured post-fork CHAINID and pre-fork historical behavior.
- Phase 4 kept the finding as likely `security-hardening`, not as a confirmed vulnerability.

## What Could Have Invalidated It

- All typed transactions were already rejected before these checks.
- Another consensus-critical validation path already enforced the exact same chain-ID rule.

## Severity Guidance

- Expected impact band: medium chain-wide domain-separation hardening
- Expected severity band: `medium_or_low`
- Rationale: The accepted hardening closes a replay-domain consistency gap across transaction admission and execution. It is medium because transaction domain errors can be chain-wide, but exploitability is not established.

## False-Positive Cautions

- No issue if mismatched chain IDs fail during signature recovery before acceptance.
- No issue if the transaction type is unreachable until the fork activates.
- Do not flag duplicate fork plumbing without an acceptance path for signed transactions.
