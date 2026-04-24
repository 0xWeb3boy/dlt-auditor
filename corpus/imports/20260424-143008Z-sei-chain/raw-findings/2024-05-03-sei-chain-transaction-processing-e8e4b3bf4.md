---
case_id: case_20240503_e8e4b3bf4
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2024-05-03
source_refs:
  - git:e8e4b3bf43a99e47ea2d7ca287089cd1fc0ff47e
  - "evmrpc/subscribe.go:90"
  - "evmrpc/config.go:229"
  - "evmrpc/config_test.go:90"
  - "evmrpc/server.go:155"
bug_class: missing-resource-limit
impact_type:
  - availability-hardening
tags:
  - rpc
  - websocket
  - subscription-limit
  - resource-control
  - availability-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best characterized as likely denial-of-service hardening for the EVM RPC websocket subscription path. It adds a configuration-backed limit for eth_newHeads subscriptions, passes that limit into SubscriptionAPI, and rejects new subscriptions once the tracked listener count reaches the configured maximum. The evidence supports resource-control hardening, but not a confirmed exploitable vulnerability or concrete availability impact.

## Observed Patch Facts

1. In `evmrpc/subscribe.go`, the patch replaces `go func() {` with `a.newHeadListenersMtx.Lock()`.

2. In `evmrpc/config.go`, the patch adds `if v := opts.Get(flagMaxSubscriptionsNewHead); v != nil {`.

3. In `evmrpc/config_test.go`, the patch adds `if k == "evm.max_subscriptions_new_head" {`.

4. In `evmrpc/server.go`, the patch replaces `Service: NewSubscriptionAPI(tmClient, &LogFetcher{tmClient: tmClient, k: k, ctxProvid...` with `Service: NewSubscriptionAPI(tmClient, &LogFetcher{tmClient: tmClient, k: k, ctxProvid...`.

## Project Context

Historical context from `evmrpc/txpool.go`, `evmrpc/tx.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `evmrpc/txpool.go`, `evmrpc/tx.go`. The strongest project-level identifiers around this patch are `config`, `tmClient`, `ctxProvider`, and `rpcSub`.

## Before/After Behavior

Before the patch, the supplied NewHeads evidence shows creation of an RPC subscription and listener channel without a visible maximum-subscription check before continuing toward listener handling. After the patch, NewHeads locks newHeadListenersMtx, checks len(newHeadListeners) against newHeadLimit, returns an error if the limit is reached, and only then inserts the listener into newHeadListeners. The patch also reads evm.max_subscriptions_new_head into Config.MaxSubscriptionsNewHead and passes it into SubscriptionConfig when constructing the websocket subscription API.

# Root Cause

The eth_newHeads subscription path did not show enforcement of a configured upper bound on active new-head listeners before listener registration, and the new-head subscription limit was not wired through the shown config/server construction path.

## Walkthrough

1. A websocket subscription request reaches SubscriptionAPI.NewHeads.

2. The function creates an RPC subscription and allocates a listener channel.

3. The pre-patch evidence does not show a limit check before the listener path proceeds.

4. The patch enters a mutex-protected section before registering the listener.

5. The code rejects the request if the active listener count is at or above newHeadLimit.

6. The configured limit is read from evm.max_subscriptions_new_head and passed into SubscriptionConfig.newHeadLimit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| evmrpc/subscribe.go | 90 | enforces the configured newHeads subscription limit before registering a listener |
| evmrpc/config.go | 229 | reads evm.max_subscriptions_new_head into runtime configuration |
| evmrpc/server.go | 155 | passes MaxSubscriptionsNewHead into the websocket SubscriptionAPI configuration |
| evmrpc/config_test.go | 90 | updates test option lookup for the new subscription limit setting |

## Code Snippets

## Snippet 1

Context: `evmrpc/subscribe.go:90` (changes a sensitive control or state-update path)

Before
```go
rpcSub := notifier.CreateSubscription()
	listener := make(chan map[string]interface{})

	go func() {
```
After
```go
rpcSub := notifier.CreateSubscription()
	listener := make(chan map[string]interface{})
	a.newHeadListenersMtx.Lock()
	defer a.newHeadListenersMtx.Unlock()
	if uint64(len(a.newHeadListeners)) >= a.subscriptonConfig.newHeadLimit {
		return nil, errors.New("no new subscription can be created")
	}
	a.newHeadListeners[rpcSub.ID] = listener
```

## Snippet 2

Context: `evmrpc/config.go:229` (changes a sensitive control or state-update path)

Before
```go
}
	}
	return cfg, nil
}
```
After
```go
}
	}
	if v := opts.Get(flagMaxSubscriptionsNewHead); v != nil {
		if cfg.MaxSubscriptionsNewHead, err = cast.ToUint64E(v); err != nil {
			return cfg, err
		}
	}
	return cfg, nil
