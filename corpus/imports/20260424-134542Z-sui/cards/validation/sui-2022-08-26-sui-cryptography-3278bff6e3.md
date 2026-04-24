# Validation Card

## Metadata

- ID: `sui-2022-08-26-sui-cryptography-3278bff6e3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-error-misclassification`

## What Confirmed The Issue

- Commit message names malicious validator input causing honest validators to stop consensus progress.
- Patch introduces explicit NarwhalHandlerError categories separating local node errors from rejected Narwhal transaction/input verification failures.
- Database consensus-index load failures are explicitly mapped to NodeError, preserving stop-on-local-state-error behavior.
- Generic ExecutionStateError classification for SuiError and FragmentInternalError is removed from the shown paths.

## What Could Have Invalidated It

- No full end-to-end exploit trace is provided.
- The provided hunks do not show the complete new input verification path.
- No concrete corrupted object, checkpoint, or finalized invalid state outcome is demonstrated.
- No evidence supports cryptographic primitive breakage or signature forgery.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: high
- Rationale: Confirmed integrity or authorization impact on a consensus/state path generally warrants high severity unless a narrow deployment condition reduces reachability.

## False-Positive Cautions

- Supported attacker model is a malicious validator or consensus participant, not arbitrary unauthenticated remote users.
- Supported impact is consensus liveness denial of service and possible state-safety risk from misclassified local errors.
- Do not classify this as a cryptography or signature-validation flaw based on the supplied evidence.
- Do not claim theft, asset loss, or proven state corruption from the provided patch alone.
