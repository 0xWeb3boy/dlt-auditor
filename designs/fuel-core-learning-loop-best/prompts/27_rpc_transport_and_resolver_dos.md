# Prompt Family: RPC Transport And Resolver DoS

## Use This For

- Public HTTP, GraphQL, JSON-RPC, WebSocket, subscription, playground, debug, and admin APIs.
- Transport-level connection exhaustion, slow body attacks, response aggregation, and resolver panics.
- Public resolver assumptions around pagination, cursor selectors, and unreachable branches.

## Prompt

```text
Hunt for public API availability bugs at both layers: before a request is decoded, and after it reaches a resolver.

Focus on:
- HTTP listener and service construction
- request body readers, content-length handling, chunked transfer, idle read timeout, and per-connection tasks
- GraphQL/JSON-RPC resolver validation, pagination helpers, subscriptions, and batch/response aggregation
- resolver-by-resolver argument-shape matrices for public pagination, cursor, range, and connection fields
- route-specific timeout, body-size, depth, complexity, and max-response policies
- public functions containing `unreachable!`, `panic!`, `expect`, `unwrap`, or comments that assume a previous validator made a shape impossible

Search patterns:
- large `Content-Length` where the server waits while the client drips bytes slowly
- connections accepted before max connection, per-IP, idle-timeout, or read-timeout limits are reserved
- request body limits that apply only after buffering or after expensive parsing
- one route with body/timeout/depth/complexity limits and another related route without equivalent limits
- GraphQL connection fields where `before`/`after`, cursors, `first`, and `last` can appear in combinations the resolver does not handle
- resolver branches where both `first` and `last` are absent, both are present, or cursor-only queries pass schema validation
- helper-level rejections that are assumed but not proven at each resolver call site
- public API schemas that allow optional cursor/count/range arguments while resolver code assumes one of them is present
- panics from "unreachable" pagination direction, impossible enum variants, missing default cases, or empty result assumptions
- batch or subscription paths that aggregate responses before enforcing max response size
- slow clients that hold file descriptors, memory, worker tasks, or semaphore permits without making parser progress
- P2P, RPC, and admin connection limits that are configured separately but share the same process resources

For every public pagination/connection/range resolver, build a compact argument-shape matrix. Include at least:
- no count and no cursor
- `after` only or equivalent lower cursor only
- `before` only or equivalent upper cursor only
- `first` only
- `last` only
- cursor plus matching count
- both counts or incompatible cursor/count combinations

For each row, state whether the shape is rejected by schema/parser, rejected by the shared helper, reaches resolver code safely, or reaches a panic/unchecked assumption. A claim that "the helper rejects it" must cite the exact helper branch and explain why the resolver cannot bypass it.

Mandatory resolver-local panic drill:
- Search the schema and resolver files for every public field that accepts GraphQL connection arguments such as `first`, `last`, `before`, `after`, `cursor`, `pagination`, `direction`, `count`, or `range`.
- For each resolver, not just each helper, inspect the local branch that derives `(count, direction)` or assumes one of `first`/`last` is present.
- If the repository has connection fields named like `blocks`, `transactions`, `coins`, `messages`, `receipts`, or `balances`, test or reason through these exact public shapes:
  - `{ field(after: "1") { edges { node { id } } } }`
  - `{ field(before: "1") { edges { node { id } } } }`
  - `{ field(after: "1", before: "2") { edges { node { id } } } }`
  - the same shapes with neither `first` nor `last`.
- Treat `after`/`before` cursor-only queries as externally accepted until the schema/parser/helper branch rejecting that exact resolver call is cited. Do not reuse a generic helper conclusion for sibling resolvers without proving the call site passes through it before any resolver-local `unreachable!`.
- Preserve separate candidates for process-aborting resolver panics even when nearby GraphQL findings cover cost accounting, slow bodies, or HTTP listener limits.

Mandatory HTTP transport phase split:
- Separate slow-header, idle no-header, slow-body, large `Content-Length`, chunked-transfer, keep-alive, response-write, and subscription-lifetime risks.
- A body-size limit only kills maximum body allocation after it is applied; it does not by itself kill slow body read, large declared content length, idle connection, partial header, or response streaming.
- A route timeout only kills the phases that enter the routed service. It does not by itself kill accepted sockets waiting for headers, and it may not kill long-lived subscriptions or response bodies.
- Keep both slow body / large `Content-Length` and open idle socket variants when no same-phase control is visible. They may share one root "transport admission" candidate only if the dossier explicitly lists each phase and kill test.

Questions to answer:
1. What happens before the request body is complete?
2. Which timeout protects header read, body read, resolver execution, response write, and idle connection lifetime?
3. Is max body size enforced before allocation and parsing, or only after buffering?
4. Do public resolver argument combinations exactly match the helper's preconditions?
5. Can a cursor-only or count-less pagination query reach an `unreachable!`, `expect`, or unchecked direction branch?
6. Are public API panics caught and converted to request errors, or do they abort the process?
7. Do connection limits cover unauthenticated HTTP clients, not just protocol peers?
8. Does the route remain safe under many idle sockets, slow body drip, small junk bodies, and repeated malformed requests?
9. If a body limit exists, which attack phase does it actually kill: buffered allocation, slow body read, header read, idle socket, response write, or subscription lifetime?
10. Are sibling routes or subscription endpoints protected by the same transport controls as ordinary query/mutation routes?
11. Does each public connection resolver reject `after` only and `before` only before the resolver-local direction/count code?
12. Does a large declared `Content-Length` with a byte-at-a-time body have a read deadline, minimum throughput rule, or connection admission cap at the body-read phase?
13. Do idle sockets with zero request bytes have a header-read or connection-lifetime deadline at the accept/parser phase?

Candidate retention rules:
- Keep an API panic candidate when an externally accepted argument shape reaches a process-aborting branch, even if neighboring resolvers use the same helper safely.
- Keep a transport resource candidate when the code lacks a visible limit at the relevant phase; downgrade severity if deployment defaults reduce exposure, but do not kill slow-read or idle-socket risk solely because post-routing body/complexity limits exist.
- Keep cursor-only resolver panic candidates even if the issue appears in only one or two sibling connection fields. Process abort via public API is enough.
- Keep slow body and idle/open-socket transport candidates as separate submechanisms unless a same-phase compensating control kills each one.
- Reject only when an actual control is shown at the same phase and scope as the proposed attack.

Severity guidance:
- Medium by default for unauthenticated public API process crash or sustained resource exhaustion.
- Lower if the route is local-only or debug-only by default and clearly documented.
```
