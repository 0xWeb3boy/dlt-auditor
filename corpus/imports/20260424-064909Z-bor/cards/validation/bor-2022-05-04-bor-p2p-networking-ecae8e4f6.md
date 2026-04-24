# Validation Card

## Metadata

- ID: `bor-2022-05-04-bor-p2p-networking-ecae8e4f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation-regression`

## What Confirmed The Issue

- cmd/utils/flags.go switches CLI handling from legacy PeerRequiredBlocks naming to RequiredBlocks.
- eth/ethconfig/gen_config.go restores RequiredBlocks from config instead of the stale field, fixing config-to-runtime propagation.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No hunk shows the downstream hash comparison or peer rejection/disconnect logic.
- No evidence shows that unconfigured nodes were affected or that the issue was remotely exploitable by default.
