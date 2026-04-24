# Validation Card

## Metadata

- ID: `bor-2022-12-06-bor-p2p-networking-50a778207`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `path-validation`

## What Confirmed The Issue

- A new shared VerifyPath helper is introduced specifically for filesystem path handling.
- Multiple call sites stop using supplied paths directly and instead use canonicalPath returned by VerifyPath.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No base-directory or allowlisted-root check is shown in the helper.
- No proof is provided that an attacker can control the affected path inputs in a meaningful threat model.
