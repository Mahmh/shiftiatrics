from pydantic import BaseModel

class Credentials(BaseModel):
    username: str
    password: str


class EmployeeInfo(BaseModel):
    employee_name: str


class ShiftInfo(BaseModel):
    shift_name: str
    start_time: str
    end_time: str


class ScheduleInfo(BaseModel):
    schedule: list[list[int]]