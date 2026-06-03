# Delayed Identity Reservation And Public Keys

## Family Objective

Find bugs where a source-side action accepts value, authority, or registration data before the delayed sink validates public-key semantics, ownership, uniqueness, or identity reservation.

## Hunt Steps

1. Enumerate identity-bearing actions: validator creation, delegation, operator registration, withdrawal setup, claim creation, key rotation, committee admission, bridge recipient registration, and registry insertion.
2. For each identity, split validation into syntax, encoding, curve or semantic validity, source-side ownership, sink-side uniqueness, later consumer compatibility, and recovery/refund behavior.
3. Trace public keys and consensus keys past first storage. Include conversion helpers, address derivation, staking or registry state, active-set construction, signature verification, decompression, slashing, rewards, exports, and cross-runtime adapters.
4. Search for length-only checks, address-only checks, allowlist-only checks, or conversion helpers that construct key objects without proving curve membership.
5. Search for sink-side uniqueness checks that are not reserved at source admission. Include public keys, consensus keys, operator addresses, validator IDs, withdrawal IDs, claim IDs, registry keys, and message offsets.
6. Build a two-actor timeline:
   - actor A reserves or stores the shared sink identity with lower value, weaker ownership, malformed data, or a different account;
   - actor B later completes a legitimate source-side action involving the same identity;
   - the delayed sink rejects, downgrades, or strands actor B's value or authority;
   - recovery, retry, refund, or rename is absent or insufficient.
7. For malformed public keys, build a consumer timeline:
   - source admission stores the key;
   - no semantic key validation runs before persistence;
   - a deterministic consensus or validator-set consumer later decodes, decompresses, verifies, exports, or counts the key;
   - the consumer error is returned, persisted, skipped, or made consensus-visible.
8. Distinguish self-loss from third-party griefing. Self-loss may still matter if it halts consensus or active-set construction; third-party griefing needs actor B's unrecoverable value, authority, identity, or participation loss.

## Candidate Requirements

For every candidate, include:

- source entrypoint and accepted value, authority, or registration;
- sink identity and uniqueness or semantic-validation rule;
- public-key validation matrix when keys are involved;
- two-actor timeline for front-running or malformed-reservation cases;
- downstream consumer that makes the late validation security-relevant;
- recovery/refund/retry path or proof that it is missing;
- concrete impact and minimal reproducer.

## False-Positive Controls

- Do not report a malformed key if all untrusted paths validate curve membership before persistence or before any deterministic consumer can see it.
- Do not report duplicate identity self-loss as third-party griefing without two actors and a shared sink identity.
- Do not report late rejection if a durable, usable recovery path restores the source-side value or authority.
