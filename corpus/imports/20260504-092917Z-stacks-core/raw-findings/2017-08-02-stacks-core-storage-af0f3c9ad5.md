---
case_id: case_20170802_af0f3c9ad5
project: stacks-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2017-08-02
source_refs:
  - git:af0f3c9ad589f907cb45d5852b2f240a981e7172
  - "blockstack_client/subdomains.py:427"
  - "blockstack_client/subdomains.py:450"
  - "blockstack_client/subdomains.py:490"
  - "blockstack_client/profile.py:408"
bug_class: address-bound-authorization-hardening
impact_type:
  - authorization-bypass-risk
confidence: medium
tags:
  - blockchain-core
  - subdomains
  - authorization
  - signature-verification
  - ownership-binding
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is security relevant but the vulnerability thesis is not established by the supplied evidence. The grounded evidence shows subdomain code moving from pubkey-oriented handling toward Bitcoin-address-based ownership, address-bound mutable-data lookup, and scriptSig-style verification. However, the full update acceptance path, validation outcome, and attacker capability are not shown, so this should not be treated as a confirmed vulnerability fix.

## Observed Patch Facts

1. In `blockstack_client/subdomains.py`, the patch replaces `if user_data_pubkey is None:` with `data_address=owner_addr, owner_address=None,`.

2. In `blockstack_client/subdomains.py`, the patch replaces `def sign(sk, plaintext):` with `def verify(address, plaintext, scriptSigb64):`.

3. In `blockstack_client/subdomains.py`, the patch replaces `data = key.public_key().to_hex()` with `pubkey = key.public_key()`.

4. In `blockstack_client/profile.py`, the patch replaces `except jsonschema.ValidationError:` with `except jsonschema.ValidationError as e:`.

## Project Context

Historical context from `blockstack_client/data.py`, `blockstack_client/zonefile.py` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `blockstack_client/data.py`, `blockstack_client/zonefile.py`. The strongest project-level identifiers around this patch are `None`, `pubkey`, `plaintext`, and `user_data_pubkey`.

## Before/After Behavior

Before the patch, the shown subdomain profile path could default a missing zonefile data pubkey to an owner public key and called `storage.get_mutable_data` with `data_address=None`. After the patch, profile retrieval passes `data_address=owner_addr`, where `owner_addr` comes from `my_rec.address`. The signature helper changed from public-key/raw-signature verification to an address plus scriptSig-like verification interface. Ownership encoding changed from a `pubkey:data:<hex pubkey>` style entry to returning the public key's Bitcoin address. The `profile.py` change only adds logging for validation exceptions and is diagnostic.

# Root Cause

The evidence supports a narrower root cause: subdomain ownership-related code was not consistently represented or checked through the owning Bitcoin address in the shown paths. It does not prove that this inconsistency allowed unauthorized subdomain updates, mutable-data substitution, or replay.

## Walkthrough

1. `subdomain_record_to_profile(my_rec)` derives `owner_addr` from `my_rec.address`.

2. The old shown profile-fetch path could use a defaulted public key while leaving `data_address` unset.

3. The patched profile-fetch path passes `data_address=owner_addr` to `storage.get_mutable_data`.

4. `encode_pubkey_entry(key)` changed from emitting public-key hex data to deriving and returning the public key's address.

5. The local verification API changed from `verify(pk, plaintext, sigb64)` to `verify(address, plaintext, scriptSigb64)`.

6. These changes indicate address-bound subdomain ownership handling, but the evidence does not show a complete vulnerable state transition before the patch.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| blockstack_client/subdomains.py | 412 | Converts a subdomain record into profile data and binds mutable-data retrieval to my_rec.address via data_address=owner_addr. |
| blockstack_client/subdomains.py | 450 | Replaces raw pubkey signature verification with address plus scriptSig-style verification for plaintext. |
| blockstack_client/subdomains.py | 485 | Encodes subdomain ownership material as the public key's Bitcoin address instead of a pubkey:data entry. |
| blockstack_client/profile.py | 383 | Logs profile account schema validation exceptions; appears diagnostic and not part of the security invariant. |

## Code Snippets

## Snippet 1

Context: `blockstack_client/subdomains.py:427` (changes a sensitive control or state-update path)

Before
```python
pass # no pubkey defined in zonefile

    if user_data_pubkey is None:
        user_data_pubkey = owner_pubkey.to_hex()

    try:
        user_profile = storage.get_mutable_data(
            None, user_data_pubkey, blockchain_id=None,
```
After
```python
pass # no pubkey defined in zonefile

    try:
        user_profile = storage.get_mutable_data(
            None, user_data_pubkey, blockchain_id=None,
            data_address=owner_addr, owner_address=None,
            urls=urls, drivers=None, decode=True,
        )
```

## Snippet 2

Context: `blockstack_client/subdomains.py:450` (changes signature or replay validation logic)

Before
```python
#   2> didn't want this code to necessarily depend on virtualchain

def sign(sk, plaintext):
    signer = ecdsa.SigningKey.from_pem(sk.to_pem())
    blob = signer.sign_deterministic(plaintext, hashfunc = hashlib.sha256)
    return base64.b64encode(blob)

def verify(pk, plaintext, sigb64):
```
After
```python
#   2> didn't want this code to necessarily depend on virtualchain

def verify(address, plaintext, scriptSigb64):
    assert isinstance(address, str)

    scriptSig = base64.b64decode(scriptSigb64)

    vb = keylib.b58check.b58check_version_byte(address)
```

