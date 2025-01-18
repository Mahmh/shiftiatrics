package tests.engine;
import server.engine.*;
import java.util.*;
import java.time.LocalDate;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

public class ShiftSchedulerTest {
    /** Test that employees meet minimum work hours when shifts are sufficient. */
    public static void testMinWorkHoursConstraint() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();
        final int numDays = 20;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            20, 2023, 10,
            true, false, false,
            1
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        HashMap<Integer, Integer> workHours = ShiftScheduler.getWorkHoursOfEmployees(idSchedule, shifts, numDays);
        for (Employee employee : employees) {
            if (workHours.get(employee.getId()) < employee.getMinWorkHours()) {
                throw new AssertionError("Employee " + employee.getName() + " did not meet minimum work hours.");
            }
        }
    }

    /** Test that employees do not exceed max work hours. */
    public static void testMaxWorkHoursConstraint() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();
        final byte numDays = 10;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays, 
            10, 2023, 10,
            true, false, false,
            1
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        HashMap<Integer, Integer> workHours = ShiftScheduler.getWorkHoursOfEmployees(idSchedule, shifts, numDays);
        for (Employee employee : employees) {
            if (workHours.get(employee.getId()) > employee.getMaxWorkHours()) {
                throw new AssertionError("Employee " + employee.getName() + " exceeded max work hours.");
            }
        }
    }

    /** Test that no employees are assigned shifts when the list of shifts is empty. */
    public static void testNoShiftsAvailable() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = new ArrayList<>(); // No shifts
        List<Holiday> holidays = setup.initHolidays();

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            5, 2023, 10,
            true, true, false,
            employees.size()
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        for (int[][] day : idSchedule) for (int[] shift : day) {
            if (shift.length != 0) throw new AssertionError("Shifts must not be assigned when no shifts are available.");
        }
    }

    /** Test that all employees have equal shifts when multiEmpOneShift is true. */
    public static void testEqualShiftsWithMultiEmpOneShift() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            5, 2023, 10,
            true, true, false,
            employees.size()
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);
        HashMap<Integer, Integer> shiftCounts = ShiftScheduler.getShiftCountsOfEmployees(idSchedule);
        if (shiftCounts.isEmpty()) throw new AssertionError("No shifts were assigned.");
        
        int expectedShiftCount = shiftCounts.values().iterator().next(); // All must have the same count
        for (int count : shiftCounts.values()) {
            if (count != expectedShiftCount) throw new AssertionError("Employees do not have equal shifts.");
        }
    }

    /** Test that holidays are respected. */
    public static void testHolidaysRespected() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();
        holidays.add(new Holiday("Holiday", Arrays.asList(1), "2023-10-04", "2023-10-06")); // Alice on holiday from 4th to 6th October
        final int numDays = 10;
        final int year = 2023;
        final int month = 10;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            numDays, year, month,
            true, true, false,
            employees.size()
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        for (int day = 0; day < numDays; day++) {
            LocalDate currentDate = LocalDate.of(year, month, day+1);
            for (int shift = 0; shift < shifts.size(); shift++) {
                for (int empId : idSchedule[day][shift]) {
                    if (empId == 1 && (currentDate.isAfter(LocalDate.of(2023, 10, 3)) && currentDate.isBefore(LocalDate.of(2023, 10, 7)))) {
                        throw new AssertionError("Employee Alice was assigned a shift during her holiday.");
                    }
                }
            }
        }
    }

    /** Test that employees are not assigned to shifts on their holidays. */
    public static void testEmployeesNotAssignedOnHolidays() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();
        holidays.add(new Holiday("Holiday", Arrays.asList(2), "2023-10-04", "2023-10-05")); // Bob on holiday from 4th to 5th October
        final int numDays = 10;
        final int year = 2023;
        final int month = 10;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            numDays, year, month,
            true, true, false,
            employees.size()
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);
    
        for (int day = 0; day < numDays; day++) {
            LocalDate currentDate = LocalDate.of(year, month, day+1);
            for (int shift = 0; shift < shifts.size(); shift++) {
                for (int empId : idSchedule[day][shift]) {
                    if (empId == 2 && (currentDate.isEqual(LocalDate.of(2023, 10, 4)) || currentDate.isEqual(LocalDate.of(2023, 10, 5)))) {
                        throw new AssertionError("Employee Alice was assigned a shift during her holiday.");
                    }
                }
            }
        }
    }

    /** Test that employees are not assigned to more than one shift per day when multiShiftsOneEmp is false. */
    public static void testSingleShiftPerDayConstraint() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();
        final int numDays = 10;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            numDays, 2023, 10,
            true, true, false,
            employees.size()
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        for (int day = 0; day < numDays; day++) {
            Set<Integer> assignedEmployees = new HashSet<>();
            for (int shift = 0; shift < shifts.size(); shift++) {
                for (int empId : idSchedule[day][shift]) {
                    if (!assignedEmployees.add(empId)) {
                        throw new AssertionError("Employee " + empId + " was assigned to more than one shift on day " + (day+1));
                    }
                }
            }
        }
    }

    /** Test that employees are assigned to multiple shifts in at least 1 day when multiShiftsOneEmp is true. */
    public static void testMultipleShiftsPerDayAllowed() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();
        final int numDays = 30;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            numDays, 2023, 10,
            true, true, true,
            employees.size()
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        Map<Integer, Integer> empIdToSingleShiftDays = new HashMap<>();
        for (int day = 0; day < numDays; day++) {
            Map<Integer, Integer> dailyShiftCounts = new HashMap<>();

            for (int shift = 0; shift < shifts.size(); shift++) for (int empId : idSchedule[day][shift]) {
                dailyShiftCounts.put(empId, dailyShiftCounts.getOrDefault(empId, 0) + 1);
            }

            for (Map.Entry<Integer, Integer> entry : dailyShiftCounts.entrySet()) {
                if (entry.getValue() != 1) continue;
                empIdToSingleShiftDays.put(entry.getKey(), empIdToSingleShiftDays.getOrDefault(entry.getKey(), 0) + 1);
            }
        }

        for (Map.Entry<Integer, Integer> entry : empIdToSingleShiftDays.entrySet()) {
            if (entry.getValue() == numDays) throw new AssertionError("Employee " + entry.getKey() + " was assigned to only one shift on all days.");
        }
    }

    /** Test that the schedule is balanced when multiEmpOneShift is false. */
    public static void testBalancedScheduleWithoutMultiEmpOneShift() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            10, 2023, 10,
            true, false, false,
            1
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        HashMap<Integer, Integer> shiftCounts = ShiftScheduler.getShiftCountsOfEmployees(idSchedule);
        int minShifts = Collections.min(shiftCounts.values());
        int maxShifts = Collections.max(shiftCounts.values());
        if (maxShifts-minShifts > 1) throw new AssertionError("Schedule is not balanced. Max shifts: " + maxShifts + ", Min shifts: " + minShifts);
    }

    /** Test that IllegalArgumentException is thrown when multiEmpOneShift is false and maxEmpsInShift > 1. */
    public static void testIllegalArgumentExceptionForInvalidMaxEmpsInShift() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();
        final int numDays = 10;

        try {
            ShiftScheduler.generateSchedule(
                employees, shifts, holidays,
                numDays, 2023, 10,
                true, false, false,
                2 // Invalid as multiEmpOneShift is false
            );
            throw new AssertionError("Expected IllegalArgumentException was not thrown.");
        } catch (IllegalArgumentException e) {}
    }

    /** Test that no shift has more than one employee when maxEmpsInShift is 1. */
    public static void testMaxEmpsInShiftConstraint() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();
        final int numDays = 10;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            numDays, 2023, 10,
            true, true, false,
            1 // maxEmpsInShift is 1
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        for (int[][] day : idSchedule) {
            for (int[] shift : day) {
                if (shift.length > 1) {
                    throw new AssertionError("Shift has more than one employee when maxEmpsInShift is 1.");
                }
            }
        }
    }

    /** Test that at least one shift has more than one employee when maxEmpsInShift > 1 */
    public static void testAtLeastOneShiftWithMultipleEmployees() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();
        final int numDays = 10;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(
            employees, shifts, holidays,
            numDays, 2023, 10,
            true, true, false,
            2 // maxEmpsInShift is 2
        );
        int[][][] idSchedule = convertToIdSchedule(schedule);

        boolean found = false;
        for (int[][] day : idSchedule) {
            for (int[] shift : day) {
                if (shift.length > 1) {
                    found = true;
                    break;
                }
            }
            if (found) break;
        }

        if (!found) throw new AssertionError("No shift has more than one employee when maxEmpsInShift is > 1.");
    }

    /** Utility method to convert Employee[][][] schedule to int[][][] schedule with Employee IDs. */
    private static int[][][] convertToIdSchedule(Employee[][][] schedule) {
        int[][][] idSchedule = new int[schedule.length][][];

        for (int day = 0; day < schedule.length; day++) {
            idSchedule[day] = new int[schedule[day].length][];
            for (int shift = 0; shift < schedule[day].length; shift++) {
                idSchedule[day][shift] = Arrays.stream(schedule[day][shift])
                                               .mapToInt(Employee::getId)
                                               .toArray();
            }
        }

        return idSchedule;
    }

    /** Runs a given test function */
    private static void runTest(Runnable testMethod, String testName, AtomicInteger numPassed, AtomicInteger numFailed) {
        try {
            testMethod.run();
            System.out.println("[PASSED] " + testName);
            numPassed.incrementAndGet();
        } catch (AssertionError e) {
            System.err.println("[FAILED] " + testName + ": " + e.getMessage());
            numFailed.incrementAndGet();
        }
    }


    public static void main(String[] args) {
        AtomicInteger numPassed = new AtomicInteger(0);
        AtomicInteger numFailed = new AtomicInteger(0);

        // Run tests in parallel
        Stream.<Runnable>of(
            () -> runTest(ShiftSchedulerTest::testMinWorkHoursConstraint, "testMinWorkHoursConstraint", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testMaxWorkHoursConstraint, "testMaxWorkHoursConstraint", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testNoShiftsAvailable, "testNoShiftsAvailable", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testEqualShiftsWithMultiEmpOneShift, "testEqualShiftsWithMultiEmpOneShift", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testHolidaysRespected, "testHolidaysRespected", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testEmployeesNotAssignedOnHolidays, "testEmployeesNotAssignedOnHolidays", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testSingleShiftPerDayConstraint, "testSingleShiftPerDayConstraint", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testMultipleShiftsPerDayAllowed, "testMultipleShiftsPerDayAllowed", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testBalancedScheduleWithoutMultiEmpOneShift, "testBalancedScheduleWithoutMultiEmpOneShift", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testIllegalArgumentExceptionForInvalidMaxEmpsInShift, "testIllegalArgumentExceptionForInvalidMaxEmpsInShift", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testMaxEmpsInShiftConstraint, "testMaxEmpsInShiftConstraint", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testAtLeastOneShiftWithMultipleEmployees, "testAtLeastOneShiftWithMultipleEmployees", numPassed, numFailed)
        ).parallel().forEach(Runnable::run);

        System.out.println(numPassed.get() + " passed, " + numFailed.get() + " failed");
    }
}


/** Sets up tests for ShiftSchedulerTest */
final class TestSetup {
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
        shifts.add(new Shift("08:00", "16:00"));
        shifts.add(new Shift("16:00", "00:00"));
        if (allShifts) shifts.add(new Shift("00:00", "08:00"));
        return shifts;
    }

    public List<Holiday> initHolidays() {
        holidays = new ArrayList<>();
        return holidays;
    }
}