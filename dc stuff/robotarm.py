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

    def calculate_joint_angles(self, x, y, z):
        l1 = l2 = .18
        y += 0.0355
        z -= .1021
        d = np.sqrt(x**2 + y**2)
        theta1 = np.arctan2(y, x)
        theta3 = np.arccos((d**2 + z**2 - l1**2 - l2**2) / (2 * l1 * l2))
        theta2 = np.arctan2(z, d) + np.arctan2(l2 * np.sin(theta3), l1 + l2 * np.cos(theta3))
        return map(np.degrees, [theta1, theta2, theta3, -1 * (np.degrees(theta2) - np.degrees(theta3))])

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

    def execute_movement(self, coords):
        angles = self.calculate_joint_angles(*coords)
        abs_angles = self.absframe(*angles)
        command = "J0,{:.2f},J1,{:.2f},J2,{:.2f},J3,{:.2f};".format(*abs_angles)
        self.send_command(command)
        self.wait_done()

    def send_coords(self):
        coordinates = [(0.30, 0, 0.048), (0.20, 0, 0.048), (0.20, 0.05, 0.048), 
                       (0.30, 0.05, 0.048), (0.30, 0, 0.048)]
        for coord in coordinates:
            self.execute_movement(coord)
        self.send_command("HOME;")

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