---
case_id: case_20171117_a4a43a4de
project: rippled
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: access-control
source_quality: high
date: 2017-11-17
source_refs:
  - git:a4a43a4de9b783a57cb2cbe721217b5a7230fa5b
  - "src/ripple/net/impl/HTTPClient.cpp:280"
  - "src/ripple/app/misc/detail/WorkSSL.h:86"
  - "src/ripple/net/RegisterSSLCerts.h:1"
  - "src/ripple/net/impl/RegisterSSLCerts.cpp:1"
bug_class: tls-sni-hostname-setup
impact_type:
  - tls-certificate-validation-hardening
confidence: medium
tags:
  - tls
  - sni
  - certificate-validation
  - http-client
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a TLS/SNI setup improvement, not a confirmed vulnerability fix. The substantive shown change is in src/ripple/net/impl/HTTPClient.cpp, where verified SSL connections now call mSocket.setTLSHostName(mDeqSites[0]) after DNS resolution and before async_connect. This is security-relevant because SNI can affect certificate selection, but the evidence does not establish a certificate-validation bypass, wrong-certificate acceptance, attacker control, or access-control issue.

## Observed Patch Facts

1. In `src/ripple/net/impl/HTTPClient.cpp`, the patch replaces `boost::asio::async_connect (` with `// If we intend to verify the SSL connection, we need to`.

2. In `src/ripple/app/misc/detail/WorkSSL.h`, the patch replaces `rfc2818_verify (` with `rfc2818_verify(`.

3. In `src/ripple/net/RegisterSSLCerts.h`, the patch adds `//------------------------------------------------------------------------------`.

4. In `src/ripple/net/impl/RegisterSSLCerts.cpp`, the patch adds `//------------------------------------------------------------------------------`.

## Project Context

The changed code sits primarily in `src/ripple/net/impl`, `src/ripple/net`, `src/ripple/app/misc/detail`, which anchors the finding in the `access-control` area of the project. Historical context from `src/ripple/net/AutoSocket.h`, `src/ripple/net/impl/RPCSub.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/net/AutoSocket.h`, `src/ripple/net/impl/RPCSub.cpp`. The strongest project-level identifiers around this patch are `boost::asio::ssl::rfc2818_verification`, `rippled`, `notice`, and `domain`. Nearby tests or test-like files include `src/ripple/beast/hash/tests/hash_metrics.h`.

## Before/After Behavior

Before the patch, the shown HTTP client path proceeded from successful DNS resolution toward async_connect with no visible SNI hostname assignment. After the patch, when httpClientSSLContext->sslVerify() is true, the code sets the TLS hostname to mDeqSites[0] before connecting. The WorkSSL.h hunk still delegates to boost::asio::ssl::rfc2818_verification(domain)(preverified, ctx) and appears formatting-only in the supplied evidence. The RegisterSSLCerts files are introduced, but the visible snippets only show file headers, so certificate-loading behavior cannot be assessed from the provided input.

# Root Cause

No grounded vulnerability root cause is established. The closest supported issue is missing pre-connect SNI hostname setup for verified outbound TLS connections in the shown HTTP client path, which could affect server certificate selection for SNI-dependent hosts.

## Walkthrough

1. The HTTP client reaches the successful DNS resolution branch and logs Resolve complete.

2. In the before snippet, the next visible operation is async_connect, with no shown call that sets a TLS hostname for SNI.

3. In the after snippet, a comment states that the default domain for SNI must be set before connecting when SSL verification is intended.

4. The after code checks httpClientSSLContext->sslVerify() and calls mSocket.setTLSHostName(mDeqSites[0]) before connect.

5. The WorkSSL.h hunk preserves use of Boost RFC2818 hostname verification; no behavioral verification change is shown.

6. The RegisterSSLCerts additions may support platform certificate availability, but only headers are visible in the supplied snippets.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/net/impl/HTTPClient.cpp | 280 | Sets TLS server hostname for SNI before connecting when SSL verification is enabled. |
| src/ripple/app/misc/detail/WorkSSL.h | 86 | Uses Boost RFC2818 hostname verification helper; provided diff shows no substantive behavior change. |
| src/ripple/net/RegisterSSLCerts.h | 1 | Introduces certificate registration interface/header, likely for platform certificate availability. |
| src/ripple/net/impl/RegisterSSLCerts.cpp | 1 | Introduces certificate registration implementation, likely for platform certificate availability. |

## Code Snippets

## Snippet 1

Context: `src/ripple/net/impl/HTTPClient.cpp:280` (changes a sensitive control or state-update path)

Before
```cpp
JLOG (j_.trace()) << "Resolve complete.";

            boost::asio::async_connect (
                mSocket.lowest_layer (),
```
After
```cpp
JLOG (j_.trace()) << "Resolve complete.";

            // If we intend  to verify the SSL connection, we need to
            // set the default domain for server name indication *prior* to
            // connecting
            if (httpClientSSLContext->sslVerify())
                mSocket.setTLSHostName(mDeqSites[0]);
```

## Snippet 2

Context: `src/ripple/app/misc/detail/WorkSSL.h:86` (changes a sensitive control or state-update path)

