# Code-Shape Card

## Metadata

- ID: `bor-2024-04-30-bor-cryptography-bd8fe6260`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `operand-decoding-error`

## Code Shape Summary

- The only runtime change shown is in core/vm/eips.go, where opAuthCall stops popping one extra stack item while decoding AUTHCALL operands. That supports a real opcode-decoding bug in an authorization-related path, but the provided evidence does not establish an exploitable security vulnerability. Root cause: opAuthCall consumed one more stack item than the subsequent logic used, so later operands could be shifted relative to the intended AUTHCALL layout.

## Search Motifs

- input decoder feeds state-changing logic before semantic validation
- error path logs or ignores invalid data instead of failing closed
- security-relevant state changes occur before all invariants are checked

## Typical Asymmetry

- Attacker-controlled data crosses untrusted protocol input to trusted node logic boundary and reaches state mutation or security-relevant decision before the missing property is enforced.

## Patch Pattern

- Remove stray operand consumption in opcode stack decoding and tighten tests around the affected authorization flow.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
