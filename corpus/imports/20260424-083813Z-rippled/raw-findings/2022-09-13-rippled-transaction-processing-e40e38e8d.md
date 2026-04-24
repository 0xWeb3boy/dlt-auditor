---
case_id: case_20220913_e40e38e8d
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2022-09-13
source_refs:
  - git:e40e38e8d3ce447668215fd8dfb37a1a2b5504e9
  - "src/ripple/app/tx/impl/NFTokenMint.cpp:41"
  - "src/ripple/protocol/TxFlags.h:121"
  - "src/ripple/protocol/Feature.h:75"
  - "src/ripple/protocol/impl/Feature.cpp:448"
bug_class: unauthorized-resource-consumption
impact_type:
  - resource-exhaustion
  - economic-denial-of-service
tags:
  - blockchain-core
  - transaction-processing
  - nftoken
  - trustline
  - unauthorized-resource-consumption
  - issuer-reserve-exhaustion
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch removes the NFTokenMint tfTrustLine capability through the fixRemoveNFTokenAutoTrustLine amendment. The commit message and added code comments explicitly state that the old capability could be used to attack the NFToken issuer by allowing transfers to add TrustLines to the issuer without explicit issuer permission, increasing the issuer's reserve without bound.

## Observed Patch Facts

1. In `src/ripple/app/tx/impl/NFTokenMint.cpp`, the patch replaces `if (ctx.tx.getFlags() & tfNFTokenMintMask)` with `// Prior to fixRemoveNFTokenAutoTrustLine, transfer of an NFToken between`.

2. In `src/ripple/protocol/TxFlags.h`, the patch replaces `constexpr std::uint32_t const tfNFTokenMintMask =` with `// Prior to fixRemoveNFTokenAutoTrustLine, transfer of an NFToken between`.

3. In `src/ripple/protocol/Feature.h`, the patch replaces `static constexpr std::size_t numFeatures = 50;` with `static constexpr std::size_t numFeatures = 51;`.

4. In `src/ripple/protocol/impl/Feature.cpp`, the patch adds `REGISTER_FIX (fixRemoveNFTokenAutoTrustLine, Supported::yes, DefaultVote::yes);`.

## Project Context

The changed code sits primarily in `src/ripple/app/tx/impl`, `src/ripple/app/tx`, `src/ripple/protocol`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/ripple/app/tx/impl/NFTokenMint.h`, `src/ripple/app/tx/impl/NFTokenCreateOffer.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/protocol/SField.h`, `src/ripple/protocol/impl/STTx.cpp`. The strongest project-level identifiers around this patch are `Supported::yes`, `issuer`, `std::uint32_t`, and `NFToken`. Nearby tests or test-like files include `src/ripple/beast/unit_test/results.hpp`, `src/ripple/beast/unit_test/reporter.hpp`.

## Before/After Behavior

Before the patch, tfTrustLine was an accepted NFTokenMint flag under the NFToken mint flag mask, enabling a token configuration where later NFToken transfers could add TrustLines to the issuer without explicit issuer permission. After the patch, the new fixRemoveNFTokenAutoTrustLine amendment is registered and the NFTokenMint flag handling is changed to disable minting with tfTrustLine when the amendment applies.

# Root Cause

The protocol allowed an issuer-affecting mint-time flag whose consequences occurred later during transfers by other accounts. That let non-issuer activity create TrustLines to the issuer and impose reserve costs without explicit issuer consent.

## Walkthrough

1. NFTokenMint previously accepted tfTrustLine as a valid mint flag because the NFToken mint mask included it among allowed flags.

2. The added comments state that an NFToken minted with tfTrustLine could cause a TrustLine to be added to the issuer during later transfers.

3. Those transfers could occur between accounts other than the issuer, so the issuer did not explicitly authorize each TrustLine.

4. The comments describe two accounts repeatedly trading the NFToken back and forth to build any number of TrustLines on the issuer.

5. Those TrustLines increased the issuer's reserve without bound, creating a resource exhaustion or reserve inflation issue.

6. The fix introduces and registers fixRemoveNFTokenAutoTrustLine and disables minting with tfTrustLine under that amendment.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/tx/impl/NFTokenMint.cpp | 41 | NFTokenMint preflight validation path where tfTrustLine minting is disabled by the fix amendment |
| src/ripple/protocol/TxFlags.h | 121 | NFTokenMint flag definitions and mask governing whether tfTrustLine is accepted as a mint flag |
| src/ripple/protocol/impl/Feature.cpp | 448 | Registers fixRemoveNFTokenAutoTrustLine as a supported default-yes amendment |
| src/ripple/protocol/Feature.h | 75 | Updates feature bitset capacity to include the new amendment |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/tx/impl/NFTokenMint.cpp:41` (updates aggregate accounting or lifecycle state)

Before
```cpp
return ret;

    if (ctx.tx.getFlags() & tfNFTokenMintMask)
        return temINVALID_FLAG;
```
After
```cpp
return ret;

    // Prior to fixRemoveNFTokenAutoTrustLine, transfer of an NFToken between
    // accounts allowed a TrustLine to be added to the issuer of that token
    // without explicit permission from that issuer.  This was enabled by
    // minting the NFToken with the tfTrustLine flag set.
    //
    // That capability could be used to attack the NFToken issuer.  It
```

## Snippet 2

Context: `src/ripple/protocol/TxFlags.h:121` (updates aggregate accounting or lifecycle state)

