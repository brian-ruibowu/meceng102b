import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
rawImg = "images/special_shape.jpg"
image = cv2.imread(rawImg, cv2.IMREAD_GRAYSCALE)

# Apply adaptive thresholding
thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Use Hough Transform to detect lines in the image
lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, threshold=80, minLineLength=30, maxLineGap=10)

# Function to calculate the intersection of two lines
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return None  # Lines don't intersect

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

# Initialize figure for plotting
plt.figure(figsize=(10, 10))

# Iterate over the detected lines
for line in lines:
    x1, y1, x2, y2 = line[0]
    plt.plot([x1, x2], [y1, y2], 'b')  # Plot the line

# Calculate intersections between each pair of lines
intersections = []
for i, line1 in enumerate(lines):
    for line2 in lines[i+1:]:
        pt1 = (line1[0][0], line1[0][1]), (line1[0][2], line1[0][3])
        pt2 = (line2[0][0], line2[0][1]), (line2[0][2], line2[0][3])
        intersection = line_intersection(pt1, pt2)
        if intersection:  # If lines intersect
            intersections.append(intersection)

# Plot the intersections
for point in intersections:
    plt.plot(point[0], point[1], 'ro')  # Plot the intersection point

# Customize the plot
plt.axis('equal')
plt.xlim(0, 1000)  # Adjust according to your image size
plt.ylim(1000, 0)  # Adjust according to your image size
plt.grid(True)
plt.show()

# Save the plot
# Extract the base name of the file
base_name = os.path.basename(rawImg)

# Remove 'results' from the path if it exists and append '_analyzed'
base_name = base_name.replace('results', '')

# Define the new filename
new_base_name = os.path.splitext(base_name)[0] + '_analyzed.png'
analyzed_image_name = f"results/{new_base_name}"

# Save the figure
plt.savefig(analyzed_image_name)