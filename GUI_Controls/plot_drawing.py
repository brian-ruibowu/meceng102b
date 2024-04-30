import matplotlib.pyplot as plt

def plot_data(file_path):
    x_coords = []
    y_coords = []

    # Open the file and read the lines
    with open('output_data.txt', 'r') as file:
        lines = file.readlines()

    # Extract x and y coordinates from each line
    for line in lines:
        parts = line.split()
        x = float(parts[0])
        y = float(parts[1])
        x_coords.append(x)
        y_coords.append(y)

    # Plotting the data
    plt.figure(figsize=(1, 1))
    plt.scatter(x_coords, y_coords, c='blue', marker='o')  # Scatter plot
    plt.plot(x_coords, y_coords, 'r-', linewidth=1)  # Line plot connecting the points
    plt.title('2D Plot of Coordinates')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.show()

# Usage example
plot_data('GUI_Controls\output.txt')  # Replace 'output.txt' with the path to your data file
