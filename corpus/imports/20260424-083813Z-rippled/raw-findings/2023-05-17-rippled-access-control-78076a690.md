---
case_id: case_20230517_78076a690
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: access-control
source_quality: medium
date: 2023-05-17
source_refs:
  - git:78076a69038be72102bcf90076f69f79ce78987c
  - "src/ripple/rpc/handlers/AccountObjects.cpp:174"
  - "src/ripple/rpc/handlers/AccountObjects.cpp:61"
  - "src/ripple/rpc/handlers/NoRippleCheck.cpp:93"
  - "src/ripple/rpc/handlers/GatewayBalances.cpp:70"
bug_class: improper-input-acceptance
impact_type:
  - credential-exposure-risk
confidence: medium
tags:
  - rpc
  - input-validation
  - secret-handling
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The change hardens rippled RPC account parsing by removing legacy `RPC::accountFromString` handling from multiple account-query handlers and requiring `parseBase58<AccountID>` instead. The evidence supports a security-hardening finding around preventing secret-like material from being accepted in account identifier fields, but it does not establish an authorization bypass, state-changing exploit, or proven credential disclosure.

## Observed Patch Facts

1. In `src/ripple/rpc/handlers/AccountObjects.cpp`, the patch replaces `AccountID accountID;` with `auto const id = parseBase58<AccountID>(params[jss::account].asString());`.

2. In `src/ripple/rpc/handlers/AccountObjects.cpp`, the patch replaces `AccountID accountID;` with `auto id = parseBase58<AccountID>(params[jss::account].asString());`.

3. In `src/ripple/rpc/handlers/NoRippleCheck.cpp`, the patch replaces `std::string strIdent(params[jss::account].asString());` with `auto id = parseBase58<AccountID>(params[jss::account].asString());`.

4. In `src/ripple/rpc/handlers/GatewayBalances.cpp`, the patch replaces `bool const bStrict =` with `auto id = parseBase58<AccountID>(strIdent);`.

## Project Context

The changed code sits primarily in `src/ripple/rpc/handlers`, `src/ripple/rpc`, which anchors the finding in the `access-control` area of the project. Historical context from `src/ripple/rpc/handlers/AccountOffers.cpp`, `src/ripple/rpc/handlers/AccountLines.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/rpc/handlers/AccountOffers.cpp`, `src/ripple/rpc/handlers/AccountLines.cpp`. The strongest project-level identifiers around this patch are `jss::account`, `auto`, `RPC::accountFromString`, and `result`.

## Before/After Behavior

Before the patch, handlers such as `doAccountObjects`, `doAccountNFTs`, `doNoRippleCheck`, and `doGatewayBalances` passed caller-supplied account identifiers to `RPC::accountFromString`, which the commit message says could interpret seeds, public keys, or passphrases as account-like input. After the patch, these handlers parse the value with `parseBase58<AccountID>` and return or inject `rpcACT_MALFORMED` when parsing fails. `GatewayBalances` also removes the legacy `strict` option path.

# Root Cause

The root cause was permissive legacy parsing at RPC account-identifier boundaries: fields intended for public account IDs were routed through a parser that could treat non-account secret-like strings as valid legacy inputs instead of rejecting them as malformed.

## Walkthrough

1. A caller supplies an `account` value, or in `GatewayBalances` an `account` or `ident` value, to an RPC account-query handler.

2. Before the patch, affected handlers constructed an `AccountID` through `RPC::accountFromString`, sometimes influenced by a `strict` option.

3. The commit message states that this legacy parser allowed seeds and public keys to be used where accounts were expected.

4. The patched handlers call `parseBase58<AccountID>` on the supplied account identifier instead.

5. If parsing fails, the handler returns or injects `rpcACT_MALFORMED` and stops processing.

6. Only successfully parsed public account IDs are used for later account-specific logic.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/rpc/handlers/AccountObjects.cpp | 174 | `doAccountObjects` now rejects non-AccountID `account` values instead of using `RPC::accountFromString` legacy parsing. |
| src/ripple/rpc/handlers/AccountObjects.cpp | 61 | `doAccountNFTs` now requires `account` to parse as `AccountID` and returns `rpcACT_MALFORMED` otherwise. |
| src/ripple/rpc/handlers/NoRippleCheck.cpp | 93 | `doNoRippleCheck` now validates `account` as a base58 account ID before continuing. |
| src/ripple/rpc/handlers/GatewayBalances.cpp | 70 | `doGatewayBalances` removes `strict`/`accountFromString` handling and accepts only parsed account IDs from `account` or `ident`. |

## Code Snippets

## Snippet 1

Context: `src/ripple/rpc/handlers/AccountObjects.cpp:174` (changes a sensitive control or state-update path)

Before
```cpp
return result;

    AccountID accountID;
    {
        auto const strIdent = params[jss::account].asString();
        if (auto jv = RPC::accountFromString(accountID, strIdent))
        {
            for (auto it = jv.begin(); it != jv.end(); ++it)
```
After
```cpp
return result;

    auto const id = parseBase58<AccountID>(params[jss::account].asString());
    if (!id)
    {
        RPC::inject_error(rpcACT_MALFORMED, result);
        return result;
    }
```

## Snippet 2

Context: `src/ripple/rpc/handlers/AccountObjects.cpp:61` (changes a sensitive control or state-update path)

Before
```cpp
return result;

    AccountID accountID;
    {
        auto const strIdent = params[jss::account].asString();
        if (auto jv = RPC::accountFromString(accountID, strIdent))
        {
            for (auto it = jv.begin(); it != jv.end(); ++it)
```
After
```cpp
return result;

    auto id = parseBase58<AccountID>(params[jss::account].asString());
    if (!id)
    {
        RPC::inject_error(rpcACT_MALFORMED, result);
        return result;
    }
```

