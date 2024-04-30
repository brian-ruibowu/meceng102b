def adjust_z_values_based_on_next(coordinates):
    # Loop through the coordinates from the second to the last one
    for i in range(1, len(coordinates)):
        current_x, current_y, current_z = coordinates[i]
        prev_x, prev_y, prev_z = coordinates[i-1]

        # Change the previous coordinate's Z to 0.03 if the current Z is 0.03
        if current_z == 0.03 and prev_z != 0.03:
            coordinates[i-1] = (prev_x, prev_y, 0.03)

    return coordinates

def read_and_process_coordinates(input_file, output_file):
    coordinates = []

    # Read coordinates from the file
    with open(input_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split()
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
            coordinates.append((x, y, z))

    # Adjust the Z values
    adjusted_coordinates = adjust_z_values_based_on_next(coordinates)

    # Save the adjusted coordinates back to the file
    with open(output_file, 'w') as file:
        for x, y, z in adjusted_coordinates:
            file.write(f"{x:.5f} {y:.5f} {z:.2f}\n")

# Path to the input/output file
file_path = 'output_data.txt'

# Process the coordinates and save them back to the same file
read_and_process_coordinates(file_path, file_path)
