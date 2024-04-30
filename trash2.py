import numpy as np
import matplotlib.pyplot as plt

# Given values
l = 40.75  # Example length
rho = 2.25  # Example radius of the rolling circle
c1 = 1.0  # Example constant for the cycloidal gear
c2 = 1.5  # Example constant for the internal gear
N = 36  # Example number of teeth for the cycloidal gear
m = 1   # Example tooth number difference for the nonpin design

# Function to calculate the coordinates of the internal gear profile
def internal_gear_profile(l, rho, c1, c2, N, m, theta1_range):
    x_o = []
    y_o = []
    for theta1 in theta1_range:
        theta2 = N / (N + m) * theta1
        phi2 = N / (N + 1) * theta1  # Assuming phi1 is similar to theta1 for plotting
        phi1 = theta1
        alpha = np.arctan2(c1 * (N + 1) * np.sin(phi1), l - c1 * (N + 1) * np.cos(phi1))
        x = -c2 * np.sin(theta2) + c1 * np.sin(theta1 - theta2 - phi2) + rho * np.sin(alpha + theta1 - theta2 + phi1 - phi2) - l * np.sin(theta1 - theta2 + phi1 - phi2)
        y = -c2 * np.cos(theta2) - c1 * np.cos(theta1 - theta2 - phi2) - rho * np.cos(alpha + theta1 - theta2 + phi1 - phi2) + l * np.cos(theta1 - theta2 + phi1 - phi2)
        x_o.append(x)
        y_o.append(y)
    return x_o, y_o

# Generate theta1 values
theta1_range = np.linspace(0, 2 * np.pi, 1000)

# Generate the internal gear profile
x_o, y_o = internal_gear_profile(l, rho, c1, c2, N, m, theta1_range)

# Plotting the internal gear profile
plt.figure(figsize=(8, 8))
plt.plot(x_o, y_o, label='Internal Gear Profile (Nonpin Design)')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Internal Gear Profile (Nonpin Design)')
plt.axis('equal')
plt.grid(True)
plt.legend()
plt.show()