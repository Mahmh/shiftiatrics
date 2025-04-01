package tests.engine;
import server.engine.*;
import java.util.*;

/** Sets up tests for ShiftSchedulerTest */
public class TestSetup {
    private static final int MIN_WORK_HOURS = 100;
    private static final int MAX_WORK_HOURS = 173;
    private List<Employee> employees;
    private List<Shift> shifts;
    private List<Holiday> holidays;

    public List<Employee> initEmployees() { return initEmployees(false); }
    public List<Employee> initEmployees(boolean allEmps) {
        employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", MIN_WORK_HOURS, MAX_WORK_HOURS));
        employees.add(new Employee(2, "Bob", MIN_WORK_HOURS, MAX_WORK_HOURS));
        if (allEmps) {
            employees.add(new Employee(3, "Charlie", MIN_WORK_HOURS, MAX_WORK_HOURS));
            employees.add(new Employee(4, "Diana", MIN_WORK_HOURS, MAX_WORK_HOURS));
        }
        return employees;
    }

    public List<Shift> initShifts() { return initShifts(false); }
    public List<Shift> initShifts(boolean allShifts) {
        shifts = new ArrayList<>();
        shifts.add(new Shift("D", "08:00", "16:00"));
        shifts.add(new Shift("E", "16:00", "00:00"));
        if (allShifts) shifts.add(new Shift("N", "00:00", "08:00"));
        return shifts;
    }

    public List<Holiday> initHolidays() {
        holidays = new ArrayList<>();
        return holidays;
    }
}