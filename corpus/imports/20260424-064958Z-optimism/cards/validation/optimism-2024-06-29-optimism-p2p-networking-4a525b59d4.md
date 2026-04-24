# Validation Card

## Metadata

- ID: `optimism-2024-06-29-optimism-p2p-networking-4a525b59d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-selection-hardening`

## What Confirmed The Issue

- sync.go disables outbound peer request handling for non-static peers when syncOnlyReqToStatic is enabled.
- host.go adds IsStatic(peerID) and exposes SyncOnlyReqToStatic() so the sync client can enforce the policy.
- NewSyncClient now reads the host capability and activates the restriction only when the policy flag is set.
- The change affects the P2P sync request path, which is a security-sensitive network trust boundary.

## What Could Have Invalidated It

- No evidence shows the old behavior enabled a concrete attack or exploitable bug.
- No evidence shows the new flag is enabled by default or broadly deployed.
- No evidence ties the change to resource exhaustion, remote DoS, integrity loss, or auth bypass.
- No test or commit text demonstrates an adversarial scenario against non-static peers.

## Severity Guidance

- Expected impact band: security-hardening-or-correctness
- Expected severity band: low_or_informational

## False-Positive Cautions

- No evidence shows the old behavior enabled a concrete attack or exploitable bug.
- No evidence shows the new flag is enabled by default or broadly deployed.
- No evidence ties the change to resource exhaustion, remote DoS, integrity loss, or auth bypass.
