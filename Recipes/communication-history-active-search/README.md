# Communication History Active Search

This recipe is a read-only Helix Lava Application pattern for browsing Rock
communications with server-owned status, type, text, and pagination filters.
It keeps the first implementation intentionally narrow: communication metadata
and aggregate recipient outcomes, with no message-body preview or write action.

The reference contains no ONE&ALL page IDs, routes, people, or production
configuration. Configure the optional detail page locally.

## What the Pattern Teaches

- Put the filter shell and the result query in separate endpoints so HTMX can
  replace only the table and pager.
- Allowlist enum filters and page sizes before they reach SQL, then pass search
  text through Lava SQL parameters rather than interpolating it.
- Reset pagination whenever a filter changes and keep pagination state in the
  shared filter form.
- Page communications before calculating per-communication recipient totals so
  aggregate work is bounded to the visible rows.
- Use Rock's actual communication status enum: transient `0`, draft `1`,
  pending approval `2`, approved `3`, and denied `4`. Approval is not itself a
  guarantee that every recipient was sent or delivered.
- Treat communication history as sensitive staff data even when the endpoint
  performs only reads.

## Files

- `src/list.lava`: filter form, initial render, and HTMX page state.
- `src/results.lava`: parameterized query, bounded pagination, result rows, and
  recipient aggregates.
- `config/configuration.example.json`: public-safe application rigging shape.
- `tests/static_contract.py`: executable query and public-safety invariants.
- `recipe.json`: machine-readable recipe metadata.
- `LICENSE`: license for this recipe package only.

## Adapt It

1. Create a Helix Lava Application named for the local communication history
   experience.
2. Add a GET `list` endpoint with ApplicationView security.
3. Add a GET `results` endpoint with ApplicationView security and the `Sql`
   Lava command enabled.
4. Copy `configuration.example.json` into application rigging. Set a local
   communication detail page only if authorized users should open records.
5. Update the two relative endpoint routes if the application slug changes.
6. Add a secured Rock page and render the `list` endpoint from its Lava
   Application Content block.
7. Test query plans and response times against local communication volume.

## Security Boundary

Both endpoints must require a Rock-authenticated staff session and permissions
appropriate for communication history. Read-only SQL still exposes names,
delivery outcomes, scheduling, and internal communication activity.

The example deliberately excludes message bodies, SMS text, recipient names,
addresses, phone numbers, and recipient-level errors. Adding any of those
requires separate privacy, authorization, and retention review. Do not add
approval, resend, cancel, or delete actions to this GET endpoint.

## Validation

- Unauthenticated and unauthorized users cannot load either endpoint.
- Status `3` is labeled Approved rather than Sent.
- Status, type, search, and page-size changes reset to page one.
- Invalid enum values fall back to all and invalid page sizes fall back to 25.
- Search text containing quotes, percent characters, or brackets cannot alter
  the SQL statement structure.
- No page can request more than 100 rows.
- Recipient aggregates match a sample of known communications.
- Transient communications and message bodies are absent.
- Empty results and the first/last page controls render correctly.

Run the static contract after adapting or updating the package:

```bash
python3 tests/static_contract.py
```

## Compatibility

The pattern uses standard Communication, CommunicationRecipient, PersonAlias,
and Person tables plus Helix Lava Application endpoint behavior. Verify enum
values, indexes, command security, and endpoint routing against the target Rock
release. The reference was last reviewed against the Rock 17/18 model family
in July 2026.

## Official References

- [Communication History and Analytics](https://community.rockrms.com/documentation/engagement/communications/communication-reports/communication-history-analytics)
- [Helix Lava Application Endpoints](https://community.rockrms.com/developer/helix/lava-applications/endpoints)
- [Rock Model Map](https://community.rockrms.com/modelmap)
