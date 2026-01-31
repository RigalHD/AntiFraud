# Anti-fraud REST API (Olympiad assignment)

The primary source of API requirements is the OpenAPI specification: `openapi.yml`.

## Quick start

- Recommended starting point (for beginners): `docs/getting-started.md`
- Full assignment description and scoring: `docs/assignment.md`
- DSL rules (support tiers, validation, execution): `docs/dsl.md`
- Local setup and quick testing: `docs/local-run.md`
- FAQ and common errors: `docs/faq.md`
- Glossary of terms: `docs/glossary.md`

## Repository structure

- `openapi.yml` — API specification
- `docs/` — assignment documentation (what to implement and how it is evaluated)

---

## Changelog

### v1.1.1 (Last task update)

- The `timezone` field returned to `GET /stats/transactions/timeseries`

### v1.1.0

- Clarified that filtering by `userId` is ignored for USER in `GET /transactions`
- The `timezone` field was removed from `GET /stats/overview` and `GET /stats/transactions/timeseries`
- Fixed minor typos.

### v1.0.9

- Clarified that the fields `amount` and `gmv` in `/transactions` and `/stats` are stored up to 2 decimal 
places (otherwise rounded according to the rules of mathematics)

### v1.0.8

- Added default value for `from` in `GET /transactions`
- Fixed minor typos.

### v1.0.7

- The mentions of `metadata` and `timestamp` have been removed from the DSL.
- Fixed minor typos.

### v1.0.6

- Clarified that the `near` and `position` fields in the `POST /fraud-rules/validate` are checked only for the presence of

### v1.0.5

- Validation rollback for `dslExpression` in `POST /fraud-rules`: the field is no longer validated.
- Added rule sorting for `GET /fraud-rules`: by `priority` (ASC).
- The `enabled` field has been removed from transaction results.
- Fixed minor typos.

### v1.0.4

- Clarified that `dslExpression` is validated in `POST /fraud-rules`, but detailed DSL validation errors are not returned
- Fixed validation of `ruleResults` in `POST /transactions`: no sorting by id
- Clarified that the `userId` field is required for `POST /transactions`
- Fixed minor typos.

### v1.0.3

- Changed user sorting specification for `GET /users`: by `createdAt` (ASC).
- Removed required response `{"status": "ok"}` for `GET /ping`
- Clarified the rule of formation `lastSeenAt` for `GET /stats/users/{id}/risk-profile`: any user action, including the creation of a user transaction by the administrator
- Fixed minor typos.

### v1.0.2

- Added error codes table with HTTP status mapping.
- Removed `USER_NOT_FOUND` error code, use `NOT_FOUND` instead.
- Removed `DSL_UNSUPPORTED_TIER` and `DSL_TOO_COMPLEX` error codes, along with all related logic.
- Clarified that `message` and `fieldErrors[].issue` content is not validated by autotests.
- Added user sorting specification for `GET /users`: by `id` (ASC).
- Added `page`/`size` validation rules (min/max) with 422 on invalid values.
- Clarified DSL normalization: redundant and logic-neutral parentheses are removed.
- Clarified `near` field: 2 characters before and 2 after the error position.
- Fixed minor typos.
- `gmv` is now required in MerchantRiskRow.

### v1.0.1

- OpenAPI: added `expiresIn` to auth response example, added 409 code for `PUT /fraud-rules/{id}`.
- OpenAPI: removed "if name uniqueness is enabled" wording - rule name uniqueness is now mandatory.
- Updated run examples in `local-run.md`.
- Fixed minor typos.
