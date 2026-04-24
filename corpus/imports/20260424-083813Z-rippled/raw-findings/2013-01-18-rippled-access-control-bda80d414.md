---
case_id: case_20130118_bda80d414
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: access-control
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: medium
source_quality: high
tags:
  - blockchain-core
  - access-control
  - privilege-misuse
  - rpc
date: 2013-01-18
source_refs:
  - git:bda80d41448224d1e1dd0086276e1110d85ed2b0
  - "src/cpp/ripple/WSConnection.h:93"
  - "src/cpp/ripple/CallRPC.cpp:566"
  - "src/cpp/ripple/RPCServer.cpp:130"
  - "src/cpp/ripple/RPCServer.cpp:33"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is security-relevant and likely hardens RPC admin access, but the supplied evidence does not fully prove an exploitable authorization bypass. The grounded change is that HTTP and WebSocket RPC paths stop relying only on coarse interface or peer-address assumptions and instead call iAdminGet on the request path, with an explicit FORBID handling path for WebSocket RPC.

## Observed Patch Facts

1. In `src/cpp/ripple/WSConnection.h`, the patch replaces `jvResult["result"] = mRPCHandler.doCommand(` with `int iRole = mHandler->getPublic()`.

2. In `src/cpp/ripple/CallRPC.cpp`, the patch removes `if (theConfig.RPC_USER.empty() && theConfig.RPC_PASSWORD.empty())`.

3. In `src/cpp/ripple/RPCServer.cpp`, the patch replaces `Json::Value valParams = valRequest["params"];` with `Json::Value valParams = jvRequest["params"];`.

4. In `src/cpp/ripple/RPCServer.cpp`, the patch removes `if (mSocket.remote_endpoint().address().to_string()=="127.0.0.1") mRole = RPCHandler:...`.

## Project Context

The changed code sits primarily in `src/cpp/ripple`, `src/cpp`, which anchors the finding in the `access-control` area of the project. Historical context from `src/cpp/ripple/RPCHandler.cpp`, `src/cpp/ripple/RPCHandler.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/cpp/ripple/RPCHandler.cpp`, `src/cpp/ripple/main.cpp`. The strongest project-level identifiers around this patch are `Json::Value`, `RPCHandler::GUEST`, `Json`, and `RPCHandler::ADMIN`. Nearby tests or test-like files include `src/cpp/websocketpp/websocketpp.xcodeproj/xcuserdata/jcar.xcuserdatad/xcschemes/fuzzing_server.xcscheme`, `src/cpp/websocketpp/websocketpp.xcodeproj/xcuserdata/jcar.xcuserdatad/xcschemes/fuzzing_client.xcscheme`.

## Before/After Behavior

Before the patch, non-public WebSocket RPC requests were dispatched as RPCHandler::ADMIN, and HTTP RPC connections from 127.0.0.1 were assigned RPCHandler::ADMIN during connection setup. After the patch, WebSocket RPC computes a role with iAdminGet for non-public handling and returns rpcFORBIDDEN for FORBID, while HTTP RPC assigns mRole in handleRequest using iAdminGet with the parsed request and remote endpoint address. The command-line client-side rpc_user/rpc_password requirement was removed, but that alone is not evidence of a server-side vulnerability fix.

# Root Cause

The supported root cause is reliance on coarse connection or interface properties for RPC admin role assignment rather than a request-specific authorization decision. The evidence does not prove that those properties were attacker-controllable or outside the intended trust boundary.

## Walkthrough

1. Review the WebSocket RPC hunk: before, non-public handlers passed RPCHandler::ADMIN directly to doCommand; after, they call iAdminGet and handle RPCHandler::FORBID.

2. Review the HTTP RPC connection hunk: before, 127.0.0.1 connections were marked ADMIN at connection setup; after, that assignment is removed.

3. Review the HTTP RPC request hunk: after, mRole is assigned by iAdminGet using the parsed request and remote endpoint address.

4. Treat the CallRPC.cpp removal as supporting the model change, not as root-cause evidence by itself.

5. Bound the claim: the evidence supports a security-relevant admin authorization model change, but not a confirmed remote exploit or specific admin-method impact.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/cpp/ripple/WSConnection.h | 93 | WebSocket RPC request handler now computes request role with iAdminGet for non-public interfaces and blocks RPCHandler::FORBID before doCommand. |
| src/cpp/ripple/RPCServer.cpp | 33 | HTTP RPC connection setup no longer grants ADMIN solely because the peer address is 127.0.0.1. |
| src/cpp/ripple/RPCServer.cpp | 130 | HTTP RPC request parsing now assigns mRole via iAdminGet using the parsed request and remote endpoint address. |
| src/cpp/ripple/CallRPC.cpp | 566 | Command-line RPC client no longer requires configured rpc_user/rpc_password before building a request, aligning with the changed admin access model rather than acting as the server-side gate. |

## Code Snippets

## Snippet 1

Context: `src/cpp/ripple/WSConnection.h:93` (changes an authorization or privilege gate)

Before
```c
Json::Value	jvResult(Json::objectValue);

		jvResult["result"] = mRPCHandler.doCommand(
			jvRequest,
			mHandler->getPublic() ? RPCHandler::GUEST : RPCHandler::ADMIN);

		// Currently we will simply unwrap errors returned by the RPC
```
After
```c
Json::Value	jvResult(Json::objectValue);

		int iRole	= mHandler->getPublic()
						? RPCHandler::GUEST		// Don't check on the public interface.
						: iAdminGet(jvRequest, "127.0.0.1");	// XXX Fix this to return the remote IP.

		if (RPCHandler::FORBID == iRole)
		{
```

