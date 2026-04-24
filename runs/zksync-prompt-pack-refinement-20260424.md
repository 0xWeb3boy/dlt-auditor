# zksync Prompt-Pack Refinement Proposal

Target repo: `/testing/zksync`
Evidence folder: `/testing/zksync/validated-findings/kept`
Findings analyzed: 11
Findings skipped: none

## Repo Context Summary

zksync is a ZK-rollup system with funds held on Ethereum L1 and off-chain state transitions proven by SNARKs. The codebase splits into smart contracts, server/core services, API service, Ethereum sender, witness generator/prover server, prover workers, storage, circuits, transaction types, and SDKs.

Important trust boundaries:

- User/API boundary: REST/JSON-RPC requests and transaction submissions enter API and tx sender paths.
- Wallet signature boundary: user wallet signatures authorize ChangePubKey and other account-control operations.
- Prover boundary: prover workers interact with witness generator/prover server endpoints to fetch jobs and publish proof status/results.
- Circuit witness boundary: untrusted or constructed witness data enters circuit constraints that define valid rollup state transitions.
- L1 event boundary: Ethereum logs for deposits/withdrawals/finalization are parsed and turned into L2 storage/accounting state.
- Configuration/deployment boundary: environment secrets configure admin and prover authentication.

High-risk entrypoint categories:

- Transaction admission and batch signature checks.
- ChangePubKey signing/verification in core types and SDKs.
- Circuit synthesis paths for transfer, transfer-to-new, and ChangePubKey operations.
- Public API handlers that use request-selected block/storage identifiers.
- Prover/witness generator HTTP endpoints.
- L1 event parsers and finalization storage writers.
- Startup configuration loading for privileged service secrets.

Lifecycle/state-machine patterns that matter:

- Operation data is represented across transaction structs, signed bytes, circuit witnesses, pubdata, storage, and L1 calldata.
- Prover jobs move through fetch, working_on, publish, stopped/status endpoints.
- Withdrawal events are ordered by L1 block and log index, not by block alone.
- Account-control auth varies across ECDSA, CREATE2, EIP712, onchain, legacy, and SDK compatibility paths.

## Finding Inventory

- `2019-05-12-zksync-storage-046a706f0.md`
- `2019-07-09-zksync-cryptography-3833fee9c.md`
- `2019-09-03-zksync-cryptography-136c8d4e5.md`
- `2020-02-11-zksync-cryptography-23bdca5c9.md`
- `2020-02-27-zksync-transaction-processing-0ad13b212.md`
- `2020-12-04-zksync-storage-e3a41dec7.md`
- `2020-12-10-zksync-transaction-processing-e81d133a7.md`
- `2020-12-24-zksync-transaction-processing-ba3bb4b61.md`
- `2021-01-20-zksync-cryptography-ab8697742.md`
- `2022-09-13-zksync-transaction-processing-0bf5cd634.md`
- `2022-09-14-zksync-transaction-processing-8efea04e6.md`

## Finding-To-Mechanism Analysis

### 2019-05-12 panic-on-missing-storage-record

- Repo-specific mechanism: `handle_get_block_by_id` used a request path block id to load a COMMIT operation and called `expect` on a missing row. Patch returned JSON `not found`.
- Generic invariant: request-selected storage records must be optional at API boundaries.
- Missing property: absent-state handling.
- Code shape: route parameter -> DB lookup -> unwrap/expect -> API panic.
- Hunt recipe: inspect public read APIs that fetch canonical state by caller-supplied id and look for unwrap/expect/panic after database lookups.
- False-positive killers: unreachable endpoint, prior proof that record always exists, panic fully contained without user-visible availability effect.

### 2019-07-09 missing-circuit-constraint

- Repo-specific mechanism: transfer circuit added equality between operation signer pubkey and source account pubkey, then pushed it into validity flags.
- Generic invariant: witness-provided signer identity must be constrained to committed account state.
- Missing property: witness/account key binding.
- Code shape: witness field used in operation validation without equality constraint against state leaf/account object.
- Hunt recipe: map every witness field used to authorize a state transition, then confirm it is constrained to committed state before validity flags are aggregated.
- False-positive killers: equivalent constraint already exists in a mandatory helper; changed code is test-only or unreachable.

### 2019-09-03 missing-signature-message-binding

