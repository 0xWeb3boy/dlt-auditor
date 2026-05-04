---
case_id: case_20250610_7be023090
project: zksync-era
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: access-control
confidence: medium
source_quality: medium
date: 2025-06-10
source_refs:
  - git:7be0230906ae09b47a255be8bcc8c7d35daf9ef4
  - "private-rpc/src/rpc/rpc-service.ts:3"
  - "private-rpc/check_api_coverage.py:1"
  - "private-rpc/src/rpc/rpc-method-handlers.ts:18"
  - "private-rpc/src/rpc/rpc-service.ts:109"
impact_type:
  - unauthorized-rpc-method-exposure
tags:
  - blockchain-core
  - access-control
  - rpc
  - allowlist
  - private-rpc
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported security-relevant change is that private RPC dispatch moved away from permissive fallback delegation and blacklist-style filtering toward explicit handler allowlisting. The strongest direct evidence is that the default handler for unregistered methods changed from forwarding the caller-supplied method and params to the target RPC to returning an unauthorized response.

## Observed Patch Facts

1. In `private-rpc/src/rpc/rpc-service.ts`, the patch changes a sensitive implementation path.

2. In `private-rpc/check_api_coverage.py`, the patch adds `#!/usr/bin/env python3`.

3. In `private-rpc/src/rpc/rpc-method-handlers.ts`, the patch replaces `// Filter out debug_* methods` with `/* ─────────────────────────────`.

4. In `private-rpc/src/rpc/rpc-service.ts`, the patch replaces `handle: (context, method, params, id) => delegateCall({ url: context.targetRpcUrl, id...` with `handle: (_context, _method, _params, id) => unauthorized(id)`.

## Project Context

The changed code sits primarily in `private-rpc/src/rpc`, `private-rpc/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `private-rpc/src/rpc/delegate-call.ts`, `private-rpc/esbuild.ts` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `private-rpc/src/rpc/methods/utils.ts`, `private-rpc/src/rpc/delegate-call.ts`. The strongest project-level identifiers around this patch are `forbiddenMethod`, `import`, `from`, and `method`.

## Before/After Behavior

Before the patch, RpcCallHandler.tryCall selected a registered handler or used defaultHandler, and defaultHandler delegated unregistered methods to context.targetRpcUrl via delegateCall. The handler registry evidence shows selected forbiddenMethod entries for debug_* and en_* methods. After the patch, defaultHandler returns unauthorized(id) for unregistered methods, and the registry is shown as an explicit allHandlers list with allowed entries such as unrestricted eth_blockNumber, unrestricted eth_chainId, and validatedEthereumCall('eth_call', 2).

# Root Cause

The root cause supported by the evidence was an overly permissive RPC dispatch boundary: methods without an explicit handler were still forwarded upstream. This made private RPC exposure depend partly on blocking known-bad methods rather than requiring every exposed method to be explicitly registered and reviewed.

## Walkthrough

1. A JSON-RPC request reaches RpcCallHandler.tryCall.

2. tryCall resolves this.handlers[method] or falls back to defaultHandler.

3. Before the patch, defaultHandler called delegateCall with the caller-controlled method and params.

4. The before registry snippet shows explicit forbiddenMethod entries for selected namespaces, consistent with blacklist-style filtering.

5. The patch removes delegateCall usage from rpc-service.ts and imports unauthorized.

6. After the patch, defaultHandler ignores the supplied method and params and returns unauthorized(id).

7. The after registry snippet shows explicit allowed handler entries, including validatedEthereumCall('eth_call', 2).

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| private-rpc/src/rpc/rpc-service.ts | 103 | RPC dispatch selects a registered handler or the default handler for unknown methods |
| private-rpc/src/rpc/rpc-service.ts | 109 | Default handler changed from delegating arbitrary methods to returning unauthorized |
| private-rpc/src/rpc/rpc-method-handlers.ts | 18 | RPC method registry changed from blacklist-oriented filtering toward explicit allowed handlers |
| private-rpc/src/rpc/methods/utils.ts | 1 | Shared RPC method authorization/delegation utilities for protected call paths |
| private-rpc/src/rpc/methods/eth_call.ts | 1 | Call simulation validation path implicated by eth_call and state override handling |

## Code Snippets

## Snippet 1

Context: `private-rpc/src/rpc/rpc-service.ts:3` (changes a sensitive control or state-update path)

Before
```ts
import { Authorizer } from '@/permissions/authorizer';
import { FastifyReplyType } from 'fastify/types/type-provider';
import { delegateCall } from './delegate-call';
import { errorResponse, invalidRequest } from './json-rpc';

