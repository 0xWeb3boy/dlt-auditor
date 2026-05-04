# Code-Shape Card

## Metadata

- ID: `stacks-core-2020-02-21-stacks-core-cryptography-7703c74593`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-resource-accounting`

## Code Shape Summary

- The patch adds cost-accounting propagation to trait signature parsing. Before the change, `parse_trait_type_repr` called `TypeSignature::parse_type_repr` for trait function argument and return types without passing a `CostTracker`. After the change, `parse_trait_type_repr` accepts a mutable tracker, the define-trait runtime path passes the VM `Environment`, and recursive type parsing can charge its existing `TYPE_PARSE_STEP` cost.

## Search Motifs

- Motif 1: request body decoded before max-size enforcement
- Motif 2: panic or unwrap reachable from peer-controlled protocol data
- Motif 3: execution cost or resource budget charged inconsistently across error cases

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Move size, cost, and error checks to the boundary and convert panic or ambiguous errors into explicit validation failures.

## False Match Warnings

- The input may already be bounded by transport framing.
- A panic in test-only or unreachable internal code is not an externally reachable denial of service.
