---
case_id: case_20200806_5c4b8153c6
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2020-08-06
source_refs:
  - git:5c4b8153c68c02957c4f14f264a8db95e5c09c54
  - "web3.js/src/publickey.js:111"
  - "web3.js/src/publickey.js:3"
  - "web3.js/module.flow.js:30"
  - "web3.js/module.flow.js:16"
bug_class: missing-off-curve-address-validation
impact_type:
  - security-invariant-bypass
tags:
  - blockchain-core
  - cryptography
  - program-derived-address
  - ed25519
  - invariant-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Solana web3.js program-address derivation by adding an explicit ed25519 curve-membership rejection in `PublicKey.createProgramAddress`. The evidence supports a missing off-curve validation gate in the client helper, but does not establish a concrete exploit, known private key, replay issue, or runtime consensus vulnerability.

## Observed Patch Facts

1. In `web3.js/src/publickey.js`, the patch replaces `hash = await sha256(new Uint8Array(new BN(hash, 16).toBuffer()));` with `let publicKeyBytes = new BN(hash, 16).toBuffer();`.

2. In `web3.js/src/publickey.js`, the patch replaces `/**` with `//$FlowFixMe`.

3. In `web3.js/module.flow.js`, the patch adds `static findProgramAddress(`.

4. In `web3.js/module.flow.js`, the patch adds `declare export type PublicKeyNonce = [PublicKey, number];`.

## Project Context

The changed code sits primarily in `web3.js/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `web3.js/src/transaction.js`, `web3.js/src/sysvar.js` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `web3.js/src/transaction.js`, `web3.js/src/sysvar.js`. The strongest project-level identifiers around this patch are `PublicKey`, `hash`, `import`, and `from`. Nearby tests or test-like files include `web3.js/test/mockrpc/get-recent-blockhash.js`, `web3.js/test/publickey.test.js`.

## Before/After Behavior

Before the patch, `createProgramAddress` hashed the seed/program-id/domain buffer, hashed again over BN-converted bytes, and returned a `PublicKey` from the resulting hex string without a visible curve-membership check. After the patch, it hashes once, converts the digest to bytes, rejects the result if `is_on_curve(publicKeyBytes)` is true, and only returns a `PublicKey` for off-curve bytes.

# Root Cause

The web3.js PDA derivation helper did not visibly enforce the off-curve requirement before constructing and returning a `PublicKey` from derived seed material.

## Walkthrough

1. `web3.js/src/publickey.js` derives address material from seeds, `programId.toBuffer()`, and the `ProgramDerivedAddress` marker.

2. The previous code performed a second SHA-256 over BN-converted hash bytes and returned `new PublicKey('0x' + hash)`.

3. The patch imports `tweetnacl` and exposes `nacl.lowlevel` support used by the curve check.

4. The patched code converts the SHA-256 digest into `publicKeyBytes`.

5. It calls `is_on_curve(publicKeyBytes)` before constructing the `PublicKey`.

6. If the derived bytes are on-curve, it throws `Invalid seeds, address must fall off the curve`.

7. Flow declarations are updated to include `PublicKeyNonce` and `findProgramAddress`; these are supporting API/type changes, not the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| web3.js/src/publickey.js | 3 | adds tweetnacl low-level access used for ed25519 curve membership checks |
| web3.js/src/publickey.js | 105 | derives program address bytes from seeds/program id and rejects on-curve addresses |
| web3.js/module.flow.js | 16 | exports PublicKeyNonce type for program-address search API |
| web3.js/module.flow.js | 30 | declares findProgramAddress API returning a valid address and nonce |

## Code Snippets

## Snippet 1

Context: `web3.js/src/publickey.js:111` (changes signature or replay validation logic)

Before
```javascript
]);
    let hash = await sha256(new Uint8Array(buffer));
    hash = await sha256(new Uint8Array(new BN(hash, 16).toBuffer()));
    return new PublicKey('0x' + hash);
  }
}
```
After
```javascript
]);
    let hash = await sha256(new Uint8Array(buffer));
    let publicKeyBytes = new BN(hash, 16).toBuffer();
    if (is_on_curve(publicKeyBytes)) {
      throw new Error(`Invalid seeds, address must fall off the curve`);
    }
    return new PublicKey(publicKeyBytes);
  }
```

## Snippet 2

Context: `web3.js/src/publickey.js:3` (changes a sensitive control or state-update path)

Before
```javascript
import BN from 'bn.js';
import bs58 from 'bs58';
import {sha256} from 'crypto-hash';

