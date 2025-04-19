package server.engine.common;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

/** Represents an employee with an ID, name, and *monthly* work hours. */
public record Employee(int id, String name, int minWorkHours, int maxWorkHours) {
    public Employee { if (minWorkHours > maxWorkHours) throw new IllegalArgumentException("minWorkHours is greater than maxWorkHours"); }
    public Employee(int id, String name) { this(id, name, -1, -1); }

    @Override
    public String toString() { return name + " (id=" + id + ")"; }

    @Override
    public int hashCode() { return Objects.hash(id); }

    /** @return true if both employees are equal by ID only, false otherwise. */
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Employee employee = (Employee) obj;
        return id == employee.id();
    }

    /**
     * Checks if the employee is on holiday on the specified date.
     * @param holidays The list of holidays.
     * @param currentDate The date being evaluated.
     * @return true if the employee is on holiday, false otherwise.
     */
    public boolean isOnHoliday(List<Holiday> holidays, LocalDate currentDate) {
        return holidays.stream().anyMatch(h -> h.assignedTo().contains(this.id) &&
                !currentDate.isBefore(h.startDate()) &&
                !currentDate.isAfter(h.endDate()));
    }

    /**
     * Checks whether the given employee has already been assigned to a shift on the specified day.
     * This prevents assigning the same employee to multiple shifts in one day if not allowed.
     * @param schedule The schedule matrix.
     * @param day The day index to check.
     * @return true if the employee is already assigned on that day, false otherwise.
     */
    public boolean isAlreadyAssigned(Employee[][][] schedule, int day) {
        for (Employee[] shift : schedule[day]) {
            if (shift != null && Arrays.asList(shift).contains(this)) return true;
        }
        return false;
    }
}