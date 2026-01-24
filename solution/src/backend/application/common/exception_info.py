from backend.domain.exception.dsl import DSLError, DSLInvalidFieldError, DSLInvalidOperatorError, DSLParseError

DSL_ERRORS_CODES = {
    DSLError: "DSL_ERROR",
    DSLParseError: "DSL_PARSE_ERROR",
    DSLInvalidFieldError: "DSL_INVALID_FIELD",
    DSLInvalidOperatorError: "DSL_INVALID_OPERATOR",
}
