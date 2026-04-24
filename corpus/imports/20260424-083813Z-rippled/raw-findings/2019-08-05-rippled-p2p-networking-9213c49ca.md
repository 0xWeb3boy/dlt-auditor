---
case_id: case_20190805_9213c49ca
project: rippled
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: p2p-networking
confidence: medium
source_quality: high
date: 2019-08-05
source_refs:
  - git:9213c49ca1ac8f0f5acb11ba2a105b15a2f8121f
  - "src/ripple/net/impl/SSLHTTPDownloader.cpp:114"
  - "src/ripple/app/misc/detail/WorkSSL.h:93"
  - "src/ripple/net/impl/SSLHTTPDownloader.cpp:33"
  - "src/ripple/net/AutoSocket.h:117"
bug_class: tls-client-config-hardening
impact_type:
  - outbound-tls-verification-hardening
tags:
  - tls
  - ssl
  - certificate-verification
  - outbound-http-client
  - validator-sites
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is likely security-relevant because it changes ValidatorSite and SSLHTTPDownloader outbound HTTPS paths to use a shared HTTPClientSSLContext and adds explicit pre-connect and post-connect verification calls. The evidence supports an SSL configuration/verification correctness fix, but not a proven exploitable man-in-the-middle issue or any consensus/ledger impact.

## Observed Patch Facts

1. In `src/ripple/net/impl/SSLHTTPDownloader.cpp`, the patch replaces `if (ssl_verify_)` with `ec = ssl_ctx_.preConnectVerify(*stream_, host);`.

2. In `src/ripple/app/misc/detail/WorkSSL.h`, the patch replaces `if (ec)` with `auto err = ec ? ec : context_.postConnectVerify(stream_, host_);`.

3. In `src/ripple/net/impl/SSLHTTPDownloader.cpp`, the patch replaces `SSLHTTPDownloader::init(Config const& config)` with `SSLHTTPDownloader::download(`.

4. In `src/ripple/net/AutoSocket.h`, the patch replaces `static bool rfc2818_verify (std::string const& domain, bool preverified,` with `void async_handshake (handshake_type type, callback cbFunc)`.

## Project Context

The changed code sits primarily in `src/ripple/net/impl`, `src/ripple/net`, `src/ripple/app/misc/detail`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `src/ripple/net/impl/RPCSub.cpp`, `src/ripple/net/SSLHTTPDownloader.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/net/impl/RPCSub.cpp`, `src/ripple/net/SSLHTTPDownloader.h`. The strongest project-level identifiers around this patch are `stream_`, `boost`, `domain`, and `fail`. Nearby tests or test-like files include `src/ripple/beast/hash/tests/hash_metrics.h`.

## Before/After Behavior

Before the patch, SSLHTTPDownloader used local SSL verification setup, including conditional SNI handling, and WorkSSL::onConnect proceeded to async_handshake after only checking the TCP connect error. After the patch, both paths route through HTTPClientSSLContext: SSLHTTPDownloader calls preConnectVerify before async_connect, and WorkSSL calls preConnectVerify during setup and postConnectVerify after connect before continuing.

# Root Cause

SSL client setup was implemented inconsistently across outbound HTTPS client paths, so configured SSL behavior for ValidatorSites and SSLHTTPDownloader may not have been applied uniformly. The provided evidence does not prove verification was fully disabled or exploitable in deployed configurations.

## Walkthrough

1. The commit subject says ValidatorSites should honor SSL config settings and the body mentions refactoring common SSL client setup plus SSLHTTPDownloader tests.

2. SSLHTTPDownloader now owns a config-backed HTTPClientSSLContext instead of relying on the removed local init(Config const&) path shown in the diff.

3. SSLHTTPDownloader calls ssl_ctx_.preConnectVerify(*stream_, host) before boost::asio::async_connect and fails if that setup returns an error.

4. WorkSSL now uses HTTPClientSSLContext and calls context_.postConnectVerify(stream_, host_) after connect before async_handshake proceeds.

5. An older inline RFC2818 verification helper in AutoSocket is removed, consistent with centralizing verification behavior, though the helper itself is not shown to be the root cause.

6. The evidence supports a TLS configuration/verification fix, while claims about direct MITM exploitability, authentication bypass, or consensus compromise remain unsupported.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/misc/detail/WorkSSL.h | 36 | ValidatorSite HTTPS client path constructs HTTPClientSSLContext and runs pre-connect and post-connect verification around TLS setup. |
| src/ripple/app/misc/detail/WorkSSL.h | 93 | Connection callback now fails if postConnectVerify rejects the SSL stream or host before async_handshake continues. |
| src/ripple/net/impl/SSLHTTPDownloader.cpp | 27 | SSLHTTPDownloader now owns a configured HTTPClientSSLContext rather than separate local initialization state. |
| src/ripple/net/impl/SSLHTTPDownloader.cpp | 108 | Downloader applies preConnectVerify before TCP connect, covering SNI and configured verification setup. |
| src/ripple/net/HTTPClientSSLContext.h | 21 | Common SSL client context abstraction for applying config-backed certificate and hostname verification behavior. |
| src/ripple/net/AutoSocket.h | 117 | Older inline RFC2818 verification helper is removed as verification logic moves into the common SSL context path. |

## Code Snippets

## Snippet 1

Context: `src/ripple/net/impl/SSLHTTPDownloader.cpp:114` (changes a sensitive control or state-update path)

