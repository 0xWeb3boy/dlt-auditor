# Validation Card

## Metadata

- ID: `scroll-2023-03-27-scroll-storage-f26ab8b7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insecure-file-permissions`

## What Confirmed The Issue

- Evidence 1: In `bridge/cmd/app/mock_app.go`, the patch replaces `return os.WriteFile(b.bridgeFile, data, 0644)` with `return os.WriteFile(b.bridgeFile, data, 0600)`.
- Evidence 2: In `common/docker/docker_app.go`, the patch replaces `func (b *DockerApp) L1Client() (*ethclient.Client, error) {` with `func (b *App) L1Client() (*ethclient.Client, error) {`.
- Evidence 3: In `common/docker/docker_app.go`, the patch replaces `func (b *DockerApp) L2Client() (*ethclient.Client, error) {` with `func (b *App) L2Client() (*ethclient.Client, error) {`.

## What Could Have Invalidated It

- Compensating control 1: If the generated file contains only public test data and no privileged material, the case is usually just hygiene rather than security hardening.
- Compensating control 2: If the file lives in an isolated ephemeral sandbox where no other principal can read it, the practical security impact is much lower.
- Compensating control 3: Receiver renames or helper refactors in nearby files are not the core issue; the security-relevant part is the permission mode on the file write.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the generated file contains only public test data and no privileged material, the case is usually just hygiene rather than security hardening.
- Caution 2: If the file lives in an isolated ephemeral sandbox where no other principal can read it, the practical security impact is much lower.
- Caution 3: Receiver renames or helper refactors in nearby files are not the core issue; the security-relevant part is the permission mode on the file write.
