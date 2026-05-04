---
case_id: case_20211111_93e7c65a8
project: snarkvm
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: medium
date: 2021-11-11
source_refs:
  - git:93e7c65a8c693a5d09479cb8d9a5e2d90c04d182
  - "algorithms/src/crh/bhp.rs:150"
  - "gadgets/src/algorithms/encryption/ecies_poseidon.rs:576"
  - "gadgets/src/algorithms/encryption/ecies_poseidon.rs:494"
  - "dpc/src/record/record.rs:112"
bug_class: cryptographic-domain-separation-hardening
impact_type:
  - cryptographic-binding-hardening
confidence: medium
tags:
  - blockchain-core
  - cryptography
  - encryption
  - domain-separation
  - poseidon
  - zero-knowledge-gadgets
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is clearly in sensitive cryptographic code and appears to improve or correct encryption-scheme derivations, especially by adding an `AleoEncryption2021` domain separator to ECIES Poseidon gadget sponge absorption and deriving record commitment randomness from the record view key. However, the supplied evidence does not prove a vulnerability, exploit path, forgery, decryption issue, replay issue, or native/gadget mismatch. Treat this as security-relevant but unconfirmed hardening/correctness work, not a validated vulnerability fix.

## Observed Patch Facts

1. In `algorithms/src/crh/bhp.rs`, the patch replaces `pub(crate) fn hash_bits_inner(&self, input: &[bool]) -> Result<G, CRHError> {` with `/// Precondition: number of elements in 'input' == 'num_bits'.`.

2. In `gadgets/src/algorithms/encryption/ecies_poseidon.rs`, the patch replaces `sponge.absorb(cs.ns(|| "absorb"), [symmetric_key.x].iter())?;` with `let domain_separator = FpGadget::alloc_constant(cs.ns(|| "domain_separator"), || {`.

3. In `gadgets/src/algorithms/encryption/ecies_poseidon.rs`, the patch replaces `sponge.absorb(cs.ns(|| "absorb"), [ecdh_value.x].iter())?;` with `let domain_separator = FpGadget::alloc_constant(cs.ns(|| "domain_separator"), || {`.

4. In `dpc/src/record/record.rs`, the patch replaces `/// Returns a record from the given account view key and ciphertext.` with `fn view_key_to_comm_randomness(record_view_key: N::RecordViewKey) -> Result<N::Progra...`.

## Project Context

