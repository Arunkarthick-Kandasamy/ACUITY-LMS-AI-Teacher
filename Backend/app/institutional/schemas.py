from __future__ import annotations

from pydantic import BaseModel


class SchoolCreate(BaseModel):
    name: str
    code: str
    address: str | None = None
    phone: str | None = None
    domains: list[str] = []


class SchoolUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class SchoolResponse(BaseModel):
    id: str
    name: str
    code: str
    address: str | None = None
    phone: str | None = None
    is_active: bool
    domains: list[str] = []

    model_config = {"from_attributes": True}


class AddDomainRequest(BaseModel):
    domain: str
    is_primary: bool = False
