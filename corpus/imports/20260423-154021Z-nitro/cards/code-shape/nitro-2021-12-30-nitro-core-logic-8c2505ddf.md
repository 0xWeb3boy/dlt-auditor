# Code-Shape Card

## Metadata

- ID: `nitro-2021-12-30-nitro-core-logic-8c2505ddf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-management`

## Code Shape Summary

- Short description of what the buggy code looked like: The supplied diff supports validator-machine state-management hardening: validation now fetches a host-IO machine before cloning, and mutators now reject frozen machines. The evidence does not establish a concrete vulnerability, attacker trigger, or protocol-level security failure.

## Search Motifs

- Motif 1: clone or copy operations performed from cached machine pointers instead of freshly fetched canonical state
- Motif 2: mutator methods that do not check whether the machine is frozen or shared
- Motif 3: stateful VM helpers that reuse host-io or backing state across validation calls

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Fetch the canonical base object at use time and add fail-closed guards to mutating APIs so shared or frozen instances cannot be modified silently.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