## Snippet 2

Context: `src/cpp/ripple/CallRPC.cpp:566` (changes an authorization or privilege gate)

Before
```cpp
Json::Value jvRpcParams(Json::arrayValue);

		if (theConfig.RPC_USER.empty() && theConfig.RPC_PASSWORD.empty())
			throw std::runtime_error("You must set rpcpassword=<password> in the configuration file. "
			"If the file does not exist, create it with owner-readable-only file permissions.");

		if (vCmd.empty()) return 1;												// 1 = print usage.
```
After
```cpp
Json::Value jvRpcParams(Json::arrayValue);

		if (vCmd.empty()) return 1;												// 1 = print usage.
```

## Snippet 3

Context: `src/cpp/ripple/RPCServer.cpp:130` (changes an authorization or privilege gate)

Before
```cpp
// Parse params
	Json::Value valParams = valRequest["params"];
	if (valParams.isNull())
		valParams = Json::Value(Json::arrayValue);
	else if (!valParams.isArray())
		return(HTTPReply(400, "params unparseable"));
```
After
```cpp
// Parse params
	Json::Value valParams = jvRequest["params"];

	if (valParams.isNull())
	{
		valParams = Json::Value(Json::arrayValue);
	}
```

## Snippet 4

Context: `src/cpp/ripple/RPCServer.cpp:33` (changes an authorization or privilege gate)

Before
```cpp
{
	//std::cerr << "RPC request" << std::endl;
	if (mSocket.remote_endpoint().address().to_string()=="127.0.0.1") mRole = RPCHandler::ADMIN;
	else mRole = RPCHandler::GUEST;

	boost::asio::async_read_until(mSocket, mLineBuffer, "\r\n",
		boost::bind(&RPCServer::handle_read_line, shared_from_this(), boost::asio::placeholders::error));
```
After
```cpp
{
	//std::cerr << "RPC request" << std::endl;
	boost::asio::async_read_until(mSocket, mLineBuffer, "\r\n",
		boost::bind(&RPCServer::handle_read_line, shared_from_this(), boost::asio::placeholders::error));
```

# Fix Pattern

Move RPC role assignment from connection/interface assumptions to request-time authorization checks, and reject forbidden requests before invoking the RPC command handler.

## How It Was Fixed

The patch removes HTTP connection-time ADMIN assignment based solely on 127.0.0.1, adds request-time role assignment through iAdminGet in RPCServer::handleRequest, changes WebSocket RPC handling to derive non-public roles through iAdminGet, and adds an explicit rpcFORBIDDEN response when iAdminGet returns RPCHandler::FORBID.

# Why It Matters

1. Reduces reliance on implicit trust in local address or non-public interface status.

2. Adds an explicit forbidden path before WebSocket RPC command dispatch.

3. Aligns HTTP and WebSocket RPC ingress paths around request-time authorization.

4. Does not by itself prove remote unauthenticated exploitability.

# Evidence Notes

Strong evidence: WSConnection.h changes direct ADMIN dispatch to iAdminGet plus FORBID handling; RPCServer.cpp removes localhost ADMIN assignment and adds iAdminGet in request handling. Limits: the provided input does not include iAdminGet implementation, full doCommand dispatch behavior, listener exposure, affected admin methods, or proof that localhost/non-public access was outside the intended trust boundary. The draft's 'confirmed security-fix' and 'admin-authz-bypass' labels are stronger than the evidence supports. Protocol security invariant: RPC admin privileges should be assigned through an explicit request-time authorization decision, and forbidden requests should be rejected before command dispatch. Verification notes: The patch does not prove that a remote unauthenticated attacker could reach the affected RPC listener. The patch does not show the full iAdminGet policy or credential validation rules. The patch does not identify which RPC methods were admin-only or what impact each method had. The evidence does not prove that localhost users were outside the intended trust boundary before the change. The CallRPC.cpp change alone is not a server-side authorization fix. No external inspection was performed per instruction. Exploitability is not established from the supplied hunks alone. CallRPC.cpp is supporting evidence only, not proof of a server-side access-control flaw. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The supplied patch evidence supports keeping this as security hardening: RPC admin role assignment is moved away from coarse interface or localhost assumptions and toward request-time authorization through iAdminGet, with an explicit FORBID path for WebSocket RPC. The evidence does not prove a concrete exploitable authorization bypass, so security-fix would be too strong, but the access-control tightening is clear enough for a security-focused corpus.

## Security Evidence

1. Commit subject explicitly says the RPC admin access security model changed.
2. WebSocket RPC no longer dispatches all non-public requests as RPCHandler::ADMIN and instead calls iAdminGet.
3. WebSocket RPC adds explicit handling for RPCHandler::FORBID before command dispatch.
4. HTTP RPC removes connection-time ADMIN assignment based solely on 127.0.0.1.
5. HTTP RPC later assigns mRole using iAdminGet with the parsed request and remote endpoint address.

## Missing Evidence

1. No iAdminGet implementation is supplied to confirm exact credential or policy behavior.
2. No evidence shows whether the affected RPC listeners were reachable by untrusted attackers.
3. No affected admin-only RPC methods or concrete privileged operations are identified.
4. No proof that localhost or non-public interface assumptions crossed the intended trust boundary.

## Claim Boundaries

1. Validate as security-hardening, not a confirmed exploitable security-fix.
2. Do not claim remote unauthenticated admin access from the supplied evidence alone.
3. Treat CallRPC.cpp as supporting model-change evidence, not standalone server-side authorization proof.
4. The supported claim is request-time RPC admin authorization tightening.
