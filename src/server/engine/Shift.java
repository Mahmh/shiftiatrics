package server.engine;

/** Class for employee shifts */
public record Shift(String name, String startTime, String endTime, int length) {
    /**
     * Constructs a Shift object and calculates its length in minutes.
     * @param name Name of the shift (e.g., "Morning", "Night", etc.)
     * @param start The start time in 24-hour format (e.g., "08:30").
     * @param end The end time in 24-hour format (e.g., "18:45").
     */
    public Shift(String name, String start, String end) {
        this(name, start, end, calculateLength(start, end));
    }

    /**
     * Determines whether the shift is a night shift. A shift is considered a night shift if:
     * <ul>
     * <li>The shift name (case-insensitive) is "n" or "night"</li>
     * <li>OR the shift starts at or after 22:00 (10 PM) or before 06:00 (6 AM)</li>
     * </ul>
     * @return true if the shift qualifies as a night shift, false otherwise.
     */
    public boolean isNightShift() {
        String lowerName = this.name.toLowerCase();
        int startMinutes = convertToMinutes(this.startTime);
        return lowerName.equals("n") || lowerName.equals("night") || startMinutes >= 22 * 60 || startMinutes < 6 * 60;
    }

    /**
     * Calculates the length of the shift in minutes.
     * @param start The start time in "HH:mm" format.
     * @param end The end time in "HH:mm" format.
     * @return The duration of the shift in minutes.
     */
    private static int calculateLength(String start, String end) {
        int startMinutes = convertToMinutes(start);
        int endMinutes = convertToMinutes(end);
        if (endMinutes < startMinutes) {
            endMinutes += 24 * 60;
        }
        return endMinutes - startMinutes;
    }

    /**
     * Converts a time in "HH:mm" format to the total number of minutes past midnight.
     * @param time The time string in 24-hour format.
     * @return The total minutes past midnight.
     */
    private static int convertToMinutes(String time) {
        String[] parts = time.split(":");
        int hours = Integer.parseInt(parts[0]);
        int minutes = Integer.parseInt(parts[1]);
        return hours * 60 + minutes;
    }
}