package tests.engine.algorithms.A1;
import server.engine.algorithms.A1.T1;
import server.engine.common.*;
import tests.engine.*;
import java.util.List;
import java.util.stream.Stream;
import java.util.concurrent.atomic.AtomicInteger;

public class T1Test {
    public static void main(String[] args) {
        AtomicInteger passed = new AtomicInteger(0), failed = new AtomicInteger(0);

        // Run tests in parallel
        Stream.<Runnable>of(
            () -> Utils.runTest(T1Test::testBasicRotationPattern, "testBasicRotationPattern", passed, failed),
            () -> Utils.runTest(T1Test::testAssignmentsRespectsMaxWorkHours, "testAssignmentsRespectsMaxWorkHours", passed, failed),
            () -> Utils.runTest(T1Test::testPostProcessingFixesUnderworkedEmployees, "testPostProcessingFixesUnderworkedEmployees", passed, failed),
            () -> Utils.runTest(T1Test::testAllShiftsCovered, "testAllShiftsCovered", passed, failed)
        ).parallel().forEach(Runnable::run);

        System.out.println(passed.get() + " passed, " + failed.get() + " failed");
        System.exit(failed.get() > 0 ? 1 : 0);
    }
    

    private static void testBasicRotationPattern() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true); // 4 employees
        List<Shift> shifts = setup.initShifts(true);        // 3 shifts (D, E, N)
        List<Holiday> holidays = setup.initHolidays();

        T1.generate(employees, shifts, holidays, 10, 2025, 4); // April 2025
    }

    private static void testAssignmentsRespectsMaxWorkHours() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();

        Schedule schedule = T1.generate(employees, shifts, holidays, 30, 2025, 4);
        var workHours = schedule.getWorkHoursOfEmployees();

        for (Employee e : employees) {
            int actual = workHours.getOrDefault(e.id(), 0);
            if (actual > e.maxWorkHours()) {
                throw new AssertionError("❌ " + e.name() + " exceeded max work hours: " + actual);
            }
        }
    }

    private static void testPostProcessingFixesUnderworkedEmployees() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();

        Schedule schedule = T1.generate(employees, shifts, holidays, 30, 2025, 4);
        var workHours = schedule.getWorkHoursOfEmployees();

        for (Employee e : employees) {
            int actual = workHours.getOrDefault(e.id(), 0);
            if (actual < e.minWorkHours()) {
                throw new AssertionError("❌ " + e.name() + " underworked: " + actual + " < min " + e.minWorkHours());
            }
        }
    }

    private static void testAllShiftsCovered() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();

        Schedule schedule = T1.generate(employees, shifts, holidays, 7, 2025, 4);
        Employee[][][] data = schedule.schedule();

        for (int day = 0; day < data.length; day++) {
            for (int shiftIdx = 0; shiftIdx < data[day].length; shiftIdx++) {
                if (data[day][shiftIdx] == null || data[day][shiftIdx].length == 0) {
                    throw new AssertionError("❌ Day " + (day + 1) + " - Shift " + shifts.get(shiftIdx).name() + " has no assignment.");
                }
            }
        }
    }
}