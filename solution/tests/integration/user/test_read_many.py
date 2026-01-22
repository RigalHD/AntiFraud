import pytest

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception, validate_validation_error
from tests.utils.misc_types import AuthorizedUser


async def test_ok(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    authorized_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    users = (await api_client.read_users(page=0, size=20)).expect_status(200).unwrap()

    assert len(users.items) == 3
    assert users.total == 3
    assert users.page == 0
    assert users.size == 20

    users_dict = {
        admin_user.user.id: admin_user.user,
        authorized_user.user.id: authorized_user.user,
        another_authorized_user.user.id: another_authorized_user.user,
    }

    seen_ids = set()

    for user in users.items:
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
        assert user.created_at == dict_user.created_at

    expected_users = sorted(users_dict.values(), key=lambda u: u.created_at)
    
    assert seen_ids == set(users_dict.keys())
    assert users.items == expected_users


async def test_page(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    authorized_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    users = (await api_client.read_users(page=1, size=2)).expect_status(200).unwrap()

    users_list = [admin_user, authorized_user, another_authorized_user]
    users_list.sort(key=lambda x: x.user.created_at)

    assert len(users.items) == 1
    assert users.total == 3
    assert users.page == 1
    assert users.size == 2

    assert users.items[0] == users_list[-1].user


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


async def test_forbidden(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (await api_client.read_users()).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)
