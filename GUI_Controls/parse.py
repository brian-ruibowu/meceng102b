import json
import numpy as np

def process_drawing_data(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    output_lines = []  # Store formatted text lines
    first_point = True # Flag to identify the first point
    prev_x = None      # Initialize previous x
    prev_y = None      # Initialize previous y

    # Loop through paths in the data
    for segment in data:
        paths = segment['paths']
        for point in paths:
            x = point['x']
            y = point['y']
            # Adjust and scale x and y
            x = round(x / 3200 + 0.05, 5)
            y = round(y / 3200 + 0.05, 5)
            
            # Determine z based on the distance from the previous point
            z = 0
            if prev_x is not None and prev_y is not None:
                dist = np.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
                if dist > 0.004:
                    z = 0.03  # Set z to 0.03 if the point is significantly different

            # Handle the very first point differently
            if first_point:
                z = 0.03  # Ensure the first point always has z = 0.03
                first_point = False

            # Add the processed line to output_lines
            output_lines.append(f"{x} {y} {z}")

            # Update previous coordinates for the next iteration
            prev_x = x
            prev_y = y

    # Write output to a text file
    with open(output_file, 'w') as file:
        for line in output_lines:
            file.write(line + '\n')


# Usage example:
process_drawing_data('drawing_data.json', 'output_data.txt')