---
case_id: case_20170424_00515f37c
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
impact_type:
  - state-accounting
  - economic-distortion
confidence: medium
source_quality: high
date: 2017-04-24
source_refs:
  - git:00515f37ca65bf48064de2b1d250111846854050
  - "src/transactions/InflationOpFrame.cpp:105"
  - "src/transactions/InflationOpFrame.cpp:117"
  - "src/transactions/InflationTests.cpp:328"
  - "src/transactions/InflationOpFrame.cpp:76"
bug_class: protocol-accounting-invariant
tags:
  - blockchain-core
  - transaction-processing
  - inflation
  - state-accounting
  - consensus-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Stellar Core inflation accounting so ledger versions greater than 7 increase `totalCoins` once by the separately computed `inflationAmount`, while preserving the older per-winner accounting for ledger versions <= 7. The evidence supports a protocol accounting fix in a consensus-relevant inflation path, but does not establish direct theft, attacker control, or live exploitability.

## Observed Patch Facts

1. In `src/transactions/InflationOpFrame.cpp`, the patch adds `if (ledgerManager.getCurrentLedgerVersion() <= 7)`.

2. In `src/transactions/InflationOpFrame.cpp`, the patch adds `if (ledgerManager.getCurrentLedgerVersion() > 7)`.

3. In `src/transactions/InflationTests.cpp`, the patch replaces `// minVote to participate in inflation` with `SECTION("total coins")`.

4. In `src/transactions/InflationOpFrame.cpp`, the patch replaces `int64 amountToDole = bigDivide(lcl.totalCoins, INFLATION_RATE_TRILLIONTHS,` with `auto inflationAmount = bigDivide(lcl.totalCoins, INFLATION_RATE_TRILLIONTHS,`.

## Project Context

The changed code sits primarily in `src/transactions`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/transactions/TransactionFrame.cpp`, `src/transactions/TxEnvelopeTests.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/transactions/TransactionFrame.cpp`, `src/transactions/TxEnvelopeTests.cpp`. The strongest project-level identifiers around this patch are `totalCoins`, `feePool`, `auto`, and `toDoleThisWinner`.

## Before/After Behavior

Before the patch, `amountToDole` combined newly computed inflation with `lcl.feePool`, and `lcl.totalCoins` was increased during each successful winner payout by `toDoleThisWinner`. After the patch, `inflationAmount` is kept separate from `amountToDole`; for ledger versions > 7, `totalCoins` is increased once by `inflationAmount` after leftovers are returned to the fee pool, while the old behavior remains gated to ledger versions <= 7.

# Root Cause

The old accounting path updated `totalCoins` from distributed payout amounts even though those payouts were derived from a pool containing both newly minted inflation and existing fee-pool funds. This could make the aggregate monetary counter depend on payout distribution mechanics rather than solely on newly created inflation.

## Walkthrough

1. `InflationOpFrame::doApply` computes inflation from current `totalCoins`.

2. Before the patch, that computed value was stored in `amountToDole` and then increased by `lcl.feePool`.

3. The payout loop subtracted each winner payout from `leftAfterDole`, increased `lcl.totalCoins` by the payout amount, credited the winner balance, and stored the account change.

4. Because the payout amount came from `amountToDole`, the `totalCoins` update could reflect fee-pool redistribution as well as newly minted inflation.

5. The patch introduces a separate `inflationAmount` variable and defines `amountToDole` as `inflationAmount + lcl.feePool`.

6. For ledger versions <= 7, the old per-winner `totalCoins` increment is preserved.

7. For ledger versions > 7, leftover funds are returned to `feePool` and `totalCoins` is increased once by `inflationAmount`.

8. Tests add coverage around `feePool` and `totalCoins` behavior in the inflation test suite.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/transactions/InflationOpFrame.cpp | 76 | Separates newly minted `inflationAmount` from `amountToDole`, which also includes the pre-existing `feePool`. |
| src/transactions/InflationOpFrame.cpp | 105 | Restricts old per-winner `totalCoins` increments to ledger versions <=7 for compatibility. |
| src/transactions/InflationOpFrame.cpp | 117 | For ledger versions >7, increments `totalCoins` exactly once by `inflationAmount` after returning unclaimed funds to the fee pool. |
| src/transactions/InflationTests.cpp | 328 | Adds regression coverage around `feePool` and `totalCoins` behavior in inflation tests. |

## Code Snippets

## Snippet 1

Context: `src/transactions/InflationOpFrame.cpp:105` (updates aggregate accounting or lifecycle state)

Before
```cpp
{
            leftAfterDole -= toDoleThisWinner;
            lcl.totalCoins += toDoleThisWinner;
            winner->getAccount().balance += toDoleThisWinner;
            winner->storeChange(inflationDelta, db);
```
After
```cpp
{
            leftAfterDole -= toDoleThisWinner;
            if (ledgerManager.getCurrentLedgerVersion() <= 7)
            {
                lcl.totalCoins += toDoleThisWinner;
            }
            winner->getAccount().balance += toDoleThisWinner;
            winner->storeChange(inflationDelta, db);
```

## Snippet 2

Context: `src/transactions/InflationOpFrame.cpp:117` (updates aggregate accounting or lifecycle state)

Before
```cpp
// put back in fee pool as unclaimed funds
    lcl.feePool += leftAfterDole;

    inflationDelta.commit();
```
After
```cpp
// put back in fee pool as unclaimed funds
    lcl.feePool += leftAfterDole;
    if (ledgerManager.getCurrentLedgerVersion() > 7)
    {
        lcl.totalCoins += inflationAmount;
    }

    inflationDelta.commit();
```

## Snippet 3

Context: `src/transactions/InflationTests.cpp:328` (updates aggregate accounting or lifecycle state)

Before
```cpp
3);
    }
    // minVote to participate in inflation
    const int64 minVote = 1000000000LL;
