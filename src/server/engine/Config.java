package server.engine;
import java.util.List;

/** Configuration for shift scheduling logic. */
public record Config(
    boolean multiShiftsOneEmp,          // (Optional) Allow multiple shifts per employee per day
    int maxEmpsInShift,                 // Max employees in a single shift
    boolean useRotationPattern,         // Whether to use `rotationPattern`
    List<String> rotationPattern,       // (Optional) e.g., ["Day", "Evening", "Night", null, null]
    boolean avoidBackToBackNights,      // Prevent consecutive night shifts
    int maxShiftsPerWeek            // (Optional) Weekly shift cap per employee
) {
    @Override
    public boolean useRotationPattern() {
        return rotationPattern != null && !rotationPattern.isEmpty() ? useRotationPattern : false;
    }

    @Override
    public boolean avoidBackToBackNights() {
        // If rotationPattern exists, override and disable avoidBackToBackNights (since it's implied by pattern)
        return rotationPattern != null && !rotationPattern.isEmpty() ? false : avoidBackToBackNights;
    }
}