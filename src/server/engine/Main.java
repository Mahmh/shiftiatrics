package server.engine;
import server.engine.common.*;
import server.engine.algorithms.A1.T1;
import java.util.List;
import java.util.Arrays;

/** Demo class */
public class Main {
    public static void main(String[] args) {
        List<Employee> employees = List.of(
            new Employee(1, "Alice"),
            new Employee(2, "Bob"),
            new Employee(3, "Jack"),
            new Employee(4, "Diana"),
            new Employee(5, "Sam"),
            new Employee(6, "Emily")
        );

        List<Shift> shifts = List.of(
            new Shift("D", "07:00", "15:00"), // Day: 7AM - 3PM
            new Shift("E", "15:00", "23:00"), // Evening: 3PM - 11PM
            new Shift("N", "23:00", "07:00") // Night: 11PM - 7AM (next day)
        );

        List<Holiday> holidays = List.of(
            new Holiday("Holiday", Arrays.asList(4), "2025-10-01", "2025-10-30") // Diana on annual leave holiday
        );

        Schedule schedule = T1.generate(employees, shifts, holidays, 30, 2025, 9);
        schedule.print();
    }
}