Before
```cpp
}

    if (ssl_verify_)
    {
        // If we intend to verify the SSL connection, we need to set the
        // default domain for server name indication *prior* to connecting
        if (!SSL_set_tlsext_host_name(stream_->native_handle(), host.c_str()))
        {
```
After
```cpp
}

    ec = ssl_ctx_.preConnectVerify(*stream_, host);
    if (ec)
        return fail(dstPath, complete, ec, "preConnectVerify");

    boost::asio::async_connect(
```

## Snippet 2

Context: `src/ripple/app/misc/detail/WorkSSL.h:93` (changes a sensitive control or state-update path)

Before
```c
WorkSSL::onConnect(error_code const& ec)
{
    if (ec)
        return fail(ec);

    stream_.async_handshake(
```
After
```c
WorkSSL::onConnect(error_code const& ec)
{
    auto err = ec ? ec : context_.postConnectVerify(stream_, host_);
    if (err)
        return fail(err);

    stream_.async_handshake(
```

## Snippet 3

Context: `src/ripple/net/impl/SSLHTTPDownloader.cpp:33` (changes signature or replay validation logic)

Before
```cpp
}

bool
SSLHTTPDownloader::init(Config const& config)
{
    boost::system::error_code ec;
    if (config.SSL_VERIFY_FILE.empty())
    {
```
After
```cpp
}

bool
SSLHTTPDownloader::download(
```

## Snippet 4

Context: `src/ripple/net/AutoSocket.h:117` (changes signature or replay validation logic)

Before
```c
}


    static bool rfc2818_verify (std::string const& domain, bool preverified,
                                boost::asio::ssl::verify_context& ctx, beast::Journal j)
    {
        using namespace ripple;
```
After
```c
}

    void async_handshake (handshake_type type, callback cbFunc)
    {
```

# Fix Pattern

Centralize outbound SSL client configuration in a shared context object and require affected client paths to pass explicit verification checkpoints before continuing connection setup.

## How It Was Fixed

The affected HTTPS client code was routed through HTTPClientSSLContext. SSLHTTPDownloader constructs the shared context and calls preConnectVerify before connecting. WorkSSL constructs the same context, performs pre-connect setup, and adds postConnectVerify after connect before async_handshake.

# Why It Matters

1. Configured SSL trust and verification settings must be applied consistently.

2. Validator-site and downloader fetches cross a network trust boundary.

3. Incorrect TLS setup can weaken peer identity checks even without a demonstrated exploit.

4. No evidence shows direct ledger, consensus, privilege, or authentication impact.

# Evidence Notes

Grounded evidence includes src/ripple/net/impl/SSLHTTPDownloader.cpp replacing local ssl_verify_ handling with ssl_ctx_.preConnectVerify, src/ripple/app/misc/detail/WorkSSL.h adding context_.postConnectVerify before async_handshake, SSLHTTPDownloader construction using HTTPClientSSLContext, and removal of an AutoSocket RFC2818 helper. The commit message supports the narrower claim that SSL config settings were not honored consistently for ValidatorSites. Stronger claims about full certificate-verification bypass or practical exploitability are not established. Protocol security invariant: Outbound HTTPS client paths that fetch validator-site or downloader content should consistently apply the configured SSL client context, including trust configuration and host/certificate verification setup, before allowing the TLS connection workflow to proceed. Verification notes: The patch does not prove that certificate verification was fully disabled in all affected deployments. The patch does not prove man-in-the-middle exploitability by itself. The patch does not show validator consensus or ledger integrity being directly compromised. The patch includes refactoring and test changes, so only the SSL verification/configuration path should be treated as security-relevant. No authentication bypass or privilege escalation is demonstrated by the provided evidence. No issue text for #2990 is provided. No failing/passing test details are provided beyond file names. No deployment configuration or exploit path is shown. Confidence is medium because the code and commit subject support security relevance, but the vulnerability impact is bounded by limited evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `tls-client-config-hardening`
Final impact type: `outbound-tls-verification-hardening`
Final tags: `tls, ssl, certificate-verification, outbound-http-client, validator-sites, hardening`

The supplied patch evidence supports a conservative security-hardening classification: outbound SSL/HTTPS client paths were changed to use a shared config-backed SSL context and to run explicit pre-connect and post-connect verification steps. This is security-sensitive TLS behavior, but the evidence does not prove a concrete exploitable vulnerability, complete certificate-verification bypass, MITM exploit, consensus impact, or authentication impact. The original security-fix label is too strong for the provided evidence.

## Security Evidence

1. Commit subject says ValidatorSites now honor SSL config settings.
2. SSLHTTPDownloader now calls ssl_ctx_.preConnectVerify before async_connect and fails on error.
3. WorkSSL constructs HTTPClientSSLContext from Config and calls preConnectVerify during setup.
4. WorkSSL::onConnect now calls context_.postConnectVerify before continuing to async_handshake.
5. Changes affect outbound SSL/HTTPS client code and certificate/host verification setup.

## Missing Evidence

1. No issue text for #2990 is provided.
2. No exploit scenario or attacker-controlled network path is shown.
3. No evidence proves certificate verification was fully disabled before the patch.
4. No failing or passing test details are provided beyond test file names.
5. No direct consensus, ledger integrity, authentication, or privilege impact is demonstrated.

## Claim Boundaries

1. Retain only as TLS/SSL client hardening, not as a proven vulnerability fix.
2. Do not claim confirmed MITM exploitability from this patch alone.
3. Do not claim consensus or ledger compromise.
4. Do not generalize beyond ValidatorSite/SSLHTTPDownloader outbound SSL configuration and verification behavior.
