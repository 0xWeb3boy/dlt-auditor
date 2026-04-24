---
case_id: case_20200518_df29e98ea
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2020-05-18
source_refs:
  - git:df29e98ea51e762491ef8549e0e9b1932e16eea0
  - "src/ripple/core/impl/Config.cpp:481"
  - "src/ripple/app/misc/impl/AmendmentTable.cpp:523"
  - "src/ripple/app/misc/impl/AmendmentTable.cpp:174"
  - "src/ripple/app/misc/impl/AmendmentTable.cpp:654"
bug_class: consensus-threshold-rounding
impact_type:
  - protocol-governance-integrity
confidence: medium
tags:
  - blockchain-core
  - consensus
  - amendment-voting
  - threshold-rounding
  - integer-arithmetic
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a consensus-amendment threshold rounding fix. The commit message explicitly says amendment ballot counting could allow majority with slightly less than 80% support due to integer arithmetic and rounding semantics. The strongest code evidence is in AmendmentTable voting, where AmendmentSet construction now receives consensus rules and the validation set and exposes trusted validation count and threshold state. The evidence does not establish remote exploitability, unauthorized validator voting power, or that a fork occurred.

## Observed Patch Facts

1. In `src/ripple/core/impl/Config.cpp`, the patch replaces `// Do not load trusted validator configuration for standalone mode` with `if (getSingleSection(`.

2. In `src/ripple/app/misc/impl/AmendmentTable.cpp`, the patch replaces `auto vote = std::make_unique<AmendmentSet>();` with `auto vote = std::make_unique<AmendmentSet>(rules, valSet);`.

3. In `src/ripple/app/misc/impl/AmendmentTable.cpp`, the patch replaces `};` with `int`.

4. In `src/ripple/app/misc/impl/AmendmentTable.cpp`, the patch removes `v[jss::vote] = votesFor * 256 / votesNeeded;`.

## Project Context

The changed code sits primarily in `src/ripple/core/impl`, `src/ripple/core`, `src/ripple/app/misc/impl`, which anchors the finding in the `consensus` area of the project. Historical context from `src/ripple/core/impl/TimeKeeper.cpp`, `src/ripple/core/impl/SociDB.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/misc/NetworkOPs.cpp`, `src/ripple/app/misc/FeeVoteImpl.cpp`. The strongest project-level identifiers around this patch are `std::make_unique`, `const`, `vote`, and `auto`.

## Before/After Behavior

Before the patch, doVoting constructed an empty AmendmentSet and then processed trusted validations afterward, and JSON reporting included an integer-scaled vote ratio computed as votesFor * 256 / votesNeeded. After the patch, doVoting constructs AmendmentSet with rules and valSet, logs trusted validation count and threshold, and exposes those values through accessors. JSON reporting now shows count, validations, and threshold rather than the old ratio. Config parsing also adds validated amendment majority timing configuration, which the commit identifies as consensus-sensitive.

# Root Cause

Based on the commit message, the root cause was integer arithmetic and rounding semantics in amendment ballot counting that could make the effective majority threshold slightly lower than the intended 80% support requirement.

## Walkthrough

1. The commit message directly states that amendment ballot counting could reach majority with slightly less than 80% support.

2. The central implementation evidence is in AmendmentTableImpl::doVoting, where AmendmentSet construction changes from an empty object to AmendmentSet(rules, valSet).

3. New accessors expose trustedValidations() and threshold(), grounding that trusted validation count and computed threshold became explicit AmendmentSet state.

4. The JSON path previously emitted an integer ratio using votesFor * 256 / votesNeeded; the shown after-state reports threshold-related fields without that ratio.

5. Config parsing adds SECTION_AMENDMENT_MAJORITY_TIME validation, but this is supporting consensus-parameter evidence rather than the root cause.

6. The evidence supports a consensus threshold bug, but not a claim of remote exploitability or demonstrated network divergence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/misc/impl/AmendmentTable.cpp | 523 | builds amendment vote set from consensus rules and trusted validations before amendment majority decisions |
| src/ripple/app/misc/impl/AmendmentTable.cpp | 174 | exposes trusted validation count and computed activation threshold used by amendment voting state |
| src/ripple/app/misc/impl/AmendmentTable.cpp | 654 | reports amendment vote counts and threshold, removing the old integer vote ratio output |
| src/ripple/core/impl/Config.cpp | 481 | parses amendment majority timing configuration, a consensus-sensitive hysteresis parameter |

## Code Snippets

## Snippet 1

Context: `src/ripple/core/impl/Config.cpp:481` (changes a sensitive control or state-update path)

Before
```cpp
COMPRESSION = beast::lexicalCastThrow<bool>(strTemp);

    // Do not load trusted validator configuration for standalone mode
    if (!RUN_STANDALONE)
```
After
```cpp
COMPRESSION = beast::lexicalCastThrow<bool>(strTemp);

    if (getSingleSection(
            secConfig, SECTION_AMENDMENT_MAJORITY_TIME, strTemp, j_))
    {
        using namespace std::chrono;
        boost::regex const re(
            "^\\s*(\\d+)\\s*(minutes|hours|days|weeks)\\s*(\\s+.*)?$");
```

