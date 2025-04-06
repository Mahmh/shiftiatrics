package server.engine.algorithms;
import server.engine.common.*;
import java.util.*;
import java.util.stream.Collectors;
import java.time.DayOfWeek;
import java.time.LocalDate;

public class A1 {
    private static final record ShiftSlot(int day, int shiftIdx, Shift shift) {}
    private static final EnumSet<DayOfWeek> weekendDays = EnumSet.of(DayOfWeek.FRIDAY, DayOfWeek.SATURDAY);
    private static final List<String> rotationPattern = Arrays.asList("D", "E", "N", null, null);
    private static final int maxShiftsPerWeek = 5;
    private static final int maxEmpsInShift = 3;
    
    /**
     * Generates a shift schedule strictly following a given rotation pattern.
     * Each employee follows the pattern with a staggered offset.
     * When an employee is unavailable (holiday), the next eligible employee fills in,
     * strictly respecting the rotation pattern.
     * @return 3D array where each day and shift contains an array of assigned employees.
     */
    public static Schedule generate(List<Employee> employees, List<Shift> shifts, List<Holiday> holidays, int numDays, int year, int month) {
        final int defaultMinWorkHours = Utils.calcMinWorkHours(year, month, weekendDays);
        final int defaultMaxWorkHours = Utils.calcMaxWorkHours(year, month, weekendDays);

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
    
        final int patternLength = rotationPattern.size();
    
        for (int day = 0; day < numDays; day++) {
            final int currentDay = day;
            LocalDate currentDate = LocalDate.of(year, month, currentDay + 1);
            boolean isNewWeek = currentDate.getDayOfWeek() == DayOfWeek.SUNDAY;
            if (isNewWeek) shuffledEmployees.forEach(e -> totalWeeklyShifts.put(e, 0));
    
            List<List<Employee>> todayAssignments = new ArrayList<>();
            for (int i = 0; i < shifts.size(); i++) todayAssignments.add(new ArrayList<>());


            // Step 1: Strict Rotation Assignment
            for (int empIdx = 0; empIdx < shuffledEmployees.size(); empIdx++) {
                Employee employee = shuffledEmployees.get(empIdx);
                final int maxWorkHours = employee.maxWorkHours() != -1 ? employee.maxWorkHours() : defaultMaxWorkHours;
                final int patternPos = (currentDay + empIdx) % patternLength;

                String todayShiftName = rotationPattern.get(patternPos);
                if (todayShiftName == null) continue;
    
                Integer shiftIdx = shiftIndexMap.get(todayShiftName);
                if (shiftIdx == null) continue;

                Shift shift = shifts.get(shiftIdx);
                
                if (isEligible(employee, shift, shiftIdx, holidays, currentDate, schedule, totalWorkMinutes, totalWeeklyShifts, todayAssignments, maxWorkHours, currentDay)) {
                    todayAssignments.get(shiftIdx).add(employee);
                    totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
                    totalWeeklyShifts.put(employee, totalWeeklyShifts.get(employee) + 1);
                    totalWorkMinutes.put(employee, totalWorkMinutes.get(employee) + shift.length());
                }
            }
    

            // Step 2: Fill-in Empty Shifts (Least Work Hours Employees)
            for (int shiftIdx = 0; shiftIdx < shifts.size(); shiftIdx++) {
                final int currentShiftIdx = shiftIdx; 
                Shift shift = shifts.get(currentShiftIdx);
                List<Employee> assigned = todayAssignments.get(currentShiftIdx);

                if (assigned.size() >= 1) continue;
    
                List<Employee> candidates = shuffledEmployees.stream()
                    .filter(e -> isEligible(
                        e, shift, currentShiftIdx, holidays, currentDate, schedule, 
                        totalWorkMinutes, totalWeeklyShifts, todayAssignments, 
                        e.maxWorkHours() != -1 ? e.maxWorkHours() : defaultMinWorkHours,
                        currentDay
                    ))
                    .sorted(Comparator.comparingInt(totalWorkMinutes::get))
                    .collect(Collectors.toList());
    
                for (Employee candidate : candidates) {
                    if (assigned.size() >= 1) break;
                    assigned.add(candidate);
                    totalShiftsAssigned.put(candidate, totalShiftsAssigned.get(candidate) + 1);
                    totalWeeklyShifts.put(candidate, totalWeeklyShifts.get(candidate) + 1);
                    totalWorkMinutes.put(candidate, totalWorkMinutes.get(candidate) + shift.length());
                }
            }
    
            for (int shiftIdx = 0; shiftIdx < shifts.size(); shiftIdx++) {
                List<Employee> assigned = todayAssignments.get(shiftIdx);
                schedule[day][shiftIdx] = assigned.toArray(new Employee[0]);
            }
        }

        // Step 3: Post-process underworked employees
        for (Employee employee : shuffledEmployees) {
            final int minWorkHours = employee.minWorkHours() != -1 ? employee.minWorkHours() : defaultMinWorkHours;
            final int maxWorkHours = employee.maxWorkHours() != -1 ? employee.maxWorkHours() : defaultMaxWorkHours;

            int workedMinutes = totalWorkMinutes.getOrDefault(employee, 0);
            final int minRequiredMinutes = minWorkHours * 60;
            if (workedMinutes == 0 || workedMinutes >= minRequiredMinutes) continue;

            // Step 3.1: Collect all eligible evening shifts
            List<ShiftSlot> eligibleSlots = new ArrayList<>();

            for (int day = 0; day < numDays; day++) {
                // Prevent assignment if yesterday's pattern was "N"
                int patternPos = (day - 1 + shuffledEmployees.indexOf(employee)) % rotationPattern.size();
                if (day > 0 && "N".equalsIgnoreCase(rotationPattern.get(patternPos))) continue;

                LocalDate date = LocalDate.of(year, month, day + 1);
                for (int shiftIdx = 0; shiftIdx < shifts.size(); shiftIdx++) {
                    Shift shift = shifts.get(shiftIdx);

                    if (!shift.name().equalsIgnoreCase("E")) continue;
                    if (Utils.isOnHoliday(employee, holidays, date)) continue;
                    if (Utils.isAlreadyAssigned(employee, schedule, day)) continue;
                    if (schedule[day][shiftIdx] == null) schedule[day][shiftIdx] = new Employee[0];
                    if (schedule[day][shiftIdx].length >= maxEmpsInShift) continue;

                    int projectedMinutes = workedMinutes + shift.length();
                    if (projectedMinutes / 60 > maxWorkHours) continue;

                    eligibleSlots.add(new ShiftSlot(day, shiftIdx, shift));
                }
            }

            // Step 3.2: Shuffle and sort by least-filled shifts
            Collections.shuffle(eligibleSlots); // fairness
            eligibleSlots.sort(Comparator.comparingInt(slot -> schedule[slot.day][slot.shiftIdx].length)); // prioritize emptier shifts

            // Step 3.3: Assign the employee to shifts until minWorkHours met
            for (ShiftSlot slot : eligibleSlots) {
                if (workedMinutes >= minRequiredMinutes) break;

                List<Employee> updated = new ArrayList<>(Arrays.asList(schedule[slot.day][slot.shiftIdx]));
                updated.add(employee);
                schedule[slot.day][slot.shiftIdx] = updated.toArray(new Employee[0]);

                workedMinutes += slot.shift.length();
                totalWorkMinutes.put(employee, workedMinutes);
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
     * @return true if the employee is eligible for the shift, false otherwise.
     */
    public static boolean isEligible(
        Employee employee,
        Shift shift,
        int shiftIdx,
        List<Holiday> holidays,
        LocalDate currentDate,
        Employee[][][] schedule,
        Map<Employee, Integer> totalWorkMinutes,
        Map<Employee, Integer> totalWeeklyShifts,
        List<List<Employee>> todayAssignments,
        int maxWorkHours,
        int day
    ) {
        return (
            !Utils.isOnHoliday(employee, holidays, currentDate) &&
            !Utils.isAlreadyAssigned(employee, schedule, day) &&
            totalWeeklyShifts.get(employee) < maxShiftsPerWeek &&
            todayAssignments.get(shiftIdx).size() < 1 &&
            (totalWorkMinutes.get(employee) + shift.length()) / 60 <= maxWorkHours
        );
    }
}