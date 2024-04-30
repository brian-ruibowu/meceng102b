import numpy as np
import matplotlib.pyplot as plt

def compute_derivative(torque, speed):
    dTds = np.zeros_like(speed)
    
    # Forward difference for the first point
    dTds[0] = (torque[1] - torque[0]) / (speed[1] - speed[0]) if speed[1] != speed[0] else 0
    
    # Central difference for interior points
    for i in range(1, len(speed) - 1):
        delta_speed = speed[i + 1] - speed[i - 1]
        if delta_speed != 0:
            dTds[i] = (torque[i + 1] - torque[i - 1]) / delta_speed
        else:
            dTds[i] = 0
    
    # Backward difference for the last point
    dTds[-1] = (torque[-1] - torque[-2]) / (speed[-1] - speed[-2]) if speed[-1] != speed[-2] else 0
    
    return dTds

# Constants
A = np.pi/2
L = 0.3
w = 8*2*np.pi/60
M = 9.07
g = 9.81
N = 0.8
n = 9
Im = 0
slope = -0.0625  # Km^2
t = np.arange(0, 10.01, 0.01)
torque = 1/n/N*(-1*(Im+M*L**2)*A/2*np.cos(w*t)*w**2 + M*g*L*np.sin(A/2*(1-np.cos(w*t))))
speed = A/2*np.sin(w*t)*w*n

# Numerically find derivative of torque with respect to speed
dTds = compute_derivative(torque, speed)

# Find where the derivative is closest to the slope of the winding line
minIndex = np.argmin(np.abs(dTds - slope))

# Use the point just before the change to calculate the y-intercept
tangentSpeed = speed[minIndex]
tangentTorque = torque[minIndex]
b = tangentTorque - slope * tangentSpeed

# Generate winding line values
speed_range = np.linspace(np.min(speed), np.max(speed), 1000)
winding_line_values = slope * speed_range + b

# Plotting
plt.figure()
plt.plot(speed[:-1], dTds[1:], 'b-', linewidth=2)
plt.plot(speed_range, winding_line_values, 'r--', linewidth=2)
plt.xlabel('Speed (rad/s)')
plt.ylabel('dT/ds (Nm/rad/s)')
plt.title('dT/ds vs. Speed and Tangent Winding Line')
plt.legend(['dT/ds vs. Speed', 'Tangent Winding Line'], loc='best')
plt.grid(True)
plt.xlim([0, 8])
plt.ylim([0, 5])
plt.show()