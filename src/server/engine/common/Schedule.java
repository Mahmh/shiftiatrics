package server.engine.common;
import java.util.*;

public record Schedule(Employee[][][] schedule, List<Employee> employees, List<Shift> shifts) {
    /** @return a mapping from `Employee.id` to the total number of shifts they have worked, according to the given schedule. */
    public HashMap<Integer, Integer> getShiftCountsOfEmployees() {
        HashMap<Integer, Integer> shiftCounts = new HashMap<>();
        for (Employee[][] day : schedule)
            for (Employee[] shift : day)
                for (Employee emp : shift) 
                    shiftCounts.put(emp.id(), shiftCounts.getOrDefault(emp.id(), 0) + 1);
        return shiftCounts;
    }

    /** @return a mapping from `Employee.id` to the total number of work hours accumulated from all the days in the given schedule. */
    public HashMap<Integer, Integer> getWorkHoursOfEmployees() {
        HashMap<Integer, Integer> workHours = new HashMap<>();

        for (Employee[][] day : schedule) 
            for (int shiftIndex = 0; shiftIndex < day.length; shiftIndex++) {
                Employee[] shift = day[shiftIndex];
                int shiftLength = shifts.get(shiftIndex).length(); // Shift length in minutes
                for (Employee emp : shift) {
                    workHours.put(emp.id(), workHours.getOrDefault(emp.id(), 0) + shiftLength / 60);
                }
            }

        return workHours; // Total work hours per employee over all days
    }

    /** Prints the schedule to stdout. */
    public void print() {
        // Print each day of the schedule on its own line
        for (int day = 0; day < schedule.length; day++) {
            StringBuilder line = new StringBuilder("Day " + (day + 1) + ":\t");

            for (int shift = 0; shift < schedule[day].length; shift++) {
                String shiftName = shifts.get(shift).name();
                line.append(shiftName).append(" [");

                if (schedule[day][shift].length == 0) {
                    line.append("None");
                } else {
                    for (int i = 0; i < schedule[day][shift].length; i++) {
                        Employee emp = schedule[day][shift][i];
                        String name = employees.stream()
                            .filter(e -> e.id() == emp.id())
                            .findFirst()
                            .map(Employee::name)
                            .orElse("Unknown");
                        line.append(name);
                        if (i < schedule[day][shift].length - 1) line.append(", ");
                    }
                }
                line.append("] \t");
            }

            System.out.println(line.toString().trim());
        }

        // Print shift counts and work hours
        HashMap<Integer, Integer> shiftCounts = getShiftCountsOfEmployees();
        HashMap<Integer, Integer> workHours = getWorkHoursOfEmployees();
        System.out.println("\nShift counts and work hours:");
        for (Employee employee : employees) {
            int shiftCount = shiftCounts.getOrDefault(employee.id(), 0);
            int workHour = workHours.getOrDefault(employee.id(), 0);
            System.out.println(employee.name() + ":\t" + shiftCount + " shifts\t" + workHour + " hours");
        }
    }
}