- Repo-specific mechanism: transfer-to-new circuit began reconstructing serialized transaction bits and verifying they match allocated signature-message data.
- Generic invariant: signature-verified bytes must equal the transaction fields executed by the circuit.
- Missing property: signed-message field binding.
- Code shape: signature verification over allocated/witness bytes while execution consumes side fields.
- Hunt recipe: in circuit signature paths, reconstruct canonical signed payload from constrained fields and compare it to the bytes used by the verifier.
- False-positive killers: shared helper already binds all fields; storage/formatting hunks are unrelated.

### 2020-02-11 nonce-binding-in-circuit

- Repo-specific mechanism: ChangePubKey offchain circuit/witness flow began carrying nonce into witness data, pubdata, operation arguments, and constraining it to current account nonce.
- Generic invariant: transaction nonce in witness/public data must match the account nonce consumed by the state transition.
- Missing property: nonce-state binding.
- Code shape: replay/order field appears in tx semantics but not in proof/public-data constraints.
- Hunt recipe: compare nonce fields across transaction struct, witness struct, pubdata encoder, and circuit constraints for every auth-sensitive op.
- False-positive killers: nonce already checked by mandatory parent circuit or admission gate; added field is only display/logging.

### 2020-02-27 authorization-message-domain-separation-hardening

- Repo-specific mechanism: ChangePubKey Ethereum auth moved from opaque bytes to a readable zkSync registration message containing action-specific context.
- Generic invariant: account-control signatures should bind protocol/action/account/key in an unambiguous user-visible domain.
- Missing property: human-readable authorization domain.
- Code shape: wallet signs opaque bytes for a privileged state change.
- Hunt recipe: inspect wallet/SDK signing APIs for opaque byte signatures that authorize account-control changes; ask what the user and verifier know the signature means.
- False-positive killers: typed-data or verifier-side domain binding already exists; text change is only UI and not the verified payload.

### 2020-12-04 missing-prover-api-authentication

- Repo-specific mechanism: prover server/client coordination added JWT/bearer-token validation and client bearer auth.
- Generic invariant: privileged worker coordination APIs must authenticate service clients.
- Missing property: service-to-service authentication.
- Code shape: internal HTTP server exposes job/status/publish endpoints before request auth is enforced.
- Hunt recipe: enumerate internal operator/prover/worker APIs, then verify both client credentials and server-side validation are active at route handling.
- False-positive killers: mandatory mTLS/reverse-proxy auth already protects every request; client token generation has no server check.

### 2020-12-10 insecure-default-secret-detection

- Repo-specific mechanism: config loading logs an error if admin/prover auth secrets are `sample` outside localhost.
- Generic invariant: non-local deployments must not silently run privileged auth with known sample secrets.
- Missing property: production-secret safety check.
- Code shape: documented test secret reaches privileged auth config in production-like mode.
- Hunt recipe: search startup config for sample/default secrets used by admin, prover, sequencer, validator, or bridge services; check whether production modes fail closed or only warn.
- False-positive killers: localhost/test-only config; secret replaced before use; warning unreachable or invisible.

### 2020-12-24 missing-authentication

- Repo-specific mechanism: witness generator/prover server had `HttpAuthentication::bearer` constructed, but `.wrap(auth)` was commented out. Patch restored the middleware.
- Generic invariant: constructing auth middleware is not enough; it must wrap the actual route tree.
- Missing property: authentication middleware enforcement.
- Code shape: validator object exists beside route builder but is not attached to the served app.
- Hunt recipe: grep for auth middleware construction and independently verify every sensitive route is under the middleware in the actual server builder.
- False-positive killers: equivalent auth at reverse proxy/service mesh; service strictly not network-reachable; routes are read-only.

### 2021-01-20 transaction-authentication-hardening

- Repo-specific mechanism: CREATE2 accounts reject supplied Ethereum signature data in single and batch verification; disabled Close transaction account_id path returns an error rather than panicking.
- Generic invariant: transaction auth mode must match account-control mode; extra auth material must not become alternate authority.
- Missing property: account-auth-mode consistency.
- Code shape: account type/creation mode and signature variant are validated separately or asymmetrically.
- Hunt recipe: compare all account-type branches across single and batch transaction verification; reject auth variants forbidden for that account type.
- False-positive killers: extra signature was ignored before every security decision; modified path unreachable from submitted transactions.

### 2022-09-13 cross-domain-signature-replay

