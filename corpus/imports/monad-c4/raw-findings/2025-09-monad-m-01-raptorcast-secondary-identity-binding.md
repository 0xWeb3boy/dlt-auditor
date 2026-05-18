---
id: monad-c4-2025-09-m-01
source: Code4rena 2025-09 Monad report
source_report: /testing/learning/2025-09-monad-report.md
report_date: 2026-02-26
audit_start_date: 2025-09-16
severity: medium
---

## [[M-01] Lack of authorization in RaptorCast Secondary protocol group messages allows arbitrary node impersonation leading to DoS](https://code4rena.com/audits/2025-09-monad/submissions/F-125)

*Submitted by [dontonka](https://code4rena.com/audits/2025-09-monad/submissions/S-623), also found by [0xAsen](https://code4rena.com/audits/2025-09-monad/submissions/S-103), [0xvd](https://code4rena.com/audits/2025-09-monad/submissions/S-385), [KeccakCrew](https://code4rena.com/audits/2025-09-monad/submissions/S-156), [luncy](https://code4rena.com/audits/2025-09-monad/submissions/S-854), and [zcai](https://code4rena.com/audits/2025-09-monad/submissions/S-924)*

- `bft/monad-raptorcast/src/raptorcast_secondary/client.rs`[#L256-L283](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-raptorcast/src/raptorcast_secondary/client.rs#L256-L283)
- `bft/monad-raptorcast/src/raptorcast_secondary/client.rs`[#L285-L393](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-raptorcast/src/raptorcast_secondary/client.rs#L285-L393)
- `bft/monad-raptorcast/src/raptorcast_secondary/publisher.rs`[#L305-L330](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-raptorcast/src/raptorcast_secondary/publisher.rs#L305-L330)

A vulnerability exists in the RaptorCast Secondary protocol’s group management system where **identity fields in messages are never validated against the cryptographic signature**. While messages are cryptographically signed and the signature is verified in RaptorCast, the protocol fails to check that the recovered public key matches identity claims within the message payload (such as `validator_id`, `node_id`, etc.) at the application level which opens the door for multiple DoS attacks. This can essentially **DoS the entire RaptorCast Secondary protocol**, meaning fullnode would most likely need to fallback on using BlockSync in order to get blocks information.

**The Protocol Flow**

```
┌─────────────┐                              ┌─────────────┐
│  Validator  │                              │  Full Node  │
│  (Alice)    │                              │    (Bob)    │
└──────┬──────┘                              └──────┬──────┘
       │                                            │
       │  1. PrepareGroup (Invitation)              │
       │    "Hey Bob, want to join my group         │
       │     for rounds 100-110?"                   │
       ├───────────────────────────────────────────>│
       │                                            │
       │  2. PrepareGroupResponse (RSVP)            │
       │    "Yes, I accept!"                        │
       │<───────────────────────────────────────────┤
       │                                            │
       │  3. ConfirmGroup (Finalize)                │
       │    "Great! The group is: Bob, Carol, Dave" │
       ├───────────────────────────────────────────>│
       │                                            │
       │  4. Now they can RaptorCast messages       │
       │    together for rounds 100-110             │
       ├═══════════════════════════════════════════>│
       │                                            │
```

### Attack Scenarios

This allows an attacker to:

- **PrepareGroup Impersonation**: impersonate any validator by sending a `PrepareGroup` message to fullnode with a victim’s `validator_id`. This can be used to block legitimate validators from grouping with fullnode (group slot exhaustion DoS - `max_num_group` is only 3). Another angle would be to fill `pending_confirms` with fake information which would waste resources (CPU, Memory). Reputation attack is also a concern.

```python
### Attack flow
1. Attacker generates own keypair (attacker_key)
2. Creates PrepareGroup message:
   {
     validator_id: victim_validator_pubkey,  # Impersonation!
     max_group_size: 10,
     start_round: 1000,
     end_round: 1240
   }
3. Signs message with attacker_key (NOT victim's key)
4. Sends to full nodes
5. Full nodes accept (no validation) and respond to ATTACKER
```

- **PrepareGroupResponse Injection**: impersonate any fullnode by sending `PrepareGroupResponse` messages to validator with a victim’s `node_id`.

  ```python
  ### Attack flow
  ```
- Attacker observes validator sending PrepareGroup (round 1000)
- Attacker generates 10 fake full node identities
- For each fake identity:
  Creates PrepareGroupResponse {
  req: PrepareGroup(validator*id=observed, start*round=1000, …),
  node*id: fake*fullnode*pubkey, # Impersonation!
  accept: true
  }
  Signs with attacker*key (NOT fake fullnode’s key)
  Sends to validator
- Validator processes all 10 responses (no validation)
- Validator attempts to create group with 10 members

- **ConfirmGroup Poisoning**: impersonate any validator by sending `ConfirmGroup` messages to fullnode with a victim’s `validator_id`.

  ```python
  ### Attack flow
  ```
- Attacker sends PrepareGroup as fake validator (rounds 1000-1240)
- Full node accepts and responds
- Attacker sends ConfirmGroup {
  prepare: PrepareGroup(validator*id=fake*validator, …),
  peers: [attacker*node*1, attacker*node*2, …], # Malicious peers!
  name*records: [fake*records*with*attacker_IPs]
  }
- Full node accepts ConfirmGroup (no validation)
- Full node updates peer discovery with attacker’s IPs
- Full node connects exclusively to attacker infrastructure


### Root Cause

The RaptorCast message handling performs two-stage validation:

```
Stage 1: Cryptographic Signature Validation ✅ IMPLEMENTED
  └─ Recovers public key from signature
  └─ Verifies signature is cryptographically valid
  └─ Result: "from" = recovered_pubkey

Stage 2: Identity Field Validation ❌ MISSING
  └─ Compare message.validator_id to "from" 
  └─ Compare message.node_id to "from"
  └─ Result: NEVER PERFORMED
```

The vulnerability exists because Stage 2 is completely missing.

### Impact

MEDIUM-LOW

- **DoS legitimate traffic**: while there is resource waste involved in those DoS attacks, the main impact is they allow the disabling of the `RaptorCast Secondary protocol` functionality, creating noise, degradation and confusion in the chain in terms of block propagation.

### Likelihood

HIGH

- Anyone can trigger this attack (see PoC), no need to be an official node in the chain (validator, full node, etc.), it simply requires connection to the node port, which is required to be open as this is how peers communicate together in Monad.
- There is no cost for this attack in terms of money, only very little resources are needed and very little effort to sustain it.

### Recommended mitigation steps

All three vulnerabilities stem from missing identity validation. **A single comprehensive fix addresses all impacts:**

This is not a working version of the mitigation (will not compile), but gives a good idea of what I have in mind.

```rust
// Unified fix for all three message types
fn validate_group_message_identity(
    msg: &FullNodesGroupMessage,
    recovered_pubkey: &PublicKey,
    validator_set: &ValidatorSet,
) -> Result<(), ValidationError> {
    match msg {
        FullNodesGroupMessage::PrepareGroup(prep) => {
            // Fix for Attack Vector 1
            if prep.validator_id.pubkey() != recovered_pubkey {
                return Err(ValidationError::ValidatorIdMismatch);
            }
            if !validator_set.contains(&prep.validator_id) {
                return Err(ValidationError::NotInValidatorSet);
            }
        }
        
        FullNodesGroupMessage::PrepareGroupResponse(resp) => {
            // Fix for Attack Vector 2
            if resp.node_id.pubkey() != recovered_pubkey {
                return Err(ValidationError::NodeIdMismatch);
            }
        }
        
        FullNodesGroupMessage::ConfirmGroup(conf) => {
            // Fix for Attack Vector 3
            if conf.prepare.validator_id.pubkey() != recovered_pubkey {
                return Err(ValidationError::ValidatorIdMismatch);
            }
            if !validator_set.contains(&conf.prepare.validator_id) {
                return Err(ValidationError::NotInValidatorSet);
            }
            
            // Validate peer list integrity
            if conf.peers.len() != conf.name_records.len() {
                return Err(ValidationError::PeerRecordMismatch);
            }
            for (peer, record) in conf.peers.iter().zip(&conf.name_records) {
                if record.recover_pubkey()? != *peer {
                    return Err(ValidationError::InvalidPeerSignature);
                }
            }
        }
    }
    
    Ok(())
}
```

[View detailed Proof of Concept](https://code4rena.com/audits/2025-09-monad/submissions/F-125)

---
