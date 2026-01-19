from backend.application.forms.base import BaseForm
from backend.domain.misc_types import Gender, MaritalStatus
from pydantic import Field


class UserForm(BaseForm):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=72)
    fullName: str = Field(min_length=2, max_length=200)
    age: int | None = Field(default=None, ge=18, le=120)
    region: str | None = Field(default=None, max_length=32)
    gender: Gender | None = Field(default=None)
    maritalStatus: MaritalStatus | None = Field(default=None)
    