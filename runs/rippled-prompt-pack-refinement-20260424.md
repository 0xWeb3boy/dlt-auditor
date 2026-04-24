# rippled Prompt-Pack Refinement Notes

Target repo: `/testing/rippled`

Finding source: `/testing/rippled/validated-findings/kept`

Corpus bundle referenced: `/testing/dlt-ai-audit-system/corpus/imports/20260424-083813Z-rippled`

Date: 2026-04-24

## Repo Context Summary

`rippled` is the XRP Ledger server implementation. Its security-relevant surface is not a single block executor; it is a transaction-processing pipeline, consensus engine, validator trust system, overlay network, RPC/API layer, and amendment-gated protocol implementation.

The core transaction shape is split across preflight, preclaim, authorization, `doApply`, generated ledger side effects, and invariant checking. The important code areas are `src/libxrpl/tx/transactors`, `src/libxrpl/tx/invariants`, `include/xrpl/tx`, `include/xrpl/protocol`, and ledger object helpers. Many kept findings are about checks performed in one transaction phase but not at the exact state-transition sink, or about invariant detectors failing to cover all generated side effects.

Consensus is proposal/validation based. Safety depends on prior-ledger binding, transaction-set identity, close-time and round state, trusted validator sets, quorum thresholds, amendment activation rules, and wrong-ledger or catch-up transitions. The relevant areas are `src/xrpld/consensus`, `src/xrpld/app/consensus`, `src/xrpld/app/ledger`, and validation-related trust code.

Validator trust material has several namespaces: long-term validator master keys, ephemeral validation keys, manifests, revocation state, validator-list publishers, configured quorum or trust thresholds, fetched validator-list sites, and overlay-distributed validator-list messages. Bugs in this repo often come from conflating those namespaces or validating one trust layer while caching or applying another.

## Finding Inventory

The kept set contains 73 findings:

- 53 `input_validation_and_invariant_enforcement`
- 13 `authz_and_role_gates`
- 4 `signature_binding_and_signer_scope`
- 2 `attestation_trust_and_freshness`
- 1 `checked_arithmetic_and_parameter_bounds`

Missing-property distribution:

- 15 authorization
- 13 accounting-integrity
- 10 input-and-state-invariant-validation
- 9 consensus-safety-invariant
- 6 signer-scope-and-domain-binding
- 6 trust-root-and-freshness-validation
- 5 reserve-enforcement
- 4 input-validation
- 4 numeric-bounds
- 1 resource-accounting

Subsystem distribution:

- 26 transaction-processing
- 15 core-logic
- 10 access-control
- 7 consensus
- 5 cryptography
- 4 p2p-networking
- 3 rpc-client-api
- 2 storage
- 1 staking

## Finding-To-Mechanism Analysis

