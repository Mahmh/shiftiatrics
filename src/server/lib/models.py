from typing import Optional
from pydantic import BaseModel, Field
from src.server.lib.types import ScheduleType, QueryType

class Credentials(BaseModel):
    email: str
    password: str
    __repr__ = lambda self: f"Credentials(email='{self.email}')"


class Cookies(BaseModel):
    account_id: Optional[int] = Field(default=None)
    token: Optional[str] = Field(default=None)
    available = lambda self: (self.account_id is not None and self.token is not None) and self.account_id > 0 and len(self.token) > 0


class ScheduleInfo(BaseModel):
    schedule: ScheduleType
    month: int
    year: int


class HolidayInfo(BaseModel):
    holiday_name: str
    assigned_to: list[int]
    start_date: str
    end_date: str


class ContactUsSubmissionData(BaseModel):
    name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    query_type: QueryType
    description: str