package server.engine.common;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

public class Utils {
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
     * Calculates the number of shifts an employee has worked in the current week (starting from Sunday).
     * @param daysWorked List of days the employee has worked.
     * @param currentDay The current day being evaluated.
     * @return The number of shifts worked during the current week.
     */
    public static int getWeeklyShifts(List<Integer> daysWorked, int currentDay) {
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
            if (shift != null && Arrays.asList(shift).contains(employee)) return true;
        }
        return false;
    }
}