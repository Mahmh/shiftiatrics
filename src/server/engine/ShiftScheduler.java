package server.engine;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.*;

/** Class for generating shift schedules for employees. */
public class ShiftScheduler {
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
     * @return A 2D array where each row represents a day, and each column represents an employee assigned to a shift.
     */
    public static Employee[][] generateSchedule(List<Employee> employees, int numShiftsPerDay) {
        int daysInMonth = getCurrentMonthDays()[1];

        Employee[][] schedule = new Employee[daysInMonth][numShiftsPerDay];
        Map<Employee, Integer> shiftCounts = new HashMap<>();
        for (Employee employee : employees) {
            shiftCounts.put(employee, 0);
        }

        Random random = new Random();

        // Generate schedule for each day
        for (int day = 0; day < daysInMonth; day++) {
            List<Employee> availableEmployees = new ArrayList<>(employees);
            Collections.shuffle(availableEmployees, random);

            // Sort employees by shift count and randomize tie-breaking
            availableEmployees.sort(Comparator.comparingInt(shiftCounts::get).thenComparingInt(e -> random.nextInt()));

            for (int shift = 0; shift < numShiftsPerDay; shift++) {
                if (!availableEmployees.isEmpty()) {
                    Employee selectedEmployee = availableEmployees.remove(0);
                    schedule[day][shift] = selectedEmployee;
                    shiftCounts.put(selectedEmployee, shiftCounts.get(selectedEmployee) + 1);
                }
            }
        }

        // Print shift counts for debugging and verification
        System.out.println("\nTotal shifts worked by each employee:");
        for (Map.Entry<Employee, Integer> entry : shiftCounts.entrySet()) {
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

        Employee[][] schedule = generateSchedule(employees, 3);
        System.out.println();
        for (int day = 0; day < schedule.length; day++) {
            System.out.print("Day " + (day + 1) + ": Shifts:\t");
            for (int shift = 0; shift < schedule[day].length; shift++) {
                System.out.print(schedule[day][shift] + (shift < schedule[day].length - 1 ? ", " : ""));
            }
            System.out.println();
        }
    }
}