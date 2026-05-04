# Validation Card

## Metadata

- ID: `snarkos-2023-06-15-snarkos-rpc-client-api-5cc2764ae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-deserialization`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Use bincode options with MAXIMUM_MESSAGE_SIZE, fixed integer encoding, and trailing-byte policy at each affected deserialize site.
- Root-cause evidence from the finding: The changed deserializers did not apply an explicit bincode decode limit when parsing peer message bytes. For messages containing collection-like fields such as block locators or peer lists, default deserialization could rely on encoded length metadata without the same explicit size policy used by the network codec. 1. A node message-specific `deserialize(bytes: BytesMut)` method receives bytes for ChallengeRequest, Ping, or PeerResponse. 2. Before the patch, the method passed the byte reader di

## What Could Have Invalidated It

- Transport rejects frames before deserializer sees them.
- Deserializer uses a bounded reader wrapper elsewhere.

## Severity Guidance

- Expected impact band: `availability`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls memory or CPU exhaustion during decode; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- A lower layer that already bounds the exact byte slice reduces but may not remove allocation risk
- Small fixed-size message structs are less concerning
- Non-peer test fixtures are not attack surface
