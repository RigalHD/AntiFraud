COMPARATION_OPERATORS = (">", ">=", "<", "<=", "=", "!=")

STRING_COMPARATION_OPERATORS = ("=", "!=")


def is_dsl_valid(dsl_expression: str) -> bool:
    return False


def normalize_dsl(dsl_expression: str) -> str:
    for operator in COMPARATION_OPERATORS:
        dsl_expression.replace(operator, " " + operator + " ")

    dsl_expression = " ".join(dsl_expression.split())

    return dsl_expression
