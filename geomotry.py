import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
rawImg = "images/special_shape.jpg"
image = cv2.imread(rawImg, cv2.IMREAD_GRAYSCALE)

# Apply adaptive thresholding
thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Check if any contours were detected
if not contours:
    print("No contours were detected.")
    exit()

# Process the largest contour
main_contour = max(contours, key=cv2.contourArea)

# Approximate the contour to simplify it
epsilon = 0.01 * cv2.arcLength(main_contour, True)
approx = cv2.approxPolyDP(main_contour, epsilon, True)

# Determine the plot limits
x_coords, y_coords = zip(*[(point[0][0], point[0][1]) for point in approx])
x_min, x_max, y_min, y_max = min(x_coords), max(x_coords), min(y_coords), max(y_coords)

# Calculate the scaling factor
contour_width = x_max - x_min
contour_height = y_max - y_min
scale_factor = 20 / max(contour_width, contour_height)  # cm/pixel

# Determine the plot limits for the 25 cm square (outer frame)
outer_frame_size = 25  # cm

# Since we are scaling to a 20 cm square and then adding a 2.5 cm border,
# we center the 20 cm square within the 25 cm square
center_x = (x_min + x_max) / 2 * scale_factor
center_y = (y_min + y_max) / 2 * scale_factor
plot_x_min = center_x - (outer_frame_size / 2)
plot_x_max = center_x + (outer_frame_size / 2)
plot_y_min = center_y - (outer_frame_size / 2)
plot_y_max = center_y + (outer_frame_size / 2)

# Initialize figure
plt.figure(figsize=(10, 10))

# Determine the scaled frame size for the inner frame
inner_frame_size = 20  # cm

# Scale the contour coordinates
scaled_contour = [(pt[0][0] * scale_factor, pt[0][1] * scale_factor) for pt in approx]

# Determine the limits for the inner frame (20 cm square)
inner_x_min = center_x - (inner_frame_size / 2)
inner_x_max = center_x + (inner_frame_size / 2)
inner_y_min = center_y - (inner_frame_size / 2)
inner_y_max = center_y + (inner_frame_size / 2)

# Plot the scaled contour and annotate with the scaled polynomial equations
for i in range(len(scaled_contour)):
    pt1, pt2 = scaled_contour[i], scaled_contour[(i + 1) % len(scaled_contour)]
    
    if pt1[0] == pt2[0]:  # Vertical line
        # Plot vertical line using plt.plot for consistency
        plt.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]], label=f'Side {i+1}')
        plt.text(pt1[0], (pt1[1] + pt2[1]) / 2, f'x = {round(pt1[0],2)}')
    else:
        # Fit a line (1st degree polynomial) between the two endpoints
        coeffs = np.polyfit([pt1[0], pt2[0]], [pt1[1], pt2[1]], 1)
        poly_eq = np.poly1d(coeffs)

        # Determine the x-values for the line segment between pt1 and pt2
        x_vals = np.linspace(pt1[0], pt2[0], 100)
        y_vals = poly_eq(x_vals)

        # Plot the line segment for the side of the triangle
        plt.plot(x_vals, y_vals, label=f'Side {i+1}')

        # Annotate the line segment with its equation
        mid_x = (pt1[0] + pt2[0]) / 2
        mid_y = poly_eq(mid_x)
        plt.text(mid_x, mid_y, f'y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}', ha='center')

# Customize the plot to show the outer frame of 25 cm
plt.axis('equal')
plt.xlim(plot_x_min, plot_x_max)
plt.ylim(plot_y_max, plot_y_min)  # y limits inverted to match image coordinates
plt.grid(True)

# Extract the base name of the file
base_name = os.path.basename(rawImg)

# Remove 'results' from the path if it exists and append '_analyzed'
if 'images' in base_name:
    base_name = base_name.replace('images', '')

if '.png' in base_name:
    base_name = base_name.replace('.png', '')

if '.jpg' in base_name:
    base_name = base_name.replace('.jpg', '')

if '.jpeg' in base_name:
    base_name = base_name.replace('.jpeg', '')

# Define the new filename
new_base_name = os.path.splitext(base_name)[0] + '_analyzed.png'
analyzed_image_name = f"results/{base_name}_analyzed.png"

# Save the figure
plt.savefig(analyzed_image_name)

# If you want to also show the plot uncomment the next line
plt.show()
