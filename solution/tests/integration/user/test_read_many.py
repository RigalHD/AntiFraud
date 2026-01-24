import asyncio
from uuid import UUID

import pytest

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.forms.user import AdminUserForm
from backend.domain.entity.user import User
from backend.domain.misc_types import Role
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception, validate_validation_error
from tests.utils.misc_types import AuthorizedUser


async def test_ok(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    admin_user_form: AdminUserForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    admin_user_form.role = Role.USER

    jobs = []
    for i in range(4):
        form = admin_user_form.model_copy(update={"email": f"user{i}@example.com"})
        jobs.append(api_client.create_user(form))

    users_dict: dict[UUID, User] = {
        response.expect_status(201).unwrap().id: response.unwrap() for response in await asyncio.gather(*jobs)
    }
    users_dict[admin_user.user.id] = admin_user.user

    resp_users = (await api_client.read_users(page=0, size=20)).expect_status(200).unwrap()

    assert len(resp_users.items) == 5
    assert resp_users.total == 5
    assert resp_users.page == 0
    assert resp_users.size == 20

    seen_ids = set()

    for user in resp_users.items:
        dict_user = users_dict.get(user.id)
        seen_ids.add(user.id)

        assert dict_user is not None
        assert user.id == dict_user.id
        assert user.email == dict_user.email
        assert user.full_name == dict_user.full_name
        assert user.age == dict_user.age
        assert user.region == dict_user.region
        assert user.gender == dict_user.gender
        assert user.marital_status == dict_user.marital_status
        assert user.role == dict_user.role
        assert user.is_active == dict_user.is_active
        assert user.updated_at == dict_user.updated_at
        assert user.created_at == dict_user.created_at

    assert seen_ids == set(users_dict.keys())


async def test_ok_page(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    admin_user_form: AdminUserForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    admin_user_form.role = Role.USER

    jobs = []
    for i in range(2):
        form = admin_user_form.model_copy(update={"email": f"user{i}@example.com"})
        jobs.append(api_client.create_user(form))

    [response.expect_status(201).unwrap() for response in await asyncio.gather(*jobs)]

    resp_users = (await api_client.read_users(page=1, size=1)).expect_status(200).unwrap()

    assert len(resp_users.items) == 1
    assert resp_users.total == 3
    assert resp_users.page == 1
    assert resp_users.size == 1


@pytest.mark.parametrize(
    ("page", "size"),
    [(-1, 10), (1, 0), (-1, -10), (0, 101)],
)
async def test_invalid_page_and_size(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    page: int,
    size: int,
) -> None:
    invalid_fields = {}
    if page < 0:
        invalid_fields["page"] = page
    if size <= 0 or size > 100:
        invalid_fields["size"] = size

    api_client.authorize(admin_user.access_token)

    err_data = (await api_client.read_users(page=page, size=size)).expect_status(422).err_unwrap()

    validate_validation_error(data=err_data, invalid_fields=invalid_fields)


async def test_no_auth(api_client: AntiFraudApiClient) -> None:
    error_data = (await api_client.read_users()).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_forbidd(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (await api_client.read_users()).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)
