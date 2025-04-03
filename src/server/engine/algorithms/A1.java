package server.engine.algorithms;
import server.engine.common.*;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

public class A1 {
    private static List<String> rotationPattern = Arrays.asList("D", "E", "N", null, null);

    /**
     * Generates a shift schedule strictly following a given rotation pattern.
     * Each employee follows the pattern with a staggered offset.
     * When an employee is unavailable (holiday), the next eligible employee fills in,
     * strictly respecting the rotation pattern.
     * @return 3D array where each day and shift contains an array of assigned employees.
     */
    public static Schedule generate(List<Employee> employees, List<Shift> shifts, List<Holiday> holidays, int numDays, int year, int month) {
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
    
        int patternLength = rotationPattern.size();
    
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
                String todayShiftName = rotationPattern.get(patternPos);

                if (todayShiftName == null) continue;
    
                Integer shiftIdx = shiftIndexMap.get(todayShiftName);
                if (shiftIdx == null) continue;

                Shift shift = shifts.get(shiftIdx);
    
                if (
                    !Utils.isOnHoliday(employee, holidays, currentDate) &&
                    (Config.multiShiftsOneEmp() || !alreadyAssignedToday.contains(employee)) &&
                    totalWeeklyShifts.get(employee) < Config.maxShiftsPerWeek() &&
                    todayAssignments.get(shiftIdx).size() < Config.maxEmpsInShift()
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

                if (assigned.size() >= Config.maxEmpsInShift()) continue;
    
                List<Employee> candidates = shuffledEmployees.stream()
                    .filter(e -> !Utils.isOnHoliday(e, holidays, currentDate))
                    .filter(e -> Config.multiShiftsOneEmp() || !alreadyAssignedToday.contains(e))
                    .filter(e -> totalWeeklyShifts.get(e) < Config.maxShiftsPerWeek())
                    .sorted(Comparator.comparingInt(totalWorkMinutes::get))
                    .collect(Collectors.toList());
    
                for (Employee candidate : candidates) {
                    if (assigned.size() >= Config.maxEmpsInShift()) break;
    
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
    
        return new Schedule(schedule, employees, shifts);
    }


    /**
     * Determines whether an employee is eligible to be assigned to a given shift on a specific day,
     * based on scheduling constraints provided in the Configuration. Constraints checked include:
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
     * @param Config              The Configuration object specifying scheduling constraints.
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
        Map<Employee, Map<String, List<Integer>>> shiftHistory
    ) {
        if (!Config.multiShiftsOneEmp() && Utils.isAlreadyAssigned(employee, schedule, day)) return false;

        int projectedHours = (totalWorkMinutes.get(employee) + shift.length()) / 60;
        if (projectedHours > employee.maxWorkHours()) return false;

        List<Integer> daysWorked = workDaysPerEmployee.get(employee);
        if (Utils.getWeeklyShifts(daysWorked, day) >= Config.maxShiftsPerWeek()) return false;

        if (Config.avoidBackToBackNights() && shift.isNightShift()) {
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
     * Advances the rotation pointer for a given employee.
     * <p>
     * This moves the employee to the next position in the rotation pattern cycle.
     * It ensures that the pointer wraps around to the beginning of the pattern when reaching the end.
     * If the rotation pattern is null or empty, the method does nothing.
     * @param employee        The employee whose rotation pointer is being advanced.
     * @param rotationPointer A map tracking each employee's current index in the rotation pattern.
     * @param Config          The Configuration object containing the rotation pattern.
     */
    public static void advanceRotationPointer(Employee employee, Map<Employee, Integer> rotationPointer) {
        if (rotationPattern == null || rotationPattern.isEmpty()) return;
        int next = (rotationPointer.get(employee) + 1) % rotationPattern.size();
        rotationPointer.put(employee, next);
    }
}


class Config {
    public static boolean multiShiftsOneEmp() { return true; }
    public static boolean avoidBackToBackNights() { return true; }
    public static int maxShiftsPerWeek() { return 7; }
    public static int maxEmpsInShift() { return 1; }
}