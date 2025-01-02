package server.engine;
import java.util.*;

/** Class for generating shift schedules for employees. */
public class ShiftScheduler {
    /**
     * Generates a balanced shift schedule for a given list of shifts and employees.
     * @param employees The list of employees.
     * @param shifts The list of shifts.
     * @param numDays The number of days to include in the schedule (i.e., its extent).
     * @param useWorkHours Whether or not to regard employees' min & max work hours.
     * @param multiEmpOneShift Whether or not to put more than one employee in a shift to compensate for work hours. Works only if `useWorkHours` is already true.
     * @param multiShiftsOneEmp Whether or not employees can be assigned to more than one shift per day.
     * @return A 3D array where each row represents a day, and each column represents a shift, containing a list of employees assigned to that shift.
     */
    public static Employee[][][] generateSchedule(
        List<Employee> employees, 
        List<Shift> shifts,
        int numDays,
        boolean useWorkHours,
        boolean multiEmpOneShift,
        boolean multiShiftsOneEmp
    ) {
        Employee[][][] schedule = new Employee[numDays][shifts.size()][];
        HashMap<Employee, Integer> totalWorkMinutes = new HashMap<>();
        HashMap<Employee, Integer> totalShiftsAssigned = new HashMap<>();

        // Initialize total work minutes and shift counts
        for (Employee employee : employees) {
            totalWorkMinutes.put(employee, 0);
            totalShiftsAssigned.put(employee, 0);
        }

        for (int day = 0; day < numDays; day++) {
            for (int shiftIndex = 0; shiftIndex < shifts.size(); shiftIndex++) {
                Shift shift = shifts.get(shiftIndex);
                List<Employee> assignedEmployees = new ArrayList<>();
                int remainingMinutes = shift.getLength();

                List<Employee> availableEmployees = new ArrayList<>(employees);

                // Sort employees by shift count to enforce strict balancing
                availableEmployees.sort(Comparator.comparingInt(totalShiftsAssigned::get)
                        .thenComparingInt(totalWorkMinutes::get)
                        .thenComparingInt(e -> new Random().nextInt()));

                for (Employee employee : availableEmployees) {
                    if (remainingMinutes <= 0) break;
                
                    int currentTotalMinutes = totalWorkMinutes.get(employee);
                    boolean withinLimits = (!useWorkHours || (
                        (employee.getMaxWorkHours() == -1 || (currentTotalMinutes + shift.getLength()) / 60 <= employee.getMaxWorkHours())
                    ));
                
                    // Check if the employee is already assigned to another shift on the same day
                    boolean alreadyAssigned = false;
                
                    if (!multiShiftsOneEmp) {
                        for (int otherShiftIndex = 0; otherShiftIndex < shifts.size(); otherShiftIndex++) {
                            Employee[] otherShiftEmployees = schedule[day][otherShiftIndex];
                            if (otherShiftEmployees != null && Arrays.asList(otherShiftEmployees).contains(employee)) {
                                alreadyAssigned = true;
                                break;
                            }
                        }
                    }
                
                    if (!withinLimits || alreadyAssigned) continue;
                
                    assignedEmployees.add(employee);
                    totalWorkMinutes.put(employee, currentTotalMinutes + shift.getLength());
                    totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
                    remainingMinutes -= shift.getLength();
                
                    // Only assign one employee if multiple employees per shift is not allowed.
                    if (!multiEmpOneShift) break; 
                }                        

                schedule[day][shiftIndex] = assignedEmployees.toArray(new Employee[0]);
            }
        }

        // Final balancing step to ensure strict equality in shift counts
        if (multiEmpOneShift) {
            int maxShifts = Collections.max(totalShiftsAssigned.values());
            for (Employee employee : employees) {
                int assignedShifts = totalShiftsAssigned.get(employee);
                if (assignedShifts < maxShifts) {
                    System.out.println("Rebalancing required for " + employee.getName());
                    Random random = new Random();
                    // Add an extra shift for the under-assigned employee in a random slot
                    while (assignedShifts < maxShifts) {
                        int randomDay = random.nextInt(numDays);
                        int randomShift = random.nextInt(shifts.size());
                        List<Employee> currentShift = new ArrayList<>(Arrays.asList(schedule[randomDay][randomShift]));

                        // Ensure the employee is not already in this shift
                        if (!currentShift.contains(employee)) {
                            // Check if the employee is already assigned to another shift on the same day
                            boolean alreadyAssigned = false;
                        
                            if (!multiShiftsOneEmp) {
                                for (int otherShiftIndex = 0; otherShiftIndex < shifts.size(); otherShiftIndex++) {
                                    Employee[] otherShiftEmployees = schedule[randomDay][otherShiftIndex];
                                    if (otherShiftEmployees != null && Arrays.asList(otherShiftEmployees).contains(employee)) {
                                        alreadyAssigned = true;
                                        break;
                                    }
                                }
                            }
                        
                            if (!alreadyAssigned) {
                                currentShift.add(employee);
                                schedule[randomDay][randomShift] = currentShift.toArray(new Employee[0]);
                                totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
                                assignedShifts++;
                            }
                        }                                         
                    }
                }
            }
        }

        return schedule;
    }

