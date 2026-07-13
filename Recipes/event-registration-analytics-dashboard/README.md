# Event Registration Analytics Dashboard Recipe

This recipe is a read-only starting point for a secured Rock RMS Helix Lava
Application that summarizes one registration instance. It separates people
from registration records, shows capacity and weekly pace, keeps wait-list
counts explicit, and adds optional campus, fee-choice, demographic,
staff/serving, department, and prior-event comparisons.

The package is intentionally generic. It contains no production IDs, private
routes, people, organization branding, or working local defaults. Copy the
example configuration into the Lava Application rigging and replace only the
features your Rock instance can define and verify.

## What the Pattern Teaches

- Name the reporting grain. A registration can contain multiple registrants,
  so registered people and registration records are separate metrics.
- Define confirmed and wait-list populations once and reuse those predicates
  throughout the dashboard.
- Compare pace at the same event stage by aligning days remaining until the
  registration closes rather than comparing calendar dates.
- Make optional people segments mutually exclusive through explicit
  precedence. This reference checks staff first, then a locally configured
  serving-verifier group, then the remaining population.
- Treat serving verification and department hierarchy as local configuration,
  not as universal Rock behavior.
- Use registration fee items as breakout or option choices only after
  confirming that the target template models selections that way.
- Keep source values intact. Optional label cleanup affects dashboard output
  only and does not modify fee-item names.
- Use semantic HTML and CSS for compact charts so values remain selectable,
  printable, and available to assistive technology.
- Protect a read-only staff dashboard as sensitive data even when contact
  details and free-text answers are omitted.

## Files

- `src/dashboard.lava`: runnable reference endpoint and responsive dashboard.
- `config/configuration.example.json`: application-rigging contract with
  invalid or disabled defaults.
- `tests/static_contract.py`: public-boundary and query-safety checks.
- `recipe.json`: machine-readable external recipe metadata.
- `LICENSE`: license for this recipe package only.

## Required Adaptation

1. Create a Helix Lava Application with a secured GET endpoint. Enable only the
   `Sql` Lava command on the endpoint.
2. Copy `configuration.example.json` into its configuration rigging.
3. Set `registrationInstanceId` to a locally verified registration instance.
   The endpoint stops with an adaptation message while this value is zero.
4. Review capacity. The query prefers `RegistrationInstance.MaxAttendees` and
   uses `capacityFallback` only when the instance has no configured capacity.
5. Configure optional IDs only after confirming their model and meaning:
   registrant campus attribute, source attribute, staff group, serving-verifier
   group, serving root group, and department group type.
6. If fee items are not breakout choices, leave the fee panel unused or adapt
   it. Use `feeGroupNameContains` to limit fee groups when a template also has
   unrelated fees.
7. Copy `src/dashboard.lava` into the endpoint and render it from a Lava
   Application Content block on a staff-authorized page.
8. Run `python3 tests/static_contract.py`, then complete the live validation
   checklist below.

All numeric IDs are adaptation points. Do not copy IDs from another Rock
instance. Prefer a documented stable local lookup process and re-verify IDs
after migrations or restores.

## Metric Definitions

- **Registered people:** non-wait-list `RegistrationRegistrant` rows for the
  configured instance.
- **Registrations:** distinct `Registration` records containing at least one
  confirmed registrant.
- **Wait list:** registrants whose `OnWaitList` value is true.
- **Added in seven days:** confirmed registrants created during the rolling
  seven-day window.
- **Capacity:** instance `MaxAttendees`, with the configured fallback used only
  when that value is absent.
- **Prior same stage:** confirmed registrants in the optional prior instance as
  of the date that had the same number of days remaining before its end.
- **Campus/source:** optional registrant attributes. Persisted display text is
  preferred, with the stored value used as a fallback.
- **Segments:** optional, mutually exclusive classification using staff first,
  then serving verifier, then neither. With no verifier groups configured the
  dashboard reports one unclassified segment.
- **Departments:** optional active group memberships beneath a configured
  serving root. A person can appear in more than one department, so department
  totals are not expected to equal unique serving people.
- **Fee choices:** active fee items for the registration template. Active fee
  groups are shown, along with selected inactive fee groups when their active
  items still have confirmed selections.

Age bands use `BirthYear`, so they are suitable for broad operational
segmentation rather than exact birthday calculations.

## Security Boundary

This recipe issues read queries only. That does not make the page public-safe.

- Require a Rock-authenticated staff session.
- Restrict both page and Lava Application View authorization to approved roles.
- Enable only `Sql`; do not enable entity modification or workflow commands.
- Keep the endpoint GET-only while it is read-only.
- Omit email, phone, addresses, payment details, and arbitrary/free-text
  registration answers unless a separate privacy review explicitly approves
  them.
- Keep names and operational classifications behind staff authorization.
- A future write action requires a separate endpoint with authorization, CSRF
  protection, validation, audit logging, and rollback planning.

## Performance Boundary

The reference performs several bounded aggregate queries and returns at most
`maxRegistrantRows` drilldown rows. Test query plans and response time with a
representative production-sized instance. For large events, replace the local
drilldown filter with server-side filtering and pagination. Do not increase the
row cap without measuring database and browser cost.

## Validation

1. Confirm the registered-people count matches a known instance total.
2. Confirm registrations and people differ correctly for a multi-person
   registration.
3. Confirm wait-list people are excluded from every confirmed aggregate and
   remain visible in the separate wait-list metric and drilldown.
4. Confirm segment counts sum exactly to confirmed people.
5. Confirm a staff member who also satisfies serving verification appears only
   in staff.
6. Confirm campus/source values use the intended registrant attributes rather
   than person or registration campus by accident.
7. Confirm fee-item counts against known selections and review the configured
   active/historical behavior.
8. Confirm department totals disclose their many-to-many nature and the badge-
   only/unassigned bucket.
9. Confirm prior-stage comparison is disabled when no prior instance is set and
   aligns by days remaining when configured.
10. Confirm the drilldown cap, empty state, reset, and filters behave correctly.
11. Confirm unauthorized page access is denied and direct unauthorized endpoint
    access does not reveal data.
12. Confirm desktop and mobile layouts have no clipped labels or internal
    vertical scrolling, and confirm the browser console and Lava output contain
    no errors.

## Rollback

Disable or remove the Lava Application endpoint and page block, then restore
the previous page configuration. No data rollback is required because this
recipe performs no writes.

## Compatibility

The reference uses standard registration, person, attribute, fee, and group
tables plus SQL Server window functions and `STRING_AGG`. It was derived from a
production implementation on the Rock 17/18 model family in July 2026, but this
sanitized package still requires validation against the target Rock release,
schema, data volume, registration design, and authorization model.
