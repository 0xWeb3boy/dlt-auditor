---
case_id: case_20150119_e252c634c
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: high
date: 2015-01-19
source_refs:
  - git:e252c634cb40c8ef7f9bcd542f5418a937929620
  - "p2p/crypto.go:178"
  - "p2p/crypto.go:55"
  - "p2p/crypto_test.go:12"
  - "p2p/peer.go:223"
bug_class: public-key-validation
impact_type:
  - availability
confidence: medium
tags:
  - infrastructure
  - p2p-networking
  - p2p
  - crypto-handshake
  - public-key-validation
  - input-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a responder-side invalid-public-key check added during an in-progress p2p crypto handshake integration, not a clearly established vulnerability fix. The patch changes respondToHandshake to accept raw DER bytes, decode them locally, and return an error on invalid input, but the commit message and surrounding edits are dominated by refactoring/integration work and explicitly note the flow still crashes later in DH setup.

## Observed Patch Facts

1. In `p2p/crypto.go`, the patch replaces `func (self *cryptoId) respondToHandshake(auth, sessionToken []byte, remotePubKey *ecd...` with `func (self *cryptoId) respondToHandshake(auth, remotePubKeyDER, sessionToken []byte)...`.

2. In `p2p/crypto.go`, the patch replaces `func (self *cryptoId) Run(remotePubKeyDER []byte) (rw *secretRW) {` with `func (self *cryptoId) Run(conn io.ReadWriter, remotePubKeyDER []byte, sessionToken []...`.

3. In `p2p/crypto_test.go`, the patch replaces `prvInit, _ := crypto.GenerateKey()` with `prv0, _ := crypto.GenerateKey()`.

4. In `p2p/peer.go`, the patch replaces `var readLoop func(chan Msg, chan error, chan bool)` with `var readLoop func(chan<- Msg, chan<- error, <-chan bool)`.

## Project Context

