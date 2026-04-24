# Code-Shape Card

## Metadata

- ID: `bor-2024-08-21-bor-p2p-networking-f88af2000`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation`

## Code Shape Summary

- The grounded change is a downloader hardening fix in eth/downloader/bor_downloader.go. On header-processing termination in non-beacon mode, the code now consults a gotHeaders flag, compares the peer-advertised total difficulty to the local head total difficulty, and returns errStallingPeer when the peer claimed a stronger chain but no headers were delivered. Root cause: The termination path lacked an explicit final validation that a peer claiming a stronger chain had actually produced header progress before sync termination was accepted.

## Search Motifs

- handshake or protocol handler advances peer state before validating identity, key, or request correlation
- sync response is accepted without matching an outstanding request or expected peer capability
- peer-controlled metadata is trusted for scheduling, scoring, or chain progress before verification

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Add an end-of-stream consistency check that reconciles claimed sync strength with observed delivery, and convert a no-progress stronger-chain claim into an explicit peer fault.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
