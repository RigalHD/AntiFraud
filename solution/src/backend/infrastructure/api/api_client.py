import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from adaptix import NameStyle, Retort, dumper, name_mapping
from aiohttp import ClientSession
from descanso import RestBuilder
from descanso.client import AsyncResponseWrapper
from descanso.http.aiohttp import AiohttpClient
from descanso.request import HttpRequest
from descanso.response import BaseResponseTransformer
from descanso.response import HttpResponse as DescansoHttpResponse
from descanso.response_transformers import ErrorRaiser
from pydantic import EmailStr

from backend.application.forms.fraud_rule import (
    DSLValidationForm,
    FraudRuleForm,
    UpdateFraudRuleForm,
)
from backend.application.forms.transaction import TransactionForm
from backend.application.forms.user import AdminUserForm, UpdateUserForm, UserForm
from backend.application.fraud_rule.validate_dsl import DSLInfo
from backend.application.transaction.dto import TransactionDecision, TransactionsList
from backend.application.user.dto import UsersList
from backend.domain.entity.fraud_rule import FraudRule
from backend.domain.entity.user import User
from backend.infrastructure.api.models import APIResponse, PingResponse
from backend.infrastructure.auth.login import WebLoginForm
from backend.infrastructure.serialization.api_client import api_dump_serializer, api_load_serializer
from backend.presentation.web.controller.login import LoginResponse


class ApiResponseTransformer(BaseResponseTransformer):
    def need_response_body(self, response: DescansoHttpResponse) -> bool:
        return True

    def transform_response(
        self,
        request: HttpRequest,
        response: DescansoHttpResponse,
    ) -> DescansoHttpResponse:
        data = None
        http_response = {
            "status": response.status_code,
            "url": request.url.rstrip("/"),
        }
        error_data = None

        if response.status_code >= 200 and response.status_code < 300 and response.body:
            data = json.loads(response.body)
        elif response.status_code >= 400:
            error_data = json.loads(response.body)

        response.body = {
            "data": data,
            "httpResponse": http_response,
            "errorData": error_data,
        }

        return response


rest = RestBuilder(
    request_body_dumper=api_dump_serializer,
    response_body_loader=api_load_serializer,
    query_param_dumper=Retort(),
    response_body_pre_load=ApiResponseTransformer(),
)


