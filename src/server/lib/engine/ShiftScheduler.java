package server.lib.engine;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.*;

/** Class for generating shift schedules for employees. */
public class ShiftScheduler {
    // Type aliases
    public static final class Schedule extends LinkedHashMap<String, List<Employee>> {}
    public static final class ShiftCounts extends HashMap<Employee, Integer> {}
    public static final class ShiftCountEntry extends AbstractMap.SimpleEntry<Employee, Integer> {
        public ShiftCountEntry(Employee key, Integer value) { super(key, value); }
    }

    /**
     * Retrieves the current month and its number of days.
     * @return An array where the first element is the month and the second is the number of days.
     */
    public static final int[] getCurrentMonthDays() {
        LocalDate now = LocalDate.now();
        int month = now.getMonthValue();
        int year = now.getYear();
        int days = YearMonth.of(year, month).lengthOfMonth();
        return new int[]{month, days};
    }


    /**
     * Generates a balanced shift schedule for a given number of employees and shifts.
     * @param employees The list of employees.
     * @param numShiftsPerDay The number of shifts per day.
     * @return A Schedule object mapping each day to the list of employees assigned to shifts.
     */
    public static Schedule generateSchedule(List<Employee> employees, int numShiftsPerDay) {
        Integer daysInMonth = getCurrentMonthDays()[1];

        Schedule schedule = new Schedule();
        ShiftCounts shiftCounts = new ShiftCounts();
        for (Employee employee : employees) shiftCounts.put(employee, 0);

        Random random = new Random();

        // Generate schedule for each day
        for (int day = 1; day <= daysInMonth; day++) {
            List<Employee> availableEmployees = new ArrayList<>(employees);
            Collections.shuffle(availableEmployees, random);
            List<Employee> dailyShifts = new ArrayList<>();
            
            // Sort employees by shift count and randomize tie-breaking
            availableEmployees.sort(Comparator.comparingInt(shiftCounts::get).thenComparingInt(e -> random.nextInt()));

            for (int shift = 0; shift < numShiftsPerDay; shift++) {
                if (!availableEmployees.isEmpty()) {
                    Employee selectedEmployee = availableEmployees.remove(0);
                    dailyShifts.add(selectedEmployee);
                    shiftCounts.put(selectedEmployee, shiftCounts.get(selectedEmployee) + 1);
                }
            }

            schedule.put("Day " + day, dailyShifts);
        }

        // Print shift counts for debugging and verification
        System.out.println("\nTotal shifts worked by each employee:");
        for (ShiftCountEntry entry : shiftCounts.entrySet().stream().map(e -> new ShiftCountEntry(e.getKey(), e.getValue())).toList()) {
            System.out.println(entry.getKey() + ": " + entry.getValue() + " shifts");
        }

        return schedule;
    }


    public static void main(String[] args) {
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "John"));
        employees.add(new Employee(2, "Bob"));
        employees.add(new Employee(3, "Charlie"));
        employees.add(new Employee(4, "Diana"));
        employees.add(new Employee(5, "Eve"));
        employees.add(new Employee(6, "Frank"));
        employees.add(new Employee(7, "Grace"));
        employees.add(new Employee(8, "Hank"));
        employees.add(new Employee(9, "Ivy"));
        employees.add(new Employee(10, "Jack"));

        int[] currentMonth = getCurrentMonthDays();
        System.out.println("Current month: " + currentMonth[0] + ", Days: " + currentMonth[1]);

        Schedule schedule = generateSchedule(employees, 3);
        System.out.println();
        for (Map.Entry<String, List<Employee>> entry : schedule.entrySet()) {
            System.out.println(entry.getKey() + ": Shifts:\t" + entry.getValue());
        }
    }
}