# Validation Card

## Metadata

- ID: `stellar-core-2015-06-01-stellar-core-cryptography-a0bd68890`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vblocking-threshold-off-by-one`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Node::isVBlocking changed its leftTillBlock initialization from N - T to N - T + 1.
- SCP tests were updated around v-blocking and quorum behavior.

## What Could Have Invalidated It

- If the predicate is only used in offline analysis, severity should drop.
- If quorum sets cannot reach the affected boundary, exploitability is limited.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high_or_medium
- Rationale: Consensus threshold arithmetic is safety-critical, but the finding is likely hardening because no concrete network-level exploit is demonstrated.

## False-Positive Cautions

- Do not flag threshold arithmetic without confirming the protocol formula.
- Do not assume every quorum utility affects live consensus.
