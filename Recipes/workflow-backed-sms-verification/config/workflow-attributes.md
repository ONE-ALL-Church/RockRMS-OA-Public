# Verification Workflow Contract

Create a persisted workflow type dedicated to SMS verification. Do not reuse a
business workflow that grants access or changes a person record.

## Workflow Attributes

| Key | Field type | Purpose |
| --- | --- | --- |
| `Candidate` | Person | Primary person alias selected by an exact, unique match. |
| `Code` | Text | Short-lived delivery value. Clear it immediately after the SMS action. |
| `CodeHash` | Text | SHA-256 digest checked by the verification endpoint. |
| `SessionGuid` | Text | Random challenge identifier returned to the browser. |
| `IntendedAction` | Text | Local action key that prevents using a challenge on another form. |
| `ExpiresAt` | Text or Date Time | UTC/local server expiration interpreted consistently by all endpoints. |
| `Attempts` | Integer | Failed and successful verification attempts. |
| `Verified` | Boolean | Set only by the verification endpoint. |
| `ConsumedAt` | Text or Date Time | Set once by the final-submit recheck. |
| `RequestIp` | Text | Bounded audit/rate-limit input; apply the organization's retention policy. |

## Activation Actions

1. Send `Code` by SMS to `Candidate` using an approved SMS transport.
2. Immediately clear `Code` from workflow state.
3. Complete the delivery activity without changing the candidate person.

The hash limits accidental disclosure of the code in workflow views and
exports. A six-digit code has low entropy, so the hash is not a defense against
an attacker who can read the database. Expiration, attempt limits, rate limits,
single use, transport security, and database access controls remain required.

Confirm whether the selected Rock communication action retains the rendered
SMS body in communication history. Apply an explicit retention decision rather
than assuming clearing the workflow attribute removes every copy.
