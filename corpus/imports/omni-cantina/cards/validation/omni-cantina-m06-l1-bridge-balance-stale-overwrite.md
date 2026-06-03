# Validation Card

Record: `omni-cantina-m06-l1-bridge-balance-stale-overwrite`
Project: `omni-network`
Source finding: `Omni Cantina M-6`

## Positive Confirmation

Trace withdraw setting l1BridgeBalance, bridge decrementing it, different cross-chain delays, and no refund for failed L1 token transfer.

## Preconditions To Confirm

- L1-to-Native withdraw sets l1BridgeBalance to an absolute snapshot.
- Native-to-L1 bridge decrements the mirror locally.
- A stale L1 snapshot can arrive after the decrement and overwrite it.
- L1 settlement can fail without source refund.

## False-Positive Cautions

- Global ordering serializes both bridge directions by reserve state.
- Native uses l1BridgeBalance += amount rather than overwrite with stale absolute data.
- Failed destination transfer restores the source-side native value.

## Minimal Reproduction Or Check

Simulate the report timeline and assert the fixed mirror cannot become greater than actual L1 bridge liquidity after a stale message arrives.
