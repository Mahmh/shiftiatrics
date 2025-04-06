package tests.engine;
import server.engine.common.Utils;
import server.engine.common.Employee;
import server.engine.common.Holiday;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.EnumSet;
import java.util.Set;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

public class UtilsTest {
    public static void main(String[] args) {
        AtomicInteger passed = new AtomicInteger(0), failed = new AtomicInteger(0);

        Stream.<Runnable>of(
            () -> Utils.runTest(UtilsTest::testCalcMinWorkHours, "testCalcMinWorkHours", passed, failed),
            () -> Utils.runTest(UtilsTest::testCalcMaxWorkHours, "testCalcMaxWorkHours", passed, failed),
            () -> Utils.runTest(UtilsTest::testIsOnHoliday, "testIsOnHoliday", passed, failed),
            () -> Utils.runTest(UtilsTest::testIsAlreadyAssigned, "testIsAlreadyAssigned", passed, failed),
            () -> Utils.runTest(UtilsTest::testGetWeeklyShifts, "testGetWeeklyShifts", passed, failed)
        ).parallel().forEach(Runnable::run);

        System.out.println(passed.get() + " passed, " + failed.get() + " failed");
        System.exit(failed.get() > 0 ? 1 : 0);
    }

    static void testCalcMinWorkHours() {
        Set<DayOfWeek> weekendDays = EnumSet.of(DayOfWeek.FRIDAY, DayOfWeek.SATURDAY);
        int result = Utils.calcMinWorkHours(2024, 4, weekendDays); // April 2024
        int expected = 7 * (30 - countWeekends(2024, 4, weekendDays));
        assert result == expected : "Expected " + expected + ", got " + result;
    }

    static void testCalcMaxWorkHours() {
        Set<DayOfWeek> weekendDays = EnumSet.of(DayOfWeek.FRIDAY, DayOfWeek.SATURDAY);
        int result = Utils.calcMaxWorkHours(2024, 4, weekendDays); // April 2024
        int expected = 8 * (30 - countWeekends(2024, 4, weekendDays));
        assert result == expected : "Expected " + expected + ", got " + result;
    }

    static void testIsOnHoliday() {
        Employee emp = new Employee(1, "Dr. Alice", 100, 160);
        LocalDate start = LocalDate.of(2024, 4, 10);
        LocalDate end = LocalDate.of(2024, 4, 15);
        Holiday holiday = new Holiday("Eid", List.of(1), start, end);

        assert Utils.isOnHoliday(emp, List.of(holiday), LocalDate.of(2024, 4, 12)) : "Should be on holiday";
        assert !Utils.isOnHoliday(emp, List.of(holiday), LocalDate.of(2024, 4, 9)) : "Should not be on holiday";
    }

    static void testIsAlreadyAssigned() {
        Employee emp1 = new Employee(1, "Alice", 100, 160);
        Employee emp2 = new Employee(2, "Bob", 100, 160);
        Employee[][][] schedule = new Employee[1][2][];
        schedule[0][0] = new Employee[]{emp1};
        schedule[0][1] = new Employee[]{};

        assert Utils.isAlreadyAssigned(emp1, schedule, 0) : "Alice should be already assigned";
        assert !Utils.isAlreadyAssigned(emp2, schedule, 0) : "Bob should not be assigned";
    }

    static void testGetWeeklyShifts() {
        List<Integer> daysWorked = List.of(0, 1, 2, 4, 6); // 7-day week
        int result = Utils.getWeeklyShifts(daysWorked, 6);
        assert result == 5 : "Expected 5 shifts this week, got " + result;
    }

    private static int countWeekends(int year, int month, Set<DayOfWeek> weekends) {
        int count = 0;
        YearMonth ym = YearMonth.of(year, month);
        for (int day = 1; day <= ym.lengthOfMonth(); day++) {
            DayOfWeek dow = LocalDate.of(year, month, day).getDayOfWeek();
            if (weekends.contains(dow)) count++;
        }
        return count;
    }
}