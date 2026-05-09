---
case_id: case_20201029_06067dd823
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
date: 2020-10-29
source_refs:
  - git:06067dd82304f1430a74bdfdca2d3cd79115a3b7
  - "core/src/cluster_info.rs:2063"
  - "core/src/cluster_info.rs:1990"
  - "core/src/cluster_info.rs:427"
  - "core/src/cluster_info.rs:1913"
bug_class: udp-amplification-missing-endpoint-validation
impact_type:
  - ddos-amplification
  - traffic-reflection
tags:
  - blockchain-core
  - gossip-protocol
  - udp
  - ddos-amplification
  - endpoint-validation
  - anti-spoofing
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch addresses a UDP gossip amplification issue in Solana pull-request handling. The commit explicitly cites a HackerOne report describing spoofed PullRequest source addresses causing larger PullResponse packets to be sent to victims, and the code evidence shows a new ping-pong endpoint check before pull responses are generated.

## Observed Patch Facts

1. In `core/src/cluster_info.rs`, the patch replaces `if packets.is_empty() {` with `packets`.

2. In `core/src/cluster_info.rs`, the patch replaces `self.time_gossip_write_lock("process_pull_reqs", &self.stats.process_pull_requests)` with `.zip(addrs.into_iter())`.

3. In `core/src/cluster_info.rs`, the patch adds `Protocol::PingMessage(ref ping) => {`.

