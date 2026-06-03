# Code-Shape Card

Record: `omni-cantina-m04-empty-transaction-proposal-bloat`
Project: `omni-network`
Source finding: `Omni Cantina M-4`

## Search Shape

The proposal router bounds allowed message counts but not raw transaction count, so many empty transactions decode successfully and consume resources while carrying no messages.

## Motifs

- `for rawTX range req.Txs`
- `TxDecoder`
- `tx.GetMsgs empty`
- `allowedMsgCounts`
- `ResponseProcessProposal_ACCEPT`
- `single Tx PrepareProposal`
- `100MB limit`

## Negative Signals

- ProcessProposal requires exactly one transaction.
- Empty-message transactions are rejected.
- A tight local raw transaction count or total byte limit is enforced before decode.

## Likely Fix Shape

Enforce the protocol expectation of one generated transaction per proposal, or set explicit max transaction count/byte limits and reject empty-message transactions.