## Snippet 3

Context: `blockstack_client/subdomains.py:490` (changes a sensitive control or state-update path)

Before
```python
"""
    if isinstance(key, keylib.ECPrivateKey):
        data = key.public_key().to_hex()
    elif isinstance(key, keylib.ECPublicKey):
        data = key.to_hex()
    else:
        raise NotImplementedError("No support for this key type")
```
After
```python
"""
    if isinstance(key, keylib.ECPrivateKey):
        pubkey = key.public_key()
    elif isinstance(key, keylib.ECPublicKey):
        pubkey = key
    else:
        raise NotImplementedError("No support for this key type")
```

## Snippet 4

Context: `blockstack_client/profile.py:408` (changes a sensitive control or state-update path)

Before
```python
jsonschema.validate(acct, PROFILE_ACCOUNT_SCHEMA)
            output_accounts.append(acct)
        except jsonschema.ValidationError:
            continue
```
After
```python
jsonschema.validate(acct, PROFILE_ACCOUNT_SCHEMA)
            output_accounts.append(acct)
        except jsonschema.ValidationError as e:
            log.exception(e)
            continue
```

# Fix Pattern

Replace pubkey-shaped ownership and verification inputs with Bitcoin-address-bound lookup and scriptSig-style verification interfaces.

## How It Was Fixed

The patch binds mutable-data retrieval to `owner_addr`, changes ownership encoding to an address, and changes signature verification to take an address and scriptSig-like blob. The supplied evidence does not show enough of the registrar or consensus path to confirm the security effect end to end.

# Why It Matters

1. Subdomain ownership is security-sensitive state.

2. Address-bound lookup can reduce ambiguity between public-key material and owner identity.

3. ScriptSig-style verification may better match Bitcoin ownership proofs.

4. The provided evidence is insufficient to prove an exploitable pre-patch bypass.

# Evidence Notes

Strongest evidence is in `blockstack_client/subdomains.py`: `data_address=owner_addr`, address-returning `encode_pubkey_entry`, and `verify(address, plaintext, scriptSigb64)`. The commit subject also indicates a move to Bitcoin-address ownership and signed updates. Missing evidence includes the complete verification implementation, registrar update acceptance path, consensus rules, failure behavior, replay handling, tests proving rejection of forged updates, and any attacker scenario. `profile.py` logging is unrelated to the security claim. Protocol security invariant: Subdomain ownership and related mutable-data access should be bound to the Bitcoin address recorded for the subdomain, and authorization-sensitive updates should require signature material tied to that address. The provided snippets show movement toward this invariant, but do not establish that the prior code permitted an exploitable unauthorized update or replay. Verification notes: The evidence does not prove an attacker could update another user's subdomain before the patch. The evidence does not show the full registrar update acceptance path or consensus validation path. The evidence only indicates singlesig support; multisig or script edge cases are not proven addressed. The profile.py change appears unrelated to access control or signature validation. No replay protection mechanism beyond address-bound scriptSig verification is shown in the provided snippets. Do not claim confirmed unauthorized update without the update acceptance path. Do not claim replay protection; no nonce or replay mechanism is shown. Do not treat helper or diagnostic logging changes as root cause. Keep out of the security corpus because the patch may be security relevant but the vulnerability thesis is unproven. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `address-bound-authorization-hardening`
Final impact type: `authorization-bypass-risk`
Final confidence: `medium`
Final tags: `blockchain-core, subdomains, authorization, signature-verification, ownership-binding, security-hardening`

The supplied evidence does not prove a concrete exploitable pre-patch vulnerability, so it should not be validated as a security-fix or replay bug. However, the commit subject and shown code changes clearly move subdomain ownership and update verification toward Bitcoin-address-bound authorization and scriptSig-style signature checking, which is security hardening of an ownership-sensitive path.

## Security Evidence

1. Commit subject states subdomains are now owned by Bitcoin addresses and updates require scriptSig-like signatures.
2. Profile retrieval now passes data_address=owner_addr to storage.get_mutable_data instead of leaving data_address unset.
3. Signature verification interface changes from pubkey/raw signature inputs to address plus scriptSig-like input.
4. Ownership encoding changes from pubkey:data:<hex pubkey> to the public key's Bitcoin address.

## Missing Evidence

1. No complete registrar update acceptance path is shown.
2. No caller of the new verify(address, plaintext, scriptSigb64) function is shown in the evidence.
3. No test evidence demonstrates rejection of forged, unauthorized, or replayed subdomain updates.
4. No explicit attacker scenario or prior bypass condition is established.

## Claim Boundaries

1. Treat this as address-bound authorization hardening, not a confirmed vulnerability fix.
2. Do not claim proven replay protection; no nonce or replay-specific mechanism is shown.
3. Do not claim arbitrary subdomain takeover without the full update validation path.
4. The profile.py logging change is diagnostic and should not be part of the security claim.
