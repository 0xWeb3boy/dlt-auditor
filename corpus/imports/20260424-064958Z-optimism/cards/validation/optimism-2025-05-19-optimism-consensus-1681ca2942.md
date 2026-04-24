# Validation Card

## Metadata

- ID: `optimism-2025-05-19-optimism-consensus-1681ca2942`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- Removed code that set safe_block_hash and finalized_block_hash to the newly inserted payload during startup sync.
- Removed recovery logic that returned { un_safe, safe, finalized } all equal to the unsafe head.
- New startup logic searches backward from the unsafe head using L1-origin data instead of blindly promoting the current head.
- Sync completion now routes through engine reset/startup handling before derivation proceeds, indicating deliberate re-initialization of forkchoice state.

## What Could Have Invalidated It

- No proof that an attacker could reliably trigger the bad startup state in a real deployment.
- No evidence of an observed chain split, invalid finality acceptance, or fund-impacting consequence.
- No test or trace showing downstream consensus failure from the removed promotion behavior.
- No adversary model or network-reachability details are provided in the patch excerpts.

## Severity Guidance

- Expected impact band: host-filesystem-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an attacker could reliably trigger the bad startup state in a real deployment.
- No evidence of an observed chain split, invalid finality acceptance, or fund-impacting consequence.
- No test or trace showing downstream consensus failure from the removed promotion behavior.
