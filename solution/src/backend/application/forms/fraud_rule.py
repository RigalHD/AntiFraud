from pydantic import Field

from backend.application.forms.base import BaseForm


class FraudRuleForm(BaseForm):
    name: str = Field(min_length=3, max_length=120)
    description: str = Field(max_length=500)
    dsl_expression: str = Field(alias="dslExpression", min_length=3, max_length=2000)
    enabled: bool = Field(default=True)
    priority: int = Field(ge=1)


class UpdateFraudRuleForm(FraudRuleForm):
    enabled: bool
