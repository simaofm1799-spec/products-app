from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Gender = Literal["male", "female", "other"]
Role = Literal["admin", "moderator", "user"]


class Hair(BaseModel):
    color: str | None = None
    type: str | None = None


class Address(BaseModel):
    address: str | None = None
    city: str | None = None
    state: str | None = None
    stateCode: str | None = None
    postalCode: str | None = None
    country: str | None = None


class Company(BaseModel):
    name: str | None = None
    department: str | None = None
    title: str | None = None


class UserResponse(BaseModel):
    """RESPONSE model: only the fields useful to the frontend. Never exposes password, ssn, bank data, etc.
    On create/update, DummyJSON only returns part of the fields."""

    id: int
    firstName: str | None = None
    lastName: str | None = None
    maidenName: str | None = None
    age: int | None = None
    gender: str | None = None
    email: str | None = None
    phone: str | None = None
    username: str | None = None
    birthDate: str | None = None
    image: str | None = None
    bloodGroup: str | None = None
    height: float | None = None
    weight: float | None = None
    eyeColor: str | None = None
    hair: Hair | None = None
    address: Address | None = None
    company: Company | None = None
    role: str | None = None
    university: str | None = None


class DistributionItem(BaseModel):
    label: str
    count: int


class Distribution(BaseModel):
    """How many users there are per value of a field (users without a value are left out)."""

    by: str
    total: int
    items: list[DistributionItem]  # most users first


class UserFields(BaseModel):
    """Base of the REQUEST models (create/update): the editable fields.
    Unknown fields are rejected (422) so the frontend gets feedback."""

    model_config = ConfigDict(extra="forbid")

    firstName: str | None = Field(None, min_length=1, max_length=100)
    lastName: str | None = Field(None, min_length=1, max_length=100)
    maidenName: str | None = Field(None, max_length=100)
    age: int | None = Field(None, ge=0, le=150)
    gender: Gender | None = None
    email: str | None = Field(None, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(None, max_length=30)
    username: str | None = Field(None, min_length=1, max_length=50)
    birthDate: str | None = Field(None, description="Format YYYY-M-D, as in DummyJSON")
    image: str | None = None
    bloodGroup: str | None = Field(None, max_length=5)
    height: float | None = Field(None, gt=0)
    weight: float | None = Field(None, gt=0)
    eyeColor: str | None = Field(None, max_length=30)
    role: Role | None = None


class UserCreate(UserFields):
    """Create request: first and last name are required."""

    firstName: str = Field(min_length=1, max_length=100)
    lastName: str = Field(min_length=1, max_length=100)


class UserUpdate(UserFields):
    """Partial update: only the fields sent are changed."""
