# Prompt Family: Authorization And Role Gates

## Use This For

- Missing authentication on security-sensitive RPC handlers.
- Broad membership checks where role-specific authorization is required.
- Peer authorization gaps on p2p or committee messages.
- State updates that should require authorization or update verification.
- Debug or bypass modes that weaken normal admission checks.

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

Questions to answer:
1. Who is supposed to be allowed to call this path?
2. What proof establishes that authority?
3. Is the code checking only cryptographic validity, or also role and scope?
4. Is authorization bound to the correct chain, epoch, height, committee, validator set, shard, bridge domain, or feature version?
5. Is there a state-recreation or expired-object path that skips update verification?

Report only candidates where the missing property is concrete.

Severity guidance:
- High if the bug enables unauthorized privileged actions, unauthorized validator or committee actions, bridge actions, key-share access, or unauthorized consensus/state changes.
- Medium if it weakens admission validation or requires operator/debug configuration.
```
