# Code-Shape Card

Record: `omni-cantina-h06-same-block-staking-event-order-loss`
Project: `omni-network`
Source finding: `Omni Cantina H-6`

## Search Shape

Source logs are sorted lexicographically by reduced fields rather than source log index, so Delegate can be delivered before same-block CreateValidator.

## Motifs

- `evmEvents sort Address Topics Data`
- `CreateValidator topic`
- `Delegate topic`
- `log index omitted`
- `deliverDelegate non-existing validator`
- `Delegate before CreateValidator`

## Negative Signals

- Event commitment includes original log index and preserves order.
- Dependent events are topologically ordered.
- Failed mandatory staking delivery retries or refunds.

## Likely Fix Shape

Include source log index in event ordering or preserve original log order; make failed mandatory staking delivery retryable/fail-closed.
