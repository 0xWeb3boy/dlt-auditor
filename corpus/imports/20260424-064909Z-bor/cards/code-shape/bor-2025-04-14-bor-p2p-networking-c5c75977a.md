# Code-Shape Card

## Metadata

- ID: `bor-2025-04-14-bor-p2p-networking-c5c75977a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-churn`

## Code Shape Summary

- The patch appears to add slow peer churn for saturated peer sets, but the provided evidence does not establish a concrete vulnerability. This is better treated as an operational or hardening change with unclear security status. Root cause: The supplied evidence supports a missing peer-churn mechanism when connection slots were saturated: incumbent peers could persist until timeout or protocol error, leaving limited turnover. The evidence does not show a stronger root cause such as an exploit primitive, authentication failure, or consensus issue.

## Search Motifs

- handshake or protocol handler advances peer state before validating identity, key, or request correlation
- sync response is accepted without matching an outstanding request or expected peer capability
- peer-controlled metadata is trusted for scheduling, scoring, or chain progress before verification

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Add a background peer-management path and expose the minimum server and peer classification helpers needed to support churn decisions under saturation.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
