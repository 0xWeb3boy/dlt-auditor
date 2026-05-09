---
case_id: case_20260128_9d08af56
project: nibiru
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: medium
source_quality: high
date: 2026-01-28
source_refs:
  - git:9d08af566254f07b8b68714449d46b91ecb4e25a
  - "internal/cosmos-sdk/go.sum:825"
  - "internal/cosmos-sdk/go.sum:421"
  - "internal/cosmos-sdk/go.sum:1375"
  - "internal/cosmos-sdk/go.sum:714"
bug_class: vulnerable-dependency
impact_type:
  - upstream-advisory-remediation
tags:
  - blockchain-core
  - dependency-upgrade
  - cometbft
  - security-advisory
  - csa-2026-001
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

This is best classified as a likely security dependency fix. The commit message explicitly states that CometBFT was upgraded to patched v0.37.18 for CSA-2026-001 across the root module, internal Cosmos SDK module, and test modules. The supplied diff evidence is dependency metadata and checksum churn, not a local Nibiru or Cosmos SDK implementation fix.

## Observed Patch Facts

1. In `internal/cosmos-sdk/go.sum`, the patch replaces `github.com/pelletier/go-toml/v2 v2.1.0 h1:FnwAJ4oYMvbT/34k9zzHuZNrhlz48GB3/s6at6/MHO4=` with `github.com/pelletier/go-toml/v2 v2.2.2 h1:aYUidT7k73Pcl9nb2gScu7NSrKCSHIDE89b3+6Wq+LM=`.

2. In `internal/cosmos-sdk/go.sum`, the patch replaces `github.com/go-kit/kit v0.12.0 h1:e4o3o3IsBfAKQh5Qbbiqyfu97Ku7jrO/JbohvztANh4=` with `github.com/go-errors/errors v1.4.2/go.mod h1:sIVyrIiJhuEF+Pj9Ebtd6P/rEYROXFi3BopGUQ5a...`.

3. In `internal/cosmos-sdk/go.sum`, the patch replaces `golang.org/x/xerrors v0.0.0-20220907171357-04be3eba64a2 h1:H2TDz8ibqkAF6YGhCdN3jS9O0/...` with `golang.org/x/xerrors v0.0.0-20231012003039-104605ab7028 h1:+cNy6SZtPcJQH3LJVLOSmiC7MM...`.

4. In `internal/cosmos-sdk/go.sum`, the patch replaces `github.com/lib/pq v1.10.7 h1:p7ZhMD+KsSRozJr34udlUrhboJwWAgCg34+/ZZNvZZw=` with `github.com/kylelemons/godebug v1.1.0 h1:RPNrshWIDI6G2gRW9EHilWtl7Z6Sb1BR0xunSBf0SNc=`.

## Project Context

The changed code sits primarily in `internal/cosmos-sdk`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `internal/cosmos-sdk/go.mod`, `internal/cosmos-sdk/justfile` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `internal/cosmos-sdk/go.mod`, `internal/cosmos-sdk/tx/go.sum`. The strongest project-level identifiers around this patch are `golang`, `pelletier`, `toml`, and `xerrors`. Nearby tests or test-like files include `internal/cosmos-sdk/tests/go.sum`, `internal/cosmos-sdk/tests/go.mod`.

## Before/After Behavior

Before the patch, the project dependency graph used a CometBFT baseline that the commit identifies as requiring the CSA-2026-001 security fix; the exact prior CometBFT version is not shown in the supplied evidence. After the patch, the commit message says CometBFT was upgraded to patched v0.37.18 across go.mod, go.sum, internal/cosmos-sdk/go.mod, internal/cosmos-sdk/go.sum, internal/cosmos-sdk/tests/go.mod, internal/cosmos-sdk/tests/go.sum, and internal/wasmd/tests/system/go.mod. The visible go.sum excerpts show transitive dependency updates such as pelletier/go-toml, go-kit/kit, xerrors, lib/pq, and goid, which are dependency graph effects rather than direct evidence of the CSA root cause.

# Root Cause

The grounded root cause is an unpatched upstream CometBFT dependency baseline relative to CSA-2026-001. The supplied evidence does not show the vulnerable CometBFT code path, affected function, attacker preconditions, impact, or any local application-layer defect.

