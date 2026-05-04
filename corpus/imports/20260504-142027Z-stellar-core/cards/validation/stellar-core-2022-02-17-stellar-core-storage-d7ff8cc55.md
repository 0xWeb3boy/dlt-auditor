# Validation Card

## Metadata

- ID: `stellar-core-2022-02-17-stellar-core-storage-d7ff8cc55`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-overlay-flow-control-hardening`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- TCPPeer read paths gained hasReadingCapacity checks.
- Peer send/receive paths added SEND_MORE handling.
- The patch rejects SEND_MORE from peers that did not negotiate support.

## What Could Have Invalidated It

- If all affected peers are authenticated and rate-limited elsewhere, severity drops.
- If message sizes are globally tiny and bounded, resource impact may be limited.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: Flow-control gaps can be abused for availability pressure, but the validation kept this as hardening because no concrete exploit was demonstrated.

## False-Positive Cautions

- Do not flag protocol additions that only expose counters without affecting capacity.
- Check negotiated-version behavior before claiming unsupported-message acceptance.
