# Validation Card

## Metadata

- ID: `firedancer-2025-12-02-firedancer-core-logic-52a2cbfda`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `content-length-integer-overflow`

## What Confirmed The Issue

- Evidence 1: Commit body states this fixes an OOB read vulnerability triggered by crafted Content-Length headers.
- Evidence 2: Both fd_genesis_client and fd_rpc_client parsed Content-Length with strtoul and previously accepted values greater than UINT_MAX.

## What Could Have Invalidated It

- Compensating control 1: No downstream buffer access or read site is shown in the supplied patch evidence.
- Compensating control 2: No proof of remote exploitability beyond crafted header handling is provided.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No downstream buffer access or read site is shown in the supplied patch evidence.
- Caution 2: No proof of remote exploitability beyond crafted header handling is provided.