## Walkthrough

1. The commit subject and body explicitly describe applying the required CometBFT security fix CSA-2026-001.

2. The stated remediation is an upgrade to patched CometBFT v0.37.18 across root and internal modules.

3. The changed files are Go module and checksum files, including internal Cosmos SDK and test module dependency files.

4. The visible internal/cosmos-sdk/go.sum snippets show transitive dependency version and checksum changes only.

5. No supplied evidence shows edits to local consensus, RPC, serialization, state handling, or resource-control implementation code.

6. Therefore the supported finding is an upstream vulnerable dependency upgrade, not a locally demonstrated protocol bug.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go.mod | 1 | root module dependency version for CometBFT patched baseline |
| go.sum | 1 | root module dependency checksum updates for patched dependency graph |
| internal/cosmos-sdk/go.mod | 5 | internal Cosmos SDK module dependency baseline affected by CometBFT upgrade |
| internal/cosmos-sdk/go.sum | 819 | internal Cosmos SDK transitive dependency checksum changes from dependency upgrade |
| internal/cosmos-sdk/go.sum | 415 | internal Cosmos SDK transitive dependency checksum changes from dependency upgrade |
| internal/cosmos-sdk/go.sum | 1369 | internal Cosmos SDK transitive dependency checksum changes from dependency upgrade |
| internal/cosmos-sdk/tests/go.mod | 1 | test module dependency baseline updated to align with patched CometBFT |
| internal/cosmos-sdk/tests/go.sum | 1 | test module checksum updates from patched dependency graph |
| internal/wasmd/tests/system/go.mod | 1 | system test module dependency baseline updated to align with patched CometBFT |

## Code Snippets

## Snippet 1

Context: `internal/cosmos-sdk/go.sum:825` (changes how canonical state is encoded, returned, or reconstructed)

Before
```text
github.com/pelletier/go-toml v1.2.0/go.mod h1:5z9KED0ma1S8pY6P1sdut58dfprrGBbd/94hg7ilaic=
github.com/pelletier/go-toml/v2 v2.0.6/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
github.com/pelletier/go-toml/v2 v2.1.0 h1:FnwAJ4oYMvbT/34k9zzHuZNrhlz48GB3/s6at6/MHO4=
github.com/pelletier/go-toml/v2 v2.1.0/go.mod h1:tJU2Z3ZkXwnxa4DPO899bsyIoywizdUvyaeZurnPPDc=
github.com/performancecopilot/speed v3.0.0+incompatible/go.mod h1:/CLtqpZ5gBg1M9iaPbIdPPGyKcA8hKdoy6hAWba7Yac=
github.com/petermattis/goid v0.0.0-20180202154549-b0b1615b78e5/go.mod h1:jvVRKCrJTQWu0XVbaOlby/2lO20uSCHEMzzplHXte1o=
github.com/petermattis/goid v0.0.0-20230317030725-371a4b8eda08 h1:hDSdbBuw3Lefr6R18ax0tZ2BJeNB3NehB3trOwYBsdU=
github.com/petermattis/goid v0.0.0-20230317030725-371a4b8eda08/go.mod h1:pxMtw7cyUw6B2bRH0ZBANSPg+AoSud1I1iyJHI69jH4=
```
After
```text
github.com/pelletier/go-toml v1.2.0/go.mod h1:5z9KED0ma1S8pY6P1sdut58dfprrGBbd/94hg7ilaic=
github.com/pelletier/go-toml/v2 v2.0.6/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
github.com/pelletier/go-toml/v2 v2.2.2 h1:aYUidT7k73Pcl9nb2gScu7NSrKCSHIDE89b3+6Wq+LM=
github.com/pelletier/go-toml/v2 v2.2.2/go.mod h1:1t835xjRzz80PqgE6HHgN2JOsmgYu/h4qDAS4n929Rs=
github.com/performancecopilot/speed v3.0.0+incompatible/go.mod h1:/CLtqpZ5gBg1M9iaPbIdPPGyKcA8hKdoy6hAWba7Yac=
github.com/petermattis/goid v0.0.0-20240813172612-4fcff4a6cae7 h1:Dx7Ovyv/SFnMFw3fD4oEoeorXc6saIiQ23LrGLth0Gw=
github.com/petermattis/goid v0.0.0-20240813172612-4fcff4a6cae7/go.mod h1:pxMtw7cyUw6B2bRH0ZBANSPg+AoSud1I1iyJHI69jH4=
github.com/pierrec/lz4 v1.0.2-0.20190131084431-473cd7ce01a1/go.mod h1:3/3N9NVKO0jef7pBehbT1qWhCMrIgbYNnFAZCqQ5LRc=
```

