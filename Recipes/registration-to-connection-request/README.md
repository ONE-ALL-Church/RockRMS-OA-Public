# Registration-to-Connection Request Transfer Workflow

This recipe turns each new registrant in a selected Rock registration template
into a Connection Request. It is a generic starting point for applications,
care intake, classes, serving interest, and other processes where registration
collects structured information and Connections manages staff follow-up.

The package contains no ONE&ALL entity IDs, routes, people, secrets, or
production configuration. It is informed by multiple production registration
workflows, including one pattern with hundreds of completed runs, but must be
adapted and tested in a nonproduction Rock instance before use.

## What the Pattern Teaches

- Use `RegistrantWorkflowTypeId`, not the registration-level workflow setting,
  when one Connection Request should be created for each registrant.
- Accept Rock's `RegistrationRegistrantId` workflow input and resolve the
  person through `RegistrationRegistrant.PersonAlias`.
- Read campus from `RegistrationRegistrant.Registration.Campus.Guid` and wire
  it to Create Connection Request's `Campus Attribute`; do not silently fall
  back to the person's primary campus.
- Give every deployed type, activity, action, and attribute a stable
  `ForeignKey`, then re-query the canonical row after every modify operation.
- Store the numeric source Registration ID on the Connection Request. Build
  environment-specific admin links when rendering rather than persisting a
  hostname in data.
- Capture the created Connection Request in a workflow attribute before using
  native Set Entity Attribute actions to copy additional values.
- Resolve action settings by their stable system keys and verify that every
  referenced workflow-attribute GUID belongs to the same WorkflowType.
- Keep SQL read-only. Configuration writes use Rock entity commands and
  runtime writes use native workflow actions.

## Files

- `src/workflowtype-deploy.lava`: rerunnable workflow configuration deploy.
- `config/mapping.example.json`: public-safe mapping and adaptation contract.
- `tests/verify-transfer.sql`: bounded read-only end-to-end verifier.
- `tests/static_contract.py`: executable safety and portability assertions.
- `recipe.json`: machine-readable package metadata.
- `LICENSE`: license for this package.

## Before Deployment

1. Create or select the target Connection Type, Opportunity, and Status.
2. Add a Connection Request attribute for the source registration ID. Use an
   Integer field and a locally unique key such as `SourceRegistrationId`.
3. Add any other target Connection Request attributes needed by the mapping.
4. Create matching registration-template registrant attributes.
5. Copy `workflowtype-deploy.lava` to an admin-only Lava Application endpoint.
6. Replace every value in the `ADAPTATION REQUIRED` block. Keep the values in
   sync with `mapping.example.json`.
7. Enable only `RockEntity`, `RockEntityModify`, and `Sql` for the deployment
   endpoint. The SQL blocks only resolve configuration rows.

The reference deploy includes one illustrative attribute mapping. Duplicate
the read and Set Entity Attribute action pair for each additional field. Match
field types deliberately; do not copy arbitrary strings into date, boolean,
entity, or single-select attributes without normalization.

## Deploy Safely

1. Run the deploy against a nonproduction Rock instance.
2. Review the printed WorkflowType, attribute, activity, and action IDs.
3. Run the deploy a second time. It must reuse the same stable-key rows.
4. In the workflow editor, confirm every Create Connection Request setting
   references an attribute owned by the deployed workflow.
5. Attach the workflow as the registration template's **Registrant Workflow**.
   The deploy deliberately does not change the template.
6. Submit a marked test registration through the real public registration
   experience.
7. Run `tests/verify-transfer.sql` with the resulting registrant ID.

## Duplicate Policy

The native registration trigger normally starts one registrant workflow per
new registrant. The reference does not silently merge an existing Connection
Request. Manually rerunning or backfilling the same registrant can therefore
create a duplicate.

Before a backfill or retry, query the target request's source-registration
attribute. Choose and document one policy:

- skip when that source registration already has a request;
- update the existing request through a separately reviewed workflow; or
- create another request intentionally and record why.

The verifier reports duplicate requests for the configured source
registration. Do not add a broad delete or deduplication step to this recipe.

## Security Boundary

Deployment changes Rock configuration and runtime execution creates Connection
Requests and AttributeValues. Restrict the deployment endpoint to trusted Rock
administrators, require the normal authenticated Rock session and CSRF
protection, remove or disable the endpoint after use, and audit its page and
block permissions.

Registration answers and Connection Requests can contain pastoral, contact,
care, or other sensitive information. Copy only fields staff need for follow-up
and align page, connection, attribute, retention, and reporting permissions.
Never place live IDs, URLs, or sample person data in a public fork.

## Validation

- The deploy stops while required local GUIDs or mapping keys are blank.
- A second deploy creates no duplicate WorkflowType, activity, action, or
  workflow-attribute rows.
- Every native action-setting GUID resolves to an attribute qualified to the
  deployed WorkflowType.
- Person, opportunity, status, campus, comments, and output request settings
  point to the expected workflow attributes.
- A test registration creates exactly one request for the registrant.
- Request campus equals registration campus, including a deliberate null case.
- Source Registration ID equals `RegistrationRegistrant.RegistrationId`.
- The optional mapped value matches the source registrant attribute.
- The workflow completes only after the request and copied values are saved.

Run the package checks with:

```bash
python3 tests/static_contract.py
```

## Rollback

1. Remove the Registrant Workflow assignment from the registration template so
   new submissions stop launching the workflow.
2. Deactivate the deployed WorkflowType.
3. Restore any prior template workflow assignment.
4. Review test Connection Requests manually. Do not bulk-delete historical
   requests or AttributeValues through this recipe.
5. Remove the temporary admin deployment endpoint after the rollback is
   verified.

## Compatibility

The pattern was reviewed against Rock 17 and 18 system action and field-type
contracts. Verify the action classes, setting keys, field types, registration
trigger behavior, and Connection Request attribute qualifiers in the target
release. Third-party workflow actions are not required.

## Rock References

- [RegistrationTemplate model](https://github.com/SparkDevNetwork/Rock/blob/develop/Rock/Model/Event/RegistrationTemplate/RegistrationTemplate.cs)
- [Create Connection Request workflow action](https://github.com/SparkDevNetwork/Rock/blob/develop/Rock/Workflow/Action/Connections/CreateConnectionRequest.cs)
- [Rock Model Map](https://community.rockrms.com/modelmap)
