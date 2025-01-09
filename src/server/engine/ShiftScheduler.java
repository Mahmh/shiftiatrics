package server.engine;
import java.util.*;
import java.time.LocalDate;

/** Class for generating shift schedules for employees. */
public class ShiftScheduler {
    /**
     * Generates a balanced shift schedule for a given list of shifts and employees.
     * @param employees The list of employees.
     * @param shifts The list of shifts.
     * @param holidays The list of holidays.
     * @param numDays The number of days to include in the schedule (i.e., its extent).
     * @param year The year for which the schedule is being generated.
     * @param month The month for which the schedule is being generated.
     * @param useWorkHours Whether or not to regard employees' min & max work hours.
     * @param multiEmpOneShift Whether or not to put more than one employee in a shift to compensate for work hours. Works only if `useWorkHours` is already true.
     * @param multiShiftsOneEmp Whether or not employees can be assigned to more than one shift per day.
     * @return A 3D array where each row represents a day, and each column represents a shift, containing a list of employees assigned to that shift.
     */
    public static Employee[][][] generateSchedule(
        List<Employee> employees, 
        List<Shift> shifts,
        List<Holiday> holidays,
        int numDays,
        int year,
        int month,
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
            LocalDate currentDate = LocalDate.of(year, month, day+1);
            for (int shiftIndex = 0; shiftIndex < shifts.size(); shiftIndex++) {
                Shift shift = shifts.get(shiftIndex);
                int remainingMinutes = shift.getLength();
                List<Employee> assignedEmployees = new ArrayList<>();
                List<Employee> availableEmployees = new ArrayList<>(employees);

                // Sort employees by shift count to enforce strict balancing
                availableEmployees.sort(
                    Comparator.comparingInt(totalShiftsAssigned::get)
                        .thenComparingInt(totalWorkMinutes::get)
                        .thenComparingInt(e -> new Random().nextInt())
                );

                for (Employee employee : availableEmployees) {
                    if (remainingMinutes <= 0) break;
                    if (isOnHoliday(employee, holidays, currentDate)) continue;

                    int currentTotalMinutes = totalWorkMinutes.get(employee);
                    boolean withinLimits = (!useWorkHours || (
                        (employee.getMaxWorkHours() == -1 || (currentTotalMinutes + shift.getLength()) / 60 <= employee.getMaxWorkHours())
                    ));

                    boolean alreadyAssigned = multiShiftsOneEmp ? false : isAlreadyAssigned(employee, schedule, shifts, day);
                    if (!withinLimits || alreadyAssigned) continue;

                    assignedEmployees.add(employee);
                    totalWorkMinutes.put(employee, currentTotalMinutes + shift.getLength());
                    totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
                    remainingMinutes -= shift.getLength();

                    if (!multiEmpOneShift) break; // Only assign one employee if multiple employees per shift is not allowed.
                }

                schedule[day][shiftIndex] = assignedEmployees.toArray(new Employee[0]);
            }
        }

        if (!multiEmpOneShift) return schedule;