- Repo-specific mechanism: ChangePubKey auth moved to EIP-712 typed data with explicit `chain_id`; legacy ECDSA SDK method was deprecated/hidden.
- Generic invariant: account-control signatures must bind chain/domain and typed action.
- Missing property: chain-domain signature binding.
- Code shape: raw-message signature authorizes account key changes without chain/domain in signed data.
- Hunt recipe: compare legacy and typed signing branches for account-control operations; verify chain id/domain/action/nonce are in the verified payload, not side metadata.
- False-positive killers: legacy signature already includes equivalent domain; compatibility path cannot reach production acceptance.

### 2022-09-14 withdrawal-finalization-ordering

- Repo-specific mechanism: withdrawal finalization deduped by max processed block, then changed to max log index scoped by block and carried `log_index` in `WithdrawalEvent`.
- Generic invariant: event idempotency must use full event identity, not a coarse block/batch coordinate.
- Missing property: event-identity idempotency.
- Code shape: event stream with multiple events per block keyed only by block number.
- Hunt recipe: inspect L1/L2 event finalizers and bridge watchers for watermarks keyed by block/height only; verify event index/log index/tx index is part of identity where needed.
- False-positive killers: protocol guarantees one relevant event per block; later reconciliation reprocesses skipped events before user impact.

## Family Clustering

### Cluster A: ZK witness, signature-message, and pubdata binding

Findings: `3833fee9c`, `136c8d4e5`, `23bdca5c9`.

These all involve circuit or proof-adjacent fields that must be constrained to account state, signed message bytes, nonce, or pubdata. The lesson is portable to ZK rollups and proof-based DLT systems. Existing prompts mention proof binding generally, but not the circuit-specific audit move: build a field matrix from tx struct -> witness -> pubdata -> constraint -> verifier.

Recommendation: add a new ZK-specific prompt family and cross-reference it from mapper/base hunter.

### Cluster B: Account-control signature domain and auth-mode binding

Findings: `0ad13b212`, `0bf5cd634`, `ab8697742`.

These involve wallet signatures, ChangePubKey, EIP-712, chain id, account auth modes, and legacy branches. The lesson is portable and already partly covered by `11_signature_binding_and_signer_scope.md`; it needs sharper wallet/account-control and legacy-branch wording rather than a new family.

Recommendation: refine prompt 11.

### Cluster C: Operator/prover service authentication and production secret safety

Findings: `e3a41dec7`, `e81d133a7`, `ba3bb4b61`.

These involve internal service APIs, bearer auth, auth middleware attachment, and sample shared secrets. The lesson is portable to prover, sequencer, relayer, validator, bridge, oracle, and admin services. Existing `10_authz_and_role_gates.md` discusses roles broadly, but not "middleware constructed but not installed" or "sample secrets in non-local deployment."

Recommendation: refine prompt 10 and add a startup/config safety bullet to prompt 13.

### Cluster D: Boundary input and event identity

Findings: `046a706f0`, `8efea04e6`.

These share "wrong coordinate at boundary" mechanics: missing state keyed by request id, and event finalization keyed by block rather than block+log. Existing `13_input_validation_and_invariant_enforcement.md` and `15_state_machine_and_lifecycle_consistency.md` cover this generally, but event identity/watermark wording should be sharper.

Recommendation: refine prompts 13 and 15.

## Prompt-Pack Comparison

### `00_protocol_mapper.md`

Already maps signed/proof artifacts and duplicated protocol facts. Weakness: it does not explicitly ask a ZK-rollup auditor to map transaction fields across SDK, tx type, witness, pubdata, circuit constraint, storage, and L1 calldata. It also maps extraction pipelines, but does not explicitly ask for L1 log identity coordinates such as tx hash/log index.

Decision: refine.

### `01_base_hunter.md`

Already asks for asymmetric checks and duplicated representations. Weakness: it does not explicitly say to build a field-by-field matrix for proof/circuit operations, nor to compare constructed middleware/config against actual route attachment.

Decision: refine.

### `10_authz_and_role_gates.md`

Already covers authorization and role gates. Weakness: service-to-service auth can be missed when the validator exists but is not mounted; default secrets are config safety rather than a normal role check.

Decision: refine.

### `11_signature_binding_and_signer_scope.md`

Good coverage for domain separation and legacy typed transaction formats. Weakness: account-control/wallet signatures need an instruction to compare SDK signer, node verifier, and compatibility branches, and to ensure user-visible signed content matches verifier semantics.

