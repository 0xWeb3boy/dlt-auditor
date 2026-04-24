# Validation Card

## Metadata

- ID: `sui-2022-12-20-sui-consensus-6c3e2bba3f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-epoch-invariant-hardening`

## What Confirmed The Issue

- Consensus transaction processing now loads the epoch store through load_epoch_store(current_epoch).
- AuthorityStore::load_epoch_store enforces store.epoch() == intended_epoch and returns StoreAccessEpochMismatch otherwise.
- The consensus path ignores processing when the epoch changed while a transaction is being processed.
- User transaction handling adds a certificate.epoch() != current_epoch check.

## What Could Have Invalidated It

- No advisory, CVE, issue, or commit text identifies this as a security vulnerability.
- No test or proof shows an exploitable consensus fork or validator safety violation.
- No evidence shows an attacker can trigger or control the epoch-store mismatch.
- No demonstrated impact such as asset loss, unauthorized execution, or network compromise.

## Severity Guidance

- Expected impact band: consensus-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Validate only as consensus epoch-invariant hardening.
- Do not claim a concrete exploitable vulnerability from the supplied patch alone.
- Do not claim confirmed consensus failure, fork, or asset loss.
- Checkpoint-related propagation was described as incomplete and deferred to a later PR.
