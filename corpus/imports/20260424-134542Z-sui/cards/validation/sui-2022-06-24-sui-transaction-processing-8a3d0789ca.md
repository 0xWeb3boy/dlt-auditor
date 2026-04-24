# Validation Card

## Metadata

- ID: `sui-2022-06-24-sui-transaction-processing-8a3d0789ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-execution-invariant`

## What Confirmed The Issue

- Checkpoint handling now rejects contents when all_checkpoint_transactions_executed returns false.
- Checkpoint update now rejects transaction lists that include unexecuted transactions.
- The check is placed before signing or recording checkpoint state in validator/checkpointing logic.
- Comments state the intended invariant that accepted signed/recorded checkpoints contain only processed transactions.

## What Could Have Invalidated It

- No attacker-controlled input path is demonstrated.
- No exploit scenario or proof of remote triggerability is shown.
- No concrete asset loss, unauthorized transaction execution, signature forgery, or consensus split is proven.
- No security advisory, CVE, or explicitly security-labeled regression test is provided.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as invariant hardening in checkpointing logic, not as a proven exploitable vulnerability.
- Do not claim theft, forgery, or unauthorized execution from the supplied patch alone.
- Do not claim a demonstrated consensus split; only a checkpoint/execution consistency risk is supported.
- The reconstruction gating change appears more like work avoidance or correctness unless tied to the execution invariant.
