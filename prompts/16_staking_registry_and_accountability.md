# Prompt Family: Staking, Registry, And Accountability

## Use This For

- Slashability bypass.
- Missing stake or deposit enforcement.
- Incorrect voting power assignment.
- Burn-address or reserved-address invariant failures.
- Validator-election policy or accountability logic mismatches.
- Proposer or sequencer liveness accounting gaps.

If the repo does not have staking, use this prompt for the nearest equivalent economic or accountability layer:

- validator collateral,
- sequencer bonds,
- bridge relayer bonds,
- keeper whitelists with slashable obligations,
- committee deposits,
- fault attribution and penalty logic.

## Prompt

```text
Hunt for security bugs in the staking, registry, validator-selection, sequencing, and accountability logic of a blockchain or DLT system.

Focus on economic and accountability invariants, not just cryptography.

Prioritize:
- validator election
- voting power assignment
- node expiration and debonding interactions
- slashing and freeze windows
- validator, app, bridge, or runtime registration stake requirements
- special sink or reserved addresses
- proposer, sequencer, or committee liveness accounting

Search patterns:
- cleanup or expiry code that can remove slash-relevant state too early
- threshold or election parameters represented indirectly instead of as explicit validated consensus parameters
- voting power defaults or omissions when constructing validator sets
- validator, bridge, app, or node admission paths that do not check stake, bond, or deposit requirements
- transfers to reserved addresses that use the normal transfer path
- liveness accounting that is keyed by the wrong role or committee index space
- validator, operator, signer, committee, relayer, or node registration paths where an ID-to-signer or ID-to-owner mapping is checked through a value lookup rather than an explicit presence or absence predicate on the canonical registry key
- registry joins or reactivations that check signer uniqueness but not stable numeric ID, slot, operator ID, or historical participation identifiers that the protocol treats as non-reusable

Questions to answer:
1. What economic or accountability invariant is the protocol relying on?
2. Which state must persist long enough for slashing, debonding, challenge periods, or dispute resolution?
3. Are stake or bond requirements checked both at admission and while remaining active?
4. Are validator or committee sets built with the right voting power and threshold policy?
5. Are liveness and penalty paths scoped to the right members and time windows?

Severity guidance:
- High for slashability bypass or other failures that let a malicious actor avoid accountability.
- Medium for voting-power, stake-enforcement, or liveness-accounting correctness bugs.
```
