---
case_id: case_20240324_a7c4a4772
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2024-03-24
source_refs:
  - git:a7c4a47723c21e2fc100ddb00294659eb59f588e
  - "src/ripple/app/paths/AMMLiquidity.h:138"
  - "src/ripple/app/paths/impl/AMMLiquidity.cpp:201"
  - "src/ripple/app/paths/impl/AMMLiquidity.cpp:216"
  - "src/ripple/app/paths/AMMOffer.h:142"
bug_class: amm-offer-overflow-hardening
impact_type:
  - state-integrity
  - economic-integrity
confidence: medium
tags:
  - blockchain-core
  - payment-path
  - amm
  - overflow
  - invariant-check
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to fix incorrect handling of large synthetic AMM offers in rippled's payment AMM path. The supplied evidence supports an arithmetic and invariant-handling bug: max-offer generation becomes rules-aware and optional, overflow handling can return no offer when `fixAMMOverflowOffer` is enabled, and an AMM pool-product invariant check is declared. The evidence does not establish a concrete vulnerability impact, exploitability, fund loss, ledger corruption, or denial-of-service scenario, so this should not be treated as a confirmed or likely security fix from the provided input alone.

## Observed Patch Facts

1. In `src/ripple/app/paths/AMMLiquidity.h`, the patch replaces `/** Generate max offer` with `/** Generate max offer.`.

2. In `src/ripple/app/paths/impl/AMMLiquidity.cpp`, the patch replaces `// sendmax, or available output or input funds.` with `// sendmax, or available output or input funds. Might return`.

3. In `src/ripple/app/paths/impl/AMMLiquidity.cpp`, the patch replaces `return maxOffer(balances);` with `if (!view.rules().enabled(fixAMMOverflowOffer))`.

4. In `src/ripple/app/paths/AMMOffer.h`, the patch replaces `};` with `/** Check the new pool product is greater or equal to the old pool`.

## Project Context

The changed code sits primarily in `src/ripple/app/paths`, `src/ripple/app`, `src/ripple/app/paths/impl`, which anchors the finding in the `storage` area of the project. Historical context from `src/ripple/app/paths/impl/StrandFlow.h`, `src/ripple/app/paths/impl/BookStep.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/paths/impl/StrandFlow.h`, `src/ripple/app/paths/impl/BookStep.cpp`. The strongest project-level identifiers around this patch are `balances`, `const`, `maxOffer`, and `TOut`.

## Before/After Behavior

Before the patch, the shown `AMMLiquidity::getOffer` paths called `maxOffer(balances)` unconditionally in the no-CLOB branch and after catching an overflow. After the patch, those paths pass `view.rules()`, `maxOffer` is documented as returning `std::optional`, fixed behavior generates an offer from 99% of the output balance using `swapOut`, edge cases can return `nullopt`, and overflow handling returns `std::nullopt` when `fixAMMOverflowOffer` is enabled. The patch also declares an AMM offer invariant check comparing the new and old pool product with an allowed threshold for decreases.

# Root Cause

The supported root cause is that large synthetic AMM offer generation and overflow fallback behavior could produce an unsuitable max offer instead of declining to produce one. The supplied hunks also show the addition of a pool-product invariant check, but they do not show the full implementation or prove the prior behavior violated a security property in an exploitable way.

## Walkthrough

1. `AMMLiquidity::getOffer` participates in payment-path AMM liquidity handling.

2. The old shown no-CLOB path returned a max synthetic AMM offer with `maxOffer(balances)`.

3. The old shown overflow catch path logged the overflow and still returned `maxOffer(balances)`.

4. The patch changes those call sites to use rules-aware max-offer generation.

5. With `fixAMMOverflowOffer` active, documented max-offer generation uses 99% of the output balance and can return `nullopt` for edge cases.

6. With the fix active, the overflow catch path returns `std::nullopt` instead of falling back to another max offer.

