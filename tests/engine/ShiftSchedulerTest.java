package tests.engine;
import server.engine.*;
import server.engine.common.Config;
import server.engine.common.Employee;
import server.engine.common.Holiday;
import server.engine.common.Shift;

import java.util.*;
import java.time.LocalDate;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

public class ShiftSchedulerTest {
    public static void testGetShiftCounts() {
        int[][][] schedule = {
            { {1}, {2}, {1, 2} }, // Day 1
            { {1}, {}, {2} }      // Day 2
        };
        HashMap<Integer, Integer> result = Main.getShiftCountsOfEmployees(schedule);
        assert result.get(1) == 3 : "Expected 3 for employee 1";
        assert result.get(2) == 3 : "Expected 3 for employee 2";
    }

    public static void testGetWorkHours() {
        List<Shift> shifts = List.of(
            new Shift("D", "08:00", "16:00"), // 8h
            new Shift("E", "16:00", "00:00"), // 8h
            new Shift("N", "00:00", "08:00")  // 8h
        );
        int[][][] schedule = {
            { {1}, {}, {2} },  // Day 1
            { {}, {2}, {1} }   // Day 2
        };
        HashMap<Integer, Integer> result = Main.getWorkHoursOfEmployees(schedule, shifts, 2);
        assert result.get(1) == 16 : "Expected 16h for employee 1";
        assert result.get(2) == 16 : "Expected 16h for employee 2";
    }

    public static void testIsAlreadyAssigned() {
        Employee alice = new Employee(1, "Alice");
        Employee bob = new Employee(2, "Bob");
        Employee[][][] schedule = new Employee[1][2][];
        schedule[0][0] = new Employee[] { alice };
        schedule[0][1] = new Employee[] {};
    
        assert Main.isAlreadyAssigned(alice, schedule, 0) : "Alice should be assigned";
        assert !Main.isAlreadyAssigned(bob, schedule, 0) : "Bob should not be assigned";
    }

    public static void testIsNightShiftAssigned() {
        Employee alice = new Employee(1, "Alice");
        List<Shift> shifts = List.of(
            new Shift("D", "08:00", "16:00"),
            new Shift("N", "23:00", "07:00")
        );
        Employee[][] prevDay = new Employee[2][];
        prevDay[0] = new Employee[] {};
        prevDay[1] = new Employee[] { alice };
    
        assert Main.isNightShiftAssigned(alice, prevDay, shifts) : "Alice should be flagged for night shift";
    }

    public static void testIsOnHoliday() {
        Employee alice = new Employee(1, "Alice");
        LocalDate today = LocalDate.of(2025, 10, 10);
        List<Holiday> holidays = List.of(
            new Holiday("Off", List.of(1), "2025-10-10", "2025-10-12")
        );
    
        assert Main.isOnHoliday(alice, holidays, today) : "Alice should be on holiday";
    }

    public static void testAdvanceRotationPointer() {
        Employee alice = new Employee(1, "Alice");
        Map<Employee, Integer> pointer = new HashMap<>();
        pointer.put(alice, 4);
        List<String> pattern = Arrays.asList("D", "E", "N", null, null);
        Config config = new Config(true, 1, true, pattern, false, 7);
    
        Main.advanceRotationPointer(alice, pointer, config);
        assert pointer.get(alice) == 0 : "Pointer should wrap to 0";
    }

    public static void testAlreadyAssigned() {
        Employee[][][] schedule = EligibilityTestHelper.blankSchedule(1, 1);
        schedule[0][0] = new Employee[] { EligibilityTestHelper.testEmp };
    
        boolean eligible = Main.isEligible(
            EligibilityTestHelper.testEmp,
            schedule,
            EligibilityTestHelper.dayShift,
            EligibilityTestHelper.shiftList(),
            0,
            EligibilityTestHelper.makeWorkDays(0),
            EligibilityTestHelper.makeWorkMinutes(0),
            EligibilityTestHelper.makeShiftCount(0),
            EligibilityTestHelper.emptyShiftHistory(),
            EligibilityTestHelper.baseConfig()
        );
        assert !eligible : "Should not be eligible (already assigned that day)";
    }
    
