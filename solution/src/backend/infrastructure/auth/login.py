from pydantic import EmailStr, Field

from backend.application.forms.base import BaseForm


class WebLoginForm(BaseForm):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=8, max_length=72)