7. `AMMOffer.h` now declares `checkInvariant`, indicating added validation of AMM pool-product behavior after consumption.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/paths/AMMLiquidity.h | 138 | Declares max synthetic AMM offer generation and documents the fixed bounded 99%-of-output behavior plus nullopt cases. |
| src/ripple/app/paths/impl/AMMLiquidity.cpp | 201 | Generates a max synthetic AMM offer when no CLOB quality is available, now using rules-aware behavior that can decline to produce an offer. |
| src/ripple/app/paths/impl/AMMLiquidity.cpp | 216 | Handles overflow during AMM offer generation; with the fix enabled it stops returning a fallback max offer and returns nullopt. |
| src/ripple/app/paths/AMMOffer.h | 142 | Declares an invariant check that compares new and old AMM pool product after consuming a synthetic offer. |
| src/ripple/app/paths/impl/BookStep.cpp | 37 | Wider payment book-step path that consumes AMM/CLOB offers during strand flow. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/paths/AMMLiquidity.h:138` (changes aggregate state or economic accounting)

Before
```c
generateFibSeqOffer(TAmounts<TIn, TOut> const& balances) const;

    /** Generate max offer
     */
    AMMOffer<TIn, TOut>
    maxOffer(TAmounts<TIn, TOut> const& balances) const;
};
```
After
```c
generateFibSeqOffer(TAmounts<TIn, TOut> const& balances) const;

    /** Generate max offer.
     * If `fixAMMOverflowOffer` is active, the offer is generated as:
     * takerGets = 99% * balances.out takerPays = swapOut(takerGets).
     * Return nullopt if takerGets is 0 or takerGets == balances.out.
     *
     * If `fixAMMOverflowOffer` is not active, the offer is generated as:
```

## Snippet 2

Context: `src/ripple/app/paths/impl/AMMLiquidity.cpp:201` (changes aggregate state or economic accounting)

Before
```cpp
// amount, which doesn't overflow. The size is going to be
                // changed in BookStep per either deliver amount limit, or
                // sendmax, or available output or input funds.
                return maxOffer(balances);
            }
            else if (
```
After
```cpp
// amount, which doesn't overflow. The size is going to be
                // changed in BookStep per either deliver amount limit, or
                // sendmax, or available output or input funds. Might return
                // nullopt if the pool is small.
                return maxOffer(balances, view.rules());
            }
            else if (
```

## Snippet 3

Context: `src/ripple/app/paths/impl/AMMLiquidity.cpp:216` (changes aggregate state or economic accounting)

Before
```cpp
{
            JLOG(j_.error()) << "AMMLiquidity::getOffer overflow " << e.what();
            return maxOffer(balances);
        }
        catch (std::exception const& e)
```
After
```cpp
{
            JLOG(j_.error()) << "AMMLiquidity::getOffer overflow " << e.what();
            if (!view.rules().enabled(fixAMMOverflowOffer))
                return maxOffer(balances, view.rules());
            else
                return std::nullopt;
        }
        catch (std::exception const& e)
```

## Snippet 4

Context: `src/ripple/app/paths/AMMOffer.h:142` (changes a sensitive control or state-update path)

Before
```c
return {ofrInRate, QUALITY_ONE};
    }
};
```
After
```c
return {ofrInRate, QUALITY_ONE};
    }

    /** Check the new pool product is greater or equal to the old pool
     * product or if decreases then within some threshold.
     */
    bool
    checkInvariant(TAmounts<TIn, TOut> const& consumed, beast::Journal j) const;
```

# Fix Pattern

Make large synthetic AMM offer construction rules-aware and optional, avoid retrying max-offer construction after overflow under the new feature flag, and add an explicit AMM pool-product invariant check.

## How It Was Fixed

The patch introduces `fixAMMOverflowOffer`-aware `maxOffer` behavior, updates call sites to pass `view.rules()`, changes overflow handling to return no offer when the fix is enabled, documents bounded 99%-of-output offer generation, and declares `AMMOffer::checkInvariant` for pool-product validation.

# Why It Matters

1. The changed code is in payment-path AMM offer generation.

2. Overflow handling previously still returned a max synthetic offer in the shown code.

3. The new behavior can decline to construct an unsafe or unrepresentable offer.

4. The added invariant check is relevant to AMM accounting correctness.

5. Security impact is plausible but not established by the supplied evidence.

# Evidence Notes

Grounded evidence includes the commit message, rules-aware optional max-offer documentation, changed `AMMLiquidity::getOffer` call sites, overflow handling that returns `std::nullopt` when `fixAMMOverflowOffer` is enabled, and the declaration of `AMMOffer::checkInvariant`. Unsupported claims include confirmed exploitability, direct theft, inflation, ledger corruption, denial of service, or a fully demonstrated consensus failure. The exact invariant implementation, threshold, activation behavior, and tests are not included. Protocol security invariant: Synthetic AMM offers generated for payment path processing should be representable, bounded by pool balances, and should not cause AMM pool-product invariant checks to fail outside an allowed threshold. Verification notes: The evidence does not prove remote exploitability. The evidence does not prove direct theft, inflation, or ledger corruption. The exact threshold and implementation of `checkInvariant` are not shown in the provided hunks. The patch appears consensus-sensitive, but amendment activation behavior beyond the shown `fixAMMOverflowOffer` gate is not fully shown. No tests or exploit reproduction are provided in the input. No exploit reproduction was provided. No tests were provided in the input. The `checkInvariant` implementation is not shown. Amendment activation details are only partially evidenced by the shown feature-flag checks. Classified as unclear because the patch may be security relevant, but the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `amm-offer-overflow-hardening`
Final impact type: `state-integrity, economic-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, payment-path, amm, overflow, invariant-check, security-hardening`

The evidence does not prove a concrete exploitable vulnerability, so this should not be classified as a confirmed security fix. However, the patch clearly tightens behavior in a security-sensitive blockchain payment/AMM path: large synthetic offer generation becomes bounded and optional, overflow fallback stops producing another max offer under the fix flag, and an AMM pool-product invariant check is introduced. That supports retaining it conservatively as security hardening rather than as a demonstrated security fix.

## Security Evidence

1. Commit subject and body describe improper handling of large synthetic AMM offers in the payment engine.
2. Overflow handling in AMMLiquidity::getOffer changes from returning maxOffer after overflow to returning std::nullopt when fixAMMOverflowOffer is enabled.
3. maxOffer becomes rules-aware and optional, with fixed behavior bounded to 99% of output balance and edge cases returning nullopt.
4. AMMOffer declares a pool-product invariant check for consumed synthetic offers.
5. Changes are in payment-path AMM liquidity handling, a consensus/economic correctness-sensitive subsystem.

## Missing Evidence

1. No exploit reproduction or attack scenario is provided.
2. No implementation of checkInvariant is shown in the supplied evidence.
3. No tests or failure cases are provided.
4. No direct proof of fund loss, inflation, ledger corruption, or denial of service is shown.
5. Feature activation and full consensus behavior are only partially evidenced.

## Claim Boundaries

1. Classify as hardening, not a confirmed vulnerability fix.
2. Do not claim proven theft, inflation, or consensus failure.
3. Do not claim storage-specific root cause; the supported subsystem is payment-path AMM handling.
4. Do not infer remote exploitability from the supplied patch alone.
