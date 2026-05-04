# Validation Card

## Metadata

- ID: `thor-2018-04-16-thor-transaction-processing-1166bb6a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `native-contract-hook-dispatch-hardening`

## What Confirmed The Issue

- Interpreter dispatch now checks CodeAddr against Address before invoking native hooks.
- Runtime and bridge code pass authoritative EVM and Contract objects instead of separately threaded call parameters.
- Phase 4 kept the finding as likely `security-hardening`, not as a confirmed vulnerability.

## What Could Have Invalidated It

- A separate invariant already prevented delegated calls from reaching native hooks.
- Native hooks were side-effect-free or never exposed to user-triggered execution.

## Severity Guidance

- Expected impact band: medium integrity hardening
- Expected severity band: `medium_or_low`
- Rationale: The evidence supports security hardening of a consensus-executed VM path. Impact could become chain-wide if native hooks execute under the wrong contract context, but exploitability is not proven.

## False-Positive Cautions

- No issue if native hooks are unreachable from delegated calls.
- No issue if the hook is read-only and cannot mutate privileged state.
- Treat broad VM refactors as false positives unless they add or remove a concrete dispatch gate.
