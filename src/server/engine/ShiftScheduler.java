package server.engine;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

/** Class for generating shift schedules for employees. */
public class ShiftScheduler {
    /**
     * Returns a mapping from `Employee.id` to the total number of shifts they have worked, according to the given schedule.
     * @param schedule The generated schedule as an `int[][][]` (Employee IDs).
     * @return A hash map with `Employee.id` as the key and the total shift count as the value.
     */
    public static HashMap<Integer, Integer> getShiftCountsOfEmployees(int[][][] schedule) {
        HashMap<Integer, Integer> shiftCounts = new HashMap<>();
        for (int[][] day : schedule)
            for (int[] shift : day)
                for (int employeeId : shift) {
                    shiftCounts.put(employeeId, shiftCounts.getOrDefault(employeeId, 0) + 1);
                }
        return shiftCounts;
    }

    /**
     * Returns a mapping from `Employee.id` to the total number of work hours
     * accumulated from all the days in the given schedule.
     * @param schedule The generated schedule as an `int[][][]` (Employee IDs).
     * @param shifts   The list of shifts, providing shift lengths.
     * @param numDays  The number of days in the given schedule.
     * @return A hash map with `Employee.id` as the key and the total work hours as the value.
     */
    public static HashMap<Integer, Integer> getWorkHoursOfEmployees(int[][][] schedule, List<Shift> shifts, int numDays) {
        HashMap<Integer, Integer> workHours = new HashMap<>();

        for (int[][] day : schedule) {
            for (int shiftIndex = 0; shiftIndex < day.length; shiftIndex++) {
                int[] shift = day[shiftIndex];
                int shiftLength = shifts.get(shiftIndex).length(); // Shift length in minutes
                for (int employeeId : shift) {
                    workHours.put(employeeId, workHours.getOrDefault(employeeId, 0) + shiftLength / 60);
                }
            }
        }

        return workHours; // Total work hours per employee over all days
    }

