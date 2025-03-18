from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from src.server.lib.types import ScheduleType, QueryType, PricingPlanName

class Credentials(BaseModel):
    email: str
    password: str
    __repr__ = lambda self: f"Credentials(email='{self.email}')"


class Cookies(BaseModel):
    account_id: Optional[int] = Field(default=None)
    token: Optional[str] = Field(default=None)
    available = lambda self: (self.account_id is not None and self.token is not None) and self.account_id > 0 and len(self.token) > 0


class EmployeeInfo(BaseModel):
    employee_name: str
    min_work_hours: Optional[int] = Field(default=None)
    max_work_hours: Optional[int] = Field(default=None)


class ShiftInfo(BaseModel):
    shift_name: str
    start_time: str
    end_time: str


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
    name: Optional[str] = None
    email: str
    query_type: QueryType
    description: str


class PlanDetails(BaseModel):
    max_num_pediatricians: int
    max_num_shifts_per_day: int
    max_num_schedule_requests: int


class SubscriptionInfo(BaseModel):
    plan: PricingPlanName
    price: float
    expires_at: Optional[datetime] = Field(default=None)
    plan_details: PlanDetails