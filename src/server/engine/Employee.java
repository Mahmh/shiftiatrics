package server.engine;
import java.util.Objects;

/** A struct to represent an employee with an ID, name, and *monthly* work hours. */
public record Employee(int id, String name, int minWorkHours, int maxWorkHours) {
    /**
     * Primary constructor for Employee with required work hour constraints.
     * @param id The employee ID.
     * @param name The employee's name.
     * @param minWorkHours Minimum monthly work hours.
     * @param maxWorkHours Maximum monthly work hours.
     * @throws IllegalArgumentException if minWorkHours > maxWorkHours
     */
    public Employee {
        if (minWorkHours > maxWorkHours) throw new IllegalArgumentException("minWorkHours is greater than maxWorkHours");
    }

    /** Secondary constructor for Employee without work hour constraints. */
    public Employee(int id, String name) { this(id, name, -1, -1); }

    @Override
    public String toString() { return name + " (ID: " + id + ")"; }

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
}