| Finding | Mechanism | Missing property | Prompt lesson |
|---|---|---|---|
| 2012-05-15 transaction claim | Missing authority proof for claim generator/signature material | Authorization | Hunt for transaction fields whose authority is implied by object presence rather than proved at apply time. |
| 2012-06-19 p2p proposing | Peer/validator role flags were not separated from networking participation | Authorization | Role gates must distinguish peer connectivity, proposing, and validating privileges. |
| 2012-06-25 SHAMap | Hash namespace/domain separation was too weak | Signer/hash binding | Signature/hash prompts should cover authenticated trie and map node domain prefixes, not only message signatures. |
| 2012-09-01 proposal suppression | Duplicate proposal suppression missed proposal identity | Consensus safety | Consensus prompts should bind signer, sequence, proposal hash, and prior ledger together. |
| 2013-01-18 RPC access | Administrative/API access control hardening | Authorization | API gates need source, role, method, and action-specific checks. |
| 2013-01-19 WalletAdd funding | Reserve-aware object creation was missing | Reserve enforcement | Reserve prompts must include generated account or object creation, not just explicit transfer value. |
| 2013-02-26 consensus startup | Startup could use the wrong last-closed-ledger context | Consensus safety | Consensus state-machine prompts should include cold start and ledger-context rebinding. |
| 2014-02-18 ECDSA | Signature canonicalization hardening | Signer binding | Signature prompts should check malleability and canonical form at every acceptance path. |
| 2015-07-28 ledger compatibility | Ledger compatibility was not checked strongly enough | Consensus safety | Consensus prompts should include compatibility gates before accepting ledger/proposal artifacts. |
| 2016-02-03 manifests | Validator manifests needed dual-signature/key checks | Signer binding | Trust prompts should model master key, ephemeral validation key, and revocation as separate namespaces. |
| 2016-04-21 HELLO rejection | Failed overlay handshake cleanup/resource release gap | Accounting integrity | Resource prompts should cover allocation-before-verification and rejection cleanup. |
| 2017-01-24 revocation | Validator master-key revocation handling gap | Signer binding | Revocation checks must apply to the right namespace and cache key. |
| 2017-02-23 invariants | Transaction invariant framework introduced missing global checks | Invariant validation | Prompts need a first-class ledger invariant coverage family. |
| 2017-08-07 quorum | Validator quorum and UNL-size boundary hardening | Consensus safety | Consensus prompts should test integer thresholds and small-validator-set boundaries. |
| 2017-11-17 TLS/SNI | Validator-site hostname/TLS setup hardening | Trust freshness | Trust prompts should cover remote trust-list fetch TLS/SNI binding. |
| 2018-03-02 escrow | Crypto-condition validation was incomplete | Invariant validation | Input prompts should check condition/preimage/satisfaction validation at the sink. |
| 2018-04-17 charged fee | Invariant used nominal rather than actual charged fee | Accounting integrity | Accounting prompts must distinguish estimated, nominal, charged, delivered, and persisted amounts. |
| 2018-07-27 censorship detector | Consensus observability gap | Consensus safety | Consensus prompts should include misbehavior/censorship detection as security hardening. |
| 2018-08-10 RPC signing | RPC signing access gate was incomplete | Authorization | Authorization prompts should include remote signing and administrative helper paths. |
| 2018-10-08 validator redirects | Validator-site redirect/retry hardening | Trust freshness | Trust-list fetch prompts should cover redirects, schemes, retry limits, and parser state. |
| 2018-10-23 validator scheme | Redirect scheme filtering gap | Trust freshness | Trust prompts should explicitly require scheme allowlists for fetched trust material. |
| 2018-10-31 revocation cache | Wrong revocation cache namespace | Signer binding | Prompt signer/trust systems to audit namespace-specific caches. |
| 2019-03-05 SetRegularKey | Regular-key authorization edge case | Authorization | Auth prompts should cover self-authorization, master-key state, and account recovery paths. |
| 2019-08-05 TLS client | TLS client configuration hardening | Trust freshness | Trust-list and peer prompts should cover client-side TLS verification defaults. |
| 2020-05-18 amendment rounding | Threshold rounding for amendment support | Accounting integrity | Consensus prompts should test boundary arithmetic in voting/activation thresholds. |
| 2021-02-19 Byzantine detector | Misbehavior detector coverage gap | Input validation | Consensus prompts should inspect telemetry and detector coverage for trusted and untrusted peers. |
| 2022-05-30 core input | Correctness hardening around protocol input | Input validation | Input prompts should ask for semantic object compatibility, not just syntax validity. |
| 2022-06-22 NFT amount | Negative amount accepted in NFT offer path | Numeric bounds | Numeric prompts should test protocol amount sign and representability at all constructors. |
| 2022-09-13 NFT auto trustline | Unauthorized/resource-consuming auto-created trust line | Resource accounting | Resource prompts should include auto-created ledger entries as side effects. |
| 2023-03-20 NFTokenID | Identifier collision/duplicate NFT creation | Invariant validation | Input prompts should recompute canonical IDs and lifecycle state before object creation. |
| 2023-05-17 base58 | Over-permissive account parsing | Invariant validation | Input prompts should cover strict canonical external identifier parsing. |
| 2023-08-18 consensus retention | Accepted-ledger/proposal retention state gap | Consensus safety | Consensus prompts should check retention and cleanup across catch-up or acquisition transitions. |
| 2023-09-11 peer catch-up | Peer proposal/catch-up state hardening | Consensus safety | Peer sync prompts should bind progress reports to prior ledger and consensus mode. |
| 2024-02-02 NFT reserve | Reserve enforcement for NFT path | Reserve enforcement | Accounting prompts should check every object-creation branch for owner-count and reserve. |
| 2024-03-22 consensus desync | Consensus desync hardening | Consensus safety | Consensus prompts should include wrong-ledger/switch-ledger recovery modes. |
| 2024-03-24 AMM offer | AMM offer overflow hardening | Numeric bounds | Numeric prompts should cover aggregate AMM math and overflow in offer limits. |
| 2024-04-22 AMM rounding | AMM rounding invariant gap | Accounting integrity | Accounting prompts should treat rounding direction as a security invariant. |
| 2024-11-05 reserve | Missing reserve check in new object flow | Reserve enforcement | Reserve checks must be repeated near the state write for generated objects. |
| 2025-01-23 validator threshold | Validator-list trust threshold hardening | Trust freshness | Attestation prompts should check threshold achievability and fail-closed policy. |
| 2025-01-23 trust policy | Validator-list trust policy hardening | Trust freshness | Trust prompts should map publisher trust, validator trust, and local policy separately. |
| 2025-03-11 vault auth | Vault/feature authorization hardening | Authorization | Auth prompts should include amendment-scoped transaction semantics. |
| 2025-04-07 auth recursion | Recursive authorization boundary hardening | Authorization | Auth prompts should identify recursive helper calls and stop conditions. |
| 2025-04-11 ledger integrity | Ledger-state integrity hardening | Input validation | Invariant prompts should verify affected object sets, not only the triggering object. |
| 2025-04-14 auth correctness | Authorization correctness for new protocol feature | Authorization | Auth prompts need generated side effects and feature-gated policy checks. |
| 2025-04-30 ledger invariant | Ledger-state invariant hardening | Invariant validation | Invariant detectors should latch any violation across all visited entries. |
| 2025-05-05 ledger accounting | Ledger accounting invariant hardening | Accounting integrity | Accounting prompts should compare before/after balances and obligations. |
| 2025-06-02 transaction auth | Access control in transaction processing | Authorization | Auth prompts should verify issuer/destination/asset-specific authority. |
| 2025-09-10 transaction auth | Access control for feature transaction | Authorization | Auth prompts should cover all amendment-enabled transaction types. |
| 2025-09-16 consensus ordering | Consensus ordering hardening | Consensus safety | Consensus prompts should inspect deterministic ordering salts/tie breakers. |
| 2025-09-30 signature object | Signature object confusion hardening | Signer binding | Signature prompts should bind signed object type and payload schema. |
| 2025-10-07 freeze | Missing freeze validation | Authorization | Auth prompts should include asset freeze/deep-freeze and restriction state. |
| 2025-10-09 receiver auth | Receiver authorization hardening | Authorization | Auth prompts should distinguish sender consent, receiver consent, and issuer policy. |
| 2025-10-21 reserve A | Reserve enforcement bypass | Reserve enforcement | Reserve prompts should model owner count for implicit objects. |
| 2025-10-21 reserve B | Missing reserve check | Reserve enforcement | Reserve prompts should require branch-complete reserve coverage. |
| 2025-10-31 delegate perms | Improper delegated permission enforcement | Authorization | Auth prompts should require exact transaction-shape permission matching. |
| 2025-11-04 accounting | Accounting invariant enforcement | Accounting integrity | Accounting prompts should enforce equality/two-sided relations, not one-sided checks. |
| 2025-11-07 representability | Numeric representability hardening | Numeric bounds | Numeric prompts should distinguish valid intermediate values from persistable ledger values. |
| 2025-11-14 accounting A | Resource/accounting invariant hardening | Accounting integrity | Accounting prompts should check pseudo-accounts and aggregate obligations. |
| 2025-11-14 accounting B | Resource/accounting invariant hardening | Accounting integrity | Accounting prompts should check cleanup/delete transitions for empty obligations. |
| 2025-11-16 numeric | Numeric validation hardening | Numeric bounds | Numeric prompts should cover domain-specific amount wrappers and amendment gates. |
| 2026-01-15 yield rounding | Rounding/accounting yield theft | Accounting integrity | Accounting prompts should test who benefits from rounding remainders. |
| 2026-03-09 missing validation | Missing input validation in feature path | Invariant validation | Input prompts should check field compatibility under all feature gates. |
| 2026-03-21 state overwrite | Invariant state overwrite | Invariant validation | Invariant prompts should catch overwritten detection state across visited entries. |
| 2026-04-02 accounting | Ledger accounting invariant | Accounting integrity | Accounting prompts should include loan/vault aggregate conservation. |
| 2026-04-03 accounting A | Protocol accounting invariant | Accounting integrity | Accounting prompts should test multi-entry aggregate relations. |
| 2026-04-03 accounting B | Ledger accounting invariant | Accounting integrity | Accounting prompts should test liquidation/repayment edge cases. |
| 2026-04-03 accounting C | Accounting invariant | Accounting integrity | Accounting prompts should verify invariant finalization logic. |
| 2026-04-09 staking auth cleanup | Authorization lifecycle cleanup | Authorization | Auth prompts should include permission cleanup on delete/revoke/unstake. |
| 2026-04-09 storage access | Access control for stored object path | Authorization | Auth prompts should cover object-owner and delegated storage roles. |
| 2026-04-10 asset restriction | Asset restriction enforcement | Input validation | Auth/input prompts should include issuer restrictions and transferability constraints. |
| 2026-04-20 invariant | Invariant enforcement gap | Invariant validation | Ledger-invariant prompts should cover feature-specific invariant registration. |
| 2026-04-21 structural validation | Insufficient structural validation | Invariant validation | Input prompts should require exact cardinality and type-specific field compatibility. |
| 2026-04-22 invariant overwrite | Invariant-check state overwrite | Invariant validation | Invariant prompts should catch boolean reset/last-result-wins detector bugs. |

