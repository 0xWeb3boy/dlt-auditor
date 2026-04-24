# Validation Card

## Metadata

- ID: `bor-2018-02-12-bor-p2p-networking-9123eceb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-request-response-correlation`

## What Confirmed The Issue

- udp.ping previously accepted any pong for the pending request via a callback that always returned true.
- The patched callback now requires bytes.Equal(p.(*pong).ReplyTok, hash), binding the accepted pong to the specific sent ping.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No bug report, advisory, or test demonstrates attacker-controlled exploitation of unrelated pong acceptance.
- No evidence shows concrete downstream impact such as eclipse, table poisoning, or authentication bypass.
