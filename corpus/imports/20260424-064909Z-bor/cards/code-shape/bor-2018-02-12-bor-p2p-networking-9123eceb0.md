# Code-Shape Card

## Metadata

- ID: `bor-2018-02-12-bor-p2p-networking-9123eceb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-request-response-correlation`

## Code Shape Summary

- The supplied diff shows one concrete security-adjacent hardening change in p2p/discover/udp.go: udp.ping stops accepting any pending pong and instead checks that pong.ReplyTok matches the encoded ping hash. The rest of the evidence is mainly discovery-table initialization, revalidation, and peer-diversity hygiene. From the provided material alone, this is not enough to prove a distinct exploitable vulnerability, so the safest classification is unclear rather than a confirmed security fix. Root cause: The clearest pre-patch issue in the evidence is that ping/pong handling did not correlate the accepted pong to the exact sent ping; the callback accepted any pong for that pending request. The remaining changes address initialization timing, revalidation, and routing-table hygiene, but the provided excerpts do not establish them as the root cause of a specific security flaw.

## Search Motifs

- handshake or protocol handler advances peer state before validating identity, key, or request correlation
- sync response is accepted without matching an outstanding request or expected peer capability
- peer-controlled metadata is trusted for scheduling, scoring, or chain progress before verification

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Bind asynchronous network replies to the initiating request, while tightening surrounding bootstrap and table-management checks.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
