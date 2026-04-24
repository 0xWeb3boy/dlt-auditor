# Validation Card

## Metadata

- ID: `sui-2022-12-29-sui-storage-b376f812b5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-transition-race`

## What Confirmed The Issue

- Adds an AuthorityStore RwLock tracking the current execution epoch.
- Certificate processing now acquires a guarded execution lock and rejects mismatched certificate epochs.
- Reconfiguration now acquires the write lock before reverting uncommitted epoch transactions and updating epoch state.
- Commit message states the change prevents transaction execution from running in parallel with revert and rejects previous-epoch scheduled transactions after epoch change.

## What Could Have Invalidated It

- No proof that an external attacker could trigger or exploit the race.
- No demonstrated asset loss, double execution, authorization bypass, or signature validation failure.
- No evidence of production impact or actual consensus divergence.
- No tests or reproduction showing the pre-patch race causing corrupt committed state.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as security hardening of validator epoch/state consistency, not a proven vulnerability fix.
- Do not claim funds loss, remote exploitability, or consensus break from the supplied evidence alone.
- Do not retain the original signature-related tag; the shown invariant is epoch/reconfiguration ordering, not malformed signature acceptance.
- State-corruption should be softened to an epoch-transition race because corruption is plausible but not directly proven.
