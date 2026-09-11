INTERNAL_AI_STATUS:
INSUFFICIENT_CONTEXT

PUBLIC_STATUS:
REVIEW_REQUIRED

COMPLIANCE_STATUS:
INCONCLUSIVE

REVIEW_REQUIRED:
true

REVIEW_REASON:
LEGAL_CONTEXT_INSUFFICIENT

APPLICABLE_RULE_IDS:
PRESERVED

CANDIDATE_RULE_IDS:
NOT EXPOSED

PUBLIC_CONTRACT_CHANGED:
NO

BACKEND_CHANGED:
NO

DATABASE_CHANGED:
NO

MIGRATION_REQUIRED:
NO

AI_HTTP_TEST:
PASS

BACKEND_DESERIALIZATION:
PASS

DATABASE_PERSISTENCE:
FAIL

FULL FLOW:
FAIL

ADDITIONAL_DETAILS:
The AI response mapping fix was successfully implemented and passes all unit tests and direct AI endpoint HTTP tests. 
However, the controlled live flow (Frontend -> Backend -> AI -> OCR) failed at the **DATABASE_PERSISTENCE** stage due to an independent type mismatch error in the Backend. The AI returns `normalized_value` for `NET_QUANTITY` as an integer (`440`), but the PostgreSQL `declarations` table strictly expects a string (`VARCHAR`), resulting in: `<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $41: 440 (expected str, got int)`. 
Per your instructions, I have stopped and am reporting this independent blocker without modifying the Backend to make the test pass.
