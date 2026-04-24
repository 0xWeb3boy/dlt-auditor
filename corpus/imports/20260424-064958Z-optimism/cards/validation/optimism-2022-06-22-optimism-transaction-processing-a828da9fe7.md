# Validation Card

## Metadata

- ID: `optimism-2022-06-22-optimism-transaction-processing-a828da9fe7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Constructor binding changes from only _sequencer to _sequencer, _owner, indicating explicit admin/operator separation.
- New changeSequencer(address) ABI surface adds an explicit privileged role-management path.
- New sequencer() getter and SequencerChanged event improve visibility and auditability of privileged role state.
- Commit metadata explicitly mentions testing oracle access controls and deploying with an oracle owner.

## What Could Have Invalidated It

- No Solidity patch is shown for the actual authorization checks.
- No test diff is shown proving a previously unauthorized action was possible or is now blocked.
- No evidence links the change to a disclosed exploit, incident, or concrete vulnerability report.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No Solidity patch is shown for the actual authorization checks.
- No test diff is shown proving a previously unauthorized action was possible or is now blocked.
- No evidence links the change to a disclosed exploit, incident, or concrete vulnerability report.