    public static void testExceedsMaxWorkHours() {
        Shift longShift = new Shift("L", "08:00", "20:00"); // 12 hours
    
        boolean eligible = Main.isEligible(
            EligibilityTestHelper.testEmp,
            EligibilityTestHelper.blankSchedule(1, 1),
            longShift,
            List.of(longShift),
            0,
            EligibilityTestHelper.makeWorkDays(),
            EligibilityTestHelper.makeWorkMinutes(160 * 60 - 30), // 30 minutes away from max
            EligibilityTestHelper.makeShiftCount(0),
            EligibilityTestHelper.emptyShiftHistory(),
            EligibilityTestHelper.baseConfig()
        );
        assert !eligible : "Should not be eligible (would exceed max hours)";
    }

    public static void testMaxShiftsPerWeek() {
        boolean eligible = Main.isEligible(
            EligibilityTestHelper.testEmp,
            EligibilityTestHelper.blankSchedule(7, 1),
            EligibilityTestHelper.dayShift,
            EligibilityTestHelper.shiftList(),
            6,
            EligibilityTestHelper.makeWorkDays(0, 1, 2, 3, 4, 5, 6),
            EligibilityTestHelper.makeWorkMinutes(0),
            EligibilityTestHelper.makeShiftCount(7),
            EligibilityTestHelper.emptyShiftHistory(),
            EligibilityTestHelper.baseConfig()
        );
        assert !eligible : "Should not be eligible (weekly cap reached)";
    }

    public static void testBackToBackNightShift() {
        Employee[][][] schedule = EligibilityTestHelper.blankSchedule(2, 2);
        schedule[0][1] = new Employee[] { EligibilityTestHelper.testEmp }; // Night shift yesterday
    
        Config config = new Config(false, 1, false, null, true, 7);
    
        boolean eligible = Main.isEligible(
            EligibilityTestHelper.testEmp,
            schedule,
            EligibilityTestHelper.nightShift,
            EligibilityTestHelper.shiftList(),
            1,
            EligibilityTestHelper.makeWorkDays(0),
            EligibilityTestHelper.makeWorkMinutes(0),
            EligibilityTestHelper.makeShiftCount(1),
            EligibilityTestHelper.emptyShiftHistory(),
            config
        );
        assert !eligible : "Should not be eligible (back-to-back night shift)";
    }

    public static void testIsEligibleSuccess() {
        boolean eligible = Main.isEligible(
            EligibilityTestHelper.testEmp,
            EligibilityTestHelper.blankSchedule(1, 1),
            EligibilityTestHelper.dayShift,
            EligibilityTestHelper.shiftList(),
            0,
            EligibilityTestHelper.makeWorkDays(),
            EligibilityTestHelper.makeWorkMinutes(0),
            EligibilityTestHelper.makeShiftCount(0),
            EligibilityTestHelper.emptyShiftHistory(),
            EligibilityTestHelper.baseConfig()
        );
        assert eligible : "Should be eligible (no constraints violated)";
    }    

    public static void testBasicSchedule() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();

        Config config = new Config(
            true,
            1,
            false,
            null,
            false,
            10
        );