```
After
```cpp
3);
    }

    SECTION("total coins")
    {
        auto clh = app.getLedgerManager().getCurrentLedgerHeader();
        REQUIRE(clh.feePool == 0);
        REQUIRE(clh.totalCoins == 1000000000000000000);
```

## Snippet 4

Context: `src/transactions/InflationOpFrame.cpp:76` (updates aggregate accounting or lifecycle state)

Before
```cpp
INFLATION_NUM_WINNERS, db);

    int64 amountToDole = bigDivide(lcl.totalCoins, INFLATION_RATE_TRILLIONTHS,
                                   TRILLION, ROUND_DOWN);
    amountToDole += lcl.feePool;

    lcl.feePool = 0;
```
After
```cpp
INFLATION_NUM_WINNERS, db);

    auto inflationAmount = bigDivide(lcl.totalCoins, INFLATION_RATE_TRILLIONTHS,
                                  TRILLION, ROUND_DOWN);
    auto amountToDole = inflationAmount + lcl.feePool;

    lcl.feePool = 0;
```

# Fix Pattern

Separate minted value from redistributed value, then update the aggregate monetary counter exactly once from the minted component under the newer ledger-version rules.

## How It Was Fixed

The patch adds `inflationAmount`, computes `amountToDole` from `inflationAmount + lcl.feePool`, gates the old per-winner `totalCoins` increment behind `getCurrentLedgerVersion() <= 7`, and adds a `getCurrentLedgerVersion() > 7` path that increments `totalCoins` once by `inflationAmount`.

# Why It Matters

1. Keeps monetary aggregate accounting tied to minted inflation rather than payout mechanics.

2. Avoids treating existing fee-pool redistribution as newly created supply in the newer protocol path.

3. Preserves legacy ledger-version behavior explicitly.

4. Touches a consensus-relevant inflation path.

# Evidence Notes

Supported by `src/transactions/InflationOpFrame.cpp` snippets showing separation of `inflationAmount`, ledger-version gating of the old per-winner `lcl.totalCoins += toDoleThisWinner`, and the new `lcl.totalCoins += inflationAmount` path for ledger versions > 7. Test evidence shows added inflation coverage around `feePool` and `totalCoins`. Unsupported claims removed: the evidence does not prove direct attacker theft, cryptographic failure, replay bypass, or practical exploitability on a live network. Protocol security invariant: Inflation accounting must distinguish newly minted inflation from redistribution of existing fee-pool value. Under the active ledger-version rules, `totalCoins` should increase by the protocol-created `inflationAmount`, not by payout amounts that may include pre-existing `feePool` funds. Verification notes: The patch does not prove direct theft of funds by an attacker. The patch does not show cryptographic signature or replay validation being changed. The evidence does not establish whether the bug was practically exploitable on a live network. Legacy behavior for ledger versions <=7 is intentionally preserved, so the fix applies only under the newer protocol-version path. Code evidence supports an accounting bug in inflation handling. Security classification is based on consensus monetary accounting, not on demonstrated attacker exploitability. Confidence is medium because only snippets and tests are provided, not the full protocol specification or complete regression scenario. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-accounting-invariant`
Final tags: `blockchain-core, transaction-processing, inflation, state-accounting, consensus-accounting`

The supplied patch evidence supports a security-hardening classification, not a concrete security-fix classification. The code separates newly minted inflation from redistributed fee-pool value and changes how totalCoins is updated under newer ledger versions, which tightens a consensus-relevant monetary accounting invariant. However, the evidence does not prove attacker control, theft, bypass, or practical exploitability, so retaining it as a hardening case is more conservative than treating it as a confirmed exploitable bug fix.

## Security Evidence

1. InflationOpFrame.cpp changes totalCoins accounting in the inflation operation path.
2. The patch separates inflationAmount from amountToDole, preventing feePool redistribution from being treated the same as newly minted inflation.
3. The old per-winner totalCoins increment is gated to ledger versions <= 7, while newer ledger versions increment totalCoins once by inflationAmount.
4. Regression coverage was added around feePool and totalCoins behavior.

## Missing Evidence

1. No exploit scenario or attacker-controlled path is shown.
2. No protocol specification is provided proving the old behavior violated a consensus security rule.
3. No evidence shows live-network impact, theft, signature bypass, replay issue, or denial of service.
4. The snippets do not show the full regression test assertions or resulting failure mode.

## Claim Boundaries

1. This should not be described as a cryptographic, signature, or replay vulnerability.
2. This supports consensus monetary accounting hardening rather than proven direct fund theft.
3. The validated claim is limited to inflation totalCoins and feePool accounting behavior.
4. The fix applies to ledger-version-dependent protocol behavior, preserving legacy behavior for versions <= 7.
