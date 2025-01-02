package tests.engine;
import server.engine.*;
import java.util.*;

public class ShiftSchedulerTest {
    /** Test that employees do not exceed max work hours. */
    public static void testMaxWorkHoursConstraint() {
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", 40 * 4, 160 * 4));
        employees.add(new Employee(2, "Bob", 40 * 4, 160 * 4));

        List<Shift> shifts = new ArrayList<>();
        shifts.add(new Shift("08:00", "16:00"));
        shifts.add(new Shift("16:00", "00:00"));

        int numDays = 10;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(employees, shifts, numDays, true, true, false);

        int[][][] idSchedule = convertToIdSchedule(schedule);

        HashMap<Integer, Integer> workHours = ShiftScheduler.getWorkHoursOfEmployees(idSchedule, shifts, numDays);

        for (Employee employee : employees) {
            if (workHours.get(employee.getId()) > employee.getMaxWorkHours()) {
                throw new AssertionError("Employee " + employee.getName() + " exceeded max work hours.");
            }
        }
    }

    /** Test that employees meet minimum work hours when shifts are sufficient. */
    public static void testMinWorkHoursConstraint() {
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", 40 * 4, 160 * 4));
        employees.add(new Employee(2, "Bob", 40 * 4, 160 * 4));

        List<Shift> shifts = new ArrayList<>();
        shifts.add(new Shift("08:00", "16:00"));
        shifts.add(new Shift("16:00", "00:00"));

        int numDays = 20;
        boolean useWorkHours = true;
        boolean multiEmpsOneShift = false;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(employees, shifts, numDays, useWorkHours, multiEmpsOneShift, false);

        int[][][] idSchedule = convertToIdSchedule(schedule);

        HashMap<Integer, Integer> workHours = ShiftScheduler.getWorkHoursOfEmployees(idSchedule, shifts, numDays);

        for (Employee employee : employees) {
            if (workHours.get(employee.getId()) < employee.getMinWorkHours()) {
                throw new AssertionError("Employee " + employee.getName() + " did not meet minimum work hours.");
            }
        }
    }

    /** Test that no employees are assigned shifts when the list of shifts is empty. */
    public static void testNoShiftsAvailable() {
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", 40 * 4, 160 * 4));
        employees.add(new Employee(2, "Bob", 40 * 4, 160 * 4));

        List<Shift> shifts = new ArrayList<>(); // No shifts.

        int numDays = 5;
        boolean useWorkHours = true;
        boolean multiEmpsOneShift = true;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(employees, shifts, numDays, useWorkHours, multiEmpsOneShift, false);

        int[][][] idSchedule = convertToIdSchedule(schedule);

        for (int[][] day : idSchedule) {
            for (int[] shift : day) {
                if (shift.length != 0) {
                    throw new AssertionError("Shifts should not be assigned when no shifts are available.");
                }
            }
        }
    }

    /** Test that all employees have equal shifts when multiEmpsOneShift is true. */
    public static void testEqualShiftsWithMultiEmpsOneShift() {
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", 40 * 4, 160 * 4));
        employees.add(new Employee(2, "Bob", 40 * 4, 160 * 4));
        employees.add(new Employee(3, "Charlie", 40 * 4, 160 * 4));
        employees.add(new Employee(4, "Diana", 40 * 4, 160 * 4));

        List<Shift> shifts = new ArrayList<>();
        shifts.add(new Shift("08:00", "16:00"));
        shifts.add(new Shift("16:00", "00:00"));
        shifts.add(new Shift("00:00", "08:00"));

        int numDays = 5;
        boolean useWorkHours = true;
        boolean multiEmpsOneShift = true;

        Employee[][][] schedule = ShiftScheduler.generateSchedule(employees, shifts, numDays, useWorkHours, multiEmpsOneShift, false);

        int[][][] idSchedule = convertToIdSchedule(schedule);

        HashMap<Integer, Integer> shiftCounts = ShiftScheduler.getShiftCountsOfEmployees(idSchedule);
        int expectedShiftCount = shiftCounts.values().iterator().next(); // All should have the same count.

        for (int count : shiftCounts.values()) {
            if (count != expectedShiftCount) {
                throw new AssertionError("Employees do not have equal shifts.");
            }
        }
    }

    /** Test that all employees have equal shifts when multiEmpsOneShift is true and rebalancing occurs randomly. */
    public static void testRandomRebalancing() {
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", 40 * 4, 160 * 4));
        employees.add(new Employee(2, "Bob", 40 * 4, 160 * 4));
        employees.add(new Employee(3, "Charlie", 40 * 4, 160 * 4));
        employees.add(new Employee(4, "Diana", 40 * 4, 160 * 4));

        List<Shift> shifts = new ArrayList<>();
        shifts.add(new Shift("08:00", "16:00")); // 8 hours
        shifts.add(new Shift("16:00", "00:00")); // 8 hours
        shifts.add(new Shift("00:00", "08:00")); // 8 hours

        int numDays = 5;
        boolean useWorkHours = false;
        boolean multiEmpsOneShift = true;

        Employee[][][] employeeSchedule = ShiftScheduler.generateSchedule(employees, shifts, numDays, useWorkHours, multiEmpsOneShift, false);

        // Convert schedule to int[][][]
        int[][][] schedule = convertToIdSchedule(employeeSchedule);

        // Ensure all employees have equal shifts
        HashMap<Integer, Integer> shiftCounts = ShiftScheduler.getShiftCountsOfEmployees(schedule);
        int expectedShiftCount = shiftCounts.values().iterator().next();
        for (int count : shiftCounts.values()) {
            if (count != expectedShiftCount) {
                throw new AssertionError("Employees do not have equal shifts.");
            }
        }
    }

