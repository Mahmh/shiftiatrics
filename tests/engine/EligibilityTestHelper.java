package tests.engine;
import server.engine.*;
import java.util.*;

public class EligibilityTestHelper {
    static Employee testEmp = new Employee(1, "Alice", 0, 160);
    static Shift dayShift = new Shift("D", "08:00", "16:00");
    static Shift nightShift = new Shift("N", "23:00", "07:00");

    static Config baseConfig() {
        return new Config(
            false,
            1,
            false,
            null,
            false,
            7
        );
    }

    static Employee[][][] blankSchedule(int days, int shiftsPerDay) {
        return new Employee[days][shiftsPerDay][];
    }

    static List<Shift> shiftList() {
        return List.of(dayShift, nightShift);
    }

    static Map<Employee, List<Integer>> makeWorkDays(int... days) {
        Map<Employee, List<Integer>> map = new HashMap<>();
        map.put(testEmp, Arrays.stream(days).boxed().toList());
        return map;
    }

    static Map<Employee, Integer> makeWorkMinutes(int minutes) {
        return Map.of(testEmp, minutes);
    }

    static Map<Employee, Integer> makeShiftCount(int count) {
        return Map.of(testEmp, count);
    }

    static Map<Employee, Map<String, List<Integer>>> emptyShiftHistory() {
        return Map.of(testEmp, new HashMap<>());
    }
}