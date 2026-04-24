from pydantic import BaseModel, HttpUrl, field_validator
import re

class SubmissionCreate(BaseModel):
    url: HttpUrl
    comment: str | None = None

    @field_validator("url")
    @classmethod
    def check_url_accessible(cls, v: str) -> str:
        if not re.match(r"^https?://.+\..+", str(v)):
            raise ValueError("Неверный формат ссылки")
        return str(v)

class SubmissionResponse(BaseModel):
    id: int
    status: str
    url: str | None
    class Config:
        from_attributes = True