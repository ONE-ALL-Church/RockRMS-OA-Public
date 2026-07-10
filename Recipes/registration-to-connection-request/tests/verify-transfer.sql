/*
Read-only verification for one registration-to-connection transfer.

Set all four values before running. This script performs no writes.
Use a read-only database principal whenever direct SQL access is permitted.
*/
DECLARE @RegistrationRegistrantId int = 0;
DECLARE @ConnectionOpportunityGuid uniqueidentifier = NULL;
DECLARE @SourceRegistrationAttributeKey nvarchar(100) = N'SourceRegistrationId';
DECLARE @MappedTargetAttributeKey nvarchar(100) = N'IntakeSummary';

IF @RegistrationRegistrantId <= 0 OR @ConnectionOpportunityGuid IS NULL
BEGIN
    THROW 50000, 'Set RegistrationRegistrantId and ConnectionOpportunityGuid before running.', 1;
END;

WITH RegistrantContext AS (
    SELECT
        rr.Id AS RegistrationRegistrantId,
        rr.RegistrationId,
        rr.PersonAliasId,
        r.CampusId AS RegistrationCampusId
    FROM RegistrationRegistrant rr
    INNER JOIN Registration r ON r.Id = rr.RegistrationId
    WHERE rr.Id = @RegistrationRegistrantId
),
CandidateRequests AS (
    SELECT
        rc.RegistrationRegistrantId,
        rc.RegistrationId,
        rc.PersonAliasId,
        rc.RegistrationCampusId,
        cr.Id AS ConnectionRequestId,
        cr.Guid AS ConnectionRequestGuid,
        cr.CampusId AS ConnectionRequestCampusId,
        cr.CreatedDateTime,
        sourceValue.Value AS SourceRegistrationValue,
        mappedValue.Value AS MappedTargetValue
    FROM RegistrantContext rc
    INNER JOIN ConnectionOpportunity opportunity
        ON opportunity.Guid = @ConnectionOpportunityGuid
    INNER JOIN ConnectionRequest cr
        ON cr.PersonAliasId = rc.PersonAliasId
       AND cr.ConnectionOpportunityId = opportunity.Id
    LEFT JOIN Attribute sourceAttribute
        ON sourceAttribute.EntityTypeId = 240
       AND sourceAttribute.[Key] = @SourceRegistrationAttributeKey
    LEFT JOIN AttributeValue sourceValue
        ON sourceValue.AttributeId = sourceAttribute.Id
       AND sourceValue.EntityId = cr.Id
    LEFT JOIN Attribute mappedAttribute
        ON mappedAttribute.EntityTypeId = 240
       AND mappedAttribute.[Key] = @MappedTargetAttributeKey
    LEFT JOIN AttributeValue mappedValue
        ON mappedValue.AttributeId = mappedAttribute.Id
       AND mappedValue.EntityId = cr.Id
    WHERE sourceValue.Value = CONVERT(nvarchar(50), rc.RegistrationId)
)
SELECT
    RegistrationRegistrantId,
    RegistrationId,
    ConnectionRequestId,
    ConnectionRequestGuid,
    RegistrationCampusId,
    ConnectionRequestCampusId,
    CASE
        WHEN RegistrationCampusId = ConnectionRequestCampusId THEN CAST(1 AS bit)
        WHEN RegistrationCampusId IS NULL AND ConnectionRequestCampusId IS NULL THEN CAST(1 AS bit)
        ELSE CAST(0 AS bit)
    END AS CampusMatches,
    SourceRegistrationValue,
    MappedTargetValue,
    CreatedDateTime,
    COUNT(*) OVER () AS MatchingRequestCount
FROM CandidateRequests
ORDER BY CreatedDateTime DESC, ConnectionRequestId DESC;

