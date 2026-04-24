---
case_id: case_20181023_c1a02440d
project: rippled
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2018-10-23
source_refs:
  - git:c1a02440dcb65977daf2575558d80d25fa722d99
  - "src/ripple/core/impl/Config.cpp:467"
  - "src/ripple/app/misc/impl/ValidatorSite.cpp:510"
  - "src/ripple/app/misc/impl/ValidatorSite.cpp:413"
  - "src/ripple/core/impl/Config.cpp:271"
bug_class: validator-list-redirect-scheme-hardening
impact_type:
  - validator-list-source-integrity
confidence: medium
tags:
  - validator-ops
  - validator-list
  - redirect-validation
  - url-scheme-allowlist
  - file-url
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The draft correctly rejects the unsupported replay/signature-validation theory. The grounded change is that validator-site redirects now reject schemes other than `http` and `https` while the commit adds explicit configured `file://` validator-list support. This is plausibly security-relevant hardening around validator-list retrieval, but the provided evidence does not prove a vulnerability, exploit path, validator-list validation bypass, consensus compromise, impersonation, or local-file disclosure.

## Observed Patch Facts

1. In `src/ripple/core/impl/Config.cpp`, the patch replaces `std::ifstream ifsDefault (validatorsFile.native().c_str());` with `boost::system::error_code ec;`.

2. In `src/ripple/app/misc/impl/ValidatorSite.cpp`, the patch replaces `Json::Value` with `void`.

3. In `src/ripple/app/misc/impl/ValidatorSite.cpp`, the patch adds `if (newLocation->pUrl.scheme != "http" &&`.

4. In `src/ripple/core/impl/Config.cpp`, the patch replaces `std::ifstream ifsConfig (CONFIG_FILE.c_str (), std::ios::in);` with `boost::system::error_code ec;`.

## Project Context

The changed code sits primarily in `src/ripple/core/impl`, `src/ripple/core`, `src/ripple/app/misc/impl`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/ripple/core/impl/SNTPClock.cpp`, `src/ripple/core/impl/Workers.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/core/impl/SNTPClock.cpp`, `src/ripple/app/misc/detail/WorkSSL.h`. The strongest project-level identifiers around this patch are `std::string`, `boost::system::error_code`, `std::istreambuf_iterator`, and `std::cerr`.

## Before/After Behavior

Before the patch, the visible redirect code built a new `Site::Resource` from the redirect `location` and incremented `redirCount` without a visible scheme allowlist. After the patch, redirects are rejected unless the parsed scheme is `http` or `https`. Separately, config and validators file reads now use `getFileContents` with explicit error-code checks instead of direct `std::ifstream` stream reads. The commit also adds explicit configured local `file://` validator-list support.

# Root Cause

The strongest grounded issue is a missing redirect scheme restriction in the visible validator-list fetch path. However, the evidence does not establish that this was exploitable or that it caused unauthorized local file reads, validator trust compromise, or bypass of validator-list validation. The file-read changes are robustness and diagnostics, not proven vulnerability fixes.

## Walkthrough

1. The commit adds explicit local `file://` support for configured validator-list sources.

2. The commit text says file-loaded lists are validated the same way as downloaded lists.

3. The redirect path previously created a new resource from the redirect `location` without a visible scheme check in the supplied snippet.

4. The patched redirect path rejects redirected locations unless the scheme is `http` or `https`.

5. This prevents redirects from using non-network schemes in the shown path, including the newly supported `file://` scheme.

6. The Config.cpp changes add explicit read-error handling for config and validators files.

7. No supplied evidence proves that an attacker could control the redirect in a way that produced a concrete security impact.

8. No supplied evidence proves a signature-validation bypass, replay issue, consensus compromise, validator impersonation, or local-file disclosure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/misc/impl/ValidatorSite.cpp | 413 | Rejects validator-site redirects whose new URL scheme is not http or https. |
| src/ripple/app/misc/impl/ValidatorSite.cpp | 510 | Handles fetched validator-list text uniformly, including errors from local or network fetch paths. |
| src/ripple/app/misc/detail/WorkFile.h | 34 | Introduces local file retrieval work item used for file:// validator-list sources. |
| src/ripple/core/impl/Config.cpp | 467 | Reads validators.txt through error-reporting file utility instead of silently parsing an unreadable or empty stream. |
| src/ripple/core/impl/Config.cpp | 271 | Reads the main config file through the same error-reporting file utility. |

## Code Snippets

## Snippet 1

Context: `src/ripple/core/impl/Config.cpp:467` (changes a consensus- or validator-sensitive branch)

Before
```cpp
boost::filesystem::is_symlink (validatorsFile)))
        {
            std::ifstream ifsDefault (validatorsFile.native().c_str());

            std::string data;

            data.assign (
                std::istreambuf_iterator<char>(ifsDefault),
```
After
```cpp
boost::filesystem::is_symlink (validatorsFile)))
        {
            boost::system::error_code ec;
            auto const data = getFileContents(ec, validatorsFile);
            if (ec)
            {
                Throw<std::runtime_error>("Failed to read '" +
                    validatorsFile.string() + "'." +
```

## Snippet 2

Context: `src/ripple/app/misc/impl/ValidatorSite.cpp:510` (changes a consensus- or validator-sensitive branch)