4. In `core/src/cluster_info.rs`, the patch replaces `// Pull requests take an incoming bloom filter of contained entries from a node` with `// Returns a predicate checking if the pull request is from a valid`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/src/ping_pong.rs`, `core/src/verified_vote_packets.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/ping_pong.rs`, `core/src/window_service.rs`. The strongest project-level identifiers around this patch are `packets`, `ping`, `Some`, and `Protocol::PingMessage`.

## Before/After Behavior

Before the patch, the shown pull-request path generated pull responses after basic address and response filtering, without the new endpoint-proof gate. After the patch, handle_pull_requests filters PullData through check_pull_request before generate_pull_responses, sends ping packets for addresses needing verification, and only allows verified requests to proceed to response generation. PingMessage and PongMessage are also added to Protocol::par_verify with verify() checks.

# Root Cause

The root cause was trusting the UDP source address associated with gossip PullRequest handling before the remote endpoint had proven reachability at that address. This allowed a spoofed source address to trigger larger PullResponse traffic toward a third party.

## Walkthrough

1. An attacker could send a UDP gossip PullRequest with a spoofed source address.

2. The commit message states that PullResponse packets were much larger than PullRequest packets, creating amplification risk.

3. The pre-patch evidence does not show an endpoint-proof check before pull-response generation.

4. The patch adds check_pull_request to validate address suitability and require prior ping-pong verification.

5. Unverified addresses can receive ping packets instead of immediately receiving pull responses.

6. handle_pull_requests now filters requests through that predicate before calling generate_pull_responses.

7. Protocol::par_verify now verifies PingMessage and PongMessage before accepting them.

8. The packet return behavior preserves generated ping packets even when no pull responses are produced.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/cluster_info.rs | 1913 | Adds check_pull_request predicate to validate pull request source addresses and require ping-pong verification before accepting them. |
| core/src/cluster_info.rs | 1960 | handle_pull_requests applies the verification predicate before generate_pull_responses and emits ping packets for addresses needing verification. |
| core/src/cluster_info.rs | 381 | Protocol verification path accepts PingMessage and PongMessage only if their signatures/tokens verify. |
| core/src/ping_pong.rs | 8 | Defines Ping and Pong message structures carrying signed endpoint-proof material. |
| core/src/cluster_info.rs | 2057 | Pull request handling returns generated packets, including ping packets, rather than dropping all output when no pull responses are produced. |

## Code Snippets

## Snippet 1

Context: `core/src/cluster_info.rs:2063` (changes a sensitive control or state-update path)

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

Context: `core/src/cluster_info.rs:1990` (changes a sensitive control or state-update path)

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

Context: `core/src/cluster_info.rs:427` (changes signature or replay validation logic)

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

Context: `core/src/cluster_info.rs:1913` (changes the branch that decides whether execution stops or continues)

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

Require endpoint reachability proof before sending larger UDP responses. Challenge the claimed source address with ping-pong verification, cache successful endpoints, and gate amplification-prone response generation on that verification.

## How It Was Fixed

The patch adds a PingCache-backed ping-pong mechanism, adds PingMessage and PongMessage verification, inserts check_pull_request into the pull-request handling path before response generation, and returns generated packets directly so verification pings can be emitted even when pull responses are not produced.

# Why It Matters

1. Prevents spoofed PullRequest source addresses from directly triggering larger PullResponse traffic.

2. Reduces UDP reflection and amplification risk in gossip pull handling.

3. Scopes the trust decision to endpoint reachability, not only message signature validity.

4. Leaves other possible UDP amplification vectors outside the proven scope of this evidence.

# Evidence Notes

Strong evidence comes from the commit body, which explicitly references a HackerOne report about UDP gossip amplification via spoofed PullRequest source addresses. Code evidence supports the thesis through check_pull_request in core/src/cluster_info.rs, its use before generate_pull_responses, PingMessage/PongMessage verify() handling, and packet-return changes that allow pings to be sent independently of pull responses. The evidence supports endpoint-proof amplification mitigation, not a generic replay or signature-validation vulnerability. Protocol security invariant: A node should not send amplification-prone UDP gossip PullResponse packets to a source address supplied in a PullRequest until that endpoint has proven it can receive traffic at that address. Verification notes: The patch evidence does not prove actual observed DDoS activity, only that the protocol behavior enabled amplification risk. The patch does not show complete elimination of all UDP amplification vectors in Solana gossip. The issue is not best classified as generic cryptographic replay validation; signatures support the endpoint-proof mechanism but the core bug is unauthenticated source-address use. The provided evidence does not quantify amplification beyond the commit message report. Confirmed by explicit security report reference in the commit message. Confirmed by code path gating pull-response generation on check_pull_request. Ping/pong helper code should be treated as support code, not the root cause. No evidence proves actual DDoS exploitation or complete removal of all UDP amplification vectors. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `udp-amplification-missing-endpoint-validation`
Final impact type: `ddos-amplification, traffic-reflection`
Final tags: `blockchain-core, gossip-protocol, udp, ddos-amplification, endpoint-validation, anti-spoofing`

The supplied evidence supports keeping this as a security fix. The commit body explicitly cites a HackerOne report describing UDP gossip amplification through spoofed PullRequest source addresses, and the patch adds ping-pong endpoint proof plus gates pull-response generation on successful verification. The original replay/signature-validation framing is too cryptography-specific; the validated issue is better described as missing endpoint validation enabling UDP reflection/amplification.

## Security Evidence

1. Commit message explicitly describes spoofed UDP PullRequest source addresses causing larger PullResponse traffic to a victim.
2. Patch adds check_pull_request requiring a valid address and prior ping response before accepting pull requests for response generation.
3. handle_pull_requests filters requests through the new predicate before generate_pull_responses.
4. PingMessage and PongMessage are added to protocol verification with verify() checks.
5. Packet return behavior preserves generated ping packets even when pull responses are not emitted, supporting the challenge flow.

## Missing Evidence

1. No evidence of actual exploitation or observed DDoS activity is provided.
2. Patch evidence does not prove all Solana gossip UDP amplification vectors were eliminated.
3. Provided snippets do not fully show PingCache internals or the exact token/hash matching logic.

## Claim Boundaries

1. Supported claim: this fixes a UDP gossip pull-response amplification condition caused by accepting unproven source addresses.
2. Do not classify the core bug as generic replay or signature-validation failure.
3. Do not claim complete DDoS prevention across the protocol.
4. Do not claim exploitability beyond the amplification scenario described in the commit body.
