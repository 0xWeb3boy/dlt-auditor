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
- branches that treat debug, simulation, or maintenance modes differently
- update paths that call Set* or write state without first validating against an existing object
- delegated or granular permission systems where the grant is valid for one transaction shape but the executed operation can include paths, alternative assets, generated holdings, pseudo-accounts, receiver policy, freeze state, or feature-gated fields outside that shape
- transaction preflight or admission checks that authorize a broad account or role but do not re-check the exact asset, issuer, destination, domain, state object, or generated side effect at the state-transition sink
- authorization helpers that infer permission from share ownership, receipt ownership, account flags, vault membership, staking position, or domain metadata without loading the authoritative object that defines the policy
- cleanup, revoke, delete, close, withdraw, or unstake paths where authority to remove an object is not the same as authority to dispose of its dependent obligations, delegated rights, or generated state
- authorization predicates that combine a boolean result with an error result. Errors from role, owner, policy, or registry lookup should fail closed and must not be treated as proof of access.
- sensitive sinks that accept a caller-supplied destination, recipient, authority, fee recipient, aggregator, controller, or round value when the sink can derive that value from authoritative state.
- privileged queues where admission checks authorization, owner, policy, or round freshness but dequeue, replay, retry, or execution uses cached state or a weaker predicate.
- signing or approval middleware where validation warnings, policy failures, or UI-mediated prompts default to continue instead of requiring explicit approval under a clearly unsafe mode.
- object-, resource-, or capability-based ledgers where the executed object set is derived through object references, dynamic fields, consensus-created objects, or helper summaries. Check that the final sink revalidates current ownership or capability for every mutable, deletable, wrapped, or indirectly loaded object
- paths that authorize based on a transaction sender, object ID, cached owner, or declared owner before resolving the authoritative current owner. The authorization decision should consume the same owner state that the write, delete, or transfer sink will mutate

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

Report only candidates where the missing property is concrete.

Severity guidance:
- High if the bug enables unauthorized privileged actions, unauthorized validator or committee actions, bridge actions, key-share access, or unauthorized consensus/state changes.
- Medium if it weakens admission validation or requires operator/debug configuration.
```