Before
```cpp
}

Json::Value
ValidatorSite::getJson() const
```
After
```cpp
}

void
ValidatorSite::onTextFetch(
    boost::system::error_code const& ec,
    std::string const& res,
    std::size_t siteIdx)
{
```

## Snippet 3

Context: `src/ripple/app/misc/impl/ValidatorSite.cpp:413` (changes a sensitive control or state-update path)

Before
```cpp
std::string(res[field::location]));
        ++sites_[siteIdx].redirCount;
    }
    catch (std::exception &)
```
After
```cpp
std::string(res[field::location]));
        ++sites_[siteIdx].redirCount;
        if (newLocation->pUrl.scheme != "http" &&
            newLocation->pUrl.scheme != "https")
            throw std::runtime_error("invalid scheme in redirect " +
                newLocation->pUrl.scheme);
    }
    catch (std::exception &)
```

## Snippet 4

Context: `src/ripple/core/impl/Config.cpp:271` (changes a sensitive control or state-update path)

Before
```cpp
std::cerr << "Loading: " << CONFIG_FILE << "\n";

    std::ifstream ifsConfig (CONFIG_FILE.c_str (), std::ios::in);

    if (!ifsConfig)
    {
        std::cerr << "Failed to open '" << CONFIG_FILE << "'." << std::endl;
        return;
```
After
```cpp
std::cerr << "Loading: " << CONFIG_FILE << "\n";

    boost::system::error_code ec;
    auto const fileContents = getFileContents(ec, CONFIG_FILE);

    if (ec)
    {
        std::cerr << "Failed to read '" << CONFIG_FILE << "'." <<
```

# Fix Pattern

Add an explicit URL-scheme allowlist on redirect handling and use explicit error-code-based file reads for configuration inputs.

## How It Was Fixed

`ValidatorSite::processRedirect` now throws if a redirect target is not `http` or `https`. Local file loading is kept as an explicit configured path. Config file and validators file loading now use `getFileContents` and check `boost::system::error_code` before parsing.

# Why It Matters

1. Validator-list sources influence validator trust configuration.

2. Adding `file://` support expands retrieval behavior and benefits from clear boundaries.

3. Redirects are constrained to HTTP/HTTPS in the shown code path.

4. Unreadable config inputs now produce clearer failures.

5. The evidence supports possible hardening, not a confirmed vulnerability fix.

# Evidence Notes

Supported by `src/ripple/app/misc/impl/ValidatorSite.cpp` around the added redirect scheme check and `src/ripple/core/impl/Config.cpp` around explicit file-read error handling. `WorkFile.h` supports the local file retrieval feature, but it is support code rather than a demonstrated root cause. The draft's stronger security claims should be downgraded because exploitability and security impact are not established by the provided snippets. Protocol security invariant: Validator-list content may be loaded only from intended configured sources and must still pass normal validator-list validation before affecting validator trust state. The supplied evidence also shows redirects are constrained to HTTP/HTTPS, but it does not establish an exploitable invariant violation before the patch. Verification notes: The patch does not prove bypass of validator-list signature validation. The patch does not prove consensus compromise or validator impersonation. The patch does not prove local file contents are exposed to a remote attacker. The Config.cpp file-read changes are primarily robustness/diagnostic changes, not standalone security fixes. The evidence does not support the heuristic replay-or-signature-validation classification. No proof of validator-list signature bypass is provided. No proof of consensus compromise is provided. No proof of remote local-file disclosure is provided. Config file-read changes appear robustness-oriented. Classified as unclear rather than likely because the security thesis is plausible but unproven. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validator-list-redirect-scheme-hardening`
Final impact type: `validator-list-source-integrity`
Final confidence: `medium`
Final tags: `validator-ops, validator-list, redirect-validation, url-scheme-allowlist, file-url, security-hardening`

The original replay/signature-validation framing is unsupported, but the supplied patch evidence does show a security-relevant hardening boundary: validator-list redirects are newly restricted to http/https while explicit configured file:// validator-list loading is added. That is enough to retain as hardening of a sensitive validator-list retrieval path, but not enough to call it a concrete vulnerability fix.

## Security Evidence

1. ValidatorSite::processRedirect now rejects redirect targets whose scheme is not http or https.
2. The commit adds explicit configured file:// validator-list support, making redirect/source boundaries security-relevant.
3. The commit text states file-loaded lists are still validated like downloaded lists, suggesting file support is intended as a controlled input path.
4. The changed path affects validator-list retrieval, which influences validator trust configuration.

## Missing Evidence

1. No proof that an attacker could control a validator-list redirect in a meaningful threat model.
2. No proof of local file disclosure, validator-list validation bypass, replay, signature bypass, or consensus compromise.
3. No evidence that the Config.cpp file-read error handling fixes a security bug rather than robustness and diagnostics.
4. No tests or commit text explicitly describe an exploit or vulnerability.

## Claim Boundaries

1. Classify only as security-hardening, not security-fix.
2. Do not retain the replay-or-signature-validation bug class.
3. Do not claim validator impersonation, consensus compromise, or request forgery/replay.
4. The supported claim is limited to URL scheme allowlisting for validator-list redirects during added file:// source support.
