from backend.domain.exception.dsl import DSLUnsupportedLevelError


def validate_dsl(dsl_expresssion: str) -> None:
    if "NOT" in dsl_expresssion.upper() or "(" in dsl_expresssion or ")" in dsl_expresssion:
        raise DSLUnsupportedLevelError("Неподдерживаемый уровень DSL: 4")

    if "user.age" in dsl_expresssion.lower() or "user.region" in dsl_expresssion.lower():
        raise DSLUnsupportedLevelError("Неподдерживаемый уровень DSL: 5")
