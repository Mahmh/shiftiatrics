package server.engine.common;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

public class Utils {
    /** @return minWorkHours = 7 × (numDaysInMonth - numWeekendDaysInMonth) */
    public static int calcMinWorkHours(int year, int month, Set<DayOfWeek> weekendDays) {
        YearMonth ym = YearMonth.of(year, month+1);
        int totalDays = ym.lengthOfMonth();
        int weekendCount = 0;

        for (int day = 1; day <= totalDays; day++) {
            LocalDate date = LocalDate.of(year, month+1, day);
            if (weekendDays.contains(date.getDayOfWeek())) weekendCount++;
        }
    
        return 7 * (totalDays - weekendCount);
    }

    /** @return minWorkHours = 8 × (numDaysInMonth - numWeekendDaysInMonth) */
    public static int calcMaxWorkHours(int year, int month, Set<DayOfWeek> weekendDays) {
        YearMonth ym = YearMonth.of(year, month+1);
        int totalDays = ym.lengthOfMonth();
        int weekendCount = 0;

        for (int day = 1; day <= totalDays; day++) {
            LocalDate date = LocalDate.of(year, month+1, day);
            if (weekendDays.contains(date.getDayOfWeek())) weekendCount++;
        }
    
        return 8 * (totalDays - weekendCount);
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