    /**
     * Generates a balanced shift schedule for a given list of shifts and employees.
     * @param employees List of employees to schedule.
     * @param shifts    List of daily shift types.
     * @param holidays  List of holidays when employees are unavailable.
     * @param numDays   Number of days in the schedule.
     * @param year      Year of the schedule.
     * @param month     Month of the schedule.
     * @param config    Configuration object that controls scheduling rules.
     * @return 3D array where each day and shift contains an array of assigned employees.
     */
    public static Employee[][][] generateSchedule(List<Employee> employees, List<Shift> shifts, List<Holiday> holidays, int numDays, int year, int month, Config config) {
        if (config.useRotationPattern()) return generateScheduleWithPattern(employees, shifts, holidays, numDays, year, month, config);

        Employee[][][] schedule = new Employee[numDays][shifts.size()][];
        Map<Employee, Integer> totalWorkMinutes = new HashMap<>();
        Map<Employee, Integer> totalShiftsAssigned = new HashMap<>();
        Map<Employee, List<Integer>> workDaysPerEmployee = new HashMap<>();
        Map<Employee, Map<String, List<Integer>>> shiftHistory = new HashMap<>();
        Map<Employee, Integer> rotationPointer = new HashMap<>();
    
        for (Employee employee : employees) {
            totalWorkMinutes.put(employee, 0);
            totalShiftsAssigned.put(employee, 0);
            workDaysPerEmployee.put(employee, new ArrayList<>());
            shiftHistory.put(employee, new HashMap<>());
            rotationPointer.put(employee, 0);
        }
    
        Random rand = new Random();
    
        // --- Phase 1: Assign one employee per shift, fairly distributed ---
        for (int day = 0; day < numDays; day++) {
            LocalDate currentDate = LocalDate.of(year, month, day + 1);
            Set<Employee> assignedToday = new HashSet<>();
    
            for (int shiftIndex = 0; shiftIndex < shifts.size(); shiftIndex++) {
                Shift shift = shifts.get(shiftIndex);
                List<Employee> assignedEmployees = new ArrayList<>();
    
                List<Employee> sorted = new ArrayList<>(employees);
                sorted.sort(Comparator.comparingInt(totalWorkMinutes::get).thenComparingInt(e -> rand.nextInt()));
    
                for (Employee employee : sorted) {
                    if (assignedToday.contains(employee)) continue;
                    if (isOnHoliday(employee, holidays, currentDate)) continue;
                    if (!isEligible(employee, schedule, shift, shifts, day, workDaysPerEmployee, totalWorkMinutes, totalShiftsAssigned, shiftHistory, config)) continue;
    
                    if (config.rotationPattern() != null) {
                        String expected = config.rotationPattern().get(rotationPointer.get(employee));
                        if (expected != null && !expected.equalsIgnoreCase(shift.name())) continue;
                        if (expected == null) {
                            advanceRotationPointer(employee, rotationPointer, config);
                            continue;
                        }
                    }
    
                    assignedEmployees.add(employee);
                    assignedToday.add(employee);
                    totalWorkMinutes.put(employee, totalWorkMinutes.get(employee) + shift.length());
                    totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
                    workDaysPerEmployee.get(employee).add(day);
                    shiftHistory.get(employee).computeIfAbsent(shift.name(), k -> new ArrayList<>()).add(day);
                    advanceRotationPointer(employee, rotationPointer, config);
    
                    schedule[day][shiftIndex] = assignedEmployees.toArray(new Employee[0]);
                    break; // Only one employee initially
                }
            }
    
            if (config.rotationPattern() != null) {
                for (Employee employee : employees) {
                    String expected = config.rotationPattern().get(rotationPointer.get(employee));
                    if (expected == null) advanceRotationPointer(employee, rotationPointer, config);
                }
            }
        }
    
        // --- Phase 2: Randomly fill some shifts with multiple employees ---
        if (config.maxEmpsInShift() > 1) {
            // Randomize days order
            List<Integer> daysOrder = new ArrayList<>();
            for (int i = 0; i < numDays; i++) daysOrder.add(i);
            Collections.shuffle(daysOrder, rand);
    
            for (int day : daysOrder) {
                LocalDate currentDate = LocalDate.of(year, month, day + 1);
    
                // Randomly decide to skip this day (e.g., 50% chance)
                if (rand.nextDouble() < 0.5) continue;
    
                for (int shiftIndex = 0; shiftIndex < shifts.size(); shiftIndex++) {
                    Shift shift = shifts.get(shiftIndex);
    
                    // Evening shifts have higher probability
                    double fillChance = shift.name().equalsIgnoreCase("E") ? 0.7 : 0.3;
                    if (rand.nextDouble() > fillChance) continue;
    
                    List<Employee> current = schedule[day][shiftIndex] != null
                                             ? new ArrayList<>(Arrays.asList(schedule[day][shiftIndex]))
                                             : new ArrayList<>();
    
                    if (current.size() >= config.maxEmpsInShift()) continue;
    
                    List<Employee> candidates = new ArrayList<>(employees);
                    candidates.sort(Comparator
                              .comparingInt((Employee e) -> totalWorkMinutes.get(e) >= e.minWorkHours() ? 1 : 0)
                              .thenComparingInt(totalWorkMinutes::get)
                              .thenComparingInt(e -> rand.nextInt()));
    
                    for (Employee employee : candidates) {
                        if (current.contains(employee)) continue;
                        if (isOnHoliday(employee, holidays, currentDate)) continue;
                        if (!isEligible(employee, schedule, shift, shifts, day, workDaysPerEmployee, totalWorkMinutes, totalShiftsAssigned, shiftHistory, config)) continue;
    
                        current.add(employee);
                        totalWorkMinutes.put(employee, totalWorkMinutes.get(employee) + shift.length());
                        totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
                        workDaysPerEmployee.get(employee).add(day);
                        shiftHistory.get(employee).computeIfAbsent(shift.name(), k -> new ArrayList<>()).add(day);
    
                        if (current.size() >= config.maxEmpsInShift()) break;
                    }
    
                    schedule[day][shiftIndex] = current.toArray(new Employee[0]);
                }
            }
        }
    
        return schedule;
    }


