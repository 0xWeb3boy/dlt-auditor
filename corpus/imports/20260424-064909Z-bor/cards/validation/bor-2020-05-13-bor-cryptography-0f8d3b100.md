# Validation Card

## Metadata

- ID: `bor-2020-05-13-bor-cryptography-0f8d3b100`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-boundary-validation`

## What Confirmed The Issue

- The modified code is in verifyCascadingFields, a consensus header verification path.
- The patch switches comparison from header.Extra[...] to parent.Extra[...], correcting which block supplies validator bytes.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof that the old behavior let an attacker get an invalid block accepted.
- No proof of an observed chain split, denial of service, or other concrete security impact.
