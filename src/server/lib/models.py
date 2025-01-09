from typing import Optional
from pydantic import BaseModel

ScheduleType = list[list[list[int]]]

class Credentials(BaseModel):
    username: str
    password: str

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