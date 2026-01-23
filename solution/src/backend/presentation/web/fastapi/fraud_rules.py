from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.application.forms.fraud_rule import DSLValidationForm, FraudRuleForm, UpdateFraudRuleForm
from backend.application.fraud_rule.create import CreateFraudRule
from backend.application.fraud_rule.delete import DeleteFraudRule
from backend.application.fraud_rule.read import ReadFraudRule, ReadFraudRules
from backend.application.fraud_rule.update import UpdateFraudRule
from backend.application.fraud_rule.validate_dsl import ValidateDSL
from backend.bootstrap.di.providers.parsed_data import RequestBody
from backend.domain.entity.fraud_rule import FraudRule
from backend.presentation.web.serializer import serializer

fraud_rules_router = APIRouter(route_class=DishkaRoute)


@fraud_rules_router.post("/")
async def create_fraud_rule(
    interactor: FromDishka[CreateFraudRule],
    form: RequestBody[FraudRuleForm],
) -> JSONResponse:
    result = await interactor.execute(form.data)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=201,
    )


@fraud_rules_router.post("/validate")
async def validate_dsl(
    interactor: FromDishka[ValidateDSL],
    form: RequestBody[DSLValidationForm],
) -> JSONResponse:
    """DSL поддерживается на уровне 0."""
    result = interactor.execute(form.data.dsl_expression)
    return JSONResponse(
        content=serializer.dump(result),
        status_code=201,
    )


@fraud_rules_router.get("/")
async def read_fraud_rules(interactor: FromDishka[ReadFraudRules]) -> JSONResponse:
    result = await interactor.execute()

    return JSONResponse(
        content=serializer.dump(result, list[FraudRule]),
        status_code=200,
    )


@fraud_rules_router.get("/{id}")
async def read_fraud_rule(
    id: UUID,
    interactor: FromDishka[ReadFraudRule],
) -> JSONResponse:
    result = await interactor.execute(id)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )


@fraud_rules_router.put("/{id}")
async def update_fraud_rule(
    id: UUID,
    form: RequestBody[UpdateFraudRuleForm],
    interactor: FromDishka[UpdateFraudRule],
) -> JSONResponse:
    result = await interactor.execute(form=form.data, id=id)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )


@fraud_rules_router.delete("/{id}", status_code=204)
async def delete_fraud_rule(id: UUID, interactor: FromDishka[DeleteFraudRule]) -> None:
    await interactor.execute(id)