## Snippet 2

Context: `internal/cosmos-sdk/go.sum:421` (changes how canonical state is encoded, returned, or reconstructed)

Before
```text
github.com/gin-gonic/gin v1.9.0/go.mod h1:W1Me9+hsUSyj3CePGrd1/QrKJMSJ1Tu/0hFEH89961k=
github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
github.com/go-kit/kit v0.8.0/go.mod h1:xBxKIO96dXMWWy0MnWVtmwkA9/13aqxPnvrjFYMA2as=
github.com/go-kit/kit v0.9.0/go.mod h1:xBxKIO96dXMWWy0MnWVtmwkA9/13aqxPnvrjFYMA2as=
github.com/go-kit/kit v0.10.0/go.mod h1:xUsJbQ/Fp4kEt7AFgCuvyX4a71u8h9jB8tj/ORgOZ7o=
github.com/go-kit/kit v0.12.0 h1:e4o3o3IsBfAKQh5Qbbiqyfu97Ku7jrO/JbohvztANh4=
github.com/go-kit/kit v0.12.0/go.mod h1:lHd+EkCZPIwYItmGDDRdhinkzX2A1sj+M9biaEaizzs=
github.com/go-kit/log v0.2.1 h1:MRVx0/zhvdseW+Gza6N9rVzU/IVzaeE1SFI4raAhmBU=
```
After
```text
github.com/gin-gonic/gin v1.9.0/go.mod h1:W1Me9+hsUSyj3CePGrd1/QrKJMSJ1Tu/0hFEH89961k=
github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
github.com/go-errors/errors v1.4.2/go.mod h1:sIVyrIiJhuEF+Pj9Ebtd6P/rEYROXFi3BopGUQ5a5Og=
github.com/go-kit/kit v0.8.0/go.mod h1:xBxKIO96dXMWWy0MnWVtmwkA9/13aqxPnvrjFYMA2as=
github.com/go-kit/kit v0.9.0/go.mod h1:xBxKIO96dXMWWy0MnWVtmwkA9/13aqxPnvrjFYMA2as=
github.com/go-kit/kit v0.10.0/go.mod h1:xUsJbQ/Fp4kEt7AFgCuvyX4a71u8h9jB8tj/ORgOZ7o=
github.com/go-kit/kit v0.13.0 h1:OoneCcHKHQ03LfBpoQCUfCluwd2Vt3ohz+kvbJneZAU=
github.com/go-kit/kit v0.13.0/go.mod h1:phqEHMMUbyrCFCTgH48JueqrM3md2HcAZ8N3XE4FKDg=
```

## Snippet 3

Context: `internal/cosmos-sdk/go.sum:1375` (changes how canonical state is encoded, returned, or reconstructed)

Before
```text
golang.org/x/xerrors v0.0.0-20220517211312-f3a8303e98df/go.mod h1:K8+ghG5WaK9qNqU5K3HdILfMLy1f3aNYFI/wnl100a8=
golang.org/x/xerrors v0.0.0-20220609144429-65e65417b02f/go.mod h1:K8+ghG5WaK9qNqU5K3HdILfMLy1f3aNYFI/wnl100a8=
golang.org/x/xerrors v0.0.0-20220907171357-04be3eba64a2 h1:H2TDz8ibqkAF6YGhCdN3jS9O0/s90v0rJh3X/OLHEUk=
golang.org/x/xerrors v0.0.0-20220907171357-04be3eba64a2/go.mod h1:K8+ghG5WaK9qNqU5K3HdILfMLy1f3aNYFI/wnl100a8=
google.golang.org/api v0.3.1/go.mod h1:6wY9I6uQWHQ8EM57III9mq/AjF+i8G65rmVagqKMtkk=
google.golang.org/api v0.4.0/go.mod h1:8k5glujaEP+g9n7WNsDg8QP6cUVNI86fCNMcbazEtwE=
```
After
```text
golang.org/x/xerrors v0.0.0-20220517211312-f3a8303e98df/go.mod h1:K8+ghG5WaK9qNqU5K3HdILfMLy1f3aNYFI/wnl100a8=
golang.org/x/xerrors v0.0.0-20220609144429-65e65417b02f/go.mod h1:K8+ghG5WaK9qNqU5K3HdILfMLy1f3aNYFI/wnl100a8=
golang.org/x/xerrors v0.0.0-20220907171357-04be3eba64a2/go.mod h1:K8+ghG5WaK9qNqU5K3HdILfMLy1f3aNYFI/wnl100a8=
golang.org/x/xerrors v0.0.0-20231012003039-104605ab7028 h1:+cNy6SZtPcJQH3LJVLOSmiC7MMxXNOb3PU/VUEz+EhU=
golang.org/x/xerrors v0.0.0-20231012003039-104605ab7028/go.mod h1:NDW/Ps6MPRej6fsCIbMTohpP40sJ/P/vI1MoTEGwX90=
google.golang.org/api v0.3.1/go.mod h1:6wY9I6uQWHQ8EM57III9mq/AjF+i8G65rmVagqKMtkk=
google.golang.org/api v0.4.0/go.mod h1:8k5glujaEP+g9n7WNsDg8QP6cUVNI86fCNMcbazEtwE=
```

## Snippet 4

Context: `internal/cosmos-sdk/go.sum:714` (changes how canonical state is encoded, returned, or reconstructed)

Before
```text
github.com/kr/text v0.2.0 h1:5Nx0Ya0ZqY2ygV366QzturHI13Jq95ApcVaJBhpS+AY=
github.com/kr/text v0.2.0/go.mod h1:eLer722TekiGuMkidMxC/pM04lWEeraHUUmBw8l2grE=
github.com/leodido/go-urn v1.2.1 h1:BqpAaACuzVSgi/VLzGZIobT2z4v53pjosyNd9Yv6n/w=
github.com/leodido/go-urn v1.2.1/go.mod h1:zt4jvISO2HfUBqxjfIshjdMTYS56ZS/qv49ictyFfxY=
github.com/lib/pq v1.10.7 h1:p7ZhMD+KsSRozJr34udlUrhboJwWAgCg34+/ZZNvZZw=
github.com/lib/pq v1.10.7/go.mod h1:AlVN5x4E4T544tWzH6hKfbfQvm3HdbOxrmggDNAPY9o=
github.com/libp2p/go-buffer-pool v0.1.0 h1:oK4mSFcQz7cTQIfqbe4MIj9gLW+mnanjyFtc6cdF0Y8=
github.com/libp2p/go-buffer-pool v0.1.0/go.mod h1:N+vh8gMqimBzdKkSMVuydVDq+UV5QTWy5HSiZacSbPg=
```
After
```text
github.com/kr/text v0.2.0 h1:5Nx0Ya0ZqY2ygV366QzturHI13Jq95ApcVaJBhpS+AY=
github.com/kr/text v0.2.0/go.mod h1:eLer722TekiGuMkidMxC/pM04lWEeraHUUmBw8l2grE=
github.com/kylelemons/godebug v1.1.0 h1:RPNrshWIDI6G2gRW9EHilWtl7Z6Sb1BR0xunSBf0SNc=
github.com/kylelemons/godebug v1.1.0/go.mod h1:9/0rRGxNHcop5bhtWyNeEfOS8JIWk580+fNqagV/RAw=
github.com/leodido/go-urn v1.2.1 h1:BqpAaACuzVSgi/VLzGZIobT2z4v53pjosyNd9Yv6n/w=
github.com/leodido/go-urn v1.2.1/go.mod h1:zt4jvISO2HfUBqxjfIshjdMTYS56ZS/qv49ictyFfxY=
github.com/lib/pq v1.10.9 h1:YXG7RB+JIjhP29X+OtkiDnYaXQwpS4JEWq7dtCCRUEw=
github.com/lib/pq v1.10.9/go.mod h1:AlVN5x4E4T544tWzH6hKfbfQvm3HdbOxrmggDNAPY9o=
```