## Snippet 3

Context: `src/ripple/rpc/handlers/NoRippleCheck.cpp:93` (changes a sensitive control or state-update path)

Before
```cpp
transactions ? (result[jss::transactions] = Json::arrayValue) : dummy;

    std::string strIdent(params[jss::account].asString());
    AccountID accountID;

    if (auto jv = RPC::accountFromString(accountID, strIdent))
    {
        for (auto it(jv.begin()); it != jv.end(); ++it)
```
After
```cpp
transactions ? (result[jss::transactions] = Json::arrayValue) : dummy;

    auto id = parseBase58<AccountID>(params[jss::account].asString());
    if (!id)
    {
        RPC::inject_error(rpcACT_MALFORMED, result);
        return result;
    }
```

## Snippet 4

Context: `src/ripple/rpc/handlers/GatewayBalances.cpp:70` (changes a sensitive control or state-update path)

Before
```cpp
: params[jss::ident].asString());

    bool const bStrict =
        params.isMember(jss::strict) && params[jss::strict].asBool();

    // Get info on account.
    AccountID accountID;
    auto jvAccepted = RPC::accountFromString(accountID, strIdent, bStrict);
```
After
```cpp
: params[jss::ident].asString());

    // Get info on account.
    auto id = parseBase58<AccountID>(strIdent);
    if (!id)
        return rpcError(rpcACT_MALFORMED);
    auto const accountID{std::move(id.value())};
    context.loadType = Resource::feeHighBurdenRPC;
```

# Fix Pattern

Replace permissive legacy credential-aware parsing at RPC boundaries with strict account-ID parsing, and remove obsolete `strict` controls once non-account identifiers are no longer accepted.

## How It Was Fixed

`AccountObjects.cpp` changed `doAccountObjects` and `doAccountNFTs` from `RPC::accountFromString` to `parseBase58<AccountID>`. `NoRippleCheck.cpp` now validates `params[jss::account].asString()` with `parseBase58<AccountID>`. `GatewayBalances.cpp` removed `bStrict` and `RPC::accountFromString(accountID, strIdent, bStrict)`, then parses the selected identifier directly as an `AccountID` and returns `rpcACT_MALFORMED` on failure.

# Why It Matters

1. Prevents account fields from accepting seeds, passphrases, or public keys where only public account IDs are needed.

2. Reduces the chance that integrations send secret material through RPC paths not intended to receive it.

3. Makes malformed account input fail consistently as `rpcACT_MALFORMED`.

4. The supplied evidence does not prove a concrete leak or exploit path.

# Evidence Notes

The draft's access-control framing is unsupported and should be downgraded. The provided hunks show input parsing changes in RPC handlers, not missing authorization checks or privileged state transitions. The commit message explicitly frames the old behavior as a potential security hole because secrets could be sent to unnecessary places and possibly end up in logs or errors, but the code evidence does not demonstrate an actual disclosure event. Protocol security invariant: RPC parameters that identify accounts should accept only public XRPL account IDs, not seeds, passphrases, or public keys, so secret-like input is rejected as malformed before account-specific processing. Verification notes: No authorization bypass is demonstrated by the patch evidence. No concrete seed disclosure through logs, errors, or responses is shown. No state-changing transaction path is shown as affected. No proof that public keys or seeds let callers access another account's protected data. The change is also a breaking API cleanup, but the security-relevant part is narrower: preventing secret-like inputs in account identifier fields. Code evidence supports the parser replacement from `RPC::accountFromString` to `parseBase58<AccountID>`. Commit text supports the security-hardening rationale around avoiding secret/passphrase acceptance. No evidence shows authorization bypass, protected data access, state-changing behavior, or confirmed credential leakage. Tests are listed as changed, but no specific test assertions were provided in the input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-input-acceptance`
Final impact type: `credential-exposure-risk`
Final confidence: `medium`
Final tags: `rpc, input-validation, secret-handling, security-hardening`

The provided evidence supports retaining this as security hardening, not as a concrete security fix. The commit explicitly frames legacy account parsing as allowing seeds, passphrases, or public keys where only account IDs were needed, and the patch consistently replaces permissive `RPC::accountFromString` handling with `parseBase58<AccountID>` plus malformed-input rejection. However, the evidence does not prove an actual credential leak, authorization bypass, or exploitable privilege misuse, so the original access-control and privilege-misuse framing should be downgraded.

## Security Evidence

1. Commit message says accepting secrets or passphrases in account fields is considered a bug and a potential security hole.
2. Patch changes multiple RPC account handlers to parse only `AccountID` values with `parseBase58<AccountID>`.
3. Invalid non-account input now returns or injects `rpcACT_MALFORMED` instead of being routed through legacy account/seed parsing.
4. The obsolete `strict` option path is removed where account fields are no longer interpreted as seeds.

## Missing Evidence

1. No evidence shows secrets were actually written to logs, errors, or responses.
2. No evidence shows an authorization bypass or access to protected account data.
3. No evidence shows a state-changing transaction path was affected.
4. No specific test assertions are provided to prove the rejected secret/public-key cases.

## Claim Boundaries

1. Keep as security-hardening focused on RPC input validation and secret-handling risk reduction.
2. Do not classify as access-control or privilege-misuse based on the supplied patch.
3. Do not claim confirmed credential disclosure or exploitability.
4. Do not claim that public keys or seeds allowed unauthorized account access.
