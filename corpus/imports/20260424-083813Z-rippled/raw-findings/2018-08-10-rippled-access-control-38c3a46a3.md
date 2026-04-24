---
case_id: case_20180810_38c3a46a3
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: access-control
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: high
source_quality: high
tags:
  - blockchain-core
  - access-control
  - privilege-misuse
  - rpc
  - multisig
date: 2018-08-10
source_refs:
  - git:38c3a46a337916216a1e3ad481229fe87e07d542
  - "src/ripple/rpc/handlers/Submit.cpp:49"
  - "src/ripple/rpc/handlers/SignHandler.cpp:32"
  - "src/ripple/rpc/handlers/SignFor.cpp:34"
  - "src/ripple/rpc/handlers/SignFor.cpp:51"
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is a confirmed security fix for rippled RPC transaction signing. It adds a default access-control gate to `sign`, `sign_for`, and the `submit` path used for sign-and-submit behavior, rejecting non-admin callers unless signing support is explicitly enabled in configuration. The evidence supports missing access control around server-side signing with caller-provided secrets, but not claims of proven seed theft, intercepted traffic, or transaction forgery.

## Observed Patch Facts

1. In `src/ripple/rpc/handlers/Submit.cpp`, the patch replaces `return RPC::transactionSubmit (` with `if (context.role != Role::ADMIN && !context.app.config().canSign())`.

2. In `src/ripple/rpc/handlers/SignHandler.cpp`, the patch replaces `context.loadType = Resource::feeHighBurdenRPC;` with `if (context.role != Role::ADMIN && !context.app.config().canSign())`.

3. In `src/ripple/rpc/handlers/SignFor.cpp`, the patch replaces `// Bail if multisign is not enabled.` with `if (context.role != Role::ADMIN && !context.app.config().canSign())`.

4. In `src/ripple/rpc/handlers/SignFor.cpp`, the patch replaces `return RPC::transactionSignFor (` with `auto ret = RPC::transactionSignFor (`.

## Project Context

The changed code sits primarily in `src/ripple/rpc/handlers`, `src/ripple/rpc`, which anchors the finding in the `access-control` area of the project. Historical context from `src/ripple/rpc/handlers/SubmitMultiSigned.cpp`, `src/ripple/rpc/handlers/ValidationCreate.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/rpc/handlers/SubmitMultiSigned.cpp`, `src/ripple/rpc/impl/TransactionSign.cpp`. The strongest project-level identifiers around this patch are `Role::ADMIN`, `RPC::make_error`, `role`, and `RPC::transactionSubmit`.

## Before/After Behavior

Before the patch, `doSign` entered the signing flow without the added `Role::ADMIN` or `config().canSign()` gate; `doSignFor` proceeded toward `RPC::transactionSignFor(...)` after its existing feature checks; and `doSubmit` called `RPC::transactionSubmit(...)` in the no-`tx_blob` branch, identified by the commit and mapper as sign-and-submit behavior. After the patch, these paths reject callers when `context.role != Role::ADMIN && !context.app.config().canSign()` by returning `rpcNOT_SUPPORTED` with "Signing is not supported by this server." Successful `sign_for` responses also receive a deprecation warning. The supplied evidence does not show restriction of ordinary submission with a pre-signed `tx_blob`.

# Root Cause

The root cause was that RPC handlers capable of using caller-provided seed or secret material for transaction signing were reachable without a default handler-level authorization check requiring admin role or explicit server-side signing opt-in.

## Walkthrough

1. The affected entry points are `doSubmit` in `src/ripple/rpc/handlers/Submit.cpp`, `doSign` in `src/ripple/rpc/handlers/SignHandler.cpp`, and `doSignFor` in `src/ripple/rpc/handlers/SignFor.cpp`.

2. The commit message states that `sign`, `sign_for`, and `submit` can sign or sign-and-submit transactions when given a seed, and that these commands may be exposed through command line, WebSocket, or RPC interfaces depending on configuration.

