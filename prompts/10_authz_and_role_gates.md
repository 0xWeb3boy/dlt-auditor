# Prompt Family: Authorization And Role Gates

## Use This For

- Missing authentication on security-sensitive RPC handlers.
- Broad membership checks where role-specific authorization is required.
- Peer authorization gaps on p2p or committee messages.
- State updates that should require authorization or update verification.
- Debug or bypass modes that weaken normal admission checks.
- Delegated, granular, or feature-scoped permissions that must match the exact operation being executed.

## Prompt

```text
Hunt for authorization bugs in a blockchain or DLT codebase.

Focus on code paths that already verify syntax or signatures, but may still miss one of:
- caller authentication
- peer authorization
- validator, committee, relayer, bridge, or operator role validation
- chain, subnet, shard, app, bridge, or runtime-scoped authorization
- update authorization against existing state
- feature-gated policy acceptance
- delegated permission scope
- generated-side-effect authorization

Prioritize these areas:
- consensus or ordering handlers
- p2p message handlers
- privileged RPC or admin APIs
- bridge, relayer, sequencer, proposer, validator, committee, or keeper logic
- state transition handlers
- update or registration paths

Search patterns:
- TODO comments near auth checks
- functions named authorize, authenticate, verifyPolicy, verifyAccess, verifyRole, allow*, can*, IsPeerAuthorized, Verify*Update
- code that checks "is a member" when it may need "is proposer", "is validator", "is signer for this committee", "is current bridge relayer", or "is authorized for this shard or subnet"
- handlers that decode a request and proceed straight into processing
- public RPC, REST, gRPC, or JSON-RPC methods that have a protected helper nearby but are also registered through an unprotected route, trait implementation, delegate, compatibility method, or generated service binding
- sensitive API methods removed from a public surface instead of wrapped with authentication. Treat this as attack-surface hardening and search for alternate registered paths that still reach the same sink
- branches that treat debug, simulation, or maintenance modes differently
- update paths that call Set* or write state without first validating against an existing object
- delegated or granular permission systems where the grant is valid for one transaction shape but the executed operation can include paths, alternative assets, generated holdings, pseudo-accounts, receiver policy, freeze state, or feature-gated fields outside that shape
- transaction preflight or admission checks that authorize a broad account or role but do not re-check the exact asset, issuer, destination, domain, state object, or generated side effect at the state-transition sink
- authorization helpers that infer permission from share ownership, receipt ownership, account flags, vault membership, staking position, or domain metadata without loading the authoritative object that defines the policy
- authorization helpers that answer "is any alias writable, signer, or owner-correct?" instead of "is this exact indexed object authorized for this sink?"
- nested execution, callback, or cross-program paths where duplicate account aliases, writable flags, or signer flags can be unioned across frames. Privilege in the inner frame should be the intersection of caller-granted privilege, callee-declared privilege, and the current account identity, not the broadest alias observed anywhere in the call stack.
- state parsers or transition helpers that inspect account, object, or record contents before verifying the authoritative owner program, module, namespace, or registry entry allowed to define that state type
- cleanup, revoke, delete, close, withdraw, or unstake paths where authority to remove an object is not the same as authority to dispose of its dependent obligations, delegated rights, or generated state
- lifecycle operations such as stop, revoke, rotate, close, withdraw, unregister, renew, or disable where the authority to manage the object may differ from reward owner, fee recipient, namespace owner, issuer, creator, or broad admin ownership. Load the target object and authorize against its explicit management or controller authority before mutating lifecycle state.
- stake, vote, fee, reward, withdraw, upgrade, close, and broad owner authorities are separate unless the protocol explicitly aliases them. Search for sinks that accept one authority because another authority signs nearby.
- authorization predicates that combine a boolean result with an error result. Errors from role, owner, policy, or registry lookup should fail closed and must not be treated as proof of access.
- sensitive sinks that accept a caller-supplied destination, recipient, authority, fee recipient, aggregator, controller, or round value when the sink can derive that value from authoritative state.
- privileged queues where admission checks authorization, owner, policy, or round freshness but dequeue, replay, retry, or execution uses cached state or a weaker predicate.
- signing or approval middleware where validation warnings, policy failures, or UI-mediated prompts default to continue instead of requiring explicit approval under a clearly unsafe mode.
- internal prover, sequencer, relayer, validator, oracle, admin, or worker APIs where authentication helpers, token validators, or middleware are constructed but not attached to the actual route tree, interceptor chain, RPC method, or message handler that reaches the privileged sink
- network-facing or runtime-facing components that can request privileged signatures, approvals, or key use without a narrow, role-scoped mediation boundary such as a dedicated signer worker, keyguard, approval queue, or isolated admin path
- service-to-service clients that begin sending bearer tokens, JWTs, mTLS identities, or shared-secret headers without a corresponding fail-closed server-side validation path on every sensitive endpoint
- startup or config paths where production, public, or non-local deployments can use documented sample secrets, placeholder tokens, empty passwords, default keys, or fixture credentials for privileged service authentication
- private or scoped RPC proxies where unregistered methods fall back to generic upstream delegation. Compare the intended exposed method set against the upstream method set, and verify unknown methods return unauthorized or method-not-found before reaching the upstream sink.
- debug, trace, plugin, tracer, script, or extension factories where a caller-supplied name, blank default, or custom code string is accepted before an explicit allowlist check. Sensitive factories should be deny-by-default, and policy should be enforced before construction, lookup fallback, or custom evaluator dispatch
- optional allowlists, whitelists, role filters, or policy modules that should add restrictions on top of baseline validation. Check configuration branches where absence of an optional policy constructs no validator, no middleware, no prevalidator, or a weaker sink path at all.
- object-, resource-, or capability-based ledgers where the executed object set is derived through object references, dynamic fields, consensus-created objects, or helper summaries. Check that the final sink revalidates current ownership or capability for every mutable, deletable, wrapped, or indirectly loaded object
- paths that authorize based on a transaction sender, object ID, cached owner, or declared owner before resolving the authoritative current owner. The authorization decision should consume the same owner state that the write, delete, or transfer sink will mutate
- cross-runtime adapters, precompiles, and query payload builders that accept an identity in one address namespace and execute or construct payloads in another. Require explicit state-backed association at the adapter boundary and revalidate concrete message type, caller runtime, and destination before any value transfer or privileged state mutation
- proxy, delegation, or precompile systems where authority over one source account is treated as authority to choose any target account, contract, precompile, registry key, or destination namespace entry. Check source ownership, destination vacancy, target class, and exact method or selector policy separately.
- EVM/native adapters where an allowed proxy or delegated caller can indirectly reach smart contracts, generic dispatch, governance, staking, or value-transfer sinks that the native proxy type would not allow.
- alternate entrypoints that call keepers, managers, or storage helpers directly instead of constructing the canonical message object and using the same validation or dispatch path as native transactions
- committee or signer systems where "is a member" is weaker than "is the coordinator", "is the proposer", "is the aggregator", "is the selected signer", or "is the owner for this exact round and message". Check command execution, queue dequeue, retry, and replay paths for the same role predicate.

Questions to answer:
1. Who is supposed to be allowed to call this path?
2. What proof establishes that authority?
3. Is the code checking only cryptographic validity, or also role and scope?
4. Is authorization bound to the correct chain, epoch, height, committee, validator set, shard, bridge domain, or feature version?
5. Is there a state-recreation or expired-object path that skips update verification?
6. Does the permission cover this exact transaction shape, asset class, issuer, destination, receiver policy, and feature or amendment state, or only the transaction type?
7. If the operation creates a holding, directory entry, delegate object, pseudo-account state, receipt, share, or follow-on state object, is that generated side effect authorized too?
8. Are sender consent, receiver consent, issuer policy, domain policy, and operator or admin authority treated as separate checks?
9. If the role or policy lookup returns both `(allowed, error)`, which combinations grant access, and do all errors deny?
10. Can the privileged sink derive the sensitive recipient, authority, or policy value itself instead of trusting a caller-supplied parameter?
11. Are admission, dequeue, replay, and execution checking the same authority and freshness source?
12. Is every sensitive route mounted only through the authenticated/protected surface, with authentication enforced before parameter parsing and dispatch?

Report only candidates where the missing property is concrete.

Severity guidance:
- High if the bug enables unauthorized privileged actions, unauthorized validator or committee actions, bridge actions, key-share access, or unauthorized consensus/state changes.
- Medium if it weakens admission validation or requires operator/debug configuration.
```
