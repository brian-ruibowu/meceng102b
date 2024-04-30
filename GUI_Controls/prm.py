import numpy as np
import matplotlib.pyplot as plt

def parse_line(line):
    """ Parses a line to extract information for vertical or horizontal lines and general equations. """
    line = line.strip()  # Remove leading/trailing whitespace and newline characters
    if 'x =' in line:
        # This is a vertical line
        parts = line.split(', y range: ')
        x_value = float(parts[0].split('=')[1].strip())
        y_range = parts[1].strip('[]').split(', ')
        y_start, y_end = map(float, y_range)
        return {'type': 'vertical', 'x': x_value, 'y_range': (y_start, y_end)}
    else:
        # This is a linear equation
        eq_part, range_part = line.strip().split(', x range: ')
        eq_part = eq_part.replace('y = ', '').strip()
        slope_intercept = eq_part.split('x + ')
        slope = float(slope_intercept[0])
        intercept = float(slope_intercept[1])
        x_range = range_part.strip('[]').split(', ')
        x_start, x_end = map(float, x_range)
        return {'type': 'linear', 'slope': slope, 'intercept': intercept, 'x_range': (x_start, x_end)}

def sample_points(parsed_line, num_samples=20):
    """ Generates points based on the type of line. """
    if parsed_line['type'] == 'vertical':
        x = parsed_line['x']
        y_start, y_end = parsed_line['y_range']
        y_values = np.linspace(y_start, y_end, num_samples)
        x_values = np.full_like(y_values, x)
    else:
        x_start, x_end = parsed_line['x_range']
        x_values = np.linspace(x_start, x_end, num_samples)
        y_values = parsed_line['slope'] * x_values + parsed_line['intercept']
    return list(zip(x_values, y_values))

def process_file(file_path):
    """ Processes each line in the file, samples points, and plots them. """
    nodes = []
    with open(file_path, 'r') as file:
        for line in file:
            parsed_line = parse_line(line)
            nodes.extend(sample_points(parsed_line))

    # Plotting for visualization
    plt.figure(figsize=(8, 8))  # Set the figure size to be square
    ax = plt.gca()  # Get the current axes
    ax.set_aspect('equal', adjustable='box')  # Set aspect ratio to 1
    for (x, y) in nodes:
        plt.plot(x, y, 'o', markersize=2)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Graph of Lines')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)  # Enhance grid visibility
    plt.show()

# Example usage
file_path = './results/circle_equations.txt'
process_file(file_path)