const rpcReqSchema = z.object({
```
After
```ts
import { Authorizer } from '@/permissions/authorizer';
import { FastifyReplyType } from 'fastify/types/type-provider';
import { errorResponse, invalidRequest, unauthorized } from './json-rpc';

const rpcReqSchema = z.object({
```

## Snippet 2

Context: `private-rpc/check_api_coverage.py:1` (changes a sensitive control or state-update path)

Before
```python
(no before snippet captured)
```
After
```python
#!/usr/bin/env python3
"""
check_handlers.py – RPC-coverage checker (namespace by namespace)

• Reads eth.rs and zks.rs for #[method(name = "...")]
• Reads rpc-method-handlers.ts for every eth_* / zks_* identifier
  – works whether it appears as a string literal **or** a bare variable
• Reports, per namespace:
```

## Snippet 3

Context: `private-rpc/src/rpc/rpc-method-handlers.ts:18` (changes a sensitive control or state-update path)

Before
```ts
export const allHandlers = [
    // Filter out debug_* methods
    forbiddenMethod('debug_traceBlockByHash'),
    forbiddenMethod('debug_traceBlockByNumber'),
    forbiddenMethod('debug_traceCall'),
    forbiddenMethod('debug_traceTransaction'),
```
After
```ts
export const allHandlers = [
    /* ─────────────────────────────
       Eth namespace (exact order)
       ───────────────────────────── */
    unrestricted('eth_blockNumber'),
    unrestricted('eth_chainId'),
    validatedEthereumCall('eth_call', 2),
```

## Snippet 4

Context: `private-rpc/src/rpc/rpc-service.ts:109` (changes a sensitive control or state-update path)

Before
```ts
return {
            name: 'default-handler',
            handle: (context, method, params, id) => delegateCall({ url: context.targetRpcUrl, id, method, params })
        };
    }
```
After
```ts
return {
            name: 'default-handler',
            handle: (_context, _method, _params, id) => unauthorized(id)
        };
    }
```

# Fix Pattern

Replace permissive fallback forwarding and blacklist filtering with explicit allowlisting, and reject unregistered methods at the dispatch boundary.

## How It Was Fixed

rpc-service.ts changed the default handler from delegateCall({ url: context.targetRpcUrl, id, method, params }) to unauthorized(id). rpc-method-handlers.ts was refactored toward an explicit allHandlers whitelist. check_api_coverage.py appears to be supporting coverage tooling rather than the runtime root cause.

# Why It Matters

1. Unknown private RPC methods are no longer automatically forwarded upstream.

2. The exposed RPC surface is easier to audit when methods must be explicitly registered.

3. Reducing blacklist dependence lowers the risk of accidentally exposing newly added or overlooked methods.

# Evidence Notes

Direct evidence supports an access-control hardening or fix around unregistered private RPC methods. The commit subject mentions estimate-gas protection and blocking state overrides, but the supplied hunks do not show the exact estimate-gas or state-override validation changes. The evidence also does not demonstrate exploitability, fund loss, or that all affected endpoints were externally reachable. The API coverage script is support code, not the root cause. Protocol security invariant: The private RPC service should expose only explicitly registered and reviewed JSON-RPC methods. Unknown methods should not be transparently forwarded to the target RPC, and simulation-style methods should use the intended validation and authorization path. Verification notes: The evidence does not show a demonstrated exploit transaction or proof of fund loss. The evidence does not prove that every estimate-gas endpoint was reachable by an untrusted caller before the patch. The evidence does not show the exact state override validation hunk, only the commit-level intent and related files. The API coverage script change is not itself security-sensitive except as support for handler coverage. Verified from provided evidence only; no files or external context inspected. Strongest evidence is rpc-service.ts defaultHandler changing from delegateCall to unauthorized. State override and estimate-gas claims are treated as commit intent unless shown by provided hunks. Confidence is medium rather than high because endpoint reachability and exact validation diffs are incomplete. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `unauthorized-rpc-method-exposure`
Final tags: `blockchain-core, access-control, rpc, allowlist, private-rpc`

The supplied patch evidence clearly supports security hardening of the private RPC dispatch boundary. The strongest hunk changes the default handler from forwarding arbitrary unregistered JSON-RPC methods and params to the target RPC into returning unauthorized, and the handler registry moves from blacklist-style forbidden methods toward explicit allowed handlers. This supports retaining the case, but as hardening rather than a proven security fix because the evidence does not demonstrate exploitability, external reachability, or the specific estimate-gas/state-override vulnerability claims.

## Security Evidence

1. Default RPC handler previously delegated caller-supplied method and params to context.targetRpcUrl.
2. Default RPC handler now ignores unknown method and params and returns unauthorized(id).
3. Handler registry evidence shows a shift from explicit forbiddenMethod entries to explicit allowed handlers such as unrestricted and validatedEthereumCall.
4. Commit subject explicitly references making estimate-gas endpoints protected and blocking state overrides, though only partially supported by the supplied hunks.

## Missing Evidence

1. No proof that unregistered methods were reachable by untrusted callers.
2. No exploit scenario or demonstrated impact is shown.
3. No supplied hunk directly shows estimate-gas endpoint protection changes.
4. No supplied hunk directly shows state override validation or blocking logic.
5. No evidence supports consensus or snapshot impact claims.

## Claim Boundaries

1. Validate as private RPC access-control hardening, not a confirmed exploitable vulnerability fix.
2. Do not claim fund loss, consensus failure, or transaction-processing compromise from the supplied evidence alone.
3. Do not rely on the API coverage script as runtime security evidence except as supporting maintenance for allowlist coverage.
4. State override and estimate-gas claims should be treated as commit intent unless additional patch evidence is supplied.
