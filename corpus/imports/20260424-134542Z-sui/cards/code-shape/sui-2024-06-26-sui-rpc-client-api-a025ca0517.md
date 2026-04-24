# Code-Shape Card

## Metadata

- ID: `sui-2024-06-26-sui-rpc-client-api-a025ca0517`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `traffic-control-accounting-gap`

## Code Shape Summary

- The supported finding is traffic-controller security hardening, not serialization or state-representation repair. The patch threads an explicit spam/accounting weight through authority service responses so successful gasless work can be counted by traffic-control logic.

## Search Motifs

- resource-accounting enforced after parsing but before rpc-client-api state mutation
- rpc-client-api handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Propagate explicit resource-abuse accounting metadata from business logic to the traffic-controller boundary instead of inferring spam solely from RPC success or error status.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