## Family Clustering

### 1. Amendment-Scoped Authorization And Transaction-Shape Permissions

This cluster covers the RPC signing gate, SetRegularKey behavior, vault and lending authorization, MPToken restrictions, delegate permissions, receiver authorization, freeze/deep-freeze checks, storage access control, and staking lifecycle cleanup.

The recurring mechanism is that a signer, account, role, or delegate is valid in the abstract, but not for the exact operation being executed. The dangerous differences are asset class, issuer, destination, freeze state, pseudo-account, generated ledger object, amendment status, and transaction sub-shape.

Existing prompt coverage: `10_authz_and_role_gates.md` is relevant, but it is still too role-centric. It should more forcefully ask whether permission covers the concrete state transition and all generated side effects.

### 2. Ledger Accounting, Reserve, And Invariant Coverage

This is the strongest new signal in the rippled corpus. It covers reserve enforcement, owner-count changes, actual charged fees, AMM rounding and overflow, lending/vault aggregate accounting, pseudo-account obligations, numeric representability, invariant detector state overwrite, and feature-specific invariant registration.

The recurring mechanism is not simple resource exhaustion. It is conservation and ledger-accounting correctness: all persisted objects, balances, reserves, owner counts, obligations, and aggregate fields must remain mutually consistent after the transaction and after all generated side effects.

