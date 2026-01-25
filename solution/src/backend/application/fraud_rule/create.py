from uuid import uuid4

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.exception.fraud_rule import FraudRuleNameAlreadyExistsError
from backend.application.forms.fraud_rule import FraudRuleForm
from backend.application.fraud_rule.validate_dsl import ValidateDSL
from backend.domain.entity.fraud_rule import FraudRule
from backend.domain.exception.dsl import DSLError
from backend.domain.misc_types import Role
from backend.domain.service.dsl.lex import Lexer
from backend.domain.service.dsl.normalize import ast_to_string
from backend.domain.service.dsl.parser import DSLParser


@interactor
class CreateFraudRule:
    uow: UoW
    gateway: FraudRuleGateway
    idp: UserIdProvider
    dsl_validator: ValidateDSL

    async def execute(self, form: FraudRuleForm) -> FraudRule:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        if await self.gateway.get_by_name(form.name):
            raise FraudRuleNameAlreadyExistsError(name=form.name)

        try:
            tokens = Lexer(form.dsl_expression).tokenize()
            ast = DSLParser(tokens).parse()
            dsl = ast_to_string(ast)
        except DSLError:
            dsl = form.dsl_expression

        fraud_rule = FraudRule(
            id=uuid4(),
            name=form.name,
            description=form.description,
            dsl_expression=dsl,
            priority=form.priority,
            enabled=form.enabled,
        )

        self.uow.add(fraud_rule)
        await self.uow.flush((fraud_rule,))
        await self.uow.commit()

        return fraud_rule
