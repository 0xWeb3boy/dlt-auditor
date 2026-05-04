# Validation Card

## Metadata

- ID: `stacks-core-2017-08-02-stacks-core-storage-af0f3c9ad5`
- Bug family: `authz_and_role_gates`
- Bug class: `address-bound-authorization-hardening`

## What Confirmed The Issue

- Evidence 1: In `blockstack_client/subdomains.py`, the patch replaces `if user_data_pubkey is None:` with `data_address=owner_addr, owner_address=None,`.
- Evidence 2: In `blockstack_client/subdomains.py`, the patch replaces `def sign(sk, plaintext):` with `def verify(address, plaintext, scriptSigb64):`.

## What Could Have Invalidated It

- Compensating control 1: The caller may already be authenticated by an outer dispatcher.
- Compensating control 2: The changed path may be read-only or test-only rather than a privileged mutation.

## Severity Guidance

- Expected impact band: `authorization_or_message_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The caller may already be authenticated by an outer dispatcher.
- Caution 2: The changed path may be read-only or test-only rather than a privileged mutation.