class AntiFraudApiClient(AiohttpClient):
    def __init__(self, base_url: str, session: ClientSession, token: str | None = None) -> None:
        super().__init__(
            base_url=base_url,
            session=session,
        )
        self.token = token

    def authorize(self, token: str) -> None:
        self.token = token

    def reset_authorization(self) -> None:
        self.token = None

    @asynccontextmanager
    async def asend_request(
        self,
        request: HttpRequest,
    ) -> AsyncIterator[AsyncResponseWrapper]:
        if self.token is not None:
            request.headers["Authorization"] = f"Bearer {self.token}"

        async with super().asend_request(request) as response:
            yield response

    @rest.get("ping")
    def ping(self) -> APIResponse[PingResponse]:
        raise NotImplementedError

    @rest.get("error", error_raiser=ErrorRaiser(except_codes=(500,)))
    def error(self) -> APIResponse[None]:
        raise NotImplementedError

    @rest.post("auth/register", error_raiser=ErrorRaiser(except_codes=(201, 409, 422)))
    def register(self, body: UserForm) -> APIResponse[LoginResponse]:
        raise NotImplementedError

    @rest.post("auth/login", error_raiser=ErrorRaiser(except_codes=(200, 401, 422, 423)))
    def login(self, body: WebLoginForm) -> APIResponse[LoginResponse]:
        raise NotImplementedError

    @rest.post("users/", error_raiser=ErrorRaiser(except_codes=(201, 401, 403, 409, 422)))
    def create_user(self, body: AdminUserForm) -> APIResponse[User]:
        raise NotImplementedError

    @rest.get("users/me", error_raiser=ErrorRaiser(except_codes=(200, 401)))
    def read_user(self) -> APIResponse[User]:
        raise NotImplementedError

    @rest.get("users/", error_raiser=ErrorRaiser(except_codes=(200, 401, 403, 422)))
    def read_users(self, page: int = 0, size: int = 20) -> APIResponse[UsersList]:
        raise NotImplementedError

    @rest.get("users/{id}", error_raiser=ErrorRaiser(except_codes=(200, 401, 404, 403)))
    def read_user_by_id(self, id: UUID) -> APIResponse[User]:
        raise NotImplementedError

    @rest.put("users/me", error_raiser=ErrorRaiser(except_codes=(200, 401, 403, 422)))
    def update_user(self, body: UpdateUserForm) -> APIResponse[User]:
        raise NotImplementedError

    @rest.put("users/{id}", error_raiser=ErrorRaiser(except_codes=(200, 401, 403, 404, 422)))
    def update_user_by_id(self, id: UUID, body: UpdateUserForm) -> APIResponse[User]:
        raise NotImplementedError

    @rest.delete("users/{id}", error_raiser=ErrorRaiser(except_codes=(204, 401, 403, 404)))
    def delete_user(self, id: UUID) -> APIResponse[None]:
        raise NotImplementedError

    @rest.post("fraud-rules/", error_raiser=ErrorRaiser(except_codes=(201, 401, 403, 409, 422)))
    def create_fraud_rule(self, body: FraudRuleForm) -> APIResponse[FraudRule]:
        raise NotImplementedError

    @rest.get("fraud-rules/", error_raiser=ErrorRaiser(except_codes=(200, 401, 403)))
    def read_fraud_rules(self) -> APIResponse[list[FraudRule]]:
        raise NotImplementedError

    @rest.get("fraud-rules/{id}", error_raiser=ErrorRaiser(except_codes=(200, 401, 403, 404)))
    def read_fraud_rule(self, id: UUID) -> APIResponse[FraudRule]:
        raise NotImplementedError

    @rest.put(
        "fraud-rules/{id}",
        error_raiser=ErrorRaiser(except_codes=(200, 401, 403, 404, 409, 422)),
    )
    def update_fraud_rule(self, id: UUID, body: UpdateFraudRuleForm) -> APIResponse[FraudRule]:
        raise NotImplementedError

    @rest.delete("fraud-rules/{id}", error_raiser=ErrorRaiser(except_codes=(204, 401, 403, 404)))
    def delete_fraud_rule(self, id: UUID) -> APIResponse[None]:
        raise NotImplementedError

    @rest.post("fraud-rules/validate", error_raiser=ErrorRaiser(except_codes=(200, 401, 403)))
    def validate_dsl(self, body: DSLValidationForm) -> APIResponse[DSLInfo]:
        raise NotImplementedError

    @rest.post(
        "transactions/",
        error_raiser=ErrorRaiser(except_codes=(201, 401, 403, 404, 422)),
        request_body_dumper=Retort(
            recipe=[
                dumper(datetime, lambda x: x.strftime("%Y-%m-%dT%H:%M:%SZ")),
                dumper(EmailStr, str),
                name_mapping(name_style=NameStyle.CAMEL),
            ],
        ),
    )
    def create_transaction(self, body: TransactionForm) -> APIResponse[TransactionDecision]:
        raise NotImplementedError

    @rest.get(
        "transactions/{id}",
        error_raiser=ErrorRaiser(except_codes=(200, 401, 403, 404)),
    )
    def read_transaction(self, id: UUID) -> APIResponse[TransactionDecision]:
        raise NotImplementedError

    @rest.get(
        "transactions/",
        error_raiser=ErrorRaiser(except_codes=(200, 401, 422)),
    )
    def read_transactions(
        self,
        page: int = 0,
        size: int = 20,
        userId: UUID | None = None,  # noqa: N803  Пишу в спешке, фиксить некогда
        status: str | None = None,
        isFraud: bool | None = None,  # noqa: N803  Пишу в спешке, фиксить некогда
        from_: datetime | None = None,
        to: datetime | None = None,
    ) -> APIResponse[TransactionsList]:
        raise NotImplementedError
