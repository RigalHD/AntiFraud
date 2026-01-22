from pydantic import Field

from backend.application.forms.base import BaseForm


class PagginationForm(BaseForm):
    page: int = Field(ge=0)
    size: int = Field(ge=1, le=100)
