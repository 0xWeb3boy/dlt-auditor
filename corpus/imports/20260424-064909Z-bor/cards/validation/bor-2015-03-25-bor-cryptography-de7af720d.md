# Validation Card

## Metadata

- ID: `bor-2015-03-25-bor-cryptography-de7af720d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-amplification`

## What Confirmed The Issue

- Commit body explicitly states this fixes an attack vector for DDoS traffic amplification.
- findnode.handle now checks t.db.get(fromID) == nil and returns errUnknownNode for unbonded senders.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: high

## False-Positive Cautions

- Patch does not prove complete protection against replay within the expiration window.
- Patch does not show stricter source-address validation beyond the bonding requirement.
