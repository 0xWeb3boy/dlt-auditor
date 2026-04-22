# Prompt Family: Input Validation And Invariant Enforcement

## Use This For

- Descriptor validation gaps.
- Malformed-input panics.
- Missing role-specific required fields.
- Policy-field acceptance before a protocol version enables it.
- Secret or rotation state accepted with weak validation.
- Unsafe debug configuration acceptance.

## Prompt

```text
Hunt for places where a blockchain or DLT system accepts malformed, incomplete, or semantically invalid input into privileged state.

Focus on:
- node, validator, committee, checkpoint, bridge, runtime, or descriptor objects
- policy, signer-set, bridge-set, capability, or governance-controlled objects
- genesis and sanity-check paths
- public key parsing and identity conversions
- secret publication, rotation, or replication state if the repo has such concepts
- version-gated fields, feature-gated flags, and fork-activated semantics

Search patterns:
- unmarshal functions that allow nil, empty, or wrong-length values
- role-specific fields that are optional in code but mandatory by protocol
- loops that validate only the first matching object instead of all relevant objects
- debug flags accepted without an explicit unsafe-mode acknowledgement
- helper functions that sanitize after state construction instead of rejecting bad input early
- policy fields accepted before the feature version or fork that defines them
- semantically duplicate selectors or identities, such as chain, fork, version, mode, batch, or task identifiers, that are parsed independently instead of canonicalized and compared
- metadata or derived-hash proxies used instead of the actual artifact bytes, bytecode, recovered sender, stored sequence, or canonical parsed object
- structured artifacts whose claimed identifier, hash, or version is accepted without recomputing it from the parsed canonical form before use
- duplicate parsers or encoders that reconstruct the same semantics in multiple places instead of one canonical path
- variable-length lists, blob streams, or nested objects that are consumed without asserting exact count, exact byte use, or no leftovers
- boundary code that aborts on malformed lengths, variants, or encodings instead of returning an ordinary validation failure
- state updates that derive the next value from request fields without first reading and comparing the current authoritative stored value

Questions to answer:
1. What structural invariants does the protocol require?
2. Which invariants are enforced only partially or only in some entrypoints?
3. Can malformed data panic a later helper instead of being rejected at decode time?
4. Does the path validate all advertised versions and members, or only one?
5. Are proposals, capabilities, secrets, or checkpoints scoped to the correct chain, domain, generation, epoch, or handoff context?
6. Is the code validating the real artifact, or only a proxy for it?
7. Does every consumer assert exact consumption and exact structural bounds, or can extra or mismatched data survive validation?
8. If the same protocol fact appears in more than one field or layer, does the code canonicalize them and enforce equality before continuing?

Severity guidance:
- High if bad validation can corrupt privileged committee, validator, bridge, prover, or secret-management behavior.
- Medium for malformed-input DoS and descriptor admission weaknesses.
- Low for local unsafe-configuration guards.
```
