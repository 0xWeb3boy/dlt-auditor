# Code-Shape Card

## Metadata

- ID: `reth-2023-04-12-reth-consensus-e87960ea8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-input-validation`

## Code Shape Summary

- The patch is well supported as a beacon-engine forkchoice/pipeline state-machine fix, but the provided evidence does not establish a concrete vulnerability. It moves the pipeline-run decision earlier and bases it on the full `ForkchoiceState`, including whether the announced head exists locally, rather than relying on a later fallback in payload processing.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