The changed code sits primarily in `algorithms/src/crh`, `algorithms/src`, `gadgets/src/algorithms/encryption`, which anchors the finding in the `cryptography` area of the project. Historical context from `algorithms/src/crh/pedersen_compressed.rs`, `gadgets/src/algorithms/encryption/tests.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `algorithms/src/encryption/ecies_poseidon.rs`, `gadgets/src/algorithms/signature/aleo.rs`. The strongest project-level identifiers around this patch are `TE::BaseField`, `sponge`, `absorb`, and `BaseField`.

## Before/After Behavior

Before the patch, the visible ECIES Poseidon gadget paths absorbed only bare ECDH/key coordinate material such as `[ecdh_value.x]` or `[symmetric_key.x]` before squeezing derived values. After the patch, they allocate a constant field element from `b"AleoEncryption2021"` and absorb `[domain_separator, symmetric_key]`. The record construction path now explicitly derives commitment randomness from `record_view_key` through `view_key_to_comm_randomness` before committing `ciphertext` and `owner`. The BHP hash internal API changed from slice input with internal length checking to an iterator plus explicit `num_bits` precondition.

# Root Cause

Not established. The evidence supports that the old code lacked the newly added explicit domain separator in the shown gadget paths and did not show the new helper-based record commitment randomness derivation. It does not prove that these omissions caused an exploitable cryptographic flaw.

## Walkthrough

1. The scalar-randomness ECIES gadget path computes key material from randomness and a public key, then uses a Poseidon sponge to derive downstream values.

2. The visible pre-patch sponge input in that path was only coordinate/key material, without the shown scheme-specific domain separator.

3. The patched path allocates `domain_separator` from `b"AleoEncryption2021"` and absorbs it with `symmetric_key`.

4. The ciphertext-randomizer/private-key check path received the same visible domain-separator treatment.

5. The record path now derives commitment randomness from the serialized record view key mapped into the program scalar field.

6. The BHP change makes bit count explicit for iterator-based hashing, but the provided evidence does not connect this to a security failure.

7. Nearby references to `key_commitment` and `public_key_commitment` may indicate additional binding changes, but the excerpts are incomplete and should not be treated as proven root cause evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| gadgets/src/algorithms/encryption/ecies_poseidon.rs | 472 | Encryption gadget path deriving sponge outputs from scalar randomness and public key using domain-separated symmetric key material. |
| gadgets/src/algorithms/encryption/ecies_poseidon.rs | 554 | Encryption gadget path checking ciphertext randomizer/private key encryption using domain-separated symmetric key material. |
| dpc/src/record/record.rs | 78 | Record construction path encrypting plaintext and committing ciphertext plus owner with randomness derived from the record view key. |
| dpc/src/record/record.rs | 112 | Helper converting record view key bytes into program scalar field commitment randomness. |
| algorithms/src/crh/bhp.rs | 150 | BHP hash internal bit handling path now parameterized by iterator and explicit bit count precondition. |

## Code Snippets

## Snippet 1

Context: `algorithms/src/crh/bhp.rs:150` (changes a sensitive control or state-update path)

Before
```rust
}

    pub(crate) fn hash_bits_inner(&self, input: &[bool]) -> Result<G, CRHError> {
        if input.len() > WINDOW_SIZE * NUM_WINDOWS {
            return Err(CRHError::IncorrectInputLength(input.len(), WINDOW_SIZE, NUM_WINDOWS));
        }
        debug_assert!(WINDOW_SIZE <= MAX_WINDOW_SIZE);
```
After
```rust
}

    /// Precondition: number of elements in `input` == `num_bits`.
    pub(crate) fn hash_bits_inner<S: Borrow<bool>>(
        &self,
        input: impl Iterator<Item = S>,
        num_bits: usize,
    ) -> Result<G, CRHError> {
```

## Snippet 2

Context: `gadgets/src/algorithms/encryption/ecies_poseidon.rs:576` (changes a sensitive control or state-update path)

Before
```rust
<TE::BaseField as PoseidonDefaultParametersField>::get_default_poseidon_parameters(4, false).unwrap();
        let mut sponge = PoseidonSpongeGadget::<TE::BaseField>::new(cs.ns(|| "sponge"), &params);
        sponge.absorb(cs.ns(|| "absorb"), [symmetric_key.x].iter())?;

        // Squeeze one element for the public key commitment randomness.
        let public_key_commitment_randomness =
            sponge.squeeze_field_elements(cs.ns(|| "squeeze field elements for polyMAC"), 1)?[0].clone();
```
After
```rust
<TE::BaseField as PoseidonDefaultParametersField>::get_default_poseidon_parameters(4, false).unwrap();
        let mut sponge = PoseidonSpongeGadget::<TE::BaseField>::new(cs.ns(|| "sponge"), &params);
        let domain_separator = FpGadget::alloc_constant(cs.ns(|| "domain_separator"), || {
            Ok(TE::BaseField::from_bytes_le_mod_order(b"AleoEncryption2021"))
        })?;
        sponge.absorb(cs.ns(|| "absorb"), [domain_separator, symmetric_key].iter())?;

        // Squeeze one element for the public key commitment randomness.
```

## Snippet 3

Context: `gadgets/src/algorithms/encryption/ecies_poseidon.rs:494` (changes a sensitive control or state-update path)

Before
```rust
<TE::BaseField as PoseidonDefaultParametersField>::get_default_poseidon_parameters(4, false).unwrap();
        let mut sponge = PoseidonSpongeGadget::<TE::BaseField>::new(cs.ns(|| "sponge"), &params);
        sponge.absorb(cs.ns(|| "absorb"), [ecdh_value.x].iter())?;

        // Squeeze one element for the commitment randomness.
        let commitment_randomness =
            sponge.squeeze_field_elements(cs.ns(|| "squeeze field elements for polyMAC"), 1)?[0].clone();
```
After
```rust
<TE::BaseField as PoseidonDefaultParametersField>::get_default_poseidon_parameters(4, false).unwrap();
        let mut sponge = PoseidonSpongeGadget::<TE::BaseField>::new(cs.ns(|| "sponge"), &params);
        let domain_separator = FpGadget::alloc_constant(cs.ns(|| "domain_separator"), || {
            Ok(TE::BaseField::from_bytes_le_mod_order(b"AleoEncryption2021"))
        })?;
        sponge.absorb(cs.ns(|| "absorb"), [domain_separator, symmetric_key].iter())?;

        // Squeeze one element for the commitment randomness.
```

## Snippet 4

Context: `dpc/src/record/record.rs:112` (changes a sensitive control or state-update path)

Before
```rust
}

    /// Returns a record from the given account view key and ciphertext.
    pub fn from_account_view_key(
```
After
```rust
}

    fn view_key_to_comm_randomness(record_view_key: N::RecordViewKey) -> Result<N::ProgramScalarField, RecordError> {
        Ok(N::ProgramScalarField::from_bytes_le_mod_order(&to_bytes_le![
            record_view_key
        ]?))
    }
