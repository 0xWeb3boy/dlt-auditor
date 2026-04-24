---
case_id: case_20230301_7b60006a26
project: sui
domain: blockchain-core
render_mode: heuristic
context_depth: deep
phase3_security_verdict: not-reviewed
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-03-01
source_refs:
  - git:7b60006a268e7cec1c45250b3b655af8418299ca
  - "crates/sui-types/src/messages.rs:215"
  - "crates/sui-types/src/messages.rs:258"
  - "crates/sui-types/src/messages.rs:645"
  - "crates/sui-types/src/messages.rs:138"
bug_class: resource-exhaustion
impact_type:
  - denial-of-service
  - resource-exhaustion
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - input-validation
  - resource-limits
  - resource-exhaustion
  - denial-of-service
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Add ProtocolConfig limits for various attributes of input transactions. (#8557) appears to strengthen state integrity in the transaction-processing path of sui. The strongest evidence spans `crates/sui-types/src/messages.rs` and `crates/sui-types/src/messages.rs`. The affected state likely includes `config`, `type_arguments_count`, and `fp_ensure`. The selected hunks suggest persisted or derived state could previously become inconsistent with the live runtime state. Additional project context from `crates/sui-types/src/object.rs`, `crates/sui-types/src/error.rs` was used to anchor the surrounding module behavior. Commit context: ## Description Adds various size limits for components of input transaction. ## Test Plan Updated unit tests, which did fail with old impls by hitting the new limits..

## Observed Patch Facts

1. In `crates/sui-types/src/messages.rs`, the patch replaces `/// Send SUI coins to a list of addresses, following a list of amounts.` with `impl PayAllSui {`.

2. In `crates/sui-types/src/messages.rs`, the patch replaces `/// Pay each recipient the corresponding amount using the input coins` with `impl PaySui {`.

3. In `crates/sui-types/src/messages.rs`, the patch replaces `Command::TransferObjects(_, _)` with `let mut type_arguments_count = 0;`.

4. In `crates/sui-types/src/messages.rs`, the patch replaces `#[serde_as]` with `impl MoveCall {`.

## Project Context

The changed code sits primarily in `crates/sui-types/src`, `crates/sui-types`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-types/src/object.rs`, `crates/sui-types/src/error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/object.rs`, `crates/sui-types/src/error.rs`. The strongest project-level identifiers around this patch are `config`, `type_arguments_count`, `fp_ensure`, and `UserInputError::BlockedMoveFunction`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/messages_tests.rs`, `crates/sui-types/src/unit_tests/base_types_tests.rs`.

## Before/After Behavior

1. Before the patch, `crates/sui-types/src/messages.rs` relied on `/// Send SUI coins to a list of addresses, following a list of amounts.`. After the patch, it instead uses `impl PayAllSui {`.

2. Before the patch, `crates/sui-types/src/messages.rs` relied on `/// Pay each recipient the corresponding amount using the input coins`. After the patch, it instead uses `impl PaySui {`.

3. Before the patch, `crates/sui-types/src/messages.rs` relied on `Command::TransferObjects(_, _)`. After the patch, it instead uses `let mut type_arguments_count = 0;`.

4. In deep mode, the generator also traced related identifiers into `crates/sui-types/src/object.rs`, `crates/sui-types/src/error.rs` to verify how the changed path fits into the wider subsystem behavior.

# Root Cause

The issue appears to sit at the boundary between `crates/sui-types/src/messages.rs` and `crates/sui-types/src/messages.rs`. The likely root cause was inconsistent state mutation across related storage or accounting paths.

## Walkthrough

1. In `crates/sui-types/src/messages.rs:215`, the selected hunk changes bounds, limits, or capacity handling. Notable identifiers in this step include `coins`, `UserInputError::EmptyInputCoins`, and `UserInputError::UnexpectedGasPaymentObject`. The hunk matched touches a critical implementation path, diff changes runtime guards or failure handling, diff changes resource-control logic.

2. In `crates/sui-types/src/messages.rs:258`, the selected hunk changes bounds, limits, or capacity handling. Notable identifiers in this step include `coins`, `UserInputError::EmptyInputCoins`, and `UserInputError::UnexpectedGasPaymentObject`. The hunk matched touches a critical implementation path, diff changes runtime guards or failure handling, diff changes resource-control logic.

3. In `crates/sui-types/src/messages.rs:645`, the selected hunk changes bounds, limits, or capacity handling. Notable identifiers in this step include `type_arguments_count`, `UserInputError::BlockedMoveFunction`, and `config`. The hunk matched touches a critical implementation path, diff changes resource-control logic.

4. In `crates/sui-types/src/messages.rs:138`, the selected hunk changes bounds, limits, or capacity handling. Notable identifiers in this step include `as_str`, `UserInputError::BlockedMoveFunction`, and `config`. The hunk matched touches a critical implementation path, diff changes resource-control logic. Taken together, the hunks suggest the fix spans more than one control path rather than a single isolated check.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/messages.rs | 215 | changes bounds, limits, or capacity handling |
| crates/sui-types/src/messages.rs | 258 | changes bounds, limits, or capacity handling |
| crates/sui-types/src/messages.rs | 645 | changes bounds, limits, or capacity handling |
| crates/sui-types/src/messages.rs | 138 | changes bounds, limits, or capacity handling |

## Code Snippets

## Snippet 1

Context: `crates/sui-types/src/messages.rs:215` (changes bounds, limits, or capacity handling)

Before
```rust
}

/// Send SUI coins to a list of addresses, following a list of amounts.
/// only for SUI coin and does not require a separate gas coin object.
```
After
```rust
}

impl PayAllSui {
    pub fn validity_check(
        &self,
        config: &ProtocolConfig,
        gas_payment: &ObjectRef,
    ) -> UserInputResult {
```

## Snippet 2

Context: `crates/sui-types/src/messages.rs:258` (changes bounds, limits, or capacity handling)

Before
```rust
}

/// Pay each recipient the corresponding amount using the input coins
#[derive(Debug, PartialEq, Eq, Hash, Clone, Serialize, Deserialize)]
```
After
```rust
}

impl PaySui {
    pub fn validity_check(
        &self,
        config: &ProtocolConfig,
        gas_payment: &ObjectRef,
    ) -> UserInputResult {
```

## Snippet 3

Context: `crates/sui-types/src/messages.rs:645` (changes bounds, limits, or capacity handling)

Before
```rust
));
                fp_ensure!(!is_blocked, UserInputError::BlockedMoveFunction);
            }
            Command::TransferObjects(_, _)
            | Command::SplitCoin(_, _)
            | Command::MergeCoins(_, _)
            | Command::Publish(_) => (),
        };
```
After
```rust
));
                fp_ensure!(!is_blocked, UserInputError::BlockedMoveFunction);
                let mut type_arguments_count = 0;
                for tag in call.type_arguments.iter() {
                    type_arguments_count +=
                        type_tag_validity_check(tag, config, 1, type_arguments_count)?;
                    fp_ensure!(
                        type_arguments_count < config.max_type_arguments() as usize,
```

## Snippet 4

Context: `crates/sui-types/src/messages.rs:138` (changes bounds, limits, or capacity handling)

Before
```rust
}

#[serde_as]
#[derive(Debug, PartialEq, Eq, Hash, Clone, Serialize, Deserialize)]
```
After
```rust
}

impl MoveCall {
    pub fn validity_check(&self, config: &ProtocolConfig) -> UserInputResult {
        let is_blocked = BLOCKED_MOVE_FUNCTIONS.contains(&(
            self.package,
            self.module.as_str(),
            self.function.as_str(),
```

# Fix Pattern

The fix pattern is to tighten the sensitive transaction-processing control path so the key invariant is enforced before downstream work continues.

## How It Was Fixed

The patch appears to tighten the critical transaction-processing path so the relevant invariant is enforced before downstream work continues.

# Why It Matters

1. The selected hunks affect a sensitive transaction-processing path, so even a small invariant mistake can have wider operational consequences.

2. The exact exploitability is not fully explicit from the patch alone, but the control path is important enough to justify follow-up review.

# Evidence Notes

This finding is grounded in `crates/sui-types/src/messages.rs`, `crates/sui-types/src/messages.rs`, `crates/sui-types/src/messages.rs`, `crates/sui-types/src/messages.rs`. The selected hunks were prioritized because they matched: touches a critical implementation path, diff changes runtime guards or failure handling, diff changes resource-control logic. Nearby test changes increase confidence that the patch targeted a real behavior change. Phase 3 also reviewed nearby historical project context from `crates/sui-types/src/object.rs`, `crates/sui-types/src/error.rs`. Agent-backed phase 3 failed and the report fell back to heuristic rendering: codex exec failed: "file": "crates/sui-types/src/error.rs", "role": "fp_ensure macro turns failed validation predicates into user input errors." "rationale": "The patch adds runtime validity checks on transaction message structures using ProtocolConfig limits and returns UserInputError::SizeLimitExceeded before downstream authority or execution work continues. The evidence supports a resource-control hardening in a critical transaction-processing path, not state corruption. The patch does not by itself prove a concrete exploit, consensus break, or successful denial of service, but it clearly tightens security-relevant input bounds.", <div class="data"><div class="main-wrapper" role="main"><div class="main-content"><noscript><div class="h2"><span id="challenge-error-text">Enable JavaScript and cookies to continue</span></div></noscript></div></div><script>(function(){window._cf_chl_opt = {cFPWv: 'g',cH: '1RVdKyg4LenDYMz.HSz76_OfpVofuZwNlljVu2MrazI-1777033874-1.2.1.1-ornPmVQigoVAqcGZcmX90kJnjE7_u47aNycNRuz6nNLm9D.mIuLCsHMg2dedAuLQ',cITimeS: '1777033874',cRay: '9f151fb69a1b6e1e',cTplB: '0',cTplC:1,cTplO:0,cTplV:5,cType: 'managed',cUPMDTk:"/backend-api/codex/analytics-events/events?__cf_chl_tk=JoMRQ8hNIcHQpF8UacUt0B4yK6TrTRKdiAxcikU2Ung-1777033874-1.0.1.1-QbL0n1fwPBAX3mFX8o_Yug.RWfw8W7yhx8fFNoz6Pxo",cvId: '3',cZone: 'chatgpt.com',fa:"/backend-api/codex/analytics-events/events?__cf_chl_f_tk=JoMRQ8hNIcHQpF8UacUt0B4yK6TrTRKdiAxcikU2Ung-1777033874-1.0.1.1-QbL0n1fwPBAX3mFX8o_Yug.RWfw8W7yhx8fFNoz6Pxo",md: '4QMNqaUXVuTANqlPfZqXlKuuWthCE2eTqZxehRIiTds-1777033874-1.2.1.1-_5q40FJM3Emlbi4EhjIX9mrLJCQzNWRY9jXSWeIUcI6K4xqQj56IFnhKGy.UgKFlTCpaswmgfnjDPXJGsW2w3fpjXxcRGdU83IzvRarMJmdlG5UADV_Gdrg2VguZhreNetwvPTisJ2A.FOrIX.TghU29jRonKPMA4BdlXfYYLrK3GN9MGu8ydBhFYLgzTkFmpSI_aNDIft.7HE.IMCuVtzfhGyof1hDikmR_jj5EnY8KYwZQAAYnYOIxv0r7qdNbEXt8ZxyDac7R03OmJKfwXywEqvNmBOJ8DKwapUJ71__MW6IKxta1Jw4Xi.MkII6HXstm2uG9bFmh7YZIkXEWApGaVmR_R4yAc0QmCloQZKvwtjOEu4Hz0oretmOA1q_.08rGbE8y3l_es7w9pedacUKrFb_czenJbp1hDxmxj3ndnxE3RKlOu6lgNvwfJvKaWQ5OAP3vypEx2n6Hxo5C7tk6SAw2s.GnhNwqIW4Ya0j_TjXC79c43NdxcabacHqb.rmBIONwGitgUaHIU8s8axkdVTWpQaVSlKaKdVXvCaQOnAc8beKLI6LDekThjZjzEG_Skrs6PaOL.h0vBy4r7ZJnlefCSlbuk3qt1ckePWzorIzDE4uHTqGLnv7KkL_l0p_v_VJnkCI6mRleIV1Oq8ml8Xv6I2DtKEz9dob2rqX5YZRHj2NsSEDMhva47bxL0m4FqckFXgAsHKvA2xTdYMT8CRFGRj4SM_smH0LNsVhdRsCPIi4DjtGcKdB0vnqZpCiNG569qIIlvy2H5qS3SRhl.EOxtgWyTpfNSFuqf1k8ktCLBRmbZ_wCErXE6BmjUwhGPPBQ9x5PfOxupPPmmbVZ_3QiDwNK.pvm7hru7CSl6.zgOXHF_88Z3oJgILHfdXa38OPIHdD8UOcWrByIwhVIVRUKowQPU_gmi48E6AmBj3XvIzfuTkeM7I5e6F3.xf_78NR2fgyodhDrL8_qqRA_waZcJI5cnQ5aqvVjzR7CnVJoZcSP3AwOf0usRgLdKArwgMFnqFdNROqPCKd4vKHDGH6cen72RTK9Y6VqeIY',mdrd: 'o9nTLIs0pMpl45RHJmGtF.ZvQ2Le0aY9Ez30NiU_Ffc-1777033874-1.2.1.1-Mbu8cVb3BgYYPl8XieJOnWHzdgQjkh6CRYmmO6q7B.lIsJydxr994UaJ_fEpnvBRRgo2clPPNShg5UaS5JOABvAhrvExOzlwyPFQ5oXTgVpereD.y8lhaLakb4zSC46aBf9z7XpRGqIBARTURQe_Es_7naYqVceOGXYghiSs3tSFifAI7.VCnKR1PVNRswX0B7LwZN4SoaaHBXAFCqnutfIxne_S49Ub3JBQENMrvu5tUFNwcWrPcfqTbFakYHClxATksOotl9sHozlnqGJZqKTY58PqUugyvrey8O.Cyl3q8vU9nz.aw1tqRVOEUFnEfTECTm.NQR.gbR_HUqFkafFW3FZp8vWKoY3ziK59S1jxfGjYcEAFu8x8Tf243F9iqs8p5LQhHEikkp71RifDpTOZgzRmY5M6mFaMbyJuHPVsuBjNUalZMI9lqR2s3BWk5q3qjlimsLL3cxdkJu7fbT46sd0EadDyyuKqBF5hlhh6qBs9IHiLNatf0Plvd_.8B1LCMeLwGTj5ZFo3laimv6icRHVxkb4xbMPEpa0zDrXJHdayEc3cfaalv2xf4u1kQPwFCCCw5ItZlTBQdt3qslgMA6bE3p7ny_nkKhCU0wt5ihuYEWj4YfMjVjONPIO_XXFGCz8sGiSXKV07J4hq_zoHolUFjNkkCsuP3yZNJH9iIvMDfGdm4K1ztLFxnuhBDHcdZH6MaWtl5f5qwQHhWnyg2w6LB.sdm_AHT63FDi_AWwaCH2JLft8KYkkZD8.qTgV8g9eGpagBNmBU0htxsI3QLca99bG.OSZRU9pp0olb6Glq5UVbvu7iT6mVWLmywFhGbUejoX3MKN.sAYhlUGjqL35PPdV73IlvpaxMcjaxBg1nj6lhg_xSmApKBkH0NNO.Z7H61mHJVsLic_UG3A8mATm9V.NtVlnmbmiZ54x8BrBU4ok.Nvzpu.LdNn4Y5NAnIgUkh8QP9eV3Z5iDeTXeSQpD5NEE3Z9EGVgFrbUCphuvTFUseE00wTPnptSY0FoyCCegeCZ5QyB7_onRLIUXLNeZhZ340vZDnY2gu0Ud6jTk2isg11potEs2WWfDIXRuB5vhqiBw2Q9KryJ7lOcZA.JriEZkqs5wuXXsudDL5U7eTGomZcEtAJmoFRheCD2OkdJkXKsVK3KUnr8VIao30xkU96HUUiCfwquQPG_SHW2GUXFmT.7Nhi0YGZSqnQ3tjf_rn4_iHdIr3TFebXqRak5NeiQTI9sotBN3G9E5Ld88dqIx7gYjUz0mBKu1gRhpNBDX.rIa7RG7VcyCsyWkeFxy2s95SaEu1jrCiriXUmxWuIhpvXUnBTz6IorePgvhGRj76WhbgiFVqahUJduSOkYi5YgcfoChvCe6ekCbSaaUVoIqoJPL8.gPYCmK1ARdtB4rx8nmht60VAUDaH1YJXvmgxFbNskIDKrC2T1K2hO7jAD4XggYQ4aVVhAexOQNhWhIoEzEl_GVe8n5dZN0W7VVPhk9m6r_rFkJ5UqKJ4UED5jVk.ygXDRXvDxlyDNqmBES0SW1ayYPCuh1n6xBIKK86a6wDvf39P_rEURX3HTMXBjQF8Nyqf02v5aww8k8IeS_jSFf_uNs4Yr4fI0zqK4NyLq2yT3hZhRyfB4J3194keKs9wTnY9UmX.GCeivQksqwvMoYpgJgRlKin28qg7rOB4KBt0xH_V4d4R.OYHYiW4r_9HXcZu_fqKOtdGsKwx6rLuluj2Mmplp6Upc93K9eSn_zNhYfppnjqfRWxHuRSQWhjprbNxSSYset4xMaZqfVEmnFFLbEGWFMIHVSP0AgXEDM6XNB64gwZiLVEEZ5jUHsM_S7yz655Vfjei6IDpVJncBs1_Zhx3hGit9abTiKJugZkRvfJ_o2aunbjJwHNy8G83uJ1PQQbYntQMpu7b47dG3.Ifdbri.S0dCmSnMFwV3lMN_fRlX.8AozVM2KsknEVjhlkNEQOY48dsDse.U0IIDvTzwnPnOnrxeoae6Tu9WcPX5XH37dXqOYiAoxzl6e2Pwuk4trLJYaR3..Cp2fHwNZhiQTmctHgPQfjEsZG4dCIHMHqn3Yx6kQL59IoaLijZzGR_AXeIWhp6WAdHkxBGBs.QJxvAWsvvZA34B.n1yAedPRyvktocoph3QC3QtMLin23DHBYc_JTdN3RQOpPU0bWGzYzhQ2Pm9Rkzzop73HOX2SBnjJ4qbPNoiF.1SuwTyGzRrq8au69pBERZihNON6TzQOtBbN1s.BLabahfoGIFm4Bug5jp4U93.VPb8Ooui69xtIBVlLCA7iLKkyV2aTFwg2zs79sn1VZMy1B3WSBDO5MdlaOAl_HoZJgeouLS61HQf17rxQNDfy05dNPGpWpOLiB2XvJ8V5XYjXINFr51TVubSZbeHvRz5Nijh0TvMdRk1bNtb098dq3XrrXmKPO0luKMNcYLYtEuRwhqTz33ByB26e0fAY6fKcA5OzlIK_GNxEc21U.uhy8kLMz2vO0TYIbMPDPbEhq7D.2EXKQAJCGzaQfFXiXC3su7vsAdwJKkEo5_mnO09VZjx7yX9Pap8YtoqLrzyFFrGIBc.vuA6Do2Ax1LrTSnKOfZLzzYGgm00Hr1I4VJbY0XpCSyhALxJNUQ8Rv7kjZjNRbOkQnW_SbQIc.a381VkmWB9.Vjf1oh9Ba.K.BeR00v133NRjmkbO7JiVl5iFiiRHbbE_usipApGCRUZPk3bqU1QL1hOZyPU_NGdkr1EnT7VzXOmJG2dK7_k2g1r38.u11P8sZtizxZcHqpiDKp5Gn_1OylrVyLyeXPqW',};var a = document.createElement('script');a.src = '/cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray=9f151fb69a1b6e1e';window._cf_chl_opt.cOgUHash = location.hash === '' && location.href.indexOf('#') !== -1 ? '#' : location.hash;window._cf_chl_opt.cOgUQuery = location.search === '' && location.href.slice(0, location.href.length - window._cf_chl_opt.cOgUHash.length).indexOf('?') !== -1 ? '?' : location.search;if (window.history && window.history.replaceState) {var ogU = location.pathname + window._cf_chl_opt.cOgUQuery + window._cf_chl_opt.cOgUHash;history.replaceState(null, null,"/backend-api/codex/analytics-events/events?__cf_chl_rt_tk=JoMRQ8hNIcHQpF8UacUt0B4yK6TrTRKdiAxcikU2Ung-1777033874-1.0.1.1-QbL0n1fwPBAX3mFX8o_Yug.RWfw8W7yhx8fFNoz6Pxo"+ window._cf_chl_opt.cOgUHash);a.onload = function() {history.replaceState(null, null, ogU);}}document.getElementsByTagName('head')[0].appendChild(a);}());</script></div> ERROR: Selected model is at capacity. Please try a different model. ERROR: Selected model is at capacity. Please try a different model..

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion`
Final impact type: `denial-of-service, resource-exhaustion`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, input-validation, resource-limits, resource-exhaustion, denial-of-service`

The supplied patch evidence supports security hardening, not a concrete security fix. The commit adds ProtocolConfig-backed size and validity checks on externally supplied transaction components, including coin vectors and Move type arguments, and rejects oversized input with UserInputError::SizeLimitExceeded before downstream transaction processing. This is security-relevant resource-control hardening in a blockchain transaction path, but the evidence does not prove state corruption, consensus failure, or an exploitable vulnerability.

## Security Evidence

1. Commit description states it adds size limits for components of input transactions.
2. PaySui and PayAllSui validity checks reject empty coin lists, unexpected gas payment objects, and excessive coin counts.
3. MoveCall and programmable transaction command paths now validate type argument count and depth against ProtocolConfig limits.
4. Failures return user input errors before transaction execution or authority processing continues.
5. Tests were updated and reportedly failed under the old implementation when hitting the new limits.

## Missing Evidence

1. No advisory, CVE, incident report, or exploit scenario is provided.
2. No evidence shows prior behavior caused state corruption or state-integrity failure.
3. No proof is provided that unbounded inputs caused validator crashes, consensus faults, or sustained denial of service.
4. The exact external exposure path and attacker cost are not established from the patch alone.

## Claim Boundaries

1. Treat as resource-limit hardening for transaction input validation.
2. Do not claim a confirmed exploitable vulnerability.
3. Do not retain the original state-corruption or state-integrity classification.
4. Do not infer consensus compromise beyond the fact that transaction validation is a critical blockchain path.