Existing prompt coverage: split across `13_input_validation_and_invariant_enforcement.md`, `14_resource_accounting_and_limits.md`, and `17_checked_arithmetic_and_parameter_bounds.md`. The coverage is useful but diffuse. This corpus justifies a new prompt family because ledger-accounting invariants recur across AMMs, lending, vaults, reserves, owner counts, and invariant checkers.

### 3. Consensus Proposal, Validation, Quorum, And Ordering Safety

This cluster covers proposal duplicate suppression, wrong-ledger startup, ledger compatibility, validator quorum boundaries, censorship detection, amendment threshold rounding, accepted-ledger/proposal retention, peer catch-up, desync handling, and deterministic ordering.

The recurring mechanism is context loss: accepting or suppressing consensus artifacts without binding prior ledger, proposal hash, signer, sequence, trusted validator state, active rules, and acquisition/catch-up mode.

Existing prompt coverage: `19_consensus_fork_and_payload_rule_validation.md` covers rule validation and fork consistency, but it should be extended for proposal/validation consensus systems that do not look like block-production pipelines.

### 4. Validator Trust, Manifest, Revocation, And Remote Trust-List Fetching

This cluster covers manifest dual signatures, master-key revocation, wrong revocation caches, validator-site redirects, TLS/SNI, validator-list threshold policy, and trust-list publisher policy.

