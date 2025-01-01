package server.engine;

/** Class for calculating length of shifts given 24-hour time */
public class Shift {
    private final int length;

    /**
     * Constructor to calculate the length of the shift in minutes.
     * @param start the start time in 24-hour format (e.g., "08:30").
     * @param end the end time in 24-hour format (e.g., "18:45").
     */
    public Shift(String start, String end) {
        this.length = calculateLength(start, end);
    }

    /**
     * Helper method to calculate the length of a shift in minutes.
     * @param start the start time in 24-hour format (e.g., "08:30").
     * @param end the end time in 24-hour format (e.g., "18:45").
     * @return the duration of the shift in minutes.
     */
    private int calculateLength(String start, String end) {
        int startMinutes = convertToMinutes(start);
        int endMinutes = convertToMinutes(end);
        // Handle cases where the shift spans past midnight => Add 24 hours in minutes.
        if (endMinutes < startMinutes) { endMinutes += 24 * 60; }
        return endMinutes - startMinutes;
    }

    /**
     * Converts a time in "HH:mm" format to the total number of minutes past midnight.
     * @param time the time in 24-hour format.
     * @return the total number of minutes past midnight.
     */
    private int convertToMinutes(String time) {
        String[] parts = time.split(":");
        int hours = Integer.parseInt(parts[0]);
        int minutes = Integer.parseInt(parts[1]);
        return hours * 60 + minutes;
    }

    /** @return The length of the shift in minutes. */
    public final int getLength() { return length; }
}