```

## Snippet 3

Context: `evmrpc/config_test.go:90` (changes a sensitive control or state-update path)

Before
```go
return o.maxBlocksForLog
	}
	panic("unknown key")
}
```
After
```go
return o.maxBlocksForLog
	}
	if k == "evm.max_subscriptions_new_head" {
		return o.maxSubscriptionsNewHead
	}
	panic("unknown key")
}
```

## Snippet 4

Context: `evmrpc/server.go:155` (changes bounds, limits, or capacity handling)

Before
```go
{
			Namespace: "eth",
			Service:   NewSubscriptionAPI(tmClient, &LogFetcher{tmClient: tmClient, k: k, ctxProvider: ctxProvider}, &SubscriptionConfig{subscriptionCapacity: 100}, &FilterConfig{timeout: config.FilterTimeout, maxLog: config.MaxLogNoBlock, maxBlock: config.MaxBlocksForLog}),
		},
		{
```
After
```go
{
			Namespace: "eth",
			Service:   NewSubscriptionAPI(tmClient, &LogFetcher{tmClient: tmClient, k: k, ctxProvider: ctxProvider}, &SubscriptionConfig{subscriptionCapacity: 100, newHeadLimit: config.MaxSubscriptionsNewHead}, &FilterConfig{timeout: config.FilterTimeout, maxLog: config.MaxLogNoBlock, maxBlock: config.MaxBlocksForLog}),
		},
		{
```

# Fix Pattern

Add a configuration-backed resource limit at the allocation/registration point, and perform the count-and-insert sequence under the mutex protecting the listener map.

## How It Was Fixed

The patch parses flagMaxSubscriptionsNewHead into Config.MaxSubscriptionsNewHead, passes that value to NewSubscriptionAPI via SubscriptionConfig.newHeadLimit, and updates SubscriptionAPI.NewHeads to check the active newHeadListeners count under newHeadListenersMtx before inserting a new listener. Tests were updated to recognize the new config key.

# Why It Matters

1. Bounds active server-side eth_newHeads listener registration.

2. Rejects excess subscriptions before insertion into the tracked listener map.

3. Reduces plausible resource-exhaustion risk in the websocket subscription service.

4. Does not establish consensus, transaction execution, or funds-safety impact.

# Evidence Notes

Grounded evidence is limited to evmrpc/subscribe.go, evmrpc/config.go, evmrpc/server.go, and evmrpc/config_test.go. The evidence supports a resource-control hardening interpretation. It does not prove remote unauthenticated exploitability, actual memory or goroutine exhaustion, the default limit value, behavior when the limit is zero, or impact beyond eth_newHeads subscriptions. Protocol security invariant: The EVM RPC websocket eth_newHeads subscription path should bound active server-side new-head listeners before registering another listener. Verification notes: Does not prove remote unauthenticated exploitability. Does not prove actual memory, goroutine, or node availability impact. Does not show the default limit value or whether zero has special behavior. Does not indicate consensus, transaction execution, or funds-safety impact. Does not prove broader subscription types are limited, only newHeads is shown. Classified as likely security-hardening, not a confirmed security fix. Downgraded confidence from high to medium because exploitability and impact are not shown. Kept subsystem scoped to EVM RPC websocket subscriptions rather than transaction processing. Kept bug class as missing-resource-limit because the patch directly adds and enforces a subscription count limit. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-resource-limit`
Final impact type: `availability-hardening`
Final tags: `rpc, websocket, subscription-limit, resource-control, availability-hardening`

The supplied patch evidence supports retaining this as security hardening, not a confirmed security fix. The change adds a configuration-backed maximum for eth_newHeads websocket subscriptions and enforces it before registering a new listener, which is a clear resource-control tightening on an exposed RPC subscription path. The evidence does not prove exploitability, default exposure, or an actual denial-of-service incident, so the finding should remain scoped to availability hardening.

## Security Evidence

1. Adds a newHeadLimit check before inserting into newHeadListeners.
2. Performs the listener count check and insertion under newHeadListenersMtx.
3. Wires evm.max_subscriptions_new_head from config into SubscriptionConfig.
4. Rejects excess subscription creation with an error instead of registering another listener.
5. The affected API is an eth websocket subscription path that allocates server-side listener state.

## Missing Evidence

1. No proof that the websocket RPC endpoint is unauthenticated or publicly exposed.
2. No demonstrated memory, goroutine, file descriptor, or node availability exhaustion.
3. No default value for MaxSubscriptionsNewHead is shown.
4. No evidence of an advisory, CVE, exploit report, or incident.
5. No evidence that other subscription types were affected.

## Claim Boundaries

1. Classify as resource-limit hardening for eth_newHeads subscriptions only.
2. Do not claim a confirmed exploitable denial-of-service vulnerability.
3. Do not claim consensus, transaction execution, or funds-safety impact.
4. Do not generalize the fix to all RPC subscriptions.
5. Do not rely on the transaction-processing subsystem label; the shown code is EVM RPC websocket subscription handling.
