import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class RobotArmGUI:
    def __init__(self, master):
        self.master = master
        master.title("4-DOF Robot Arm Simulator")

        # Joint angle inputs
        self.joint_labels = ['Theta 1', 'Theta 2', 'Theta 3', 'Theta 4']
        self.joint_entries = []
        for i, label in enumerate(self.joint_labels):
            ttk.Label(master, text=f"{label}:").grid(column=0, row=i)
            entry = ttk.Entry(master)
            entry.grid(column=1, row=i)
            self.joint_entries.append(entry)

        # End-effector position inputs
        self.position_labels = ['Pos X', 'Pos Y', 'Pos Z']
        self.position_entries = []
        for i, label in enumerate(self.position_labels, start=len(self.joint_labels)):
            ttk.Label(master, text=f"{label}:").grid(column=0, row=i)
            entry = ttk.Entry(master)
            entry.grid(column=1, row=i)
            self.position_entries.append(entry)

        # Forward and Inverse Kinematics buttons
        self.forward_button = ttk.Button(master, text="Forward Kinematics", command=self.forward_kinematics)
        self.forward_button.grid(column=0, row=7)
        self.inverse_button = ttk.Button(master, text="Inverse Kinematics", command=self.inverse_kinematics)
        self.inverse_button.grid(column=1, row=7)

        # Robot visualization
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.figure, master)
        self.canvas.get_tk_widget().grid(column=2, row=0, rowspan=8)
        self.update_plot()

    def forward_kinematics(self):
        # Retrieve and convert joint angles from the entries
        try:
            joint_angles = [float(entry.get()) for entry in self.joint_entries]

            C1 = np.cos(np.radians(joint_angles[0]))
            S1 = np.sin(np.radians(joint_angles[0]))
            C2 = np.cos(np.radians(joint_angles[1]))
            S2 = np.sin(np.radians(joint_angles[1]))
            C23 = np.cos(np.radians(joint_angles[1] + joint_angles[2]))
            S23 = np.sin(np.radians(joint_angles[1] + joint_angles[2]))
            
            # Define your robot's specific DH parameters here
            b1, b2, d1, d2 = 0, 0, 10, 5

            # Now construct the transformation matrix T^3_0 based on the provided forward kinematics
            # T_3_0 = np.array([[C1 * C2_3, -S1, C1 * S2_3, C1 * (b2 * C2 + b1) - S1 * d2],
            #                 [S1 * C2_3, C1, S1 * S2_3, S1 * (b2 * C2 + b1) + C1 * d2],
            #                 [S2_3, 0, -C2_3, S2 * b1 + d1],
            #                 [0, 0, 0, 1]])
            
            T_3_0 = np.array([[C1 * C23, -C1 * S23, -S1, C1 * C2 * b1 - S1 * d2],
                            [S1 * C23, -S1 * S23, C1, S1 * C2 * b1 + C1 * d2],
                            [-S23, -C23, 0, S2 * b1 + d1],
                            [0, 0, 0, 1]])
            
            end_effector_pos = T_3_0[:3, 3]
            # Update the position entries based on the calculated end-effector position
            for i, entry in enumerate(self.position_entries):
                entry.delete(0, tk.END)
                entry.insert(0, str(end_effector_pos[i]))

            self.update_plot(joint_angles, mode='angles')

        except ValueError:
            # Handle the error by informing the user or setting a default value
            print("Please fill in all the joint angle fields.")
            return


    def inverse_kinematics(self):
        # Assuming end_effector_pos is [x, y, z]
        x, y, z = [float(entry.get()) for entry in self.position_entries]
        x = x * 0.01
        y = y * 0.01
        z = z * 0.01

        l1 = .18
        l2 = .18
        y = y + 0.0355
        z = z - .1021
        # Calculate the distance d
        d = np.sqrt(x**2 + y**2)
        
        # Calculate theta1
        theta1 = np.arctan2(y, x)
        
        # Calculate theta3
        theta3 = np.arccos((d**2 + z**2 - l1**2 - l2**2) / (2 * l1 * l2))
        
        # Calculate theta2
        theta2 = np.arctan2(z, d) + np.arctan2(l2 * np.sin(theta3), l1 + l2 * np.cos(theta3))
        
        # Convert angles from radians to degrees, if needed
        theta1_deg = np.degrees(theta1)
        theta2_deg = np.degrees(theta2)
        theta3_deg = np.degrees(theta3)
        theta4_deg = -1  *(theta2_deg - theta3_deg)
        print(theta1_deg, theta2_deg, theta3_deg, theta4_deg)

        # Update the visualization
        self.update_plot([theta1_deg, theta2_deg, theta3_deg, theta4_deg], mode='position')

    def calculate_joint_positions(self, joint_angles):
        # Initialize the joint positions with the base at the origin
        joint_positions = [(0, 0, 0)]

        # Lengths of the links
        l1 = 0.18
        l2 = 0.18

        # Assuming the first joint rotates in the xy plane about the z-axis
        x1 = 0
        y1 = 0
        z1 = 0  # No movement in z for the first joint

        # Adding the position of the first joint
        joint_positions.append((x1, y1, z1))
        
        z2 = 0.05
        y2 = y1
        joint_positions.append((x1, y2, z2))

        x3, y3, z3 = self.calculate_joint3_position(0.05, joint_angles[0], l1, joint_angles[1])
        joint_positions.append((x3, y3, z3))

        x4, y4, z4 = self.calculate_joint4_position(0.05, joint_angles[0], l1, joint_angles[1], l2, joint_angles[2])
        joint_positions.append((x1, y2, z4))

        return joint_positions
    
    def calculate_joint3_position(self, L1, theta1_degrees, L2, theta2_degrees):
        # Convert degrees to radians
        theta1_radians = np.radians(theta1_degrees)
        theta2_radians = np.radians(theta2_degrees)

        # Position calculations for the end of the first link (base of Joint2)
        x1 = L1 * np.cos(theta1_radians)
        y1 = L1 * np.sin(theta1_radians)
        z1 = 0  # As it's in the xy-plane

        # Displacements caused by Joint2
        delta_x2 = L2 * np.cos(theta2_radians)
        delta_z2 = L2 * np.sin(theta2_radians)

        # Adjustments based on Joint1's rotation
        delta_y2 = delta_x2 * np.sin(theta1_radians)
        delta_x2_prime = delta_x2 * np.cos(theta1_radians)

        # Final endpoint position
        x = x1 + delta_x2_prime
        y = y1 + delta_y2
        z = z1 + delta_z2

        return x, y, z
    
    def calculate_joint4_position(self, L1, theta1_degrees, L2, theta2_degrees, L3, theta3_degrees):
        # Convert degrees to radians
        theta1_radians = np.radians(theta1_degrees)
        theta2_radians = np.radians(theta2_degrees)
        theta3_radians = np.radians(theta3_degrees)

        # First link (Joint1) calculations in the xy-plane
        x1 = L1 * np.cos(theta1_radians)
        y1 = L1 * np.sin(theta1_radians)
        z1 = 0  # z is 0 since it's in the xy-plane

        # Displacement caused by Joint2 in the xz-plane
        delta_x2 = L2 * np.cos(theta2_radians)
        delta_z2 = L2 * np.sin(theta2_radians)

        # Adjustments for Joint2 based on Joint1's rotation
        delta_y2 = delta_x2 * np.sin(theta1_radians)
        delta_x2_prime = delta_x2 * np.cos(theta1_radians)

        # Position after Joint2
        x2 = x1 + delta_x2_prime
        y2 = y1 + delta_y2
        z2 = z1 + delta_z2

        # Displacement caused by Joint3 in the xz-plane after Joint2
        delta_x3 = L3 * np.cos(theta3_radians)
        delta_z3 = L3 * np.sin(theta3_radians)

        # Adjustments for Joint3 based on the total rotation (theta1 + theta2) in the xy-plane
        # Assuming Joint3 rotates relative to the new x'-axis after Joint1 and Joint2's rotations
        total_rotation_radians = theta1_radians + theta2_radians
        delta_y3 = delta_x3 * np.sin(total_rotation_radians)
        delta_x3_prime = delta_x3 * np.cos(total_rotation_radians)

        # Final endpoint position considering Joint3
        x = x2 + delta_x3_prime
        y = y2 + delta_y3
        z = z2 + delta_z3

        return x, y, z

    def update_plot(self, joint_angles=None, mode='angles'):
        # Clear the current plot
        self.plot.clear()
        self.plot.set_xlim([-0.5, 0.5])
        self.plot.set_ylim([-0.5, 0.5])
        self.plot.set_zlim([0, 1])

        if joint_angles:
            joint_positions = self.calculate_joint_positions(joint_angles)
            
            # Plot the arm as black lines
            xs, ys, zs = zip(*joint_positions)
            self.plot.plot(xs, ys, zs, 'k-')

            # Plot the joints as red dots
            self.plot.scatter(xs, ys, zs, color='red')

            # Plot the joint angles as text labels near the joints
            for i, (x, y, z) in enumerate(joint_positions):
                if i < len(joint_angles):  # Ensure we don't go out of bounds
                    angle_text = f'{joint_angles[i]:.1f}°'
                    self.plot.text(x, y, z, angle_text, color='blue')

        self.plot.set_xlabel('X')
        self.plot.set_ylabel('Y')
        self.plot.set_zlabel('Z')

        self.canvas.draw()

if __name__ == "__main__":
    b1 = 0  # Replace with actual link length for joint 3
    b2 = 0  # Replace with actual link length for joint 4
    d1 = 10   # Replace with actual offset for joint 1
    d2 = 5   # Replace with actual offset for joints 2, 3, and 4
    
    root = tk.Tk()
    gui = RobotArmGUI(root)
    root.mainloop()