---
case_id: case_20201028_ae91270961
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
  - git:ae91270961599869e846fd7dd642c3c9090b8085
  - "core/src/cluster_info.rs:2091"
  - "core/src/cluster_info.rs:2018"
  - "core/src/cluster_info.rs:428"
  - "core/src/cluster_info.rs:1941"
bug_class: udp-amplification-via-source-spoofing
impact_type:
  - denial-of-service
  - traffic-amplification
tags:
  - blockchain-core
  - gossip-protocol
  - udp
  - source-address-spoofing
  - ddos-amplification
  - endpoint-proof
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Confirmed security fix for spoofed-source UDP amplification in Solana gossip pull handling. The commit body explicitly describes PullRequest source spoofing causing much larger PullResponse traffic to a victim, and the patch adds Ping/Pong handling plus a pull-request gate that filters requests before response generation unless the source address has passed the endpoint check.

## Observed Patch Facts

1. In `core/src/cluster_info.rs`, the patch replaces `if packets.is_empty() {` with `packets`.

2. In `core/src/cluster_info.rs`, the patch replaces `self.time_gossip_write_lock("process_pull_reqs", &self.stats.process_pull_requests)` with `.zip(addrs.into_iter())`.

3. In `core/src/cluster_info.rs`, the patch adds `Protocol::PingMessage(ref ping) => {`.

4. In `core/src/cluster_info.rs`, the patch replaces `// Pull requests take an incoming bloom filter of contained entries from a node` with `// Returns a predicate checking if the pull request is from a valid`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/src/ping_pong.rs`, `core/src/verified_vote_packets.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/ping_pong.rs`, `core/src/window_service.rs`. The strongest project-level identifiers around this patch are `packets`, `ping`, `Some`, and `Protocol::PingMessage`.

## Before/After Behavior

Before the patch, the provided evidence shows pull requests being processed into caller/filter pairs and PullResponse packets without an observed endpoint-proof gate tied to the UDP source address; filtering was limited to invalid destination addresses and empty responses. After the patch, `check_pull_request` filters pull requests by address validity and prior ping response, queues pings for addresses needing verification, and is applied before `generate_pull_responses`. Ping and Pong protocol messages are also verified and dropped when invalid.

# Root Cause

The PullRequest path lacked endpoint reachability validation before generating larger UDP PullResponse packets, allowing a spoofed source address to be used as the response destination.

## Walkthrough

1. A gossip message reaches `Protocol::par_verify` in `core/src/cluster_info.rs`.

2. The patch adds `Protocol::PingMessage` and `Protocol::PongMessage` branches that call `verify()` and reject invalid messages.

3. Pull requests enter `handle_pull_requests` in `core/src/cluster_info.rs`.

4. The new `check_pull_request` predicate checks that the source address is valid and has responded to a ping request, and appends ping packets when verification is needed.

5. `handle_pull_requests` filters incoming pull requests through that predicate before constructing caller/filter pairs for response generation.

6. Only filtered requests are passed to `generate_pull_responses`.

7. Generated responses are paired with the filtered addresses and empty responses are suppressed.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/cluster_info.rs | 382 | Adds Protocol::PingMessage and Protocol::PongMessage verification in gossip packet verification before accepting those protocol messages. |
| core/src/cluster_info.rs | 1941 | Introduces check_pull_request predicate to require valid source address and prior ping-pong response, while queuing pings for addresses needing verification. |
| core/src/cluster_info.rs | 1988 | Applies check_pull_request during handle_pull_requests before caller/filter pairs are used to generate PullResponse packets. |
| core/src/cluster_info.rs | 2018 | Changes pull response processing to pair generated responses with filtered source addresses and suppress empty responses. |
| core/src/ping_pong.rs | 8 | Defines signed Ping/Pong message structures used by the endpoint-proof mechanism. |

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

Add endpoint proof before amplification-prone UDP responses, cache successful ping-pong checks, verify Ping/Pong protocol messages, and gate PullRequest response generation on that proof.

## How It Was Fixed

The patch adds Ping/Pong protocol support and verification, introduces a PingCache according to the commit body, and adds `check_pull_request` to the gossip pull path. Requests from unverified or invalid source addresses are filtered before PullResponse generation, while ping packets are queued for addresses that need verification.

# Why It Matters

1. Reduces spoofed-source UDP amplification in the gossip pull path.

2. Prevents unauthenticated PullRequests from directly triggering larger responses to a victim address.

3. Keeps the finding scoped to endpoint-proof failure, not a cryptographic primitive flaw.

4. Does not establish protection for every UDP response path or every gossip-layer denial-of-service vector.

# Evidence Notes

Primary support comes from the commit body describing HackerOne report 991106 and the stated 34x PullRequest-to-PullResponse amplification, plus `core/src/cluster_info.rs` excerpts showing Ping/Pong verification, `check_pull_request`, and filtering before `generate_pull_responses`. `core/src/ping_pong.rs` supports the added endpoint-proof mechanism. The evidence does not support claims of remote code execution, consensus compromise, or a general cryptographic vulnerability. Protocol security invariant: A gossip node should not send large UDP PullResponse traffic to a claimed source address until that endpoint has proven reachability through the ping-pong check. Verification notes: The patch does not prove remote code execution or consensus compromise. The patch does not show a cryptographic primitive vulnerability; signatures support the endpoint-proof protocol. The provided evidence does not quantify exploitability beyond the commit/report description of amplification. The fix addresses spoofed-source PullRequest amplification, not all possible gossip-layer denial-of-service vectors. The evidence does not prove that every UDP response path in the project now has endpoint proof. Commit message explicitly identifies spoofed UDP PullRequest amplification as the issue. Code comments describe checking source address validity and prior ping response. Patch places the new predicate before PullResponse generation. Ping/Pong messages are accepted only if `verify()` succeeds. No evidence proves broader gossip DoS coverage beyond this pull-request path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `udp-amplification-via-source-spoofing`
Final impact type: `denial-of-service, traffic-amplification`
Final tags: `blockchain-core, gossip-protocol, udp, source-address-spoofing, ddos-amplification, endpoint-proof`

The supplied evidence strongly supports a security fix: the commit body explicitly describes spoofed UDP PullRequest packets causing much larger PullResponse traffic to a victim, and the patch adds a ping-pong endpoint proof plus filtering before PullResponse generation. The original cryptography/replay framing is too specific and misleading; the validated issue is spoofed-source UDP amplification in gossip pull handling.

## Security Evidence

1. Commit body cites a HackerOne report describing UDP gossip amplification via spoofed PullRequest source addresses.
2. Patch introduces Ping/Pong protocol message handling with verification before accepting those messages.
3. New check_pull_request predicate requires a valid source address and prior ping response, and queues pings for addresses needing verification.
4. handle_pull_requests filters requests through check_pull_request before generate_pull_responses creates larger responses.
5. Responses are paired only with filtered addresses and empty responses are suppressed.

## Missing Evidence

1. Provided snippets do not show the complete PingCache implementation or all cache expiry rules.
2. Evidence does not independently prove exploitability beyond the commit/report description.
3. Evidence does not show that every UDP response path in the project received endpoint proof.

## Claim Boundaries

1. Validated as a fix for spoofed-source UDP PullRequest amplification in Solana gossip handling.
2. Do not classify as a general cryptographic primitive flaw or replay/signature-validation vulnerability.
3. Do not claim remote code execution, consensus compromise, or full gossip-layer DoS prevention.
4. Security relevance is limited to endpoint reachability validation before amplification-prone PullResponse traffic.