        // Final balancing step to ensure strict equality in shift counts
        int maxShifts = Collections.max(totalShiftsAssigned.values());
        for (Employee employee : employees) {
            int assignedShifts = totalShiftsAssigned.get(employee);
            if (assignedShifts < maxShifts) {
                // Add an extra shift for the under-assigned employee in a random slot
                System.out.println("Rebalancing required for " + employee.getName());
                Random random = new Random();
                int attempts = 0;

                while (assignedShifts < maxShifts && attempts < numDays * shifts.size()) {
                    attempts++;
                    int randomDay = random.nextInt(numDays);
                    int randomShift = random.nextInt(shifts.size());
                    List<Employee> currentShift = new ArrayList<>(Arrays.asList(schedule[randomDay][randomShift]));
                    LocalDate currentDate = LocalDate.of(year, month, randomDay + 1);

                    // Ensure the employee is not already in this shift and does not have a holiday in this day
                    if (currentShift.contains(employee)) break; // Break the loop if the employee is already in the shift to avoid infinite loop
                    if (isOnHoliday(employee, holidays, currentDate)) continue;

                    boolean alreadyAssigned = multiShiftsOneEmp ? false : isAlreadyAssigned(employee, schedule, shifts, randomDay);
                    if (!alreadyAssigned) {
                        currentShift.add(employee);
                        schedule[randomDay][randomShift] = currentShift.toArray(new Employee[0]);
                        totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
                        assignedShifts++;
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
        for (int[][] day : schedule) for (int[] shift : day) for (int employeeId : shift) {
            shiftCounts.put(employeeId, shiftCounts.getOrDefault(employeeId, 0) + 1);
        }
        return shiftCounts;
    }

    /**
     * Returns a mapping from `Employee.id` to the total number of work hours accumulated
     * from all the days in the given schedule.
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

    /** @return Boolean indicating if a given employee is on holiday. */
    private static boolean isOnHoliday(Employee employee, List<Holiday> holidays, LocalDate currentDate) {
        return holidays.stream().anyMatch(holiday -> 
            holiday.getAssignedTo().contains(employee.getId()) &&
            !currentDate.isBefore(holiday.getStartDate()) &&
            !currentDate.isAfter(holiday.getEndDate())
        );
    }

    /** @return Boolean indicating if the given employee is already assigned to another shift on the same day. */
    private static boolean isAlreadyAssigned(Employee employee, Employee[][][] schedule, List<Shift> shifts, int day) {
        for (int otherShiftIndex = 0; otherShiftIndex < shifts.size(); otherShiftIndex++) {
            Employee[] otherShiftEmployees = schedule[day][otherShiftIndex];
            if (otherShiftEmployees != null && Arrays.asList(otherShiftEmployees).contains(employee)) return true;
        }
        return false;
    }

    /**
     * Prints the schedule to stdout.
     * @param employeeSchedule The schedule of employees.
     * @param employees List of employees used when generating the schedule.
     * @param shifts List of shifts used when generating the schedule.
     */
    private static void printSchedule(Employee[][][] employeeSchedule, List<Employee> employees, List<Shift> shifts) {
        int numDays = employeeSchedule.length;

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


    public static void main(String[] args) {
        List<Employee> employees = new ArrayList<>();
        employees.add(new Employee(1, "Alice", 120, 173)); // Monthly: Min 160 hours, Max 640 hours
        employees.add(new Employee(2, "Bob", 120, 173));
        employees.add(new Employee(3, "Charlie", 120, 173));
        employees.add(new Employee(4, "Diana", 120, 173));

        List<Shift> shifts = new ArrayList<>();
        shifts.add(new Shift("00:00", "08:00")); // 8 hours
        shifts.add(new Shift("08:00", "16:00")); // 8 hours
        shifts.add(new Shift("16:00", "00:00")); // 8 hours

        List<Holiday> holidays = new ArrayList<>();
        holidays.add(new Holiday("Holiday", Arrays.asList(4), "2023-10-04", "2023-10-05")); // Alice and Bob on holiday from 5th to 7th October

        Employee[][][] employeeSchedule = generateSchedule(
            employees, shifts, holidays,
            10, 2023, 10,
            true, true, false
        );
        printSchedule(employeeSchedule, employees, shifts);
    }
}





// package server.engine;
// import java.util.*;
// import java.time.LocalDate;

// /** Class for generating shift schedules for employees. */
// public class ShiftScheduler {
//     /**
//      * Generates a balanced shift schedule for a given list of shifts and employees.
//      * @param employees The list of employees.
//      * @param shifts The list of shifts.
//      * @param holidays The list of holidays.
//      * @param numDays The number of days to include in the schedule (i.e., its extent).
//      * @param year The year for which the schedule is being generated.
//      * @param month The month for which the schedule is being generated.
//      * @param useWorkHours Whether or not to regard employees' min & max work hours.
//      * @param multiEmpOneShift Whether or not to put more than one employee in a shift to compensate for work hours. Works only if `useWorkHours` is already true.
//      * @param multiShiftsOneEmp Whether or not employees can be assigned to more than one shift per day.
//      * @return A 3D array where each row represents a day, and each column represents a shift, containing a list of employees assigned to that shift.
//      */
//     public static Employee[][][] generateSchedule(
//         List<Employee> employees, 
//         List<Shift> shifts,
//         List<Holiday> holidays,
//         int numDays,
//         int year,
//         int month,
//         boolean useWorkHours,
//         boolean multiEmpOneShift,
//         boolean multiShiftsOneEmp
//     ) {
//         Employee[][][] schedule = new Employee[numDays][shifts.size()][];
//         HashMap<Employee, Integer> totalWorkMinutes = new HashMap<>();
//         HashMap<Employee, Integer> totalShiftsAssigned = new HashMap<>();

//         // Initialize total work minutes and shift counts
//         for (Employee employee : employees) {
//             totalWorkMinutes.put(employee, 0);
//             totalShiftsAssigned.put(employee, 0);
//         }

//         for (int day = 0; day < numDays; day++) {
//             LocalDate currentDate = LocalDate.of(year, month, day + 1);
//             for (int shiftIndex = 0; shiftIndex < shifts.size(); shiftIndex++) {
//                 Shift shift = shifts.get(shiftIndex);
//                 List<Employee> assignedEmployees = new ArrayList<>();
//                 int remainingMinutes = shift.getLength();

//                 List<Employee> availableEmployees = new ArrayList<>(employees);

//                 // Sort employees by shift count to enforce strict balancing
//                 availableEmployees.sort(Comparator.comparingInt(totalShiftsAssigned::get)
//                         .thenComparingInt(totalWorkMinutes::get)
//                         .thenComparingInt(e -> new Random().nextInt()));

//                 for (Employee employee : availableEmployees) {
//                     if (remainingMinutes <= 0) break;

//                     // Check if the employee is on holiday
//                     boolean onHoliday = holidays.stream()
//                         .anyMatch(holiday -> holiday.getAssignedTo().contains(employee.getId()) &&
//                                              !currentDate.isBefore(holiday.getStartDate()) &&
//                                              !currentDate.isAfter(holiday.getEndDate()));

//                     if (onHoliday) continue;

//                     int currentTotalMinutes = totalWorkMinutes.get(employee);
//                     boolean withinLimits = (!useWorkHours || (
//                         (employee.getMaxWorkHours() == -1 || (currentTotalMinutes + shift.getLength()) / 60 <= employee.getMaxWorkHours())
//                     ));

//                     // Check if the employee is already assigned to another shift on the same day
//                     boolean alreadyAssigned = false;

//                     if (!multiShiftsOneEmp) {
//                         for (int otherShiftIndex = 0; otherShiftIndex < shifts.size(); otherShiftIndex++) {
//                             Employee[] otherShiftEmployees = schedule[day][otherShiftIndex];
//                             if (otherShiftEmployees != null && Arrays.asList(otherShiftEmployees).contains(employee)) {
//                                 alreadyAssigned = true;
//                                 break;
//                             }
//                         }
//                     }

//                     if (!withinLimits || alreadyAssigned) continue;

//                     assignedEmployees.add(employee);
//                     totalWorkMinutes.put(employee, currentTotalMinutes + shift.getLength());
//                     totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
//                     remainingMinutes -= shift.getLength();

//                     if (!multiEmpOneShift) break; // Only assign one employee if multiple employees per shift is not allowed.
//                 }                        

//                 schedule[day][shiftIndex] = assignedEmployees.toArray(new Employee[0]);
//             }
//         }

//         // Final balancing step to ensure strict equality in shift counts
//         if (multiEmpOneShift) {
//             int maxShifts = Collections.max(totalShiftsAssigned.values());
//             for (Employee employee : employees) {
//                 int assignedShifts = totalShiftsAssigned.get(employee);
//                 if (assignedShifts < maxShifts) {
//                     System.out.println("Rebalancing required for " + employee.getName());
//                     Random random = new Random();
//                     // Add an extra shift for the under-assigned employee in a random slot
//                     int attempts = 0;
//                     while (assignedShifts < maxShifts && attempts < numDays * shifts.size()) {
//                         attempts++;
//                         int randomDay = random.nextInt(numDays);
//                         int randomShift = random.nextInt(shifts.size());
//                         List<Employee> currentShift = new ArrayList<>(Arrays.asList(schedule[randomDay][randomShift]));

//                         LocalDate currentDate = LocalDate.of(year, month, randomDay + 1);

//                         // Ensure the employee is not already in this shift
//                         if (!currentShift.contains(employee)) {
//                             // Check if the employee is on holiday
//                             boolean onHoliday = holidays.stream()
//                                 .anyMatch(holiday -> holiday.getAssignedTo().contains(employee.getId()) &&
//                                                     !currentDate.isBefore(holiday.getStartDate()) &&
//                                                     !currentDate.isAfter(holiday.getEndDate()));

//                             if (onHoliday) continue;

//                             // Check if the employee is already assigned to another shift on the same day
//                             boolean alreadyAssigned = false;

//                             if (!multiShiftsOneEmp) {
//                                 for (int otherShiftIndex = 0; otherShiftIndex < shifts.size(); otherShiftIndex++) {
//                                     Employee[] otherShiftEmployees = schedule[randomDay][otherShiftIndex];
//                                     if (otherShiftEmployees != null && Arrays.asList(otherShiftEmployees).contains(employee)) {
//                                         alreadyAssigned = true;
//                                         break;
//                                     }
//                                 }
//                             }

//                             if (!alreadyAssigned) {
//                                 currentShift.add(employee);
//                                 schedule[randomDay][randomShift] = currentShift.toArray(new Employee[0]);
//                                 totalShiftsAssigned.put(employee, totalShiftsAssigned.get(employee) + 1);
//                                 assignedShifts++;
//                             }
//                         } else break; // Break the loop if the employee is already in the shift to avoid infinite loop
//                     }
//                 }
//             }
//         }

//         return schedule;
//     }

//     /**
//      * Returns a mapping from `Employee.id` to the total number of shifts they have worked, according to the given schedule.
//      * @param schedule The generated schedule as an `int[][][]` (Employee IDs).
//      * @return A hash map with `Employee.id` as the key and the total shift count as the value.
//      */
//     public static HashMap<Integer, Integer> getShiftCountsOfEmployees(int[][][] schedule) {
//         HashMap<Integer, Integer> shiftCounts = new HashMap<>();
//         for (int[][] day : schedule) {
//             for (int[] shift : day) {
//                 for (int employeeId : shift) {
//                     shiftCounts.put(employeeId, shiftCounts.getOrDefault(employeeId, 0) + 1);
//                 }
//             }
//         }
//         return shiftCounts;
//     }

//     /**
//      * Returns a mapping from `Employee.id` to the total number of work hours accumulated
//      * from all the days in the given schedule.
//      *
//      * @param schedule The generated schedule as an `int[][][]` (Employee IDs).
//      * @param shifts The list of shifts, providing shift lengths.
//      * @param numDays The number of days in the given schedule.
//      * @return A hash map with `Employee.id` as the key and the total work hours as the value.
//      */
//     public static HashMap<Integer, Integer> getWorkHoursOfEmployees(int[][][] schedule, List<Shift> shifts, int numDays) {
//         HashMap<Integer, Integer> workHours = new HashMap<>();

//         for (int[][] day : schedule) {
//             for (int shiftIndex = 0; shiftIndex < day.length; shiftIndex++) {
//                 int[] shift = day[shiftIndex];
//                 int shiftLength = shifts.get(shiftIndex).getLength(); // Shift length in minutes
//                 for (int employeeId : shift) {
//                     workHours.put(employeeId, workHours.getOrDefault(employeeId, 0) + shiftLength / 60);
//                 }
//             }
//         }

//         return workHours; // Total work hours per employee over all days
//     }

//     public static void main(String[] args) {
//         // Create a list of employees
//         List<Employee> employees = new ArrayList<>();
//         employees.add(new Employee(1, "Alice", 100 * 4, 160 * 4)); // Monthly: Min 160 hours, Max 640 hours
//         employees.add(new Employee(2, "Bob", 100 * 4, 160 * 4));
//         employees.add(new Employee(3, "Charlie", 100 * 4, 160 * 4));
//         employees.add(new Employee(4, "Diana", 100 * 4, 160 * 4));

//         // Create a list of shifts
//         List<Shift> shifts = new ArrayList<>();
//         shifts.add(new Shift("00:00", "08:00")); // 8 hours
//         shifts.add(new Shift("08:00", "16:00")); // 8 hours
//         shifts.add(new Shift("16:00", "00:00")); // 8 hours

//         // Create a list of holidays
//         List<Holiday> holidays = new ArrayList<>();
//         holidays.add(new Holiday("Holiday", Arrays.asList(4), "2023-10-04", "2023-10-05")); // Alice and Bob on holiday from 5th to 7th October

//         // Generate the schedule
//         int numDays = 1;
//         int year = 2023;
//         int month = 10;
//         boolean useWorkHours = true;
//         boolean multiEmpOneShift = true;
//         boolean multiShiftsOneEmp = false;

//         Employee[][][] employeeSchedule = generateSchedule(employees, shifts, holidays, numDays, year, month, useWorkHours, multiEmpOneShift, multiShiftsOneEmp);

//         // Convert the schedule to int[][][] with employee IDs
//         int[][][] schedule = new int[numDays][shifts.size()][];
//         for (int day = 0; day < employeeSchedule.length; day++) {
//             for (int shift = 0; shift < employeeSchedule[day].length; shift++) {
//                 Employee[] shiftEmployees = employeeSchedule[day][shift];
//                 schedule[day][shift] = Arrays.stream(shiftEmployees)
//                                              .mapToInt(Employee::getId)
//                                              .toArray();
//             }
//         }

//         // Print the schedule
//         for (int day = 0; day < schedule.length; day++) {
//             System.out.println("Day " + (day + 1) + ":");
//             for (int shift = 0; shift < schedule[day].length; shift++) {
//                 System.out.print("  Shift " + (shift + 1) + ": ");
//                 if (schedule[day][shift].length == 0) {
//                     System.out.println("No employees assigned");
//                 } else {
//                     for (int employeeId : schedule[day][shift]) {
//                         System.out.print(employees.stream()
//                                                    .filter(e -> e.getId() == employeeId)
//                                                    .findFirst()
//                                                    .get()
//                                                    .getName() + " ");
//                     }
//                     System.out.println();
//                 }
//             }
//         }

//         System.out.println("Shift counts: " + getShiftCountsOfEmployees(schedule));
//         System.out.println("Work hours: " + getWorkHoursOfEmployees(schedule, shifts, numDays));
//     }
// }