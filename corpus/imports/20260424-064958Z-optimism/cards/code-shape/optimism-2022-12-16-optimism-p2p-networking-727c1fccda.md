# Code-Shape Card

## Metadata

- ID: `optimism-2022-12-16-optimism-p2p-networking-727c1fccda`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `uncaught-panic-on-untrusted-input`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing resource-and-failure-isolation. The shown pre-patch validator registration path lacked panic containment.

## Search Motifs

- untrusted bytes decompressed or parsed before enforcing output limits
- validator callback can panic instead of returning a reject/error
- single malformed item aborts an entire batch instead of being isolated
- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- resource-and-failure-isolation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that resource-and-failure-isolation was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Add a fail-closed recovery shim at a peer-input validation boundary so panics are converted into explicit rejection results.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