## Snippet 2

Context: `src/ripple/app/misc/impl/AmendmentTable.cpp:523` (changes an authorization or privilege gate)

Before
```cpp
<< majorityAmendments.size() << ", " << valSet.size();

    auto vote = std::make_unique<AmendmentSet>();

    // process validations for ledger before flag ledger
    for (auto const& val : valSet)
    {
        if (val->isTrusted())
```
After
```cpp
<< majorityAmendments.size() << ", " << valSet.size();

    auto vote = std::make_unique<AmendmentSet>(rules, valSet);

    JLOG(j_.debug()) << "Received " << vote->trustedValidations()
                     << " trusted validations, threshold is: "
                     << vote->threshold();
```

## Snippet 3

Context: `src/ripple/app/misc/impl/AmendmentTable.cpp:174` (changes an authorization or privilege gate)

Before
```cpp
return it->second;
    }
};
```
After
```cpp
return it->second;
    }

    int
    trustedValidations() const
    {
        return trustedValidations_;
    }
```

## Snippet 4

Context: `src/ripple/app/misc/impl/AmendmentTable.cpp:654` (changes a consensus- or validator-sensitive branch)

Before
```cpp
if (votesNeeded)
        {
            v[jss::vote] = votesFor * 256 / votesNeeded;
            v[jss::threshold] = votesNeeded;
        }
    }
}
```
After
```cpp
if (votesNeeded)
            v[jss::threshold] = votesNeeded;
    }
}
```

# Fix Pattern

Make the consensus activation threshold explicit and computed from the trusted validation set and consensus rules, avoiding reliance on an integer-scaled ratio that can obscure or lower the intended threshold.

## How It Was Fixed

The patch routes amendment voting through an AmendmentSet constructed with rules and valSet, adds accessors for trusted validation count and threshold, and changes reporting to expose count, validations, and threshold instead of the old integer vote ratio. It also adds parsing for amendment majority timing configuration.

# Why It Matters

1. Amendment activation is consensus-sensitive protocol behavior.

2. A rounding error can weaken the intended 80% support threshold.

3. Incorrect amendment activation could change protocol behavior earlier than intended.

4. The evidence is security-relevant but does not prove an active exploit or historical fork.

# Evidence Notes

The strongest evidence is the commit message plus AmendmentTable.cpp changes around doVoting, threshold accessors, and JSON reporting. The Config.cpp majority-time parsing is related consensus configuration support, not the demonstrated root cause. Claims about access control, remote attackers, unauthorized validators, or actual network forks are unsupported by the provided evidence. Protocol security invariant: Amendment activation should require at least 80% support from trusted validations, and integer arithmetic or rounding must not lower the effective activation threshold. Verification notes: The patch does not prove a remotely triggerable exploit path. The patch does not show unauthorized validators gaining voting power. The patch does not prove that a mainnet fork or incorrect amendment activation actually occurred. The configuration option is consensus-sensitive, but the evidence does not show a direct vulnerability from parsing alone. JSON reporting changes are supporting evidence, not by themselves consensus enforcement. Commit message explicitly names the rounding flaw and less-than-80% majority condition. Code evidence shows threshold and trusted-validation state added to AmendmentSet usage. JSON reporting changes alone do not prove enforcement behavior. No provided evidence proves exploitability beyond the consensus threshold invariant. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `consensus-threshold-rounding`
Final impact type: `protocol-governance-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, amendment-voting, threshold-rounding, integer-arithmetic`

The supplied evidence supports retaining this as a security-relevant consensus fix, but the original metadata overstates the impact. The commit message directly identifies an integer arithmetic and rounding flaw that could allow amendment activation with slightly less than the intended 80% support, and the patch evidence shows amendment voting now computes explicit trusted-validation and threshold state. This is a consensus-governance integrity issue, not proven evidence of network divergence, unauthorized validator power, or an exploitable remote attack.

## Security Evidence

1. Commit message states amendment ballot counting could reach majority with slightly less than 80% support.
2. Changed AmendmentSet construction now receives consensus rules and the validation set.
3. Patch exposes trusted validation count and computed threshold through AmendmentSet accessors.
4. JSON reporting changes remove the old integer-scaled vote ratio and report count, validations, and threshold.
5. Configuration text warns amendment activation hysteresis is a network-wide consensus parameter and changing it per server can hard-fork.

## Missing Evidence

1. No evidence that an amendment actually activated incorrectly.
2. No evidence of a realized fork or consensus split from the rounding flaw.
3. No evidence of remote exploitability or unauthenticated attacker influence.
4. No evidence that untrusted validators gained voting power.
5. Provided snippets do not fully show the threshold calculation implementation.

## Claim Boundaries

1. Supported claim: amendment activation threshold handling was corrected for an 80% support invariant.
2. Supported claim: the affected code is consensus-sensitive amendment voting logic.
3. Unsupported claim: this caused a consensus failure in production.
4. Unsupported claim: this was an access-control or privilege-check fix.
5. Unsupported claim: RPC or queue behavior is central to the vulnerability.
