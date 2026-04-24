# Validation Card

## Metadata

- ID: `sui-2022-12-21-sui-consensus-bd9fbd18d3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-boundary-reconfiguration-race`

## What Confirmed The Issue

- Certificate submission now acquires get_reconfig_state_read_lock_guard() before proceeding through verification and consensus handling.
- The code rejects user certificates when should_accept_user_certs() is false and records an epoch-boundary rejection metric.
- Pending consensus insertion now requires a ReconfigState read-lock guard for user transactions.
- The storage path asserts that user transactions are only stored while the locked reconfiguration state still accepts user certificates.

## What Could Have Invalidated It

- No evidence of a demonstrated exploit or attacker-controlled trigger is provided.
- No evidence proves actual consensus divergence, double execution, or fund loss.
- No evidence shows a cryptographic signature verification bypass.
- No full test result or failing regression scenario is included in the supplied input.

## Severity Guidance

- Expected impact band: consensus-invariant-hardening
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as consensus/reconfiguration invariant hardening rather than a confirmed consensus safety failure.
- Do not claim fund loss, double spend, or double execution from the supplied evidence.
- Do not claim signature bypass or authentication bypass.
- Do not claim all certificate types were affected; the shown guard is specifically about user certificates.
