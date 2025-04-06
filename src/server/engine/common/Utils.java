package server.engine.common;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

public class Utils {
    /** @return minWorkHours = 7 × (numDaysInMonth - numWeekendDaysInMonth) */
    public static int calcMinWorkHours(int year, int month, Set<DayOfWeek> weekendDays) {
        YearMonth ym = YearMonth.of(year, month);
        int totalDays = ym.lengthOfMonth();
        int weekendCount = 0;

        for (int day = 1; day <= totalDays; day++) {
            LocalDate date = LocalDate.of(year, month, day);
            if (weekendDays.contains(date.getDayOfWeek())) weekendCount++;
        }
    
        return 7 * (totalDays - weekendCount);
    }

    /** @return minWorkHours = 8 × (numDaysInMonth - numWeekendDaysInMonth) */
    public static int calcMaxWorkHours(int year, int month, Set<DayOfWeek> weekendDays) {
        YearMonth ym = YearMonth.of(year, month);
        int totalDays = ym.lengthOfMonth();
        int weekendCount = 0;

        for (int day = 1; day <= totalDays; day++) {
            LocalDate date = LocalDate.of(year, month, day);
            if (weekendDays.contains(date.getDayOfWeek())) weekendCount++;
        }
    
        return 8 * (totalDays - weekendCount);
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

    /** Runs a test function and sees if it passed or not.  */
    public static void runTest(Runnable testMethod, String testName, AtomicInteger numPassed, AtomicInteger numFailed) {
        try {
            testMethod.run();
            System.out.println("[PASSED] " + testName);
            numPassed.incrementAndGet();
        } catch (Exception e) {
            System.err.println("[FAILED] " + testName + ": " + e.getMessage());
            numFailed.incrementAndGet();
        }
    }
}