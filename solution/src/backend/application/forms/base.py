from pydantic import BaseModel, ConfigDict


class BaseForm(BaseModel):
    model_config = ConfigDict(extra="allow")