# Prompt Family: Reinitializer Cross-Domain Double Withdrawal

## Use This For

- Upgrade or reinitializer windows that reset messenger sender/replay state while a failed value-bearing withdrawal is being retried.
- Front-running signed governance upgrades by executing them inside a withdrawal/messenger call.

## Prompt

```text
Hunt specifically for double successful value delivery caused by upgrade/reinitializer execution during cross-domain withdrawal replay.

This is narrower than generic migration mismatch. Do not count zero-value replay, stranded withdrawals, impossible finalization, or legacy-only key mismatch unless the same value can be delivered twice.

Build the exact reentrancy trace:
1. A value-bearing withdrawal/message has previously failed and is eligible for replay.
2. The replay enters the L1 messenger/bridge path and sets the active cross-domain sender or equivalent in-progress replay guard.
3. The target call reaches attacker-controlled code.
4. Attacker-controlled code executes or triggers a signed/proposed upgrade, proxy upgrade, initializer, or reinitializer.
5. The upgrade/reinitializer resets `xDomainMsgSender`, replay guard, or equivalent in-progress state to the default value.
6. The attacker reenters the messenger/bridge with the same failed message.
7. Both the outer and inner paths can deliver value or otherwise mark success under compatible replay/finality checks.

Required table:
- withdrawal/message hash and versioned hash
- failed-message key before replay
- successful-message key before replay
- in-progress sender/guard before target call
- initializer/reinitializer that resets the guard
- who can execute the upgrade transaction and whether it can be front-run/nested
- inner replay acceptance condition
- outer replay completion condition
- value held by messenger/bridge before, after inner delivery, and after outer delivery
- final replay maps and delivered amounts

Search patterns:
- `initializer` or `reinitializer` functions that write `xDomainMsgSender` or replay guard state;
- upgrade scripts or multisig batches callable through ordinary target code;
- target calls that can execute arbitrary calldata while a failed message is in progress;
- failed-message retry paths where success is marked after the external call;
- bridge finalizers that trust messenger authentication without independent per-message replay state.

Reporting discipline:
- Preserve adjacent migration/key mismatch findings separately, but keep searching until this exact nested upgrade/reinitializer path is proven or killed.
- A found issue must name two successful value-delivery paths, not just two accepted proofs.
- If killed, name the exact blocker: upgrade cannot be executed in-call, initializer cannot run twice, guard is not reset, failed-message check blocks inner replay, value is not held, or outer path cannot also complete.
```
