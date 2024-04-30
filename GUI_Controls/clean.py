import matplotlib.pyplot as plt
import numpy as np

def plot_and_save_filtered_data(input_file, output_file):
    x_coords = []
    y_coords = []
    z_coords = []
    last_x = None
    last_y = None
    last_z = None
    processed_data = []  # To store processed lines for saving to file

    # Open the file and read the lines
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Extract x, y, and z coordinates from each line
    for line in lines:
        parts = line.split()
        x = float(parts[0])
        y = float(parts[1])
        z = float(parts[2])
        
        if last_x is not None and last_y is not None:
            # Calculate the distance to the last included point
            dist = np.sqrt((x - last_x)**2 + (y - last_y)**2)
            if dist >= 0.002 or z == 0.03:  # Include points that are far enough apart or have z = 0.03
                x_coords.append(x)
                y_coords.append(y)
                z_coords.append(z)
                processed_data.append(f"{x} {y} {z}")
                last_x, last_y, last_z = x, y, z
        else:
            # Always add the first point
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
            processed_data.append(f"{x} {y} {z}")
            last_x, last_y, last_z = x, y, z

    # Save the processed data to a file
    with open(output_file, 'w') as output_file:
        for line in processed_data:
            output_file.write(line + '\n')

    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.scatter(x_coords, y_coords, c=z_coords, cmap='viridis', marker='o')  # Scatter plot with color coding by z value
    plt.plot(x_coords, y_coords, 'r-', linewidth=1)  # Line plot connecting the points
    plt.title('2D Plot of Coordinates')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.colorbar(label='Z Value')
    plt.grid(True)
    plt.show()

# Usage example
plot_and_save_filtered_data('output_data.txt', 'output_data.txt')  # Adjust the file path as needed

