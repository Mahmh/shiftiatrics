package server.engine;
import server.engine.common.*;
import server.engine.algorithms.*;
import java.util.List;
import java.util.Arrays;

/** Class for generating shift schedules for employees. */
public class Main {
    public static void main(String[] args) {
        List<Employee> employees = List.of(
            new Employee(1, "Alice", 140, 168),
            new Employee(2, "Bob", 140, 168),
            new Employee(3, "Jack", 140, 168),
            new Employee(4, "Diana", 140, 168),
            new Employee(5, "Sam", 140, 168),
            new Employee(6, "Emily", 140, 168)
        );

        List<Shift> shifts = List.of(
            new Shift("D", "07:00", "15:00"), // Day: 7AM - 3PM
            new Shift("E", "15:00", "23:00"), // Evening: 3PM - 11PM
            new Shift("N", "23:00", "07:00") // Night: 11PM - 7AM (next day)
        );

        List<Holiday> holidays = List.of(
            new Holiday("Holiday", Arrays.asList(4), "2025-10-04", "2025-10-18") // Diana on holiday Oct 4–5
        );

        Schedule schedule = A1.generate(employees, shifts, holidays, 30, 2025, 10);
        schedule.print();
    }
}