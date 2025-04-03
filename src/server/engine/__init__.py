from datetime import datetime, timedelta, time
from jpype import java, JPackage, JInt, JString, JArray
from src.server.lib.models import ScheduleType
from src.server.db.tables import Employee, Shift, Holiday

class Engine:
    """Class for the schedule generator engine API."""
    def __init__(self, account_id: int):
        common = JPackage('server.engine.common')
        algorithms = JPackage('server.engine.algorithms')
        self.Employee = common.Employee
        self.Shift = common.Shift
        self.Holiday = common.Holiday
        self._generate = getattr(algorithms, f'A{account_id}').generate


    def generate(self, employees: list[Employee], shifts: list[Shift], holidays: list[Holiday], num_days: int, year: int, month: int) -> ScheduleType:
        """Generates the Java Schedule object, and then converts and returns it as a Pythonic list."""
        raw_schedule = self._generate(
            self._prepare_employees(employees),
            self._prepare_shifts(shifts),
            self._prepare_holidays(holidays),
            num_days,
            year,
            month
        ).schedule()

        schedule = []
        for day_schedule in raw_schedule:
            daily_shifts = []
            for shift_schedule in day_schedule:
                if shift_schedule is None:
                    daily_shifts.append([])  # No employees assigned
                else:
                    employee_ids = [employee.id() for employee in shift_schedule]
                    daily_shifts.append(employee_ids)
            schedule.append(daily_shifts)
        return schedule


    @classmethod
    def get_shift_counts_of_employees(cls, schedule: ScheduleType) -> dict[int, int]:
        """Returns a mapping from employee ID to the number of shifts they’ve worked."""
        shift_counts = {}
        for day in schedule:
            for shift in day:
                for emp_id in shift:
                    shift_counts[emp_id] = shift_counts.get(emp_id, 0) + 1
        return shift_counts


    @classmethod
    def get_work_hours_of_employees(cls, schedule: ScheduleType, shifts: list[Shift]) -> dict[int, int]:
        """
        Calculates the total work hours for each employee over the schedule.
        Returns a dict mapping employee ID to total work hours.
        """
        work_hours = {}

        for day in schedule:
            for shift_index, shift_assignments in enumerate(day):
                shift = shifts[shift_index]
                # Combine with arbitrary date to form full datetime
                start_dt = datetime.combine(datetime.today(), shift.start_time)
                end_dt = datetime.combine(datetime.today(), shift.end_time)

                # Handle overnight shifts
                if end_dt <= start_dt:
                    end_dt += timedelta(days=1)

                shift_duration = (end_dt - start_dt).seconds // 3600

                for emp_id in shift_assignments:
                    work_hours[emp_id] = work_hours.get(emp_id, 0) + shift_duration

        return work_hours


    def _prepare_employees(self, employees: list[Employee]) -> JArray:
        """Creates a list of Employee objects & convert it to Java ArrayList."""
        emp_list = [self.Employee(e.employee_id, JString(e.employee_name), e.min_work_hours, e.max_work_hours) for e in employees]
        java_emp_list = java.util.ArrayList()
        for employee in emp_list: java_emp_list.add(employee)
        return java_emp_list
    

    def _prepare_shifts(self, shifts: list[Shift]) -> JArray:
        """Creates a list of Shift objects, converting time to string format & convert it to Java ArrayList."""
        shift_list = [
            self.Shift(shift.shift_name, shift.start_time.strftime("%H:%M"), shift.end_time.strftime("%H:%M"))
            for shift in shifts
        ]
        java_shift_list = java.util.ArrayList()
        for shift in shift_list: java_shift_list.add(shift)
        return java_shift_list
    

    def _prepare_holidays(self, holidays: list[Holiday]) -> JArray:
        """Converts the given list of holidays to Java ArrayList."""
        holiday_list = [
            self.Holiday(
                JString(holiday.holiday_name),
                java.util.ArrayList([JInt(emp_id) for emp_id in holiday.assigned_to]),
                JString(holiday.start_date.strftime("%Y-%m-%d")),
                JString(holiday.end_date.strftime("%Y-%m-%d"))
            )
            for holiday in holidays
        ]
        java_holiday_list = java.util.ArrayList()
        for holiday in holiday_list: java_holiday_list.add(holiday)
        return java_holiday_list