Historical context from `p2p/protocol_test.go`, `p2p/testpoc7.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `p2p/protocol_test.go`, `p2p/testpoc7.go`. The strongest project-level identifiers around this patch are `byte`, `initiator`, `crypto`, and `cryptoId`.

## Before/After Behavior

Before the change, respondToHandshake accepted a caller-supplied *ecdsa.PublicKey and the shown code did not perform a local decode or nil-check at that entrypoint. After the change, respondToHandshake takes remotePubKeyDER, calls crypto.ToECDSAPub(remotePubKeyDER), and returns an "invalid public key" error if decoding fails. The Run API and peer wiring were also refactored to carry connection/session/role state through the handshake path.

# Root Cause

The only grounded issue shown is that the responder helper previously relied on a pre-parsed public key from its caller instead of decoding and rejecting invalid key bytes at the point of use. The provided evidence does not establish whether that was an exploitable security flaw or simply a correctness problem during handshake integration.

## Walkthrough

1. peer.loop continues to route peers into handleCryptoHandshake before traffic is treated as encrypted and authenticated.

2. cryptoId.Run is widened from a narrow helper shape to a fuller handshake entrypoint that carries connection, session token, and initiator state, indicating broader integration work.

3. On the responder path, the old respondToHandshake signature accepted a parsed remotePubKey pointer from the caller.

4. The new respondToHandshake signature accepts remotePubKeyDER, decodes it with crypto.ToECDSAPub, and returns an error if the result is nil.

5. The test updates rename and rebuild keypair setup, consistent with the commit message mentioning a wrong-pubkey test issue.

6. The commit message also says the code still crashes on DH in newSession, which cuts against treating this as a completed security fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| p2p/peer.go | 223 | peer event loop enters the crypto handshake path before encrypted/authenticated traffic is enabled |
| p2p/crypto.go | 55 | handshake orchestration API is refactored to take connection, session token, and initiator state |
| p2p/crypto.go | 178 | responder-side handshake now decodes the remote public key from DER and rejects invalid keys before further processing |
| p2p/crypto_test.go | 12 | test setup corrects which keypair is used, indicating the motivating failure was at least partly a correctness/integration issue |

## Code Snippets

## Snippet 1

Context: `p2p/crypto.go:178` (changes an authorization or privilege gate)

Before
```go
// verifyAuth is called by peer if it accepted (but not initiated) the connection
func (self *cryptoId) respondToHandshake(auth, sessionToken []byte, remotePubKey *ecdsa.PublicKey) (authResp []byte, respNonce []byte, initNonce []byte, randomPrvKey *ecdsa.PrivateKey, err error) {
	var msg []byte
	fmt.Printf("encrypted message received: %v %x\n used pubkey: %x\n", len(auth), auth, crypto.FromECDSAPub(self.pubKey))
	// they prove that msg is meant for me,
```
After
```go
// verifyAuth is called by peer if it accepted (but not initiated) the connection
func (self *cryptoId) respondToHandshake(auth, remotePubKeyDER, sessionToken []byte) (authResp []byte, respNonce []byte, initNonce []byte, randomPrivKey *ecdsa.PrivateKey, err error) {
	var msg []byte
	remotePubKey := crypto.ToECDSAPub(remotePubKeyDER)
	if remotePubKey == nil {
		err = fmt.Errorf("invalid public key")
		return
```

## Snippet 2

Context: `p2p/crypto.go:55` (changes an authorization or privilege gate)

Before
```go
}

func (self *cryptoId) Run(remotePubKeyDER []byte) (rw *secretRW) {
	if self.initiator {
		auth, initNonce, randomPrvKey, randomPubKey, err := initiator.initAuth(remotePubKeyDER, sessionToken)

		respNonce, remoteRandomPubKey, _, _ := initiator.verifyAuthResp(response)
	} else {
```
After
```go
}

func (self *cryptoId) Run(conn io.ReadWriter, remotePubKeyDER []byte, sessionToken []byte, initiator bool) (token []byte, rw *secretRW, err error) {
	var auth, initNonce, recNonce []byte
	var randomPrivKey *ecdsa.PrivateKey
	var remoteRandomPubKey *ecdsa.PublicKey
	if initiator {
		if auth, initNonce, randomPrivKey, _, err = self.startHandshake(remotePubKeyDER, sessionToken); err != nil {
```

## Snippet 3

Context: `p2p/crypto_test.go:12` (changes an authorization or privilege gate)

Before
```go
var err error
	var sessionToken []byte
	prvInit, _ := crypto.GenerateKey()
	pubInit := &prvInit.PublicKey
	prvResp, _ := crypto.GenerateKey()
	pubResp := &prvResp.PublicKey

	var initiator, responder *cryptoId
```
After
```go
var err error
	var sessionToken []byte
	prv0, _ := crypto.GenerateKey()
	pub0 := &prv0.PublicKey
	prv1, _ := crypto.GenerateKey()
	pub1 := &prv1.PublicKey

	var initiator, receiver *cryptoId
```

## Snippet 4

Context: `p2p/peer.go:223` (changes a sensitive control or state-update path)

Before
```go
defer p.conn.Close()

	var readLoop func(chan Msg, chan error, chan bool)
	if p.cryptoHandshake {
		if readLoop, err := p.handleCryptoHandshake(); err != nil {
			// from here on everything can be encrypted, authenticated
			return DiscProtocolError, err // no graceful disconnect
```
After
```go
defer p.conn.Close()

	var readLoop func(chan<- Msg, chan<- error, <-chan bool)
	if p.cryptoHandshake {
		if readLoop, err = p.handleCryptoHandshake(); err != nil {
			// from here on everything can be encrypted, authenticated
			return DiscProtocolError, err // no graceful disconnect
```

# Fix Pattern

Move key parsing to the trust boundary and fail closed on invalid key material, bundled with handshake API refactoring.

## How It Was Fixed

The responder handshake helper was changed to take raw remote public key bytes instead of a caller-provided parsed key. It now reconstructs the key locally and aborts with an error when decoding fails. Related handshake orchestration and peer-loop plumbing were updated to use the refactored interface.

# Why It Matters

1. Invalid remote key bytes are rejected earlier in the responder path.

2. The visible change is input validation, not a demonstrated auth-bypass or replay fix.

3. The surrounding patch is mostly integration work, so security impact is not established from this diff alone.

# Evidence Notes

Direct evidence is limited to p2p/crypto.go adding local DER decoding and an explicit nil-check in respondToHandshake, plus a broader Run refactor and minor peer/test updates. The commit subject emphasizes handshake integration and a wrong-pubkey test correction, and it states the code still crashes later during DH setup. Nothing in the provided diff proves exploitability, privilege impact, replay exposure, or confidentiality/integrity compromise. Protocol security invariant: Responder-side handshake code should reject invalid remote public key bytes before using that key in further handshake processing. Verification notes: The patch does not prove a network-reachable exploit, only that invalid key material is now rejected earlier. It does not show an authentication bypass, replay bug, or privilege escalation. It does not prove confidentiality or integrity loss; the observed failure mode may have been a crash or bad-session setup. Most of the diff is consistent with refactoring/integration, so the security intent is not established by the patch alone. The invalid-key rejection in respondToHandshake is directly supported by the shown before/after code. The broader Run and peer.loop changes support an integration/refactor reading of the patch. The test change supports a correctness issue around key selection but does not establish a security defect. No supplied evidence proves network-reachable exploitation or a completed vulnerability remediation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `public-key-validation`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `infrastructure, p2p-networking, p2p, crypto-handshake, public-key-validation, input-validation`

The patch adds a concrete fail-closed check in a security-sensitive p2p handshake path: the responder now decodes the remote public key itself and aborts on invalid key material. That supports retaining this as security hardening. However, the surrounding changes are clearly broader handshake integration/refactoring, the commit message describes a "first stab" and ongoing crashes, and the diff does not prove a completed fix for replay, signature validation, or another concrete exploitable vulnerability.

## Security Evidence

1. `respondToHandshake` now takes raw remote key bytes, decodes them locally, and returns `invalid public key` on failure.
2. The added check is in the responder side of the crypto handshake, before the connection is treated as encrypted/authenticated.
3. The change removes reliance on a caller-supplied parsed public key and tightens validation at the trust boundary.

## Missing Evidence

1. No proof that the prior behavior enabled exploitability rather than a correctness or crash-only issue.
2. No evidence of replay, signature bypass, privilege escalation, or confidentiality/integrity impact.
3. The commit message says the work is still incomplete and crashes later during DH/session setup.

## Claim Boundaries

1. Supported: this commit hardens responder-side public-key validation in a security-sensitive handshake path.
2. Not supported: this commit definitively fixes a replay, signature-validation, or request-forgery vulnerability.
3. Not supported: the patch alone proves a fully remediated, externally exploitable security bug.
