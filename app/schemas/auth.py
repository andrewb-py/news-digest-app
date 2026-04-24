from pydantic import BaseModel, EmailStr, field_validator
import re

class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def check_complexity(cls, v: str) -> str:
        if len(v) < 8: raise ValueError("Минимум 8 символов")
        if not re.search(r"[A-Z]", v): raise ValueError("Нужна заглавная буква")
        if not re.search(r"[a-z]", v): raise ValueError("Нужна строчная буква")
        if not re.search(r"\d", v): raise ValueError("Нужна цифра")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str