# Raw Finding Summary

Source: Omni Cantina `M-4`
Title: Malicious proposer can include empty transactions in a valid proposal
Severity: `medium`

## Normalized Summary

The report shows honest PrepareProposal returns a single unsigned transaction with MsgAddVotes and MsgExecutionPayload, while ProcessProposal decodes every transaction in req.Txs and accepts empty transactions with no messages.

## Reusable Failure Shape

The proposal router bounds allowed message counts but not raw transaction count, so many empty transactions decode successfully and consume resources while carrying no messages.

## Missing Property

`proposal-transaction-cardinality-bound`: ProcessProposal should enforce the expected transaction count and reject empty/useless transaction bloat before decoding unbounded proposer-selected transactions.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `M-4`