The recurring mechanism is namespace confusion and freshness failure. The system has validator master keys, ephemeral validation keys, publisher keys, local trust thresholds, fetched trust lists, redirects, TLS names, manifests, and caches. Accepting one layer does not imply another layer is fresh, trusted, or in the same namespace.

Existing prompt coverage: `12_attestation_trust_and_freshness.md` is strong, but should explicitly mention validator-list publisher thresholds, remote trust-list fetching, redirects, TLS/SNI binding, and revocation cache namespaces. `11_signature_binding_and_signer_scope.md` should also mention master-key to ephemeral-key manifest chains.

### 5. Structural Protocol Object Validation

This cluster covers claim authority fields, escrow conditions, negative NFT amounts, duplicate NFT IDs, strict base58 account parsing, generic transaction helpers, exact field cardinality, and protocol object lifecycle identity.

The recurring mechanism is that syntactically valid fields or generic helpers can express an invalid protocol object. The missing property is semantic compatibility: exact field cardinality, type-specific field sets, canonical identity, lifecycle uniqueness, and amendment-enabled object shape.

Existing prompt coverage: `13_input_validation_and_invariant_enforcement.md` is close, but should add generic helper/cardinality/lifecycle-identity language.

### 6. Overlay Handshake, Peer Trust, And Failed-Path Cleanup

This cluster covers failed HELLO cleanup, peer role separation, TLS client configuration, Byzantine detector coverage, and catch-up progress binding.

The recurring mechanism is allocation or trust state being updated before verification, then not released or correctly accounted on failed handoff; or peer-provided state affecting consensus/catch-up logic without enough ledger-context binding.

Existing prompt coverage: `14_resource_accounting_and_limits.md` and `21_peer_sync_progress_and_response_binding.md` mostly cover this. Only minor refinements are needed.

## Prompt-Pack Comparison

The current prompt pack already reflects lessons from Reth, Bor, and Heimdall. It is mature on duplicate representations, peer synchronization, external consensus snapshots, cached context rebinding, signature domain separation, finalization error propagation, and authenticated state proofs.

The rippled corpus adds three main deltas:

1. Account-ledger accounting deserves first-class treatment. Existing prompts mention resource accounting, numeric bounds, and invariants, but the repeated bug shape is ledger conservation across generated objects, owner counts, reserves, pseudo-accounts, aggregate obligations, and invariant detectors.

2. Authorization should be framed around exact transaction shape. Existing prompts catch missing role gates, but rippled shows many cases where the signer or delegate is valid while the particular asset, generated object, feature-gated field, freeze state, domain, or receiver policy is not authorized.

3. Consensus prompts should not overfit to block payload validation. XRPL consensus is proposal/validation/transaction-set oriented. Prompt language should cover prior-ledger binding, transaction-set identity, proposal suppression, validator trust thresholds, amendment votes, and wrong-ledger/catch-up modes.

## Proposed Prompt Changes

### Add `prompts/22_ledger_accounting_and_invariant_coverage.md`

Proposed draft:

