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
- Recheck and consume the challenge on the server immediately before the final
  action. A successful earlier browser step is not authorization.
- Keep the delivery code only as long as the workflow needs it to send the SMS.

## Files

- `src/verify-start.lava`: exact-match, rate-limit, and challenge activation.
- `src/verify-check.lava`: atomic attempt counting and code verification.
- `src/final-submit-recheck.lava`: one-time server-side challenge consumption.
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
   submission. Enable only the Lava commands each endpoint requires.
4. Copy `configuration.example.json` into application rigging and supply every
   local value. Do not add fallback production IDs to source.
5. Adapt the strict match fields to the form's actual risk. Do not weaken the
   match merely to increase match rate.
6. Place the final-submit recheck immediately before the action that uses the
   verified person context.
7. Add CSRF protection, anonymous abuse controls, TLS, authorization for any
   staff review surfaces, and an explicit data-retention decision.

## Security Boundary

The recipe verifies that someone receiving a short-lived code can complete the
specific form action. SMS can be intercepted or redirected and should not be
treated as strong identity proofing. Verification must remain optional unless
the organization has completed an appropriate risk and accessibility review.

The example hash reduces accidental plain-code exposure but does not protect a
six-digit code from an attacker who can read the database. Limit database
access, expire codes within ten minutes, accept each challenge once, count every
attempt, and do not reset failed-attempt history when resending.

Do not reveal whether a person exists. The sample returns a fake opaque session
for unmatched requests so the response shape remains consistent. Users can
still observe whether their own phone receives a message; pair the endpoint
with request throttling and monitoring.

## Validation

- Exact single match sends one code; zero or multiple matches send none.
- All start responses have the same status, message, and field shape.
- Invalid, expired, over-attempt, wrong-action, and consumed challenges fail.
- Two concurrent successful submissions cannot consume one challenge twice.
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
phone number, and Lava SQL/WorkflowActivate behavior. Verify command security,
transaction behavior, field types, communication retention, proxy-aware client
IP handling, and SQL Server support against the target Rock environment. The
reference was last reviewed against the Rock 17/18 model family in July 2026.

## Standards References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST SP 800-63B: Out-of-Band Authenticators](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
