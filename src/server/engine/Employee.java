package server.engine;
import java.util.Objects;

/** A struct to represent an employee with an ID and name. */
public class Employee {
    public final int id;
    public final String name;

    public Employee(int id, String name) {
        this.id = id;
        this.name = name;
    }

    @Override
    public final String toString() { return name + " (ID: " + id + ")"; }

    @Override
    public final int hashCode() { return Objects.hash(id); }

    @Override
    public final boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Employee employee = (Employee) obj;
        return id == employee.id;
    }
}