```

# Fix Pattern

Add explicit context/domain input to cryptographic sponge derivations and make record commitment randomness derivation explicit. Adjust hash internals to carry explicit bit counts.

## How It Was Fixed

The ECIES Poseidon gadget now absorbs a constant `AleoEncryption2021` domain separator together with derived symmetric key material in the shown encryption-check paths. The record code now computes commitment randomness through `view_key_to_comm_randomness(record_view_key)`. The BHP hash helper now takes an iterator and explicit `num_bits` rather than a boolean slice.

# Why It Matters

1. The changed code is cryptographic and consensus-sensitive in nature.

2. Domain separation can prevent accidental cross-context reuse, but the provided evidence does not show such reuse occurred.

3. Record commitment randomness derivation affects commitment behavior, but exploitability is not demonstrated.

4. The BHP change may be correctness or API alignment rather than a vulnerability fix.

# Evidence Notes

Grounded evidence comes from `gadgets/src/algorithms/encryption/ecies_poseidon.rs`, `dpc/src/record/record.rs`, and `algorithms/src/crh/bhp.rs`. Unsupported claims removed: no confirmed exploit, no proven plaintext recovery, no proven forgery, no proven replay issue, no proven access-control issue, and no proven native/gadget divergence. The commit subject says `Fix encryption scheme`, but the supplied excerpts are insufficient to validate this as a security fix for corpus inclusion. Protocol security invariant: Cryptographic encryption and commitment derivations should use the intended key material and context-specific inputs consistently. The provided evidence shows changes to Poseidon sponge inputs, record commitment randomness derivation, and BHP bit-length plumbing, but it does not establish that the previous behavior violated a concrete security invariant exploitable by an attacker. Verification notes: Exploitability is not proven by the provided patch evidence. No concrete forgery, decryption, replay, or access-control bypass is shown. The BHP change may be correctness or API alignment unless tied to a specific malformed-input security path. The evidence does not prove whether native and gadget encryption previously diverged in all call paths. The commit reasons mention access control and resource control, but the visible hunks mainly support cryptographic binding/domain-separation analysis. No tests or exploit demonstrations are provided in the input. The excerpts show changed cryptographic derivation inputs but not the full old/new scheme semantics. The BHP change should not be counted as security-relevant without additional evidence. Keep out of the security corpus unless external evidence links this patch to a concrete vulnerability or documented security invariant violation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cryptographic-domain-separation-hardening`
Final impact type: `cryptographic-binding-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, cryptography, encryption, domain-separation, poseidon, zero-knowledge-gadgets`

The supplied patch evidence does not prove a concrete exploitable vulnerability, but it does show security-sensitive cryptographic derivations being tightened. In particular, ECIES Poseidon gadget paths changed from absorbing bare key/ECDH coordinate material to absorbing an explicit scheme domain separator together with symmetric key material. That is sufficient for a conservative security-hardening corpus entry, while avoiding stronger claims such as plaintext recovery, forgery, replay, or access-control bypass.

## Security Evidence

1. ECIES Poseidon gadget derivations now allocate and absorb a constant domain separator derived from "AleoEncryption2021".
2. The changed sponge inputs affect encryption-related commitment/randomness derivation paths in zero-knowledge gadget code.
3. The commit subject is "Fix encryption scheme" and the touched files are cryptographic encryption, commitment, and record code.
4. Record commitment randomness derivation was made explicit from the record view key, affecting cryptographic commitment behavior.

## Missing Evidence

1. No advisory, test, exploit, or failing case is provided.
2. No evidence proves plaintext disclosure, forgery, replay, or consensus breakage.
3. The excerpts do not establish whether native and gadget encryption previously diverged in an exploitable way.
4. The BHP iterator and num_bits change is not tied to a demonstrated security condition.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed vulnerability fix.
2. Do not claim attacker exploitability from the provided evidence alone.
3. Do not treat the BHP API change as independently security-relevant.
4. Do not claim access-control or resource-control impact despite those automated reasons appearing in commit metadata.
