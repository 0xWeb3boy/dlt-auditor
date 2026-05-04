# Validation Card

## Metadata

- ID: `stacks-core-2024-02-07-stacks-core-p2p-networking-8778d4f74a`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-role-enforcement`

## What Confirmed The Issue

- Evidence 1: In `stacks-signer/src/runloop.rs`, the patch removes `/// Helper function for determining the coordinator public key given the the public keys`.
- Evidence 2: In `stacks-signer/src/client/stacks_client.rs`, the patch replaces `/// Retrieve the signer slots stored within the stackerdb contract` with `/// Calculate the coordinator address by comparing the provided public keys against t [truncated]`.

## What Could Have Invalidated It

- Compensating control 1: The caller may already be authenticated by an outer dispatcher.
- Compensating control 2: The changed path may be read-only or test-only rather than a privileged mutation.

## Severity Guidance

- Expected impact band: `authorization_or_message_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: The caller may already be authenticated by an outer dispatcher.
- Caution 2: The changed path may be read-only or test-only rather than a privileged mutation.