    /** Test that monthly work hours are correctly calculated. */
    public static void testTotalWorkHoursCalculation() {
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", 40 * 4, 160 * 4));
        employees.add(new Employee(2, "Bob", 40 * 4, 160 * 4));
    
        List<Shift> shifts = new ArrayList<>();
        shifts.add(new Shift("08:00", "16:00")); // 8 hours
        shifts.add(new Shift("16:00", "00:00")); // 8 hours
    
        int numDays = 5;
        boolean useWorkHours = false;
        boolean multiEmpsOneShift = false;
    
        Employee[][][] employeeSchedule = ShiftScheduler.generateSchedule(employees, shifts, numDays, useWorkHours, multiEmpsOneShift, false);
    
        // Convert schedule to int[][][]
        int[][][] schedule = convertToIdSchedule(employeeSchedule);
    
        HashMap<Integer, Integer> workHours = ShiftScheduler.getWorkHoursOfEmployees(schedule, shifts, numDays);
    
        // Calculate total hours in the schedule
        int assignedShifts = 0;
        for (int[][] day : schedule) {
            for (int[] shift : day) {
                if (shift.length > 0) assignedShifts++;
            }
        }
    
        // Ensure scaling accounts for actual assigned shifts
        int actualTotalHours = assignedShifts*8;
    
        for (Map.Entry<Integer, Integer> entry : workHours.entrySet()) {
            int hours = entry.getValue();
            if (hours != actualTotalHours / employees.size()) { // Divide among employees
                throw new AssertionError("Monthly work hours calculation is incorrect for Employee ID: " + entry.getKey());
            }
        }
    }

    /** Test that an employee may have more than one shift per day */
    public static void testAllowMultipleShiftsPerDayTrue() {
        List<Employee> employees = Arrays.asList(
            new Employee(1, "Alice"),
            new Employee(2, "Bob"),
            new Employee(3, "Charlie")
        );

        List<Shift> shifts = Arrays.asList(
            new Shift("08:00", "12:00"),
            new Shift("13:00", "17:00"),
            new Shift("18:00", "22:00")
        );

        Employee[][][] schedule = ShiftScheduler.generateSchedule(employees, shifts, 1, false, false, true);

        // Validate that employees can appear in multiple shifts in a single day
        Set<Employee> employeesAssigned = new HashSet<>();
        for (int shiftIndex = 0; shiftIndex < shifts.size(); shiftIndex++) {
            for (Employee e : schedule[0][shiftIndex]) {
                employeesAssigned.add(e);
            }
        }
        if (employeesAssigned.size() < employees.size()) {
            throw new AssertionError("Test failed: Not all employees were assigned to multiple shifts when allowed.");
        }
    }

    /** Test that an employee may not have more than one shift per day */
    public static void testAllowMultipleShiftsPerDayFalse() {
        List<Employee> employees = Arrays.asList(
            new Employee(1, "Alice"),
            new Employee(2, "Bob"),
            new Employee(3, "Charlie")
        );

        List<Shift> shifts = Arrays.asList(
            new Shift("08:00", "12:00"),
            new Shift("13:00", "17:00"),
            new Shift("18:00", "22:00")
        );

        Employee[][][] schedule = ShiftScheduler.generateSchedule(employees, shifts, 1, false, false, false);

        // Validate that no employee appears in more than one shift in a single day
        Set<Employee> employeesAssigned = new HashSet<>();
        for (int shiftIndex = 0; shiftIndex < shifts.size(); shiftIndex++) {
            for (Employee e : schedule[0][shiftIndex]) {
                if (!employeesAssigned.add(e)) {
                    throw new AssertionError("Test failed: Employee " + e.getName() + " was assigned to multiple shifts in a single day when not allowed.");
                }
            }
        }
    }

    /**
     * Utility method to convert Employee[][][] schedule to int[][][] schedule with Employee IDs.
     * @param schedule The schedule with Employee objects.
     * @return The schedule with Employee IDs.
     */
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

    public static void main(String[] args) {
        byte numPassed = 0;
        try {
            testEqualShiftsWithMultiEmpsOneShift();
            System.out.println("[PASSED] testEqualShiftsWithMultiEmpsOneShift");
            numPassed += 1;

            testMaxWorkHoursConstraint();
            System.out.println("[PASSED] testMaxWorkHoursConstraint");
            numPassed += 1;

            testMinWorkHoursConstraint();
            System.out.println("[PASSED] testMinWorkHoursConstraint");
            numPassed += 1;

            testNoShiftsAvailable();
            System.out.println("[PASSED] testNoShiftsAvailable");
            numPassed += 1;

            testRandomRebalancing();
            System.out.println("[PASSED] testRandomRebalancing");
            numPassed += 1;

            testTotalWorkHoursCalculation();
            System.out.println("[PASSED] testMonthlyWorkHoursCalculation");
            numPassed += 1;

            testAllowMultipleShiftsPerDayTrue();
            System.out.println("[PASSED] testAllowMultipleShiftsPerDayTrue");
            numPassed += 1;

            testAllowMultipleShiftsPerDayFalse();
            System.out.println("[PASSED] testAllowMultipleShiftsPerDayFalse");
            numPassed += 1;

            System.out.println("All " + numPassed + " tests have passed.");
        } catch (AssertionError e) {
            System.err.println("[FAILED] " + e.getMessage());
            System.out.println(numPassed + " tests have passed.");
            System.exit(1);
        }
    }
}