Before
```c
constexpr std::uint32_t const tfTransferable           = 0x00000008;

constexpr std::uint32_t const tfNFTokenMintMask =
    ~(tfUniversal | tfBurnable | tfOnlyXRP | tfTrustLine | tfTransferable);

// NFTokenCreateOffer flags:
constexpr std::uint32_t const tfSellNFToken            = 0x00000001;
```
After
```c
constexpr std::uint32_t const tfTransferable           = 0x00000008;

// Prior to fixRemoveNFTokenAutoTrustLine, transfer of an NFToken between
// accounts allowed a TrustLine to be added to the issuer of that token
// without explicit permission from that issuer.  This was enabled by
// minting the NFToken with the tfTrustLine flag set.
//
// That capability could be used to attack the NFToken issuer.  It
```

## Snippet 3

Context: `src/ripple/protocol/Feature.h:75` (updates aggregate accounting or lifecycle state)

Before
```c
// large to make the FeatureBitset, it MAY be larger. It MUST NOT be less than
// the actual number of amendments. A LogicError on startup will verify this.
static constexpr std::size_t numFeatures = 50;

/** Amendments that this server supports and the default voting behavior.
```
After
```c
// large to make the FeatureBitset, it MAY be larger. It MUST NOT be less than
// the actual number of amendments. A LogicError on startup will verify this.
static constexpr std::size_t numFeatures = 51;

/** Amendments that this server supports and the default voting behavior.
```

## Snippet 4

Context: `src/ripple/protocol/impl/Feature.cpp:448` (updates aggregate accounting or lifecycle state)

Before
```cpp
REGISTER_FIX    (fixNFTokenNegOffer,            Supported::yes, DefaultVote::no);
REGISTER_FEATURE(NonFungibleTokensV1_1,         Supported::yes, DefaultVote::no);

// The following amendments have been active for at least two years. Their
```
After
```cpp
REGISTER_FIX    (fixNFTokenNegOffer,            Supported::yes, DefaultVote::no);
REGISTER_FEATURE(NonFungibleTokensV1_1,         Supported::yes, DefaultVote::no);
REGISTER_FIX    (fixRemoveNFTokenAutoTrustLine, Supported::yes, DefaultVote::yes);

// The following amendments have been active for at least two years. Their
```

# Fix Pattern

Remove or gate a protocol flag that allows future third-party transactions to impose issuer reserve costs without issuer consent.

## How It Was Fixed

The patch adds the fixRemoveNFTokenAutoTrustLine amendment, registers it as supported with default yes voting, updates feature capacity, and changes NFTokenMint flag validation/definitions so tfTrustLine minting is disabled under the amendment.

# Why It Matters

1. Prevents third parties from imposing unbounded reserve burden on an issuer.

2. Preserves issuer consent for TrustLine-related resource costs.

3. Limits the finding to issuer reserve inflation/resource exhaustion, not theft or memory corruption.

# Evidence Notes

The strongest evidence is the commit message and the added comments in NFTokenMint.cpp and TxFlags.h, which explicitly describe unauthorized TrustLine creation, repeated transfer buildup, and unbounded issuer reserve increase. The Feature.cpp and Feature.h changes support that this behavior was fixed through a new amendment. The provided evidence does not support claims of fund theft, remote code execution, memory corruption, consensus bypass, or arbitrary ledger mutation. Protocol security invariant: An NFToken mint flag must not allow later transfers by other accounts to create TrustLines to the issuer without the issuer's explicit permission, because those TrustLines can increase the issuer's reserve burden. Verification notes: The patch evidence does not prove theft of funds or direct token loss. The patch evidence does not show remote code execution, memory corruption, or consensus bypass. The exact transaction sequence and economic cost are not shown beyond the described repeated transfer/trustline reserve growth. The evidence supports issuer resource exhaustion/reserve inflation, not arbitrary ledger-state mutation. Security relevance is explicitly stated in the commit message and code comments. The exact exploit transaction sequence is not fully shown, but the vulnerable behavior and impact are directly documented in the patch comments. Tests are mentioned in the changed files list, but their contents were not provided, so no specific test assertion is claimed. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `unauthorized-resource-consumption`
Final impact type: `resource-exhaustion, economic-denial-of-service`
Final tags: `blockchain-core, transaction-processing, nftoken, trustline, unauthorized-resource-consumption, issuer-reserve-exhaustion`

The supplied commit message and added code comments directly describe an attack enabled by the NFTokenMint tfTrustLine flag: transfers could add TrustLines to the issuer without issuer permission, allowing repeated trades to increase the issuer's reserve without bound. The patch introduces a protocol amendment to remove that minting capability, so the evidence supports retaining this as a security fix, with the impact framed conservatively as unauthorized resource consumption/economic denial of service rather than arbitrary state corruption or theft.

## Security Evidence

1. Commit body explicitly says the tfTrustLine feature could be used to attack the NFToken issuer.
2. Added comments state TrustLines could be added to the issuer without explicit issuer permission.
3. Added comments describe repeated transfers building any number of TrustLines and increasing the issuer's reserve without bound.
4. The patch registers fixRemoveNFTokenAutoTrustLine as a supported default-yes fix amendment.
5. The changed NFTokenMint/TxFlags evidence shows the risky mint flag behavior is being disabled or removed.

## Missing Evidence

1. The supplied snippets do not show the full final conditional logic in NFTokenMint::preflight.
2. The exact exploit transaction sequence is described in comments but not demonstrated in provided tests.
3. No test assertions are included in the supplied evidence, despite test files being listed.
4. The evidence does not quantify the reserve cost or operational severity.

## Claim Boundaries

1. Supports issuer reserve exhaustion/resource consumption, not fund theft.
2. Supports unauthorized issuer burden via TrustLine creation, not remote code execution or memory corruption.
3. Supports a protocol-level security fix for NFTokenMint flag behavior, not a general consensus bypass.
4. Security conclusion relies on the commit message and in-code comments plus focused amendment changes.