    /**
     * Returns a mapping from `Employee.id` to the total number of shifts they have worked, according to the given schedule.
     * @param schedule The generated schedule as an `int[][][]` (Employee IDs).
     * @return A hash map with `Employee.id` as the key and the total shift count as the value.
     */
    public static HashMap<Integer, Integer> getShiftCountsOfEmployees(int[][][] schedule) {
        HashMap<Integer, Integer> shiftCounts = new HashMap<>();
        for (int[][] day : schedule) {
            for (int[] shift : day) {
                for (int employeeId : shift) {
                    shiftCounts.put(employeeId, shiftCounts.getOrDefault(employeeId, 0) + 1);
                }
            }
        }
        return shiftCounts;
    }

    /**
     * Returns a mapping from `Employee.id` to the total number of work hours accumulated
     * from all the days in the given schedule.
     *
     * @param schedule The generated schedule as an `int[][][]` (Employee IDs).
     * @param shifts The list of shifts, providing shift lengths.
     * @param numDays The number of days in the given schedule.
     * @return A hash map with `Employee.id` as the key and the total work hours as the value.
     */
    public static HashMap<Integer, Integer> getWorkHoursOfEmployees(int[][][] schedule, List<Shift> shifts, int numDays) {
        HashMap<Integer, Integer> workHours = new HashMap<>();

        for (int[][] day : schedule) {
            for (int shiftIndex = 0; shiftIndex < day.length; shiftIndex++) {
                int[] shift = day[shiftIndex];
                int shiftLength = shifts.get(shiftIndex).getLength(); // Shift length in minutes
                for (int employeeId : shift) {
                    workHours.put(employeeId, workHours.getOrDefault(employeeId, 0) + shiftLength / 60);
                }
            }
        }

        return workHours; // Total work hours per employee over all days
    }



    public static void main(String[] args) {
        // Create a list of employees
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", 40 * 4, 160 * 4)); // Monthly: Min 160 hours, Max 640 hours
        employees.add(new Employee(2, "Bob", 40 * 4, 160 * 4));
        employees.add(new Employee(3, "Charlie", 40 * 4, 160 * 4));
        employees.add(new Employee(4, "Diana", 40 * 4, 160 * 4));

        // Create a list of shifts
        List<Shift> shifts = new ArrayList<>();
        shifts.add(new Shift("00:00", "08:00")); // 8 hours
        shifts.add(new Shift("08:00", "16:00")); // 8 hours
        shifts.add(new Shift("16:00", "00:00")); // 8 hours

        // Generate the schedule
        int numDays = 30;
        Employee[][][] employeeSchedule = generateSchedule(employees, shifts, numDays, true, true, false);

        // Convert the schedule to int[][][] with employee IDs
        int[][][] schedule = new int[numDays][shifts.size()][];
        for (int day = 0; day < employeeSchedule.length; day++) {
            for (int shift = 0; shift < employeeSchedule[day].length; shift++) {
                Employee[] shiftEmployees = employeeSchedule[day][shift];
                schedule[day][shift] = Arrays.stream(shiftEmployees)
                                             .mapToInt(Employee::getId)
                                             .toArray();
            }
        }

        // Print the schedule
        for (int day = 0; day < schedule.length; day++) {
            System.out.println("Day " + (day + 1) + ":");
            for (int shift = 0; shift < schedule[day].length; shift++) {
                System.out.print("  Shift " + (shift + 1) + ": ");
                if (schedule[day][shift].length == 0) {
                    System.out.println("No employees assigned");
                } else {
                    for (int employeeId : schedule[day][shift]) {
                        System.out.print(employees.stream()
                                                   .filter(e -> e.getId() == employeeId)
                                                   .findFirst()
                                                   .get()
                                                   .getName() + " ");
                    }
                    System.out.println();
                }
            }
        }

        System.out.println("Shift counts: " + getShiftCountsOfEmployees(schedule));
        System.out.println("Work hours: " + getWorkHoursOfEmployees(schedule, shifts, numDays));
    }
}