import matplotlib.pyplot as plt
import math

# Function to extract coordinates from a line of G-code
def extract_coordinates(line):
    coords = {'X': None, 'Y': None, 'Z': None}
    parts = line.split(' ')
    for part in parts:
        if part.startswith('X'):
            coords['X'] = float(part[1:])
        elif part.startswith('Y'):
            coords['Y'] = float(part[1:])
        elif part.startswith('Z'):
            coords['Z'] = float(part[1:])
    return coords

# Function to calculate distance between two points
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Initialize lists to hold the X and Y coordinates
x_coords = []
y_coords = []

# Open the G-code file and extract X, Y coordinates
with open('shifu_0001.ngc', 'r') as file:
    prev_x = None
    prev_y = None
    for line in file:
        line = line.strip()
        # Extract coordinates including Z
        coords = extract_coordinates(line)
        if coords['Z'] == -3:  # Check if Z-coordinate is -1
            if (line.startswith('G0') and not line.startswith('G00')):
                if coords['X'] is not None and coords['Y'] is not None:
                    # Add the first point to the list
                    if prev_x is None and prev_y is None:
                        prev_x, prev_y = coords['X'], coords['Y']
                        x_coords.append(prev_x)
                        y_coords.append(prev_y)
                    else:
                        # For subsequent points, check the distance before adding them
                        if distance(prev_x, prev_y, coords['X'], coords['Y']) <= 100:
                            x_coords.append(coords['X'])
                            y_coords.append(coords['Y'])
                            prev_x, prev_y = coords['X'], coords['Y']

# Save the coordinates to a new file
with open('output_coordinates.txt', 'w') as f:
    for x, y in zip(x_coords, y_coords):
        f.write(f"{x}, {y}\n")

# Plotting the points with a smaller marker size
plt.plot(x_coords, y_coords, marker='o', markersize=0.5)  # Adjust the markersize as needed
plt.title('Path Plot')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()