```markdown
# Ledger Accounting And Invariant Coverage

Use this prompt for account-ledger, AMM, lending, vault, staking, escrow, reserve, owner-count, fee, supply, or obligation systems where security depends on the post-transaction ledger state preserving accounting invariants.

## What To Hunt

- Transaction paths where preflight or preclaim checks reserve, fee, balance, owner count, or authorization, but `doApply` creates, deletes, mutates, or auto-creates additional ledger objects.
- Generated side effects such as trust lines, holdings, directories, tickets, delegates, receipts, pseudo-account balances, vault shares, lending obligations, or AMM positions that are not included in reserve/owner-count/accounting checks.
- Invariant detectors that visit multiple affected ledger entries but store only the last result, reset earlier detections, short-circuit incorrectly, or treat absence/empty lists as success when explicit evidence is required.
- Checks that enforce only one side of a two-sided accounting relation: lower bound without upper bound, non-negative without conservation, or asset-local balance without issuer/global aggregate consistency.
- Calculations where the estimated amount, nominal amount, charged fee, delivered amount, rounded amount, and persisted amount can differ.
- AMM, lending, vault, interest, yield, or share calculations where rounding direction determines who receives value or who is under-collateralized.
- Numeric wrapper types that distinguish syntactic validity from protocol representability; valid-but-unrepresentable values must not reach persisted ledger fields.
- Delete, cleanup, revoke, close, or liquidation paths that erase an object before proving all dependent balances, obligations, directory entries, and pseudo-account holdings are empty or transferred.
- Amendment or feature gates that change ledger object semantics; both pre-activation and post-activation branches must preserve the same global invariants or fail closed.

## Questions

1. What exact ledger entries can this transaction create, delete, or mutate directly and indirectly?
2. Which reserves, owner counts, fees, aggregate balances, obligations, or supply fields should change for each entry?
3. Is the invariant checked at the final state-transition boundary, after generated side effects and rounding?
4. Does the checker latch any violation across all visited entries, or can a later clean entry overwrite an earlier violation?
5. Are all accounting relations two-sided and exact where the protocol requires equality?
6. Are rounded or clamped values checked for representability before persistence?
7. Do cleanup paths prove that dependent objects and obligations are empty before deletion?

## High-Signal Evidence

- A transaction can create an object while bypassing the reserve or owner-count requirement for that object.
- A persisted aggregate field can diverge from the sum of child balances, shares, or obligations.
- A fee or delivered amount invariant uses an estimate instead of the actual applied amount.
- An invariant checker can observe a violation and then return success after visiting another entry.
- A valid intermediate numeric value can be serialized into an invalid or non-representable ledger amount.
- A rounding direction consistently benefits the actor invoking the transaction.

## False-Positive Filters

- Do not report mere rounding if the protocol explicitly assigns dust or remainder value and all aggregate fields remain consistent.
- Do not report missing reserve checks if a shared helper proves the exact generated object set and is called on every branch before mutation.
- Do not report invariant detector differences unless they can affect acceptance, rejection, persistence, or externally visible accounting.
```

Justification: at least 18 kept findings are directly in this family when reserve, accounting-integrity, numeric representability, and invariant detector bugs are combined. This is not merely `resource_accounting`; it is ledger conservation and invariant coverage.

### Refine `10_authz_and_role_gates.md`

Add to "look for":

```markdown
- delegated or granular permission systems where the grant is valid for one transaction shape but the executed operation can include paths, alternative assets, generated holdings, pseudo-accounts, receiver policy, freeze state, or feature-gated fields outside that shape.
- transaction preflight/preclaim checks that authorize a broad account or role but do not re-check the exact asset, issuer, destination, domain, ledger object, or generated side effect at the state-transition sink.
- authorization helpers that infer permission from share ownership, receipt ownership, account flags, vault membership, or domain metadata without loading the authoritative object that defines the policy.
- cleanup, revoke, delete, close, or unstake paths where authority to remove an object is not the same as authority to dispose of its dependent obligations or permissions.
```

Add questions:

```markdown
6. Does the permission cover this exact transaction shape, asset class, issuer, destination, receiver policy, and amendment state, or only the transaction type?
7. If the operation creates a holding, directory entry, delegate object, pseudo-account state, receipt, share, or follow-on ledger object, is that generated side effect authorized too?
8. Are sender consent, receiver consent, issuer policy, domain policy, and operator/admin authority treated as separate checks?
```