    /**
     * Generates a shift schedule strictly following a given rotation pattern.
     * Each employee follows the pattern with a staggered offset.
     * When an employee is unavailable (holiday), the next eligible employee fills in,
     * strictly respecting the rotation pattern.
     * @param employees List of employees to schedule.
     * @param shifts    List of available shifts (e.g., "D", "E", "N").
     * @param holidays  List of holidays when employees are unavailable.
     * @param numDays   Number of days in the schedule.
     * @param year      Year of the schedule.
     * @param month     Month of the schedule.
     * @param config    Configuration object that controls scheduling rules.
     * @return 3D array where each day and shift contains an array of assigned employees.
     */
    private static Employee[][][] generateScheduleWithPattern(List<Employee> employees, List<Shift> shifts, List<Holiday> holidays, int numDays, int year, int month, Config config) {
        if (!config.useRotationPattern()) throw new IllegalArgumentException("rotationPattern must be defined for this method.");

        Employee[][][] schedule = new Employee[numDays][shifts.size()][];
        List<Employee> shuffledEmployees = new ArrayList<>(employees);
        Collections.shuffle(shuffledEmployees);

        Map<String, Integer> shiftIndexMap = new HashMap<>();
        for (int i = 0; i < shifts.size(); i++) shiftIndexMap.put(shifts.get(i).name(), i);
    
        Map<Employee, Integer> totalWeeklyShifts = new HashMap<>();
        Map<Employee, Integer> totalShiftsAssigned = new HashMap<>();
        Map<Employee, Integer> totalWorkMinutes = new HashMap<>();
    
        for (Employee employee : shuffledEmployees) {
            totalWeeklyShifts.put(employee, 0);
            totalShiftsAssigned.put(employee, 0);
            totalWorkMinutes.put(employee, 0);
        }
    
        int patternLength = config.rotationPattern().size();
    
        for (int day = 0; day < numDays; day++) {
            LocalDate currentDate = LocalDate.of(year, month, day + 1);
            boolean isNewWeek = currentDate.getDayOfWeek() == DayOfWeek.MONDAY;
            if (isNewWeek) shuffledEmployees.forEach(e -> totalWeeklyShifts.put(e, 0));
    
            List<List<Employee>> todayAssignments = new ArrayList<>();
            for (int i = 0; i < shifts.size(); i++) todayAssignments.add(new ArrayList<>());
    
            Set<Employee> alreadyAssignedToday = new HashSet<>();
    
            // Step 1: Strict Rotation Assignment
            for (int empIdx = 0; empIdx < shuffledEmployees.size(); empIdx++) {
                Employee employee = shuffledEmployees.get(empIdx);
                int patternPos = (day + empIdx) % patternLength;
                String todayShiftName = config.rotationPattern().get(patternPos);
    
                if (todayShiftName == null) continue;
    
                Integer shiftIdx = shiftIndexMap.get(todayShiftName);
                if (shiftIdx == null) continue;
    
                Shift shift = shifts.get(shiftIdx);
    
                if (
                    !isOnHoliday(employee, holidays, currentDate) &&
                    (config.multiShiftsOneEmp() || !alreadyAssignedToday.contains(employee)) &&
                    totalWeeklyShifts.get(employee) < config.maxShiftsPerWeek() &&
                    todayAssignments.get(shiftIdx).size() < config.maxEmpsInShift()
                ) {
                    todayAssignments.get(shiftIdx).add(employee);
                    totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
                    totalWeeklyShifts.put(employee, totalWeeklyShifts.get(employee) + 1);
                    totalWorkMinutes.put(employee, totalWorkMinutes.get(employee) + shift.length());
                    alreadyAssignedToday.add(employee);
                }
            }
    
            // Step 2: Fill-in Empty Shifts (Least Work Hours Employees)
            for (int shiftIdx = 0; shiftIdx < shifts.size(); shiftIdx++) {
                Shift shift = shifts.get(shiftIdx);
                List<Employee> assigned = todayAssignments.get(shiftIdx);
    
                if (assigned.size() >= config.maxEmpsInShift()) continue;
    
                List<Employee> candidates = shuffledEmployees.stream()
                    .filter(e -> !isOnHoliday(e, holidays, currentDate))
                    .filter(e -> config.multiShiftsOneEmp() || !alreadyAssignedToday.contains(e))
                    .filter(e -> totalWeeklyShifts.get(e) < config.maxShiftsPerWeek())
                    .sorted(Comparator.comparingInt(totalWorkMinutes::get))
                    .collect(Collectors.toList());
    
                for (Employee candidate : candidates) {
                    if (assigned.size() >= config.maxEmpsInShift()) break;
    
                    assigned.add(candidate);
                    totalShiftsAssigned.put(candidate, totalShiftsAssigned.get(candidate) + 1);
                    totalWeeklyShifts.put(candidate, totalWeeklyShifts.get(candidate) + 1);
                    totalWorkMinutes.put(candidate, totalWorkMinutes.get(candidate) + shift.length());
                    alreadyAssignedToday.add(candidate);
                }
            }
    
            for (int shiftIdx = 0; shiftIdx < shifts.size(); shiftIdx++) {
                List<Employee> assigned = todayAssignments.get(shiftIdx);
                schedule[day][shiftIdx] = assigned.toArray(new Employee[0]);
            }
        }
    
        return schedule;
    }


