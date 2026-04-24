# Validation Card

## Metadata

- ID: `sui-2022-01-25-sui-transaction-processing-f95e29b749`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-certificate-comparison-semantics`

## What Confirmed The Issue

- CertifiedOrder represents an order signed by a quorum of authorities and carries a signature vector.
- The patch removes Eq/Hash/PartialEq behavior that previously encoded concrete signature-set details into identity semantics.
- Added comments state that multiple valid certificates can exist for the same transaction and that clients may equivocate on exact signature sets.
- The change forces future certificate comparison or hashing decisions to be deliberate rather than silently inherited through generic traits.

## What Could Have Invalidated It

- No concrete caller is shown misusing CertifiedOrder equality, hashing, deduplication, HashMap, or HashSet behavior.
- No demonstrated exploit, consensus failure, double spend, replay issue, or state corruption path is provided.
- No runtime validation change is shown; the patch is primarily API restriction and compile-time pressure.
- No test evidence in the supplied input proves a previously failing security scenario.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as security hardening rather than a confirmed vulnerability fix.
- Do not claim proven state corruption or exploitable transaction-processing failure from this evidence alone.
- Do not claim the patch implements correct certificate equality; it removes unsafe generic equality and hashing semantics.
- The supported security claim is limited to preventing accidental misuse of certificate identity semantics around signature sets.