# Fix Pattern

Upgrade the upstream dependency identified by the security advisory to the patched version and align all module files that can resolve it, refreshing checksums for the resulting dependency graph.

## How It Was Fixed

According to the commit message, CometBFT was upgraded to patched v0.37.18. The module and checksum files across the root project, internal Cosmos SDK module, and related test modules were updated so they resolve the patched dependency graph.

# Why It Matters

1. CometBFT is a consensus dependency, so running an advisory-affected version can be security relevant.

2. Keeping multiple modules aligned reduces the chance that part of the workspace resolves an older vulnerable dependency.

3. The evidence supports dependency remediation, not a specific local exploit narrative.

4. Transitive go.sum changes should not be treated as independently vulnerable without separate evidence.

# Evidence Notes

The heuristic baseline's serialization/state-representation narrative is unsupported and should be discarded. The mapper's vulnerable-dependency classification is better grounded. The strongest evidence is the commit message naming CSA-2026-001 and patched CometBFT v0.37.18, plus the list of module files changed. The visible diff excerpts do not include the CometBFT version line or upstream advisory details, so the verdict remains likely rather than confirmed. Protocol security invariant: The project should resolve CometBFT to a version patched for CSA-2026-001 wherever the root, internal Cosmos SDK, and related test modules can select that dependency. The supplied evidence does not establish the CSA failure mode or a local protocol invariant beyond avoiding the vulnerable upstream CometBFT baseline. Verification notes: The provided diff does not show the vulnerable CometBFT function or exact CSA-2026-001 root cause. The patch does not prove a local Nibiru application-layer logic bug. The serialization/state-representation classification in the heuristic baseline is not supported by the visible dependency-only evidence. No exploitability, attacker preconditions, or impact class can be proven from the provided patch alone. The transitive go.sum changes should not be treated as independently security-relevant without upstream advisory details. No local implementation change is visible in the supplied evidence. No vulnerable CometBFT function or CSA-2026-001 technical root cause is provided. The exact pre-patch CometBFT version is not shown in the supplied snippets. The dependency-only evidence is sufficient for a likely security dependency fix, but not for a more specific bug class or exploit claim. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `vulnerable-dependency`
Final impact type: `upstream-advisory-remediation`
Final tags: `blockchain-core, dependency-upgrade, cometbft, security-advisory, csa-2026-001`

The supplied evidence supports retaining this as a likely security dependency fix, not as the specific rpc-client-api serialization/state-representation issue described in the generated metadata. The commit message explicitly says it applies the required CometBFT security fix CSA-2026-001 by upgrading to patched v0.37.18 across module files. The visible patch excerpts are go.sum dependency churn and do not show the CometBFT version line or the vulnerable upstream code path, so the finding should be kept only with a conservative vulnerable-dependency framing.

## Security Evidence

1. Commit subject and body explicitly reference a CometBFT security fix and CSA-2026-001.
2. Commit states the remediation is upgrading CometBFT to patched v0.37.18.
3. Changed files are Go module/checksum files across root, internal Cosmos SDK, and test modules, consistent with dependency remediation.
4. Project context shows CometBFT is used in internal Cosmos SDK test/network code paths.

## Missing Evidence

1. Visible diff snippets do not show the actual CometBFT before/after version line.
2. No upstream CSA-2026-001 technical root cause is provided.
3. No vulnerable CometBFT function, attacker preconditions, or exploit impact is shown.
4. No local Nibiru implementation code change is visible.

## Claim Boundaries

1. Treat this as an upstream dependency security remediation only.
2. Do not claim a local rpc-client-api bug from the supplied evidence.
3. Do not claim serialization, state representation, client-view divergence, p2p, or rpc impact without advisory details.
4. Do not treat unrelated transitive go.sum changes as independently security-relevant.