### Refine `13_input_validation_and_invariant_enforcement.md`

Add:

```markdown
- transaction type or ledger-entry helpers represented with generic arrays, enums, optional fields, or builder APIs where present, absent, empty, or multi-entry fields have different protocol meaning; require exact cardinality and type-specific field compatibility before state transition.
- protocol object IDs that can be burned, deleted, recreated, or recomputed from account, sequence, issuer, asset, or amendment-scoped fields; check uniqueness against canonical identity and lifecycle state, not just current object existence.
- invariant scanners that visit many affected ledger entries but store only the last result, reset earlier detections, or treat absence/empty lists as success when the protocol requires explicit evidence.
- feature/amendment gates where a field is syntactically valid both before and after activation but has different semantic constraints after activation.
```

### Refine `17_checked_arithmetic_and_parameter_bounds.md`

Add:

```markdown
- fixed-point, decimal, AMM, lending, vault, interest, yield, reserve, or fee calculations where rounding direction itself is a security invariant; compare the exact mathematical target, rounded ledger amount, remainder handling, and stored aggregate field.
- numeric wrapper types that distinguish validity, canonicality, and representability under the active protocol rules; valid-but-unrepresentable intermediate values must not reach persisted ledger fields.
- threshold arithmetic for validator quorums, amendment activation, voting windows, or trust-list policies; test boundary values just below and above the required fraction, especially with small signer sets.
```

### Refine `12_attestation_trust_and_freshness.md`

Add:

```markdown
- validator-list, signer-set, or trust-list systems where safety depends on publisher-list availability, threshold achievability, manifest revocation, and local cached trust state staying in the same namespace.
- remote list or manifest fetchers that follow redirects, accept TLS/SNI names, or cache revocation status; check scheme allowlists, hostname binding, retry limits, and whether publisher-key revocation is checked against the publisher namespace rather than the validator namespace.
- trust threshold policies that can become impossible, trivially satisfiable, or stale when configured publishers are unavailable, revoked, duplicated, or partially trusted.
```

### Refine `11_signature_binding_and_signer_scope.md`

Add:

```markdown
- key-rotation or manifest formats where a long-term master key authorizes an ephemeral validation/signing key; verify both signatures, revocation status, sequence/epoch, and namespace-specific cache lookups before accepting signed consensus artifacts.
- signed objects whose payload schema can be confused with a different transaction, manifest, validation, proposal, or ledger-object type; include object type and protocol domain in the signed bytes.
```

### Refine `19_consensus_fork_and_payload_rule_validation.md`

Add:

```markdown
- proposal/validation consensus systems where agreement is over transaction sets, close times, trusted validator validations, and prior-ledger identity rather than only block payloads; check that proposal duplicate suppression, transaction-set ordering, wrong-ledger mode, and switch-ledger mode bind proposal hash, prior ledger, sequence, signer, and active rules.
- amendment or feature activation votes where quorum/majority thresholds are computed by integer or rounded arithmetic; test boundary values just below and above the policy threshold and ensure small validator sets cannot produce impossible or unsafe quorum requirements.
- consensus observability or misbehavior detectors that only watch trusted participants or only the happy path; hardening should cover untrusted reports, laggards, censorship suspicion, and desync/catch-up transitions without changing consensus rules.
```

### Refine `14_resource_accounting_and_limits.md`

Add:

```markdown
- transaction types that auto-create trust lines, holdings, directories, tickets, delegate objects, shares, receipts, or other ledger entries as a side effect; check that reserve, owner-count, and spam-cost accounting is enforced before the auto-created object reaches ledger state.
- failed protocol handshakes, upgrades, or peer-session attempts where resource/session accounting is allocated before verification; rejection paths must release or charge the same resource state as successful handoff paths.
```

### Refine `02_validation_and_impact.md`

Add missing properties:

```markdown
- ledger accounting invariant coverage
- reserve and owner-count enforcement
- amendment-scoped authorization
- validator-list trust threshold achievability
- generated-side-effect authorization
```