        Employee[][][] schedule = Main.generateSchedule(employees, shifts, holidays, 7, 2025, 10, config);
        assert schedule.length == 7 : "Schedule should have 7 days";
        for (int d = 0; d < 7; d++) {
            for (int s = 0; s < shifts.size(); s++) {
                assert schedule[d][s] != null : "Each shift should be assigned in Phase 1";
                assert schedule[d][s].length == 1 : "Only one employee per shift in Phase 1";
            }
        }
    }

    public static void testHolidayExclusion() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees();
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = List.of(
            new Holiday("Vacation", List.of(1), "2025-10-03", "2025-10-05") // Alice unavailable
        );

        Config config = new Config(true, 1, false, null, false, 10);
        Employee[][][] schedule = Main.generateSchedule(employees, shifts, holidays, 5, 2025, 10, config);

        for (int day = 2; day <= 4; day++) { // Oct 3–5
            for (Employee[] shift : schedule[day]) {
                if (shift != null) {
                    for (Employee e : shift) {
                        assert e.id() != 1 : "Alice should not be scheduled on her holiday";
                    }
                }
            }
        }
    }

    public static void testMaxEmpsInShift() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts();
        List<Holiday> holidays = setup.initHolidays();

        Config config = new Config(true, 2, false, null, false, 10);
        Employee[][][] schedule = Main.generateSchedule(employees, shifts, holidays, 5, 2025, 10, config);

        for (int d = 0; d < schedule.length; d++) {
            for (int s = 0; s < shifts.size(); s++) {
                Employee[] emps = schedule[d][s];
                assert emps != null;
                assert emps.length <= 2 : "Should not exceed maxEmpsInShift = 2";
            }
        }
    }

    public static void testRotationPatternOverride() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();

        List<String> pattern = Arrays.asList("D", "E", "N", null, null);
        Config config = new Config(true, 1, true, pattern, true, 10);
        Employee[][][] schedule = Main.generateSchedule(employees, shifts, holidays, 5, 2025, 10, config);

        for (int d = 0; d < schedule.length; d++) {
            for (int s = 0; s < shifts.size(); s++) {
                String shiftName = shifts.get(s).name();
                for (Employee e : schedule[d][s] == null ? new Employee[]{} : schedule[d][s]) {
                    // Should match rotation pattern
                    int expectedPos = (d + employees.indexOf(e)) % pattern.size();
                    String expectedShift = pattern.get(expectedPos);
                    if (expectedShift != null) {
                        assert expectedShift.equalsIgnoreCase(shiftName) : "Rotation mismatch for employee " + e.name();
                    }
                }
            }
        }
    }

    public static void testStaggeredPattern() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = new ArrayList<>();
        List<String> pattern = Arrays.asList("D", "E", "N", null, null);

        Config config = new Config(true, 1, true, pattern, true, 10);

        Employee[][][] schedule = Main.generateSchedule(employees, shifts, holidays, 10, 2025, 10, config);

        for (int day = 0; day < schedule.length; day++) {
            for (int i = 0; i < employees.size(); i++) {
                Employee emp = employees.get(i);
                int patternDay = (day + i) % pattern.size();
                String expectedShift = pattern.get(patternDay);
                if (expectedShift == null) continue;

                int shiftIndex = -1;
                for (int s = 0; s < shifts.size(); s++) {
                    if (shifts.get(s).name().equals(expectedShift)) {
                        shiftIndex = s;
                        break;
                    }
                }

                if (shiftIndex == -1) continue;

                Employee[] assigned = schedule[day][shiftIndex];
                if (assigned == null) continue;
                boolean found = Arrays.asList(assigned).contains(emp);

                assert found : "Employee " + emp.name() + " missing from shift on day " + (day + 1) + " expected: " + expectedShift;
            }
        }
    }

    public static void testHolidayFillFallback() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = List.of(
            new Holiday("Day Off", List.of(1), "2025-10-02", "2025-10-02") // Alice off
        );

        List<String> pattern = Arrays.asList("D", "E", "N", null, null);
        Config config = new Config(true, 1, true, pattern, true, 10);

        Employee[][][] schedule = Main.generateSchedule(employees, shifts, holidays, 5, 2025, 10, config);

        for (int s = 0; s < shifts.size(); s++) {
            Employee[] emps = schedule[1][s]; // Oct 2 = index 1
            if (emps == null) continue;

            for (Employee e : emps) {
                assert e.id() != 1 : "Alice should not be assigned on holiday";
            }
        }
    }

    public static void testMaxShiftsPerWeekEnforced() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();
        List<String> pattern = Arrays.asList("D", "E", "N", null, null);

        Config config = new Config(true, 1, true, pattern, true, 3); // max 3 shifts per week

        Employee[][][] schedule = Main.generateSchedule(employees, shifts, holidays, 7, 2025, 10, config);

        Map<Integer, Integer> shiftCounts = Main.getShiftCountsOfEmployees(convertToIdSchedule(schedule));
        for (Map.Entry<Integer, Integer> entry : shiftCounts.entrySet()) {
            assert entry.getValue() <= 3 : "Employee " + entry.getKey() + " exceeded 3 shifts: " + entry.getValue();
        }
    }

    public static void testMaxEmployeesInShiftRespected() {
        TestSetup setup = new TestSetup();
        List<Employee> employees = setup.initEmployees(true);
        List<Shift> shifts = setup.initShifts(true);
        List<Holiday> holidays = setup.initHolidays();
        List<String> pattern = Arrays.asList("D", "E", "N", null, null);

        Config config = new Config(true, 1, true, pattern, true, 10); // only 1 allowed

        Employee[][][] schedule = Main.generateSchedule(employees, shifts, holidays, 5, 2025, 10, config);

        for (int day = 0; day < schedule.length; day++) {
            for (int s = 0; s < shifts.size(); s++) {
                Employee[] assigned = schedule[day][s];
                if (assigned != null) {
                    assert assigned.length <= 1 : "Too many employees in shift: " + assigned.length;
                }
            }
        }
    }

    public static int[][][] convertToIdSchedule(Employee[][][] schedule) {
        int[][][] idSchedule = new int[schedule.length][][];
        for (int d = 0; d < schedule.length; d++) {
            idSchedule[d] = new int[schedule[d].length][];
            for (int s = 0; s < schedule[d].length; s++) {
                Employee[] emps = schedule[d][s];
                if (emps == null) {
                    idSchedule[d][s] = new int[0];
                    continue;
                }
                idSchedule[d][s] = Arrays.stream(emps).mapToInt(Employee::id).toArray();
            }
        }
        return idSchedule;
    }

    private static void runTest(Runnable testMethod, String testName, AtomicInteger numPassed, AtomicInteger numFailed) {
        try {
            testMethod.run();
            System.out.println("[PASSED] " + testName);
            numPassed.incrementAndGet();
        } catch (Exception e) {
            System.err.println("[FAILED] " + testName + ": " + e.getMessage());
            numFailed.incrementAndGet();
        }
    }

    public static void main(String[] args) {
        System.out.println("Engine tests:");
        AtomicInteger numPassed = new AtomicInteger(0);
        AtomicInteger numFailed = new AtomicInteger(0);

        // Run tests in parallel
        Stream.<Runnable>of(
            () -> runTest(ShiftSchedulerTest::testGetShiftCounts, "testGetShiftCounts", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testGetWorkHours, "testGetWorkHours", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testIsAlreadyAssigned, "testIsAlreadyAssigned", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testIsNightShiftAssigned, "testIsNightShiftAssigned", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testIsOnHoliday, "testIsOnHoliday", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testAdvanceRotationPointer, "testAdvanceRotationPointer", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testAlreadyAssigned, "testAlreadyAssigned", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testExceedsMaxWorkHours, "testExceedsMaxWorkHours", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testMaxShiftsPerWeek, "testMaxShiftsPerWeek", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testBackToBackNightShift, "testBackToBackNightShift", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testIsEligibleSuccess, "testIsEligibleSuccess", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testBasicSchedule, "testBasicSchedule", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testHolidayExclusion, "testHolidayExclusion", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testMaxEmpsInShift, "testMaxEmpsInShift", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testRotationPatternOverride, "testRotationPatternOverride", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testStaggeredPattern, "testStaggeredPattern", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testHolidayFillFallback, "testHolidayFillFallback", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testMaxShiftsPerWeekEnforced, "testMaxShiftsPerWeekEnforced", numPassed, numFailed),
            () -> runTest(ShiftSchedulerTest::testMaxEmployeesInShiftRespected, "testMaxEmployeesInShiftRespected", numPassed, numFailed)
        ).parallel().forEach(Runnable::run);
        System.out.println(numPassed.get() + " passed, " + numFailed.get() + " failed");
    }
}