# Workflow-Backed SMS Verification for Anonymous Rock Forms

This recipe is a security-conscious starting point for optionally recognizing
an existing Rock person during an anonymous form. It verifies control of a
submitted SMS-enabled phone and binds that event to one intended form action.
It is not identity proofing, account authentication, or phishing-resistant MFA.

The reference is intentionally generic. It contains no ONE&ALL IDs, routes,
people, phone numbers, secrets, or production configuration.

## What the Pattern Teaches

- Require an exact, unique match before sending a code. Ambiguous matches fail
  closed instead of selecting an arbitrary person.
- Return a uniform browser response whether or not a match was found. Never
  return a person or alias identifier to the browser.
- Persist challenge state in a dedicated workflow: code hash, opaque session,
  intended action, expiration, attempts, verified state, and consumption time.
- Apply both person and request-source send limits. Add edge/WAF controls or a
  challenge mechanism when anonymous traffic warrants them.
- Recheck the challenge on the server immediately before the final action and
  use the opaque session as an idempotency key. A successful earlier browser
  step is not authorization.
- Keep the delivery code only as long as the workflow needs it to send the SMS.
- Keep endpoint SQL query-only. Write workflow state through Rock's
  `ModifyWorkflow` command so normal entity behavior and cache invalidation run.

## Files

- `src/verify-start.lava`: exact-match, rate-limit, and challenge activation.
- `src/verify-check.lava`: query-only validation plus modify-command state writes.
- `src/final-submit-recheck.lava`: final recheck, audit marker, and idempotency key.
- `config/configuration.example.json`: public-safe application rigging shape.
- `config/workflow-attributes.md`: required workflow contract and delivery flow.
- `tests/static_contract.py`: executable public-safety and security invariants.
- `recipe.json`: machine-readable recipe metadata.
- `LICENSE`: license for this recipe package only.

## Adapt It

1. Create the dedicated workflow and attributes in
   `config/workflow-attributes.md`.
2. Configure the workflow to send `Code` by SMS and then clear `Code`.
3. Create POST-only Lava Application endpoints for start, check, and final
   submission. Enable `Sql` and `WorkflowActivate` for start, then `Sql` and
   `ModifyWorkflow` for check and final submission. Do not enable unrelated
   commands.
4. Copy `configuration.example.json` into application rigging and supply every
   local value. Do not add fallback production IDs to source.
5. Adapt the strict match fields to the form's actual risk. Do not weaken the
   match merely to increase match rate.
6. Place the final-submit recheck immediately before the action that uses the
   verified person context. Make that action idempotent using
   `protectedActionIdempotencyKey`.
7. Add CSRF protection, anonymous abuse controls, TLS, authorization for any
   staff review surfaces, and an explicit data-retention decision.

## Security Boundary

The recipe verifies that someone receiving a short-lived code can complete the
specific form action. SMS can be intercepted or redirected and should not be
treated as strong identity proofing. Verification must remain optional unless
the organization has completed an appropriate risk and accessibility review.

The example hash reduces accidental plain-code exposure but does not protect a
six-digit code from an attacker who can read the database. Limit database
access, expire codes within ten minutes, count every attempt, and do not reset
failed-attempt history when resending.

The reference performs no SQL writes. `ModifyWorkflow` updates `Attempts`,
`Verified`, and `ConsumedAt`. Modify commands do not provide an atomic
compare-and-set guarantee, so two concurrent final requests can both pass the
recheck. The protected operation must reject a repeated
`protectedActionIdempotencyKey` or return the result created by the first call.
Use a purpose-built Rock action or API with an application-layer transaction
when strict exactly-once execution is required.

Do not reveal whether a person exists. The sample returns a fake opaque session
for unmatched requests so the response shape remains consistent. Users can
still observe whether their own phone receives a message; pair the endpoint
with request throttling and monitoring.

## Validation

- Exact single match sends one code; zero or multiple matches send none.
- All start responses have the same status, message, and field shape.
- Invalid, expired, over-attempt, wrong-action, and consumed challenges fail.
- Concurrent successful submissions use the same idempotency key and the
  protected action produces no duplicate business result.
- The browser never receives a person ID, alias ID, or alias GUID.
- Resends are limited per candidate and request source.
- The workflow clears `Code` after delivery and retention is reviewed wherever
  the rendered SMS may be stored.
- The final protected action cannot run without the server-side recheck.

Run the static contract after adapting or updating the package:

```bash
python3 tests/static_contract.py
```

## Compatibility

The pattern uses standard workflow, workflow attribute, person alias, person,
phone number, and Lava SQL, WorkflowActivate, and ModifyWorkflow behavior.
Verify command security, modify-result handling, field types, communication
retention, proxy-aware client IP handling, idempotency, and SQL Server support
against the target Rock environment. The reference was last reviewed against
the Rock 17/18 model family in July 2026.

## Standards References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST SP 800-63B: Out-of-Band Authenticators](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
