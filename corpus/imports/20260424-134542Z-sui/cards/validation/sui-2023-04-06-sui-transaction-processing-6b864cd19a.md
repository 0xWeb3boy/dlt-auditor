# Validation Card

## Metadata

- ID: `sui-2023-04-06-sui-transaction-processing-6b864cd19a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-ownership-validation`

## What Confirmed The Issue

- Gas validation changed from checking only the primary gas_object owner to checking every object in more_gas_objs plus the primary gas object.
- The rejected condition is security-sensitive ownership state: gas objects must be Owner::AddressOwner.
- Commit body explicitly says an immutable gas coin could be deleted by gas smashing and that this was not intended.
- Execution context adds an invariant assertion preventing deletion effects for immutable input objects.

## What Could Have Invalidated It

- No proof of theft, balance inflation, or direct fund extraction.
- No evidence that arbitrary immutable objects could be deleted beyond the gas-coin path described.
- No evidence of remote unauthenticated exploitability or node-wide denial of service.
- Some added deletion checks are debug or invariant hardening rather than the primary production rejection path.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: high
- Rationale: Confirmed integrity or authorization impact on a consensus/state path generally warrants high severity unless a narrow deployment condition reduces reachability.

## False-Positive Cautions

- Classify as incomplete ownership validation causing possible immutable gas-object deletion.
- Impact should be limited to protocol state integrity, not liveness.
- Do not claim arbitrary object deletion or asset theft from the supplied patch alone.
- Downstream invariant checks are supporting hardening; the primary fix is validating all gas coin owners.