    /**
     * Determines whether an employee is eligible to be assigned to a given shift on a specific day,
     * based on scheduling constraints provided in the configuration. Constraints checked include:
     * <ul>
     * <li>Whether the employee is already assigned that day (if multiple shifts per day are not allowed).</li>
     * <li>Whether assigning this shift would exceed their maximum allowed work hours.</li>
     * <li>Whether the employee has reached the weekly shift limit.</li>
     * <li>Whether the employee worked a night shift the day before (if back-to-back night shifts are disallowed).</li>
     * <li>Whether the minimum gap between same shift types is violated.</li>
     * </ul>
     * @param employee            The employee to evaluate.
     * @param schedule            The current 3D schedule matrix (day → shift → employees).
     * @param shift               The shift being evaluated for assignment.
     * @param day                 The current day index.
     * @param workDaysPerEmployee A map of employee to list of days they've worked.
     * @param totalWorkMinutes    A map of employee to total number of minutes worked so far.
     * @param totalShiftsAssigned A map of employee to number of shifts assigned so far.
     * @param shiftHistory        A map of employee to shift type history (e.g., which days they worked a "D" shift).
     * @param config              The configuration object specifying scheduling constraints.
     * @return true if the employee is eligible for the shift, false otherwise.
     */
    public static boolean isEligible(
        Employee employee,
        Employee[][][] schedule,
        Shift shift,
        List<Shift> shifts,
        int day,
        Map<Employee, List<Integer>> workDaysPerEmployee,
        Map<Employee, Integer> totalWorkMinutes,
        Map<Employee, Integer> totalShiftsAssigned,
        Map<Employee, Map<String, List<Integer>>> shiftHistory,
        Config config
    ) {
        if (!config.multiShiftsOneEmp() && isAlreadyAssigned(employee, schedule, day)) return false;

        int projectedHours = (totalWorkMinutes.get(employee) + shift.length()) / 60;
        if (projectedHours > employee.maxWorkHours()) return false;

        List<Integer> daysWorked = workDaysPerEmployee.get(employee);
        if (getWeeklyShifts(daysWorked, day) >= config.maxShiftsPerWeek()) return false;

        if (config.avoidBackToBackNights() && shift.isNightShift()) {
            if (day > 0 && isNightShiftAssigned(employee, schedule[day - 1], shifts)) return false;
        }

        return true;
    }

    /**
     * Checks whether the employee worked a night shift on the previous day.
     * @param employee The employee to check.
     * @param previousDayShifts Array of assigned employees for each shift on the previous day.
     * @param shifts List of Shift objects (same order as schedule columns).
     * @return true if the employee worked a night shift the day before.
     */
    public static boolean isNightShiftAssigned(Employee employee, Employee[][] previousDayShifts, List<Shift> shifts) {
        for (int i = 0; i < previousDayShifts.length; i++) {
            Employee[] shiftEmployees = previousDayShifts[i];
            if (shiftEmployees != null && Arrays.asList(shiftEmployees).contains(employee)) {
                if (shifts.get(i).isNightShift())
                    return true;
            }
        }
        return false;
    }

    /**
     * Calculates the number of shifts an employee has worked in the current week (starting from Sunday).
     * @param daysWorked List of days the employee has worked.
     * @param currentDay The current day being evaluated.
     * @return The number of shifts worked during the current week.
     */
    private static int getWeeklyShifts(List<Integer> daysWorked, int currentDay) {
        int weekStart = currentDay - (currentDay % 7);
        int count = 0;
        for (int i = weekStart; i <= currentDay; i++) {
            if (daysWorked.contains(i))
                count++;
        }
        return count;
    }

    /**
     * Checks whether the given employee has already been assigned to a shift on the specified day.
     * This prevents assigning the same employee to multiple shifts in one day if not allowed.
     * @param employee The employee to check.
     * @param schedule The schedule matrix.
     * @param day The day index to check.
     * @return true if the employee is already assigned on that day, false otherwise.
     */
    public static boolean isAlreadyAssigned(Employee employee, Employee[][][] schedule, int day) {
        for (Employee[] shift : schedule[day]) {
            if (shift != null && Arrays.asList(shift).contains(employee))
                return true;
        }
        return false;
    }

    /**
     * Checks if the employee is on holiday on the specified date.
     * @param employee The employee to check.
     * @param holidays The list of holidays.
     * @param currentDate The date being evaluated.
     * @return true if the employee is on holiday, false otherwise.
     */
    public static boolean isOnHoliday(Employee employee, List<Holiday> holidays, LocalDate currentDate) {
        return holidays.stream().anyMatch(h -> h.assignedTo().contains(employee.id()) &&
                !currentDate.isBefore(h.startDate()) &&
                !currentDate.isAfter(h.endDate()));
    }

