from datetime import datetime
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.application.exception.base import CustomValidationError
from backend.application.forms.transaction import ManyTransactionReadForm, TransactionForm
from backend.application.transaction.create import CreateTransaction
from backend.application.transaction.read import ReadTransaction, ReadTransactions
from backend.bootstrap.di.providers.parsed_data import RequestBody
from backend.domain.misc_types import TransactionStatus
from backend.presentation.web.serializer import serializer

transactions_router = APIRouter(route_class=DishkaRoute)


@transactions_router.post("/")
async def create_transaction(
    interactor: FromDishka[CreateTransaction],
    form: RequestBody[TransactionForm],
) -> JSONResponse:
    result = await interactor.execute(form=form.data)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=201,
    )


@transactions_router.get("/")
async def read_transactions(
    interactor: FromDishka[ReadTransactions],
    page: Annotated[int, Query(ge=0)] = 0,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
    user_id: Annotated[str | None, Query(alias="userId")] = None,
    status: Annotated[TransactionStatus | None, Query()] = None,
    is_fraud: Annotated[bool | None, Query(alias="isFraud")] = None,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: Annotated[datetime | None, Query()] = None,
) -> JSONResponse:
    if user_id is None:
        u_id = user_id
    try:
        if isinstance(user_id, str):
            u_id = UUID(user_id)
    except ValueError as e:
        raise CustomValidationError(
            rejected_value=user_id,
            field="userId",
            issue="Неподходящий формат id",
        ) from e
    form = ManyTransactionReadForm(
        page=page,
        size=size,
        userId=u_id,
        status=status,
        isFraud=is_fraud,
    )
    if from_ is not None:
        form.from_ = from_
    if to is not None:
        form.to = to

    result = await interactor.execute(form=form)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )


@transactions_router.get("/{id}")
async def read_transaction(
    id: UUID,
    interactor: FromDishka[ReadTransaction],
) -> JSONResponse:
    result = await interactor.execute(id=id)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )
