from pydantic import EmailStr, Field

from backend.application.forms.base import BaseForm
from backend.domain.misc_types import Gender, MaritalStatus, Role


class UserForm(BaseForm):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=2, max_length=200, alias="fullName")
    age: int | None = Field(default=None, ge=18, le=120)
    region: str | None = Field(default=None, max_length=32)
    gender: Gender | None = Field(default=None)
    marital_status: MaritalStatus | None = Field(default=None, alias="maritalStatus")


class UpdateUserForm(BaseForm):
    full_name: str = Field(min_length=2, max_length=200, alias="fullName")
    age: int | None = Field(ge=18, le=120)
    region: str | None = Field(max_length=32)
    gender: Gender | None
    marital_status: MaritalStatus | None = Field(alias="maritalStatus")

    role: Role | None = Field(default=None)
    is_active: bool | None = Field(default=None)
