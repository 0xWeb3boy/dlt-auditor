# Prompt Family: Union Best Hit Preservation

## Use This For

- Ensuring the audit preserves distinct, already-identified high-value motif classes instead of rediscovering some and dropping others during canonicalization.
- This is not an answer key. Treat each item as a hypothesis class that still requires target-code evidence, reachability, compensating-control checks, and proportional severity.

## Prompt

```text
Run a preservation pass over the target codebase for the following motif classes. Produce concrete candidates only when target-code evidence supports the mechanism. Do not merge distinct charging predicates, value recipients, or state-coordinate bugs.

Native precompile and native-yield state:
- Blast native precompile valid selectors have a selector-specific RequiredGas table. Verify whether valid selectors actually reach those costs.
- Invalid or unknown native-precompile selectors can have different remaining-gas/revert semantics than valid selectors. Analyze `ErrExecutionReverted` and whether gas is consumed or returned.
- Native yield or balance journaling must restore all account fields on rollback, including flags/mode fields, not only numeric balance fields.

Bridge and messenger value/gas:
- Direct ETH-yield-token deposits that bypass the messenger must budget true finalizer/recipient gas, including base overhead, EIP-150 withholding, events, checks, and post-call writes.
- Direct bridge paths must compare raw token units, converted 18-decimal units, portal mint/value, provider principal, finalizer calldata amount, and event amounts.
- Discounted or rounded withdrawals must preserve replay state when real delivered value is zero or when failure bookkeeping requires extra storage writes.
- Messenger reserve-gas constants must be revalidated after adding discounted-value or failure bookkeeping storage writes.

Gas attribution and custom surcharge:
- Global transaction refunds must be compared to per-contract gas allocations. Model an attacker-controlled refunding contract in the same victim-paid transaction as a victim claimable contract.
- Reverted child calls and failed top-level transactions must be checked against transaction-wide gas tracker finalization. Model victim-paid routers, callbacks, signature checks, relayers, and paymasters.
- Custom high-frame gas penalties must be checked separately for normal CALL, STATICCALL, DELEGATECALL, CALLCODE, precompile targets, no-code/EOA targets, first-use, repeated-use, and access-list-warmed cases.
- Access-list intrinsic gas and custom warmth must be separated: intrinsic gas attribution can be wrong even if custom warmth is handled, and custom warmth can be wrong even if intrinsic attribution is intentional.

Gas maturity and helper behavior:
- Saved gas seconds or maturity counters must be checked for over-ceiling accrual, full-balance withdrawal, zero-balance carry-forward, redeposit/reaccrual, and future immediate claims.
- For saved seconds, include a resource-exhaustion/capital-at-risk analysis: can an attacker make future gas immediately refundable and keep only a small balance clawbackable while filling blocks?
- Claim helper behavior must compare claim-all, claim-max, explicit claim, and min-rate claim. Check split claims and endpoint/interior optima separately from saved-seconds carry-forward.

Deployment, code identity, and provider economics:
- Direct-genesis predeploy state must match initializer/constructor postconditions field-for-field, including initialized flags, share price, total shares, metadata, owner/governor, version, and bootstrap balances.
- Address-keyed governor, gas, yield, or config state must be checked across selfdestruct, CREATE2 redeploy, same-address code identity changes, and proxy upgrades.
- Constructor-only or non-upgradeable system contracts behind proxies need an initializer-safety check.
- Lido/provider pending or claimable exits must not remain valued at par after losses are externally knowable; claim-batch limits and oracle caps are separate motifs.
- Protocol-owned fee vaults and user balances must both be checked through negative-yield discounts, rounded claims, and L1 data-fee recovery.
- Insurance and provider-loss timing must distinguish pre-loss front-running, loss-time snapshots, post-loss deposits, and recovery distributions.
- External provider emergency modes, including Maker shutdown, must be checked against ownership of the underlying assets and available recovery calls.
- Upgrade/reinitializer flows must preserve pending withdrawals, finalized flags, successful/failed message maps, versioned hashes, output-root bindings, and replay domains.

Round-seven narrow passes:
- Build a proxied-predeploy matrix for Blast/Gas/native predeploys: proxy address, implementation address, constructor state, initializer state, proxy storage, direct-genesis storage, and future upgrade/reinitializer safety.
- Build a Lido oracle-cap table for large slashings: externally knowable loss, oracle cap or bunker delay, local share-price discount, pending/claimable exits, and early withdrawal price.
- Build a Maker shutdown table: DAI ownership in `DsrManager`/provider adapters before and after emergency shutdown, normal exit availability, and recovery authority.
- Build L1 DA fee equations for discounted withdrawals and fee-vault withdrawals: charged L2 data fee, real delivered/recovered value, owner of the fee bucket, and whether untrusted users can force timing.
- Build a custom-bookkeeping metering table: native yield, gas refund, predeploy updates, journals, post-transaction loops, and whether attacker-controlled dimensions are charged proportional gas.
- Build an upgrade storage-migration table: old/new keys for successful messages, failed messages, finalized withdrawals, request ids, output roots, nonces, and versioned hashes.
- Split high-frame precompile custom surcharge from both native-precompile `RequiredGas` and precompile wrong-recipient attribution. The exact question is whether repeated precompile calls keep target allocation zero and repeatedly pay `BlastGasParamStorageGas`.
- Split predictable-slashing insurance front-running from generic insurance residual distribution. The exact question is whether fresh deposits after a public loss but before local report/insurance accounting join the covered share set.

Round-eight miss conversion:
- For implementation takeover, do not stop at provider mutability. Directly initialize each implementation address, then enumerate implementation-local owner/admin calls and delegatecall/plugin/provider hooks reachable after that initialization.
- For constructor-only proxies, distinguish "current genesis storage is sufficient" from "future proxy upgrades can preserve constructor-only/non-upgradeable invariants." Preserve the proxy-intent mismatch even if normal genesis works today.
- For native bookkeeping overhead, promote one broad overhead candidate when attacker-controlled native work is only partially metered. It can be conditional or hardening-only, but it must not vanish behind exact precompile/surcharge candidates.
- For invalid precompile selectors, write a separate selector/revert-gas table. Valid-selector zero gas does not cover invalid-selector revert semantics.
- For Lido oracle caps, build the withdrawal-finalization discount timeline separately from deposit admission and pending-exit claim batching.
- For insurance front-running, compute old-holder and fresh-holder payoffs under exact cover, no cover, partial cover, buffer residual, and over-recovery.
- For upgrade double withdrawal, require duplicate successful value delivery across old/new replay or finalization keys. If only zero-value underdelivery is found, preserve it as adjacent but keep searching for double delivery.

Round-nine partial conversion:
- For saved gas seconds, do not let "intentional claim-rate behavior" end the review. Build a numeric capital/resource loop that tests whether old seconds make later gas immediately claimable with lower capital at risk or victim-paid resource pressure.
- For implementation bricking, preserve implementation-local takeover separately from proxy takeover. Reproduce or kill the malicious provider delegatecall and destructive/bricking effect under the active fork semantics.
- For cross-domain double withdrawal, force the nested reinitializer trace: failed value-bearing replay, target-controlled upgrade execution, `xDomainMsgSender` or equivalent guard reset, inner replay, and two successful value deliveries.
- Before final reporting, filter generic RPC, p2p, faucet, and operator findings unless they cross a Blast bridge/yield/gas/predeploy/provider settlement boundary.

Round-ten final breadth pass:
- For native bookkeeping overhead, preserve two sibling candidates: gas-refund/claimable-gas finalizer overhead and native-yield balance/share-count overhead. A candidate for only `AllocateDevGas` is not enough to cover the broad native-yield/gas-refund class.
- Build a native-yield share-count budget table covering `Balance`, `SetBalance`, `SetFlags`, `GetClaimableAmount`, `SubClaimableAmount`, `adjustShareCount`, StateDB journals, predeploy storage, automatic-account value transfers, gas buy/refund balance changes, and selfdestruct beneficiaries.
- Do not collapse native-yield balance/share-count overhead into valid-selector precompile undercharge, invalid-selector revert gas, high-frame surcharge, or gas-refund finalizer loops.

Candidate selection discipline:
- If a motif is supported but conditional, hardening-only, or below Medium, still keep it in `candidate-index.md` and `rejected-candidates.md` with its exact status. Do not erase the mechanism.
- If two motifs share a file but have different missing properties or different value recipients, keep separate candidate dossiers.
- For every preserved motif, write the reason it survives or the exact killer evidence that rules it out.

Severity guidance:
- Use the normal validation prompt for severity.
- Conditional, hardening-only, or low-severity mechanisms can be excluded from `FINAL_AUDIT_REPORT.md`, but they should remain visible in the candidate index so future refinement does not rediscover and drop them.
```