Before
```c
static bool
    rfc2818_verify (
        std::string const& domain,
        bool preverified,
        boost::asio::ssl::verify_context& ctx)
    {
        return
```
After
```c
static bool
    rfc2818_verify(
        std::string const& domain,
        bool preverified,
        boost::asio::ssl::verify_context& ctx)
    {
        return boost::asio::ssl::rfc2818_verification(domain)(preverified, ctx);
```

## Snippet 3

Context: `src/ripple/net/RegisterSSLCerts.h:1` (changes an authorization or privilege gate)

Before
```c
(no before snippet captured)
```
After
```c
//------------------------------------------------------------------------------
/*
    This file is part of rippled: https://github.com/ripple/rippled
    Copyright (c) 2016 Ripple Labs Inc.

    Permission to use, copy, modify, and/or distribute this software for any
    purpose  with  or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.
```

## Snippet 4

Context: `src/ripple/net/impl/RegisterSSLCerts.cpp:1` (changes an authorization or privilege gate)

Before
```cpp
(no before snippet captured)
```
After
```cpp
//------------------------------------------------------------------------------
/*
    This file is part of rippled: https://github.com/ripple/rippled
    Copyright (c) 2017 Ripple Labs Inc.

    Permission to use, copy, modify, and/or distribute this software for any
    purpose  with  or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.
```

# Fix Pattern

Set the intended DNS hostname on verified outbound TLS sockets before connect/handshake so SNI can influence server certificate selection, while retaining hostname verification against the logical target name.

## How It Was Fixed

The patch adds pre-connect SNI setup in src/ripple/net/impl/HTTPClient.cpp by calling mSocket.setTLSHostName(mDeqSites[0]) when SSL verification is enabled. The visible WorkSSL.h change does not alter RFC2818 verification behavior. The provided RegisterSSLCerts snippets are insufficient to validate any certificate-store behavior.

# Why It Matters

1. SNI must be available before TLS handshake for servers hosting multiple certificates on one endpoint.

2. The change better aligns the requested hostname with the certificate the server can present.

3. The evidence supports hardening or interoperability, not a proven certificate-validation bypass.

4. Access-control claims from the heuristic baseline are unsupported.

# Evidence Notes

The heuristic baseline's access-control classification is unsupported by the supplied hunks. The concrete evidence is limited to SNI setup in HTTPClient.cpp, an apparently formatting-only RFC2818 helper hunk in WorkSSL.h, and newly added RegisterSSLCerts files whose implementation details are not visible. There is no supplied evidence of missing authorization checks, disabled validation, attacker-controlled certificate acceptance, or an exploitable authentication bypass. Protocol security invariant: For outbound HTTPS/TLS connections that perform certificate verification, the client should provide the intended DNS hostname before the TLS handshake so the server can select the correct certificate via SNI, and the resulting certificate can be checked against that same hostname. The patch affects this invariant by setting the TLS host name before connect when SSL verification is enabled, but the supplied evidence does not show that invalid certificates were previously accepted. Verification notes: No evidence that certificate verification was bypassed before the patch. No evidence of access-control or privilege-check logic in the shown hunks. No evidence that an attacker could force acceptance of a wrong certificate. No evidence that SNI is set when sslVerify is disabled. RegisterSSLCerts behavior is not visible beyond file introduction snippets. Inspect setTLSHostName to confirm it configures SNI before TLS handshake. Inspect the full connection and handshake order to confirm the hostname is applied in time. Inspect RegisterSSLCerts implementation before making claims about Windows certificate-store behavior. Do not keep this in a vulnerability-fix corpus without additional evidence of exploitable certificate validation failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `tls-sni-hostname-setup`
Final impact type: `tls-certificate-validation-hardening`
Final confidence: `medium`
Final tags: `tls, sni, certificate-validation, http-client, hardening`

The supplied evidence supports retaining this as TLS security hardening, not as an access-control or privilege-misuse fix. The substantive code change sets the TLS hostname for SNI before connecting when SSL verification is enabled, which tightens security-sensitive TLS behavior by aligning the requested server name with certificate selection. However, the patch evidence does not prove that invalid certificates were previously accepted or that there was an exploitable validation bypass.

## Security Evidence

1. HTTPClient.cpp now calls mSocket.setTLSHostName(mDeqSites[0]) before connecting when sslVerify() is true.
2. The added comment explicitly ties the change to verified SSL connections and server name indication before connection.
3. WorkSSL.h continues to use Boost RFC2818 hostname verification, keeping the path in certificate/hostname verification context.
4. Commit metadata mentions Server Name Indication and Windows certificate availability.

## Missing Evidence

1. No evidence that certificate verification was previously disabled or bypassed.
2. No evidence that a wrong certificate was previously accepted.
3. RegisterSSLCerts snippets only show file headers, not certificate-store behavior.
4. No evidence supporting access-control, RPC, validator privilege, or privilege-misuse claims.

## Claim Boundaries

1. Classify as TLS/SNI hardening only, not a confirmed vulnerability fix.
2. Do not claim authorization or access-control impact from the supplied evidence.
3. Do not claim exploitable MITM or certificate-validation bypass without additional proof.
4. Do not rely on RegisterSSLCerts behavior beyond the commit metadata and visible file introduction snippets.
