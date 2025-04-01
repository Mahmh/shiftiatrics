package server.engine;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

/** Class for representing holidays */
public record Holiday(String name, List<Integer> assignedTo, LocalDate startDate, LocalDate endDate) {
    /**
     * Constructor to initialize a Holiday object from date strings.
     * @param name the name of the holiday.
     * @param assignedTo the list of employee IDs assigned to this holiday.
     * @param startDate the start date of the holiday in "yyyy-MM-dd" format.
     * @param endDate the end date of the holiday in "yyyy-MM-dd" format.
     * @throws IllegalArgumentException if startDate is after endDate.
     */
    public Holiday(String name, List<Integer> assignedTo, String startDate, String endDate) {
        this(
            name,
            assignedTo,
            LocalDate.parse(startDate, DateTimeFormatter.ofPattern("yyyy-MM-dd")),
            LocalDate.parse(endDate, DateTimeFormatter.ofPattern("yyyy-MM-dd"))
        );
        if (this.startDate.isAfter(this.endDate)) {
            throw new IllegalArgumentException("Start date must be before or equal to end date.");
        }
    }

    /** @return The duration of the holiday in days. */
    public int duration() { return (int) (endDate.toEpochDay() - startDate.toEpochDay()); }
}