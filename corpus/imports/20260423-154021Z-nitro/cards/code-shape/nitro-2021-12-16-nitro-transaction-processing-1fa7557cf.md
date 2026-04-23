# Code-Shape Card

## Metadata

- ID: `nitro-2021-12-16-nitro-transaction-processing-1fa7557cf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-default-service-exposure`

## Code Shape Summary

- Short description of what the buggy code looked like: The provided diff supports a configuration refactor in node startup, not a demonstrated vulnerability fix. It consolidates broadcaster settings into NodeConfig, renames the CLI flags, and removes a separate CreateNode parameter for feed output configuration.

## Search Motifs

- Motif 1: security-sensitive listener or broadcaster settings moved into a generic node config object
- Motif 2: constructor arguments for an exposed service disappear during config refactors
- Motif 3: feature enablement becomes implicit when flags are renamed or consolidated

## Typical Asymmetry

- What was checked in one path but missing in another: Configuration or constructor cleanup moved a security-sensitive enable decision into ordinary startup plumbing, so the code still carried the settings but no longer kept an explicit exposure gate bound to service construction.

## Patch Pattern

- What the fix changed structurally: Configuration-source consolidation and API cleanup: move subsystem settings into the main node configuration object and require explicit enablement before instantiation.

## False Match Warnings

- What looks similar but is often not a bug: If deployment policy, bind addresses, or external ACLs still keep the service non-reachable, similar refactors may be operational rather than security-relevant.
