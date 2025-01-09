package server.engine;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

/** Class for representing holidays */
public class Holiday {
    private final String holidayName;
    private final List<Integer> assignedTo;
    private final LocalDate startDate;
    private final LocalDate endDate;

    // Getters
    public String getHolidayName() { return holidayName; }
    public List<Integer> getAssignedTo() { return assignedTo; }
    public LocalDate getStartDate() { return startDate; }
    public LocalDate getEndDate() { return endDate; }
    /** @return The duration of the holiday in days. */
    public int getDuration() { return (int) (endDate.toEpochDay() - startDate.toEpochDay()); }

    /**
     * Constructor to initialize a Holiday object.
     * @param holidayName the name of the holiday.
     * @param assignedTo the list of employee IDs assigned to this holiday.
     * @param startDate the start date of the holiday in "yyyy-MM-dd" format.
     * @param endDate the end date of the holiday in "yyyy-MM-dd" format.
     */
    public Holiday(String holidayName, List<Integer> assignedTo, String startDate, String endDate) throws IllegalArgumentException {
        this.holidayName = holidayName;
        this.assignedTo = assignedTo;
        this.startDate = LocalDate.parse(startDate, DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        this.endDate = LocalDate.parse(endDate, DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        if (this.startDate.isAfter(this.endDate)) throw new IllegalArgumentException("Start date must be before or equal to end date.");
    }
}