import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
rawImg = "images/special_shape1.jpg"  # Update the path to your image
image = cv2.imread(rawImg, cv2.IMREAD_GRAYSCALE)

# Make sure img is not None
if image is None:
    raise ValueError(f"Image not found at the path: {rawImg}")

# Define the size of the area to fit the image in cm
frame_size_cm = 25
dpi = 100  # The assumed number of dots per inch for the output image

# Convert frame size from cm to pixels
frame_size_px = int(frame_size_cm * dpi / 2.54)  # Convert cm to inches and then to pixels

# Calculate the scaling factor
# We need to consider the case where either width or height is larger
scale_factor = min(frame_size_px / image.shape[1], frame_size_px / image.shape[0])

# Resize the image to fit the 25cm x 25cm area
resized_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

# Apply adaptive thresholding to the resized image
thresh = cv2.adaptiveThreshold(resized_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find contours on the resized image
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Initialize figure with white background
plt.figure(figsize=(frame_size_cm / 2.54, frame_size_cm / 2.54), facecolor='white')

# Process each contour
for contour in contours:
    # Approximate the contour to simplify it
    epsilon = 0.01 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # Scale the contour coordinates
    scaled_contour = approx.reshape(-1, 2)

    # Plot the scaled contour
    plt.plot(scaled_contour[:, 0], scaled_contour[:, 1], label='Contour')

# Customize the plot to fit the 25cm x 25cm frame
plt.xlim(0, frame_size_px)
plt.ylim(frame_size_px, 0)
plt.axis('off')  # Turn off axis labels and ticks

# Show the plot
plt.show()