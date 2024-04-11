import serial
import threading
import time
import numpy as np

class RobotArm:
    def __init__(self, port='COM7', baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for the serial connection to initialize
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            # Exit or raise an exception depending on your error handling strategy
            raise

        #robot parameter configuration
        self.l1 = 0.18
        self.l2 = 0.18
        self.l3 = 0.11
        self.lbase = 0.05
        
        #robot status initialization
        self.x = self.y = self.z = 0.0
        self.J0 = self.J1 = self.J2 = self.J3 = 0.0
        self.Done = False
        self.stop_event = threading.Event()

        # Start a thread to read from the port
        try:
            self.thread = threading.Thread(target=self.read_from_port)
            self.thread.start()
        except Exception as e:
            print(f"Error starting thread: {e}")
            # Handle thread starting failure

    def ik(self, x, y, z):
        #only works for quadrum 1 and positive arm angles
        l1 = self.l1 #arm1 length in meter
        l2 = self.l2 #arm2 length in meter
        l3 = self.l3
        y += 0.0355 #end effactor y offset from joint 1
        z -= self.lbase #end effactor z offset from joint 1
        d = np.sqrt(x**2 + y**2)
        theta1 = np.arctan2(y, x)
        theta3 = np.arccos((d**2 + z**2 - l1**2 - l2**2) / (2 * l1 * l2))
        theta2 = np.arctan2(z, d) + np.arctan2(l2 * np.sin(theta3), l1 + l2 * np.cos(theta3))
        theta4 = -1 * (np.degrees(theta2) - np.degrees(theta3))
        self.update_joints(theta1, theta2, theta3, theta4)
        #return map(np.degrees, [theta1, theta2, theta3, -1 * (np.degrees(theta2) - np.degrees(theta3))])

    def fk(self, theta1, theta2, theta3, theta4):
        # DH parameters
        d = np.array([0.1021, 0.0, 0.05])
        a = np.array([0, 0.18, 0.2055])
        alpha = np.array([0.5*np.pi, -np.pi, -np.pi])

        # End effector position relative to the last joint
        end_effector_position_relative_to_the_last_joint = np.array([0.2055, 0, 0, 1])
        T1 = np.array([
            [np.cos(theta1), -np.sin(theta1), 0, 0],
            [np.sin(theta1), np.cos(theta1), 0, 0],
            [0, 0, 1, d[0]],
            [0, 0, 0, 1]
        ])
        T2 = np.array([
            [np.cos(theta2), -np.sin(theta2), 0, 0],
            [0, 0, -1, -0.032],
            [np.sin(theta2), np.cos(theta2), 0, 0],
            [0, 0, 0, 1]
        ])
        T3 = np.array([
            [np.cos(theta3), -np.sin(theta3), 0, a[1]],
            [-np.sin(theta3), -np.cos(theta3), 0, 0],
            [0, 0, -1, -0.067],
            [0, 0, 0, 1]
        ])

        T_final = np.matmul(np.matmul(T1, T2), T3)

        coord = np.matmul(T_final, end_effector_position_relative_to_the_last_joint)

        # Return the x, y, z coordinates
        #return coord[:3]
        self.update_coord(coord[:3])
        
    def update_joints(self, j0, j1, j2, j3):
        self.J0 = j0
        self.J1 = j1
        self.J2 = j2
        self.J3 = j3

    def update_coord(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def parse_and_store(self, input_string):
        for part in input_string.split("; "):
            if part:
                label, value = part.split(": ")
                setattr(self, label, float(value))

    def read_from_port(self):
        while not self.stop_event.is_set():
            try:
                if self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                    self.parse_and_store(response)
                    self.Done = True
            except serial.SerialException as e:
                print(f"Error reading from serial port: {e}")
                self.stop_event.set()  # Stop the loop in case of error
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.stop_event.set()  # Stop the loop for any unexpected error
            else:
                time.sleep(0.1)  # Sleep if no data is available

    def send_command(self, command):
        try:
            self.ser.write((command + '\n').encode())
            self.Done = False
            time.sleep(0.1)
        except serial.SerialException as e:
            print(f"Error sending command to serial port: {e}")
        except Exception as e:
            print(f"Unexpected error sending command: {e}")

    def absframe(self, t0, t1, t2, t3):
        return t0 - self.J0, t1 - self.J1, t2 - self.J2, t3 - self.J3

    def wait_done(self, timeout=15):
        start_time = time.time()
        while not self.Done:
            if time.time() - start_time > timeout:
                print("Timeout: Target not reached.")
                break
            time.sleep(0.1)

    def move_to_coords(self, coords):
        angles = self.calculate_joint_angles(*coords)
        abs_angles = self.absframe(*angles)
        command = "J0,{:.2f},J1,{:.2f},J2,{:.2f},J3,{:.2f};".format(*abs_angles)
        self.send_command(command)
        self.wait_done()

    # def send_coords(self):
    #     coordinates = [(0.30, 0, 0.048), (0.20, 0, 0.048), (0.20, 0.05, 0.048), 
    #                    (0.30, 0.05, 0.048), (0.30, 0, 0.048)]
    #     for coord in coordinates:
    #         self.execute_movement(coord)
    #     self.send_command("HOME;")

    def close(self):
        self.stop_event.set()
        self.thread.join()
        try:
            self.ser.close()
        except serial.SerialException as e:
            print(f"Error closing serial port: {e}")
        except Exception as e:
            print(f"Unexpected error while closing serial port: {e}")

# Usage example (not to be included in the class file):
# robot_arm = RobotArm('COM7')
# robot_arm.send_coords()
# robot_arm.close()