Decision: refine.

### `13_input_validation_and_invariant_enforcement.md`

Already includes malformed-input panics, nil/partial outputs, defaults, and secrets. Weakness: public read APIs with absent canonical storage should be handled as ordinary missing state, and production sample secrets should be treated as fail-closed or at least high-signal hardening.

Decision: refine.

### `15_state_machine_and_lifecycle_consistency.md`

Already has lifecycle and range continuity language. Weakness: event stream idempotency keyed by block/height only should be called out explicitly.

Decision: refine.

### `20_authenticated_state_proof_and_persistence_integrity.md`

Good for proof material and authenticated persistence. Weakness: too broad for ZK circuit witness/public-data constraint coverage; adding all ZK-specific guidance here would muddy it.

Decision: add a new ZK circuit family and optionally cross-reference it from prompt 20.

## Proposed Prompt Changes

### Change 1: strengthen `00_protocol_mapper.md`

Target: `/testing/dlt-ai-audit-system/00_protocol_mapper.md`

Draft text to add after the signed/authenticated/proof artifact mapping section:

```text
For ZK rollups or proof-based execution systems, build a field-binding matrix for each operation family:
- user/API transaction fields,
- SDK or wallet signed payload,
- typed-data or raw-message domain fields,
- witness struct fields,
- pubdata or calldata fields,
- circuit constraints and validity flags,
- storage/account state consumed by execution,
- verifier or contract inputs.
For each field, mark which representation is authoritative and where equality, range, nonce, signer, and domain binding is enforced before proof acceptance or state commitment.
```

Draft text to add to L1/cross-chain pipeline mapping:

```text
For event-ingestion pipelines, map the full source event identity: source chain, contract, block hash/number, transaction hash/index, log index/event index, event type, and payload. Note any progress watermark or duplicate guard and whether it is keyed by the full identity or by a coarser block, batch, height, or timestamp proxy.
```

Rationale: zksync's circuit findings would be easier to hunt if the mapper forced a field matrix; withdrawal finalization would be easier if event identity coordinates were mapped up front.

Repo-specific details excluded: ChangePubKey, COMMIT, WithdrawalEvent, and zksync path names.

Overfitting risk: low; applies to many ZK rollups, bridges, indexers, and event-driven protocols.

### Change 2: strengthen `01_base_hunter.md`

Target: `/testing/dlt-ai-audit-system/01_base_hunter.md`

Draft text to add as new search tasks:

```text
For proof or circuit-backed transaction families, build a per-field comparison across transaction object, signed message, witness, public data, circuit constraints, and persisted state. Search for fields that are present in execution or public data but not constrained equal to the signed or committed representation.
```

```text
For internal service APIs, compare security objects that are constructed with the route tree or server builder that actually handles requests. Treat "validator exists nearby" as insufficient unless middleware, interceptors, or handlers are mounted on every sensitive route.
```

Rationale: catches the three circuit-binding cases and the commented-out auth middleware case without naming either.

Repo-specific details excluded: prover server route names and circuit function names.

Overfitting risk: low; these are structural audit moves.

### Change 3: strengthen `10_authz_and_role_gates.md`

Target: `/testing/dlt-ai-audit-system/prompts/10_authz_and_role_gates.md`

Draft text to add under search patterns:

```text
- internal prover, sequencer, relayer, validator, oracle, admin, or worker APIs where authentication helpers, token validators, or middleware are constructed but not attached to the actual route tree, interceptor chain, RPC method, or message handler that reaches the privileged sink
- service-to-service clients that begin sending bearer tokens, JWTs, mTLS identities, or shared-secret headers without a corresponding fail-closed server-side validation path on every sensitive endpoint
- startup or config paths where production, public, or non-local deployments can use documented sample secrets, placeholder tokens, empty passwords, default keys, or fixture credentials for privileged service authentication
```

Rationale: directly improves coverage for missing prover API auth, missing middleware attachment, and sample-secret hardening.

Repo-specific details excluded: zksync prover names, endpoint names, and `sample` constant.

Overfitting risk: low; common across operator services.

### Change 4: strengthen `11_signature_binding_and_signer_scope.md`

Target: `/testing/dlt-ai-audit-system/prompts/11_signature_binding_and_signer_scope.md`

Draft text to add under search patterns:

```text
- account-control, key-rotation, withdrawal-address, validator-key, or permission-change signatures where SDK signing, node verification, contract verification, and legacy compatibility branches do not bind the same chain/domain, action type, account, nonce, new key or permission, fee/batch context, and time range
- wallet signing APIs that sign opaque bytes for privileged actions while verification later interprets those bytes as a protocol-specific authorization; prefer typed or canonical messages that make the action and domain explicit
- account-type or auth-mode branches, such as deterministic accounts, contract accounts, create2-like accounts, multisig accounts, or legacy accounts, where one branch accepts signature material that should be forbidden for that authority model
```

Rationale: sharpens current domain-separation coverage for wallet/account-control operations and compatibility branches.

Repo-specific details excluded: ChangePubKey and EIP-712 implementation names can appear as examples elsewhere, but the runtime prompt should use generic account-control wording.

Overfitting risk: medium-low; account-control signatures are a recurring DLT pattern.

### Change 5: strengthen `13_input_validation_and_invariant_enforcement.md`

Target: `/testing/dlt-ai-audit-system/prompts/13_input_validation_and_invariant_enforcement.md`

Draft text to add under search patterns:

```text
- public RPC or REST read handlers that use caller-selected ids, heights, hashes, block numbers, account ids, or operation ids to load canonical state and then unwrap, expect, assert, or panic when the object is absent. Missing canonical state should become a structured not-found or validation error unless the protocol proves it cannot be missing.
- production-mode configuration that accepts sample secrets, placeholder keys, fixture tokens, localhost credentials, or default passwords for privileged admin, prover, relayer, sequencer, validator, or bridge endpoints. Prefer fail-closed startup; warnings alone are hardening, not full mitigation.
```

Rationale: improves hunt guidance for the API panic and sample-secret cases.

Repo-specific details excluded: COMMIT operation and concrete env var names.

Overfitting risk: low.

### Change 6: strengthen `15_state_machine_and_lifecycle_consistency.md`

Target: `/testing/dlt-ai-audit-system/prompts/15_state_machine_and_lifecycle_consistency.md`

Draft text to add under search patterns:

```text
- event ingestion, bridge watcher, withdrawal finalizer, inbox, outbox, receipt, or log-processing watermarks keyed by only block, height, batch, timestamp, or max-seen aggregate when the source can contain multiple distinct relevant events at that coordinate. Duplicate guards should use the full event identity and ordering key required by the source chain.
```

Draft question to add:

```text
10. Does every "already processed" or progress watermark use the same identity granularity as the source event stream: block plus transaction/log/event index where multiple events can share a block?
```

Rationale: catches same-block event skip patterns without naming withdrawals.

Repo-specific details excluded: withdrawal table names and exact SQL.

Overfitting risk: low; applies to many bridge/indexer/event-finalization systems.

### Change 7: optional cross-reference in `20_authenticated_state_proof_and_persistence_integrity.md`

Target: `/testing/dlt-ai-audit-system/prompts/20_authenticated_state_proof_and_persistence_integrity.md`

Draft text to add near proof-support pipelines:

```text
- In ZK or validity-proof systems, do not treat witness generation as separate from authenticated-state integrity. Check whether witness fields, public inputs, pubdata, and persisted state are mutually constrained before the proof or state root is accepted. Use the dedicated ZK circuit witness-binding family for deeper circuit review.
```

Rationale: routes auditors from generic proof/persistence integrity into the more precise new family below.

Overfitting risk: low if kept as a pointer rather than full ZK guidance.

## New Family Prompt Proposal

Draft file: `/testing/dlt-ai-audit-system/prompts/23_zk_circuit_witness_and_public_data_binding.md`

Objective: Hunt for bugs where ZK circuit witnesses, signed messages, public data, and committed account state are not bound to the same operation semantics.

Full prompt text:

```text
# Prompt Family: ZK Circuit Witness And Public Data Binding

## Use This For

- ZK rollup circuits and proof-generation code.
- Witness builders, public input builders, pubdata or calldata encoders, and verifier input construction.
- Transaction families where signatures, nonces, account keys, amounts, fees, roots, or operation arguments appear in more than one representation.

## Prompt

Hunt for bugs where a proof can be generated or accepted over witness data that is not constrained to the transaction, signature, public data, or committed state that the protocol intends.

Build a field matrix for each operation family:
- external transaction object,
- SDK or wallet signed payload,
- account or storage state consumed by execution,
- witness struct fields,
- public inputs, pubdata, calldata, or event data,
- circuit allocated variables,
- validity flags and final boolean constraints,
- verifier or contract inputs.

Search patterns:
- signer, account id, public key, address, token, amount, fee, nonce, recipient, or operation type appears in witness data but is not constrained equal to the committed account state or canonical transaction field.
- signature verification uses allocated or witness-provided message bytes, but the circuit does not reconstruct the canonical message from constrained transaction fields and compare them.
- nonce, chain/domain, batch hash, fee, time range, or operation type is present in SDK or transaction code but missing from witness, pubdata, or constraints.
- public data or calldata is emitted from helper fields that are not constrained to the same values used for state transition.
- validity flags are computed but not included in the final enforced boolean, or are enforced only for one chunk/branch of a multi-chunk operation.
- one operation variant, legacy path, offchain path, create-account path, or batch path has weaker constraints than the normal path.
- witness builders silently fill defaults, zeroes, or derived values when required protocol fields are absent.
- circuit tests check successful proof generation but not negative cases with mismatched witness fields.

Questions to answer:
1. What exact fields authorize the operation?
2. Which fields are signed by the user or account key?
3. Which fields are read from committed state?
4. Which fields are exposed as public inputs or pubdata?
5. Where does the circuit constrain equality between all representations?
6. Are nonce, signer, account id, token, amount, fee, recipient, operation type, and domain bound on every variant?
7. Does every computed validity flag feed into the final constraint?
8. Could a prover choose one value for the signature message and another value for the state transition?
9. Could public data describe a different operation than the constrained private witness?
10. Are negative tests present for mismatched signer, nonce, pubdata, and operation arguments?

False-positive filters:
- Do not report a missing local equality if a shared mandatory helper enforces the same binding on all paths before final validity.
- Do not treat witness-generation refactors as security issues unless the changed field affects proof acceptance, public data, or state transition.
- Do not infer theft or forged state unless verifier acceptance and attacker-controlled witness construction are demonstrated.
- Keep likely hardening when the patch tightens circuit constraints but exploitability is not shown.

Severity guidance:
- High if unconstrained witness/signature/public-data mismatch can authorize an invalid state transition or accepted proof.
- Medium for likely hardening where a sensitive constraint is added but redundant checks or exploitability remain unclear.
- Low for tooling-only witness generation changes that cannot affect accepted proofs or public data.
```

Why existing families are insufficient:

- `11_signature_binding_and_signer_scope.md` is good for signed artifacts, but it does not force a circuit witness/pubdata/state matrix.
- `13_input_validation_and_invariant_enforcement.md` is broad; adding circuit-specific details there would make it noisier.
- `20_authenticated_state_proof_and_persistence_integrity.md` focuses on proof material and persistence, not in-circuit operation semantics.

## Validation Notes

Held-out check: I drafted the ZK family primarily from the 2019 signer-key and signature-message cases, then checked it against the 2020 nonce-binding case. The proposed field-matrix wording would still lead an auditor to compare transaction nonce across witness, pubdata, operation arguments, and account-state constraints, so it passes the holdout check.

Remaining doubts:

- `2021-01-20` is weaker than the other kept findings; it should refine prompt wording only as auth-mode hardening, not as a confirmed exploit exemplar.
- `2020-12-10` logs an error instead of failing closed. Runtime prompts should say warnings are hardening, not full mitigation.
- Several findings are "likely/security-hardening"; prompt pack examples must avoid claiming theft, forged proofs, or consensus failure without code-path proof.

Prompts that should stay unchanged:

- `14_resource_accounting_and_limits.md`: none of the kept zksync cases materially teach resource metering.
- `16_staking_registry_and_accountability.md`: no staking/validator registry issue in kept set.
- `17_checked_arithmetic_and_parameter_bounds.md`: parser length checks appear only as supporting robustness, not a core arithmetic/bounds lesson.
- `19_consensus_fork_and_payload_rule_validation.md`: no direct consensus fork/payload validation lesson.
- `21_peer_sync_progress_and_response_binding.md`: no peer-sync mechanism in kept set.
- `22_ledger_accounting_and_invariant_coverage.md`: withdrawal finalization has fund-availability relevance, but the reusable mechanism is event identity/idempotency, better handled in prompt 15.
