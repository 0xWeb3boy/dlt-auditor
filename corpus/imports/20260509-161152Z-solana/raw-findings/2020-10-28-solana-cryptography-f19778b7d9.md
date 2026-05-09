---
case_id: case_20201028_f19778b7d9
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: high
source_quality: high
date: 2020-10-28
source_refs:
  - git:f19778b7d96ad39144420ac7889635f15da8a0e7
  - "core/src/cluster_info.rs:2091"
  - "core/src/cluster_info.rs:2018"
  - "core/src/cluster_info.rs:428"
  - "core/src/cluster_info.rs:1941"
bug_class: udp-reflection-amplification
impact_type:
  - denial-of-service
  - traffic-amplification
tags:
  - blockchain-core
  - gossip
  - udp
  - ddos-amplification
  - endpoint-proof
  - spoofed-source-address
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Confirmed security fix for UDP gossip pull reflection/amplification. The patch adds ping-pong endpoint proof and gates gossip PullResponse generation on address validity plus prior ping response state, reducing the ability to spoof a PullRequest source address and induce larger responses to a victim.

## Observed Patch Facts

1. In `core/src/cluster_info.rs`, the patch replaces `if packets.is_empty() {` with `packets`.

2. In `core/src/cluster_info.rs`, the patch replaces `self.time_gossip_write_lock("process_pull_reqs", &self.stats.process_pull_requests)` with `.zip(addrs.into_iter())`.

3. In `core/src/cluster_info.rs`, the patch adds `Protocol::PingMessage(ref ping) => {`.

4. In `core/src/cluster_info.rs`, the patch replaces `// Pull requests take an incoming bloom filter of contained entries from a node` with `// Returns a predicate checking if the pull request is from a valid`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/src/ping_pong.rs`, `core/src/verified_vote_packets.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/ping_pong.rs`, `core/src/window_service.rs`. The strongest project-level identifiers around this patch are `packets`, `ping`, `Some`, and `Protocol::PingMessage`.

## Before/After Behavior

Before the patch, the provided `handle_pull_requests` evidence shows PullResponse data generated for caller/filter pairs and response emission filtered for malformed destinations or empty responses, but no endpoint reachability proof is shown before response generation. After the patch, `check_pull_request` filters pull requests before `generate_pull_responses`, requires a valid address and prior ping response, and appends ping packets for addresses needing verification. Ping and Pong protocol messages are also verified in `Protocol::par_verify`.

# Root Cause

The gossip pull path accepted UDP PullRequest traffic without first proving that the apparent source address could receive packets sent to it. Because UDP source addresses can be spoofed, a node could be induced to send larger PullResponse traffic to a third-party address. Existing gossip signature checks did not establish endpoint reachability for the UDP response destination.

## Walkthrough

1. An attacker sends a UDP gossip PullRequest with a spoofed source address.

2. Pre-fix evidence shows PullResponse generation based on caller/filter data without a visible endpoint proof gate.

3. The old filtering shown only rejected malformed destination addresses or empty responses.

4. A syntactically valid spoofed address could therefore reach the amplification-prone response path according to the commit report and provided code context.

5. The patch adds PingMessage and PongMessage verification in `Protocol::par_verify`.

6. The patch introduces `check_pull_request`, which checks address validity and whether the address has responded to a ping.

7. Pull requests that fail this predicate are filtered before PullResponse generation, while ping packets may be queued for verification.

8. Responses are then paired with addresses that passed the predicate and empty responses are dropped.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/cluster_info.rs | 382 | Adds Protocol::PingMessage and Protocol::PongMessage verification before accepting gossip ping-pong packets. |
| core/src/cluster_info.rs | 1941 | Introduces check_pull_request predicate requiring valid address and prior ping response, while appending ping packets for addresses needing verification. |
| core/src/cluster_info.rs | 1988 | Applies pull request filtering before generating PullResponse packets and preserving destination addresses for response emission. |
| core/src/cluster_info.rs | 2018 | Changes pull request processing flow so responses are paired with verified addresses and empty responses are filtered. |
| core/src/ping_pong.rs | 8 | Defines signed Ping/Pong protocol messages used for endpoint proof. |

## Code Snippets

## Snippet 1

Context: `core/src/cluster_info.rs:2091` (changes a sensitive control or state-update path)

Before
```rust
total_bytes
        );
        if packets.is_empty() {
            return None;
        }
        Some(packets)
    }
```
After
```rust
total_bytes
        );
        packets
    }
```

## Snippet 2

Context: `core/src/cluster_info.rs:2018` (changes a sensitive control or state-update path)

Before
```rust
.generate_pull_responses(&caller_and_filters, now);

        self.time_gossip_write_lock("process_pull_reqs", &self.stats.process_pull_requests)
            .process_pull_requests(caller_and_filters, now);

        // Filter bad to addresses
        let pull_responses: Vec<_> = pull_responses
            .into_iter()