/**
 * A public key
```
After
```javascript
import BN from 'bn.js';
import bs58 from 'bs58';
import nacl from 'tweetnacl';
import {sha256} from 'crypto-hash';

//$FlowFixMe
let naclLowLevel = nacl.lowlevel;
```

## Snippet 3

Context: `web3.js/module.flow.js:30` (changes bounds, limits, or capacity handling)

Before
```javascript
programId: PublicKey,
    ): Promise<PublicKey>;
    equals(publickey: PublicKey): boolean;
    toBase58(): string;
```
After
```javascript
programId: PublicKey,
    ): Promise<PublicKey>;
    static findProgramAddress(
      seeds: Array<Buffer | Uint8Array>,
      programId: PublicKey,
    ): Promise<PublicKeyNonce>;
    equals(publickey: PublicKey): boolean;
    toBase58(): string;
```

## Snippet 4

Context: `web3.js/module.flow.js:16` (changes a sensitive control or state-update path)

Before
```javascript
declare module '@solana/web3.js' {
  // === src/publickey.js ===
  declare export class PublicKey {
    constructor(
```
After
```javascript
declare module '@solana/web3.js' {
  // === src/publickey.js ===
  declare export type PublicKeyNonce = [PublicKey, number];
  declare export class PublicKey {
    constructor(
```

# Fix Pattern

Add invariant validation at the deterministic address-construction boundary and reject derived addresses that do not satisfy the off-curve requirement.

## How It Was Fixed

The implementation replaced the previous second-hash return path with explicit byte derivation, ed25519 curve-membership checking, and an error on on-curve outputs. Supporting Flow declarations were added for the PDA search API.

# Why It Matters

1. Keeps the client helper aligned with the off-curve PDA invariant.

2. Prevents this derivation path from accepting seed outputs the patched code defines as invalid.

3. Supports signer-separation assumptions for program-derived addresses.

4. Does not prove direct fund theft, privilege escalation, replay, or a known private key.

# Evidence Notes

Grounded evidence is limited to `web3.js/src/publickey.js` and `web3.js/module.flow.js`. The strong replay/signature-validation framing from the heuristic baseline is unsupported. The patch shows client-side PDA derivation validation, not transaction replay handling, runtime consensus validation, or an demonstrated exploit. Helper/type additions should be treated as support code. Protocol security invariant: Program-derived addresses are required by the patched code comments and error path to fall off the ed25519 curve; `createProgramAddress` should reject derived bytes when `is_on_curve` reports true. Verification notes: The patch does not prove that any existing generated address had a known private key. The patch does not show transaction replay handling being changed. The patch does not show runtime consensus validation logic; evidence is limited to web3.js client-side PDA derivation/API behavior. The patch does not establish direct fund theft or privilege escalation without additional chain/runtime context. Confirmed evidence of a new `is_on_curve(publicKeyBytes)` rejection gate. Confirmed prior snippet lacks a visible curve-membership rejection. Downgraded from confirmed security-fix to likely security-hardening because exploitability is not established by the supplied evidence. Kept in corpus because the patch directly enforces a security-relevant address invariant. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-off-curve-address-validation`
Final impact type: `security-invariant-bypass`
Final tags: `blockchain-core, cryptography, program-derived-address, ed25519, invariant-validation`

The supplied patch evidence supports retaining this as security hardening: `createProgramAddress` now rejects derived public key bytes that are on the ed25519 curve, enforcing the stated program-address off-curve invariant. The evidence does not prove a concrete exploit, replay flaw, known private key, fund theft path, or runtime consensus vulnerability, so the original replay/signature-validation framing is too specific.

## Security Evidence

1. Adds `tweetnacl` low-level access for curve membership checking.
2. Changes program address derivation to compute `publicKeyBytes` and call `is_on_curve(publicKeyBytes)`.
3. Throws `Invalid seeds, address must fall off the curve` when derived bytes are on-curve.
4. Patch subject explicitly says program addresses must land off-curve.
5. Flow/API additions support program-address discovery but are secondary to the invariant check.

## Missing Evidence

1. No demonstrated exploit or attacker workflow is provided.
2. No evidence that an on-curve derived address had a known or recoverable private key.
3. No transaction replay logic is changed.
4. No runtime or consensus validation code is shown.
5. No direct fund theft, privilege escalation, or signature forgery impact is proven.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Limit the finding to client-side program-derived-address validation in web3.js.
3. Do not claim replay prevention from the supplied evidence.
4. Do not claim consensus-layer enforcement changed.
5. Do not claim concrete exploitability beyond enforcing the off-curve address invariant.
