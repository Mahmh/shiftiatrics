package server.engine.common;
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
}