```
After
```rust
.generate_pull_responses(&caller_and_filters, now);

        let pull_responses: Vec<_> = pull_responses
            .into_iter()
            .zip(addrs.into_iter())
            .filter(|(response, _)| !response.is_empty())
            .collect();
```

## Snippet 3

Context: `core/src/cluster_info.rs:428` (changes signature or replay validation logic)

Before
```rust
}
            }
        }
    }
```
After
```rust
}
            }
            Protocol::PingMessage(ref ping) => {
                if ping.verify() {
                    Some(self)
                } else {
                    inc_new_counter_info!("cluster_info-gossip_ping_msg_verify_fail", 1);
                    None
```

## Snippet 4

Context: `core/src/cluster_info.rs:1941` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    // Pull requests take an incoming bloom filter of contained entries from a node
    // and tries to send back to them the values it detects are missing.
```
After
```rust
}

    // Returns a predicate checking if the pull request is from a valid
    // address, and if the address have responded to a ping request. Also
    // appends ping packets for the addresses which need to be (re)verified.
    fn check_pull_request<'a, R>(
        &'a self,
        now: Instant,
```

# Fix Pattern

Require UDP endpoint proof before sending amplification-prone responses: verify ping/pong messages, cache successful ping responses, and gate large PullResponse generation on that reachability state.

## How It Was Fixed

The fix adds signed Ping/Pong protocol support, verifies PingMessage and PongMessage packets, introduces pull-request validation through `check_pull_request`, and changes the pull handling flow so unverified addresses receive verification pings instead of immediate PullResponse traffic.

# Why It Matters

1. Prevents spoofed UDP PullRequests from directly triggering larger gossip PullResponses to victims.

2. Moves endpoint validation before amplification-prone response generation.

3. Clarifies that signed gossip contents are not enough to prove UDP source reachability.

4. The supported scope is gossip pull reflection/amplification, not consensus or ledger compromise.

# Evidence Notes

Primary evidence is in `core/src/cluster_info.rs` around `Protocol::par_verify`, `check_pull_request`, and `handle_pull_requests`. Supporting evidence from `core/src/ping_pong.rs` shows Ping/Pong message structures. The commit message directly cites a HackerOne report describing spoofed UDP PullRequest amplification and states that PingCache tracks valid ping responses. The supplied evidence does not independently prove the reported 34x amplification ratio and does not support claims of signature forgery, validator key compromise, consensus compromise, or arbitrary reflection outside the gossip pull path. Protocol security invariant: A node should not send large UDP gossip PullResponse traffic to an address until that address has proven endpoint reachability. PullRequest handling must distinguish message signature validity from proof that the UDP source address is not spoofed. Verification notes: The patch evidence does not independently prove the reported 34x amplification ratio. The patch does not show compromise of consensus, ledger state, or validator identity keys. The issue is not proven to be a cryptographic signature forgery; signatures support the endpoint-proof mechanism. The evidence supports UDP reflection/amplification risk for gossip pull responses, not arbitrary packet reflection across all Solana networking paths. Security classification is supported by the explicit commit message and focused runtime guard changes. Bug class should be UDP reflection/amplification, not replay or generic cryptographic validation. Confidence remains high because the commit body, changed paths, and pull-request gating behavior align. Claim boundaries exclude the exact amplification ratio and effects outside gossip pull responses. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `udp-reflection-amplification`
Final impact type: `denial-of-service, traffic-amplification`
Final tags: `blockchain-core, gossip, udp, ddos-amplification, endpoint-proof, spoofed-source-address`

The supplied commit message directly describes a HackerOne-reported UDP gossip amplification issue caused by spoofed PullRequest source addresses, and the patch evidence aligns with that claim by adding ping/pong verification and gating PullResponse generation on address validity plus prior endpoint proof. This belongs in a security-fix corpus, but the original cryptography/replay-or-signature-validation classification is misleading; the supported issue is UDP reflection/amplification in gossip pull handling.

## Security Evidence

1. Commit body explicitly cites spoofed UDP PullRequest amplification and DDoS risk.
2. Patch adds PingMessage and PongMessage verification to gossip protocol handling.
3. Patch introduces check_pull_request requiring a valid address and prior ping response before accepting pull requests.
4. handle_pull_requests filters requests before generating PullResponses and pairs responses only with accepted addresses.
5. Ping/Pong structures use signatures as part of endpoint proof, supporting the anti-spoofing mechanism.

## Missing Evidence

1. Patch evidence does not independently prove the reported 34x amplification ratio.
2. No evidence supports consensus compromise, ledger corruption, or validator key compromise.
3. No evidence supports a generic signature forgery or replay vulnerability.
4. No proof is provided that every Solana UDP path was affected; evidence is limited to gossip pull responses.

## Claim Boundaries

1. Classify as UDP gossip PullRequest reflection/amplification, not broad cryptographic validation failure.
2. Impact is denial of service or traffic amplification against nodes or spoofed victims.
3. Security claim depends on the commit message plus aligned runtime guard changes.
4. Do not claim exact amplification magnitude from the patch alone.
