---
case_id: case_20230421_b149ca0b9b
project: sui
domain: infrastructure
render_mode: heuristic
context_depth: deep
phase3_security_verdict: not-reviewed
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2023-04-21
source_refs:
  - git:b149ca0b9bcf57c3fdd68a827982f226796c7d22
  - "apps/wallet/src/background/connections/ContentScriptConnection.ts:169"
  - "apps/wallet/playwright.config.ts:50"
bug_class: wallet-content-script-message-validation
impact_type:
  - unauthorized-wallet-data-access-prevention
  - message-boundary-hardening
confidence: medium
tags:
  - wallet
  - browser-extension
  - content-script
  - message-validation
  - permission-boundary
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Wallet-ext: test site-cs messaging (#9444) looks like a focused hardening change in the storage path of sui. The strongest evidence spans `apps/wallet/src/background/connections/ContentScriptConnection.ts` and `apps/wallet/playwright.config.ts`. The affected state likely includes `command`, `port`, and `process`. The visible hunks are security-relevant, but the exact exploit path is not explicit enough to name more precisely. Additional project context from `apps/wallet/webpack.config.ts`, `apps/wallet/src/background/connections/index.ts` was used to anchor the surrounding module behavior. Commit context: ## Description * make sure when a site with no permissions can not access wallet data * make sure sending messages expected from wallet popup from sites are ignored * also fixes tests failing on create and import flows * updated cs connection to throw error when it receives unknown messages * adds demo dapp to test wallet interface * enables wallet e2e tests * updates wallet e2e tests to run against local network instead of the default closes APPS-603.

## Observed Patch Facts

1. In `apps/wallet/src/background/connections/ContentScriptConnection.ts`, the patch adds `} else {`.

2. In `apps/wallet/playwright.config.ts`, the patch replaces `};` with `webServer: [`.

## Project Context

The changed code sits primarily in `apps/wallet/src/background/connections`, `apps/wallet/src/background`, `apps/wallet`, which anchors the finding in the `storage` area of the project. Historical context from `apps/wallet/webpack.config.ts`, `apps/wallet/src/background/connections/index.ts` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `apps/wallet/src/background/keyring/VaultStorage.ts`, `apps/wallet/src/background/FeatureGating.ts`. The strongest project-level identifiers around this patch are `command`, `port`, `process`, and `catch`. Nearby tests or test-like files include `apps/wallet/tests/sites-to-cs-messaging.spec.ts`, `apps/wallet/tests/lock.spec.ts`.

## Before/After Behavior

1. After the patch, `apps/wallet/src/background/connections/ContentScriptConnection.ts` now includes `} else {` where no equivalent behavior was previously visible in the extracted snippet.

2. Before the patch, `apps/wallet/playwright.config.ts` relied on `};`. After the patch, it instead uses `webServer: [`.

3. In deep mode, the generator also traced related identifiers into `apps/wallet/src/background/keyring/VaultStorage.ts`, `apps/wallet/src/background/FeatureGating.ts` to verify how the changed path fits into the wider subsystem behavior.

# Root Cause

The issue appears to sit at the boundary between `apps/wallet/src/background/connections/ContentScriptConnection.ts` and `apps/wallet/playwright.config.ts`. The likely root cause was an under-protected control path whose invariants were not enforced strongly enough.

## Walkthrough

1. In `apps/wallet/src/background/connections/ContentScriptConnection.ts:169`, the selected hunk changes a sensitive control or state-update path. Notable identifiers in this step include `catch`, `throw`, and `Error`. The hunk matched touches a critical implementation path.

2. In `apps/wallet/playwright.config.ts:50`, the selected hunk changes bounds, limits, or capacity handling. Notable identifiers in this step include `command`, `port`, and `process`. The hunk matched diff changes resource-control logic, diff changes consensus or validator logic. Taken together, the hunks suggest the fix spans more than one control path rather than a single isolated check.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| apps/wallet/src/background/connections/ContentScriptConnection.ts | 169 | changes a sensitive control or state-update path |
| apps/wallet/playwright.config.ts | 50 | changes bounds, limits, or capacity handling |

## Code Snippets

## Snippet 1

Context: `apps/wallet/src/background/connections/ContentScriptConnection.ts:169` (changes a sensitive control or state-update path)

Before
```ts
)
                );
            }
        } catch (e) {
```
After
```ts
)
                );
            } else {
                throw new Error(
                    `Unknown message, ${JSON.stringify(msg.payload)}`
                );
            }
        } catch (e) {
```

## Snippet 2

Context: `apps/wallet/playwright.config.ts:50` (changes bounds, limits, or capacity handling)

Before
```ts
},
    ],
};
```
After
```ts
},
    ],
    webServer: [
        {
            command: 'pnpm demoApp:dev',
            port: 5181,
            timeout: 30 * 1000,
            reuseExistingServer: !process.env.CI,
```

# Fix Pattern

The fix pattern is to tighten the sensitive storage control path so the key invariant is enforced before downstream work continues.

## How It Was Fixed

The patch appears to tighten the critical storage path so the relevant invariant is enforced before downstream work continues.

# Why It Matters

1. The selected hunks affect a sensitive storage path, so even a small invariant mistake can have wider operational consequences.

2. The exact exploitability is not fully explicit from the patch alone, but the control path is important enough to justify follow-up review.

# Evidence Notes

This finding is grounded in `apps/wallet/src/background/connections/ContentScriptConnection.ts`, `apps/wallet/playwright.config.ts`. The selected hunks were prioritized because they matched: touches a critical implementation path, diff changes resource-control logic, diff changes consensus or validator logic. Nearby test changes increase confidence that the patch targeted a real behavior change. Phase 3 also reviewed nearby historical project context from `apps/wallet/webpack.config.ts`, `apps/wallet/src/background/connections/index.ts`. Agent-backed phase 3 failed and the report fell back to heuristic rendering: Invalid \escape: line 1 column 950 (char 949).

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `wallet-content-script-message-validation`
Final impact type: `unauthorized-wallet-data-access-prevention, message-boundary-hardening`
Final confidence: `medium`
Final tags: `wallet, browser-extension, content-script, message-validation, permission-boundary`

The finding should be retained, but only as wallet/message-boundary hardening. The commit metadata explicitly says sites without permissions must not access wallet data and that site-originated messages expected from the wallet popup are ignored. The visible implementation evidence shows ContentScriptConnection now rejects unknown messages, which supports tightening an exposed extension messaging boundary. However, the supplied patch evidence does not show the full permission check or a concrete exploit path, and the generated storage/consensus framing is misleading.

## Security Evidence

1. Commit body states that sites with no permissions cannot access wallet data after the change.
2. Commit body states that wallet-popup messages sent from sites are ignored.
3. ContentScriptConnection adds an explicit error path for unknown message payloads.
4. Changed tests include site-to-content-script messaging coverage, indicating regression coverage around the wallet interface boundary.

## Missing Evidence

1. No full before/after code for the permission decision is supplied.
2. No test assertion excerpts show the exact no-permission wallet-data behavior.
3. The visible implementation hunk only shows unknown-message rejection, not the wallet data access path itself.
4. No advisory, issue details, or exploit scenario are provided.

## Claim Boundaries

1. Do not classify this as a storage or consensus issue based on the supplied evidence.
2. Do not claim proven wallet data theft or a concrete exploitable vulnerability.
3. The Playwright webServer/local validator changes are test infrastructure, not security evidence by themselves.
4. The supported claim is conservative hardening of wallet extension site/content-script message handling.
