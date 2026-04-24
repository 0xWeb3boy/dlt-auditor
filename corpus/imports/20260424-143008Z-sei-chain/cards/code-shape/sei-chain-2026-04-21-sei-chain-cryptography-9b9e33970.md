# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-04-21-sei-chain-cryptography-9b9e33970`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `secret-key-lifecycle-hardening`

## Code Shape Summary

- The supported finding is Ed25519 secret-key lifecycle hardening, not a proven exploitable vulnerability. The evidence shows changes to SecretKey representation, runtime cleanup registration, and SignWithTag keepalive behavior. The tmhash removal is not tied to a concrete security invariant in the supplied evidence and should be treated as cleanup/API removal unless more context is provided.

## Search Motifs

- Motif 1: runtime.SetFinalizer or cleanup captures the object being cleaned
- Motif 2: signing method lacks runtime.KeepAlive
- Motif 3: raw secret pointer exposed outside key type

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Make key reachability explicit, hide raw secret access, avoid self-retaining cleanup callbacks, and keep key objects alive through signing.

## False Match Warnings

- Secret keys are immutable byte slices with no cleanup finalizers or unsafe pointers.
- The path handles only public keys or test keys.
