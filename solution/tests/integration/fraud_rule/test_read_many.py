import asyncio
from uuid import UUID

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.forms.fraud_rule import FraudRuleForm
from backend.domain.entity.fraud_rule import FraudRule
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule_form: FraudRuleForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    jobs = []
    for i in range(5):
        form = fraud_rule_form.model_copy(update={"name": f"{fraud_rule_form.name}{i}"})
        jobs.append(api_client.create_fraud_rule(form))

    rules_dict: dict[UUID, FraudRule] = {
        response.unwrap().id: response.unwrap() for response in await asyncio.gather(*jobs)
    }

    resp_rules = (await api_client.read_fraud_rules()).expect_status(200).unwrap()

    assert len(resp_rules) == 5

    seen_ids = set()

    for rule in resp_rules:
        dict_rule = rules_dict.get(rule.id)
        seen_ids.add(rule.id)

        assert dict_rule is not None
        assert rule.id == dict_rule.id
        assert rule.name == dict_rule.name
        assert rule.description == dict_rule.description
        assert rule.dsl_expression == dict_rule.dsl_expression
        assert rule.enabled == dict_rule.enabled
        assert rule.priority == dict_rule.priority
        assert rule.updated_at == dict_rule.updated_at
        assert rule.created_at == dict_rule.created_at

    assert seen_ids == set(rules_dict.keys())


async def test_no_auth(api_client: AntiFraudApiClient) -> None:
    error_data = (await api_client.read_fraud_rules()).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (await api_client.read_fraud_rules()).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)