3. The pre-patch evidence for `doSign` shows the handler continuing into signing-related processing without the newly added admin-or-config gate.

4. The pre-patch evidence for `doSignFor` shows the handler proceeding toward `RPC::transactionSignFor(...)`; nearby comments describe parameters including a signing account secret.

5. The pre-patch evidence for `doSubmit` shows the no-`tx_blob` branch calling `RPC::transactionSubmit(...)`, which the commit describes as the submit mode that can sign-and-submit.

6. The patch adds the same authorization/configuration check before each sensitive operation and returns `rpcNOT_SUPPORTED` when the check fails.

7. The patch also adds a deprecation warning to successful `sign_for` responses, but that warning is secondary to the access-control change.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/rpc/handlers/Submit.cpp | 49 | Blocks non-admin, non-opt-in submit requests that omit tx_blob and therefore enter sign-and-submit behavior. |
| src/ripple/rpc/handlers/SignHandler.cpp | 32 | Blocks non-admin, non-opt-in direct sign requests that accept a seed/secret and produce a signed transaction. |
| src/ripple/rpc/handlers/SignFor.cpp | 34 | Blocks non-admin, non-opt-in multisign sign_for requests that accept a signing account secret. |
| src/ripple/rpc/handlers/SignFor.cpp | 51 | Adds deprecation warning to successful sign_for responses when the gated signing path is available. |

## Code Snippets

## Snippet 1

Context: `src/ripple/rpc/handlers/Submit.cpp:49` (changes an authorization or privilege gate)

Before
```cpp
auto const failType = getFailHard (context);

        return RPC::transactionSubmit (
        context.params,
        failType,
        context.role,
        context.ledgerMaster.getValidatedLedgerAge(),
        context.app,
```
After
```cpp
auto const failType = getFailHard (context);

        if (context.role != Role::ADMIN && !context.app.config().canSign())
            return RPC::make_error (rpcNOT_SUPPORTED,
                "Signing is not supported by this server.");

        auto ret = RPC::transactionSubmit (
            context.params, failType, context.role,
```

## Snippet 2

Context: `src/ripple/rpc/handlers/SignHandler.cpp:32` (changes an authorization or privilege gate)

Before
```cpp
Json::Value doSign (RPC::Context& context)
{
    context.loadType = Resource::feeHighBurdenRPC;
    NetworkOPs::FailHard const failType =
```
After
```cpp
Json::Value doSign (RPC::Context& context)
{
    if (context.role != Role::ADMIN && !context.app.config().canSign())
    {
        return RPC::make_error (rpcNOT_SUPPORTED,
            "Signing is not supported by this server.");
    }
```

## Snippet 3

Context: `src/ripple/rpc/handlers/SignFor.cpp:34` (changes an authorization or privilege gate)

Before
```cpp
Json::Value doSignFor (RPC::Context& context)
{
    // Bail if multisign is not enabled.
    if (! context.app.getLedgerMaster().getValidatedRules().
```
After
```cpp
Json::Value doSignFor (RPC::Context& context)
{
    if (context.role != Role::ADMIN && !context.app.config().canSign())
    {
        return RPC::make_error (rpcNOT_SUPPORTED,
            "Signing is not supported by this server.");
    }
```

## Snippet 4

Context: `src/ripple/rpc/handlers/SignFor.cpp:51` (changes an authorization or privilege gate)

Before
```cpp
auto const failType = NetworkOPs::doFailHard (failHard);

    return RPC::transactionSignFor (
        context.params,
        failType,
        context.role,
        context.ledgerMaster.getValidatedLedgerAge(),
        context.app);
```
After
```cpp
auto const failType = NetworkOPs::doFailHard (failHard);

    auto ret = RPC::transactionSignFor (
        context.params, failType, context.role,
        context.ledgerMaster.getValidatedLedgerAge(), context.app);

    ret[jss::deprecated] = "This command has been deprecated and will be "
                           "removed in a future version of the server. Please "
```

# Fix Pattern

Add a handler-boundary authorization and explicit-configuration gate before invoking server-side transaction signing or sign-and-submit helpers. Apply the same policy across equivalent signing entry points.

## How It Was Fixed

`Submit.cpp` now blocks non-admin, non-opt-in requests in the no-`tx_blob` sign-and-submit branch before `RPC::transactionSubmit(...)`. `SignHandler.cpp` now blocks non-admin, non-opt-in direct `sign` requests at the start of `doSign`. `SignFor.cpp` now blocks non-admin, non-opt-in `sign_for` requests at the start of `doSignFor` and adds a deprecation field to successful responses.

# Why It Matters

1. Prevents default non-admin access to seed-handling signing commands.

2. Makes server-side signing an administrative or explicit operator-enabled capability.

3. Reduces exposure of deprecated signing functionality through configured RPC, WebSocket, or CLI access paths.

4. Does not prove that seeds were intercepted or that forged transactions occurred.

# Evidence Notes

The strongest evidence is the repeated addition of `if (context.role != Role::ADMIN && !context.app.config().canSign())` followed by `RPC::make_error(rpcNOT_SUPPORTED, "Signing is not supported by this server.")` in the three signing-related handlers. The commit message explicitly identifies security implications from divulging seeds to the server, possible clear-text transport, and command-line exposure. Claims should remain bounded: the evidence does not prove universal remote exposure, exploitation, seed interception, transaction forgery, or removal of signing support. Protocol security invariant: RPC handlers that accept account seed or secret material to produce or submit signed transactions must not be available to non-admin callers by default; server-side signing should require administrative access or explicit operator opt-in. Verification notes: The patch does not prove that seeds were intercepted in transit. The patch does not prove that all deployments exposed these RPC commands remotely or without authentication. The patch does not show transaction forgery unless a caller supplies or obtains a valid seed. The patch does not appear to restrict ordinary submit with a pre-signed tx_blob. The patch is a default access restriction with an operator opt-in, not complete removal of server-side signing. Access-control checks are shown in `Submit.cpp`, `SignHandler.cpp`, and `SignFor.cpp`. The ordinary pre-signed `tx_blob` submit path is not shown as restricted by the provided evidence. The deprecation warning is support behavior, not the root security fix. Operator opt-in through `config().canSign()` means the risky functionality can still be enabled deliberately. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied commit message and patch evidence strongly support a security fix: RPC handlers that accept account seed/secret material for transaction signing were changed to reject non-admin callers unless server-side signing is explicitly enabled. The fix is an access-control restriction around sensitive signing commands, with explicit security rationale in the commit metadata. The finding is appropriately bounded and should remain in the corpus.

## Security Evidence

1. Commit message explicitly describes security implications of divulging account seeds to the server and possible clear-text or command-line exposure.
2. `doSign`, `doSignFor`, and sign-and-submit `doSubmit` paths now check `context.role != Role::ADMIN && !context.app.config().canSign()` before signing behavior.
3. Rejected callers receive `rpcNOT_SUPPORTED` with "Signing is not supported by this server."
4. The affected handlers are RPC transaction-signing entry points whose comments and commit text identify seed/secret parameters.

## Missing Evidence

1. No evidence proves actual seed theft, interception, or transaction forgery occurred.
2. No evidence proves all deployments exposed these commands remotely or unauthenticated.
3. No full diff is provided for the configuration implementation of `canSign()` beyond the shown call sites.

## Claim Boundaries

1. This validates missing/default-insufficient access control for server-side signing commands.
2. This does not validate claims of successful exploitation or compromised funds.
3. This does not claim ordinary pre-signed transaction submission was blocked.
4. The risky functionality remains available to admins or when explicitly enabled by configuration.
