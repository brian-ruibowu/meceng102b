from matplotlib.image import imread as pltRead
import matplotlib.pyplot as plt
from rembg import remove
from PIL import Image
import cv2
import numpy as np

rawImg = "images/circle.jpg"
# panda = imread(rawImg)
# print(panda.size, panda.shape, panda.ndim)

# removeBg = remove(Image.open(rawImg))
# removeBg.save("img_without_bg.png")

# bgImg = "img_without_bg.png"
# readImg = cv2.imread(bgImg)
# blackWhiteImg = cv2.cvtColor(readImg, cv2.COLOR_BGR2GRAY)
# cv2.imwrite("black_white_image.png", blackWhiteImg)

readImg = cv2.imread(rawImg)
blackWhiteImg = cv2.cvtColor(readImg, cv2.COLOR_BGR2GRAY)
cv2.imwrite("black_white_image2.png", blackWhiteImg)

removeBg = remove(Image.open("black_white_image2.png"))
removeBg.save("img_without_bg2.png")

grey_img = cv2.imread("img_without_bg2.png")
invert = cv2.bitwise_not(grey_img)
blur = cv2.GaussianBlur(invert, (21, 21), sigmaX=0,sigmaY=0)
invertedBlur = cv2.bitwise_not(blur)
sketch = cv2.divide(grey_img, invertedBlur, scale = 256.0)

cv2.imwrite("sketch.png", sketch)

readImg = cv2.imread("sketch.png")
blackWhiteImg = cv2.cvtColor(readImg, cv2.COLOR_BGR2GRAY)
cv2.imwrite("grey_sketch.png", blackWhiteImg)

removeBg = remove(Image.open("grey_sketch.png"))
removeBg.save("grey_sketch.png")

pRead = cv2.imread("grey_sketch.png", cv2.IMREAD_GRAYSCALE)
print(type(pRead), pRead.size, pRead.shape, pRead.ndim)

# plt.figure(figsize=(10, 10))
# plt.imshow(pRead, cmap='gray')
# plt.colorbar()
# plt.show()

image = cv2.imread("grey_sketch.png", cv2.IMREAD_GRAYSCALE)

# Threshold the image to isolate the circle
_, thresh = cv2.threshold(image, 60, 255, cv2.THRESH_BINARY)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Assuming the largest contour corresponds to the circle
circle_contour = max(contours, key=cv2.contourArea)

# Extract the edge points
edge_points = circle_contour.squeeze()
x_min, y_min = np.min(edge_points, axis=0)
x_max, y_max = np.max(edge_points, axis=0)

# Perform polynomial fit (for example, a 2nd-degree polynomial fit)
# Since the circle is symmetric, we can fit the upper and lower halves separately
# Fit the upper half
upper_half = edge_points[edge_points[:, 1] < 800]  # Assuming the circle is centered and 800 is the approximate y-coordinate of the center
coeffs_upper = np.polyfit(upper_half[:, 0], upper_half[:, 1], 2)

# Fit the lower half
# lower_half = edge_points[edge_points[:, 1] >= 800]
# coeffs_lower = np.polyfit(lower_half[:, 0], lower_half[:, 1], 2)

# # Generate polynomial lines
# x_fit = np.linspace(x_min, x_max, 1000)  # Generate x values within the limits of the data
# poly_upper_fit = np.polyval(coeffs_upper, x_fit)
# poly_lower_fit = np.polyval(coeffs_lower, x_fit)

# Plot the original scatter plot
plt.figure(figsize=(10, 10))
plt.scatter(edge_points[:, 0], edge_points[:, 1], c='black', marker='.')

# Overlay the polynomial fit
# plt.plot(x_fit, poly_upper_fit, c='red', label='Upper Fit')
# plt.plot(x_fit, poly_lower_fit, c='blue', label='Lower Fit')

# Invert y-axis to match image coordinates
plt.gca().invert_yaxis()

# Set the aspect ratio of the plot to be equal
plt.axis('equal')

# Set x-axis and y-axis limits to match the extent of the data
plt.xlim(x_min, x_max)
plt.ylim(y_max, y_min)  # Note the inversion to maintain the image's coordinate system

# Display the polynomial function on the plot
# upper_poly_eq = f'Upper Fit: y = {coeffs_upper[0]:.2f}x² + {coeffs_upper[1]:.2f}x + {coeffs_upper[2]:.2f}'
# lower_poly_eq = f'Lower Fit: y = {coeffs_lower[0]:.2f}x² + {coeffs_lower[1]:.2f}x + {coeffs_lower[2]:.2f}'
# plt.text(x_max / 2, y_min - 150, upper_poly_eq, color='red')
# plt.text(x_max / 2, y_min -75, lower_poly_eq, color='blue')  # Offset the lower equation text by 50 pixels

# Display the plot
plt.colorbar()
plt.legend()
plt.show()




