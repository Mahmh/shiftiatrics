package server.engine;
import java.util.Objects;

/** A struct to represent an employee with an ID, name, and *monthly* work hours. */
public class Employee {
    private final int id;
    private final String name;
    private final int minWorkHours;
    private final int maxWorkHours;

    // Getters
    public final int getId() { return id; }
    public final String getName() { return name; }
    public final int getMinWorkHours() { return minWorkHours; }
    public final int getMaxWorkHours() { return maxWorkHours; }

    // Constructors
    public Employee(int id, String name, int minWorkHours, int maxWorkHours) throws IllegalArgumentException {
        if (minWorkHours > maxWorkHours) throw new IllegalArgumentException("minWorkHours is greater than maxWorkHours");
        this.id = id;
        this.name = name;
        this.minWorkHours = minWorkHours;
        this.maxWorkHours = maxWorkHours;
    }

    public Employee(int id, String name) throws IllegalArgumentException {
        this.id = id;
        this.name = name;
        this.minWorkHours = -1;
        this.maxWorkHours = -1;
    }

    // Overrides
    @Override
    public final String toString() { return name + " (ID: " + id + ")"; }
    @Override
    public final int hashCode() { return Objects.hash(id); }
    @Override
    public final boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Employee employee = (Employee) obj;
        return id == employee.getId();
    }
}