Add validation questions:

```markdown
12. If the issue involves ledger accounting, distinguish nominal amount, charged fee, delivered amount, reserve/owner-count changes, generated objects, aggregate obligations, and invariant-detector coverage. Do not call it theft unless the state transition demonstrably lets value, debt, reserve burden, or obligations move incorrectly.
13. If the issue involves amendments or feature gates, decide whether the bug is pre-activation acceptance, post-activation missing enforcement, or cross-version compatibility hardening.
14. If the issue involves delegated permissions, identify the exact transaction sub-shape, asset, issuer, destination, receiver policy, and generated side effects covered by the grant.
```

### Refine `00_protocol_mapper.md`

Add:

```markdown
18. Map transaction application phases and invariant enforcement:
   - preflight, preclaim, signature/authorization checks, doApply, generated side effects, invariant visit/finalize hooks, and amendment gates;
   - for each transaction family, note which ledger objects can be created/deleted indirectly and where reserves, owner counts, freeze/restriction policy, and accounting aggregates are checked.

19. Map validator trust material by namespace:
   - validator master keys, ephemeral validation keys, publisher keys, manifests, revocation caches, validator lists, list publishers, quorum/threshold policy, redirect/TLS fetch policy, and overlay propagation.
```

### Refine `01_base_hunter.md`

Add hunt tasks:

```markdown
- For account-ledger systems, build a before/after accounting model for each transaction family: direct ledger entries, generated entries, reserves, owner counts, fees, supply, shares, receipts, obligations, and invariant finalizers.
- For delegated or feature-scoped authorization systems, compare the permission object to the exact executed transaction shape and every generated side effect.
- For proposal/validation consensus systems, map proposal identity, prior-ledger binding, transaction-set ordering, validator trust, quorum arithmetic, and wrong-ledger/catch-up transitions before searching for missing checks.
```

## New Family Prompt Justification

`22_ledger_accounting_and_invariant_coverage.md` is justified. The prompt pack currently has adjacent coverage but no dedicated lens for ledger conservation and invariant detector correctness. rippled repeatedly produced findings in this shape:

- reserve and owner-count bypasses
- actual charged fee versus nominal fee mismatch
- AMM/lending/vault aggregate accounting mismatch
- pseudo-account and generated-object obligations
- numeric representability before persistence
- invariant detector overwrite or incomplete coverage
- rounding-direction value movement

This family should remain portable. It applies to account-based ledgers, UTXO-like object systems, AMMs, vaults, lending, staking, token standards, escrow systems, and any DLT where transactions create indirect ledger obligations.

## Validation Notes

Anti-overfitting checks:

- The proposed new family avoids XRP-specific nouns in its core objective. It names generic accounting concepts first and uses examples only to clarify the surface.
- The refinements do not instruct the model to search for specific commits, file names, or historical bugs.
- Low-confidence TLS/client-configuration findings are not over-weighted; they are represented as small trust-fetching refinements, not a new family.
- The consensus refinement is framed around proposal/validation systems generally, so it also applies to Tendermint-like, Snowball-like, HotStuff-like, and custom BFT systems that do not expose a simple block production pipeline.

Suggested holdout validation:

- Hold out the April 2026 invariant findings (`2026-04-20`, `2026-04-21`, `2026-04-22`). The new ledger-accounting/invariant prompt should still lead a hunter toward feature-specific invariant registration, exact cardinality, and detector state overwrite.
- Hold out `2025-10-31` delegate permissions. The refined authorization prompt should still lead a hunter to compare the permission grant against the exact transaction shape and generated side effects.
- Hold out `2025-01-23` validator-list trust threshold findings. The refined attestation prompt should still lead a hunter to threshold achievability and publisher trust policy without naming XRPL validator lists.

Residual risk:

- Some early findings are broad hardening commits with limited exploit detail. They should inform language only when the same mechanism appears in later, clearer findings.
- The corpus is heavily transaction-processing biased. Future refinement should re-check whether peer sync, storage persistence, and RPC prompts need more change after those subsystems receive a larger confirmed finding set.
