# Check-In Status Dashboard Recipe

This recipe is a read-only starting point for a Rock RMS Helix Lava Application
that combines an event registration roster, group-only placements, and the
latest qualifying check-in attendance for an operating date.

It is intentionally generic. It contains no ONE&ALL instance IDs, routes,
people, or production configuration. Copy the example configuration into the
Lava Application rigging and replace every placeholder with values verified in
your Rock instance.

## What the Pattern Teaches

- Start with the registration roster, then union active non-leader group
  members who are not already registered. This preserves valid manual
  placements without duplicating registered people.
- Resolve the latest attendance through `AttendanceOccurrence`, including its
  group, location, root group type, and operating date.
- Treat waitlist, missing placement, not checked in, and present as separate
  operational states. Do not invent a checked-out state unless the local
  workflow writes a trustworthy checkout signal.
- Perform filtering and sorting in the endpoint that owns the result data.
  Whitelist sort keys and make null placement/location values sort
  deterministically.
- Keep the first version read-only and omit phone, email, registration answers,
  and other sensitive details.

## Files

- `src/roster-status.lava`: runnable reference endpoint and simple table.
- `config/configuration.example.json`: required application rigging shape.
- `recipe.json`: machine-readable recipe metadata.
- `LICENSE`: license for this recipe package only.

## Adapt It

1. Create a Lava Application with a GET endpoint and application-view security.
2. Copy `configuration.example.json` into its configuration rigging.
3. Set `registrationInstanceId` and `groupTypeIds`; verify the three group
   attribute keys or remove fields your instance does not use.
4. Copy `src/roster-status.lava` into the endpoint.
5. Add your preferred UI around the returned rows. Keep query parameters
   allowlisted and server-owned.
6. Test with registered, waitlisted, group-only, missing-placement, present,
   and not-checked-in examples.

## Security Boundary

This code issues only read queries. That does not make the page public-safe.
Restrict the Rock page and Lava Application endpoint to the staff roles that
need the roster. Do not add contact information or registration answers without
a separate privacy and authorization review. Use GET only while the recipe is
read-only; a future write action needs Rock authorization, CSRF protection,
validation, audit logging, and a rollback design.

## Compatibility

The pattern uses standard registration, group membership, attendance,
attendance occurrence, location, and group attribute tables. It still requires
verification against the schema and check-in workflow of the Rock version being
used. The reference was last reviewed against the Rock 17/18 model family in
June 2026.