    /**
     * Advances the rotation pointer for a given employee.
     * <p>
     * This moves the employee to the next position in the rotation pattern cycle.
     * It ensures that the pointer wraps around to the beginning of the pattern when reaching the end.
     * If the rotation pattern is null or empty, the method does nothing.
     * @param employee        The employee whose rotation pointer is being advanced.
     * @param rotationPointer A map tracking each employee's current index in the rotation pattern.
     * @param config          The configuration object containing the rotation pattern.
     */
    public static void advanceRotationPointer(Employee employee, Map<Employee, Integer> rotationPointer, Config config) {
        if (config.rotationPattern() == null || config.rotationPattern().isEmpty()) return;
        int next = (rotationPointer.get(employee) + 1) % config.rotationPattern().size();
        rotationPointer.put(employee, next);
    }

    /**
     * Prints the schedule to stdout.
     * @param empSchedule The schedule of employees.
     * @param employees List of employees used when generating the schedule.
     * @param shifts List of shifts used when generating the schedule.
     */
    private static void printSchedule(Employee[][][] empSchedule, List<Employee> employees, List<Shift> shifts) {
        int numDays = empSchedule.length;

        // Convert the schedule to int[][][] with employee IDs
        int[][][] schedule = new int[numDays][shifts.size()][];
        for (int day = 0; day < empSchedule.length; day++) {
            for (int shift = 0; shift < empSchedule[day].length; shift++) {
                Employee[] shiftEmployees = empSchedule[day][shift];
                if (shiftEmployees != null) {
                    schedule[day][shift] = Arrays.stream(shiftEmployees).mapToInt(Employee::id).toArray();
                } else {
                    schedule[day][shift] = new int[0]; // Prevent NullPointerException
                }
            }
        }

        // Print the schedule with shift names
        for (int day = 0; day < schedule.length; day++) {
            System.out.println("Day " + (day + 1) + ":");
            for (int shift = 0; shift < schedule[day].length; shift++) {
                String shiftName = shifts.get(shift).name();
                System.out.print("  " + shiftName + ": ");
                if (schedule[day][shift].length == 0) {
                    System.out.println("No employees assigned");
                } else {
                    for (int employeeId : schedule[day][shift]) {
                        System.out.print(employees.stream()
                                .filter(e -> e.id() == employeeId)
                                .findFirst()
                                .get()
                                .name() + " ");
                    }
                    System.out.println();
                }
            }
        }

        HashMap<Integer, Integer> shiftCounts = getShiftCountsOfEmployees(schedule);
        HashMap<Integer, Integer> workHours = getWorkHoursOfEmployees(schedule, shifts, numDays);

        System.out.println("\nShift counts and work hours:");
        for (Employee employee : employees) {
            int shiftCount = shiftCounts.getOrDefault(employee.id(), 0);
            int workHour = workHours.getOrDefault(employee.id(), 0);
            System.out.println(employee.name() + ":\t" + shiftCount + " shifts\t" + workHour + " hours");
        }
    }


    public static void main(String[] args) {
        List<Employee> employees = List.of(
            new Employee(1, "Alice", 140, 168),
            new Employee(2, "Bob", 140, 168),
            new Employee(3, "Jack", 140, 168),
            new Employee(4, "Diana", 140, 168),
            new Employee(5, "Sam", 140, 168),
            new Employee(6, "Emily", 140, 168)
        );

        List<Shift> shifts = List.of(
            new Shift("D", "07:00", "15:00"), // Day: 7AM - 3PM
            new Shift("E", "15:00", "23:00"), // Evening: 3PM - 11PM
            new Shift("N", "23:00", "07:00") // Night: 11PM - 7AM (next day)
        );

        List<Holiday> holidays = List.of(
            new Holiday("Holiday", Arrays.asList(4), "2025-10-04", "2025-10-18") // Diana on holiday Oct 4–5
        );

        List<String> rotationPattern = Arrays.asList("D", "E", "N", null, null);

        Config config = new Config(
            true,
            1,
            true,
            rotationPattern,
            true,
            7
        );

        Employee[][][] empSchedule = generateSchedule(employees, shifts, holidays, 30, 2025, 10, config);
        printSchedule(empSchedule, employees, shifts);
    }
}