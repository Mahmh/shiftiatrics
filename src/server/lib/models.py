from typing import Optional
from pydantic import BaseModel

ScheduleType = list[list[list[int]]]

class Credentials(BaseModel):
    email: str
    password: str
    __repr__ = lambda self: f"Credentials(email='{self.email}')"

class Cookies(BaseModel):
    account_id: Optional[int] = None
    token: Optional[str] = None
    available = lambda self: (self.account_id is not None and self.token is not None) and self.account_id > 0 and len(self.token) > 0


class EmployeeInfo(BaseModel):
    employee_name: str
    min_work_hours: Optional[int] = None
    max_work_hours: Optional[int] = None


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