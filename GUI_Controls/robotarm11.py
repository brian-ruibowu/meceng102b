import serial
import threading
import time
import numpy as np

class RobotArm:
    def __init__(self, port='COM4', baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for the serial connection to initialize
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            # Exit or raise an exception depending on your error handling strategy
            raise

        #robot parameter configuration
        self.Dis = 0.049
        self.l1 = 0.18
        self.l2 = 0.18
        #self.l3 = 0.1035
        self.l3=0.127
        self.lbase = 0.17

        self.previousR = 0

        self.d = np.array([self.lbase, 0.0, -0.034])
        self.a = np.array([0, self.l1, self.l2])
        self.alpha = np.array([0.5*np.pi, -np.pi, -np.pi])
        
        #robot status initialization
        self.x = self.y = self.z = 0.0
        self.J0 = 0.0
        self.J1 = 0.0
        self.J2 = 0.0
        self.J3 = 0.0
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
        if x<0.05 or x>0.22 or y<0.05 or y>0.22 or z<-0.01 or z>0.2:
            print("IK Value Exceeds Limits")
        else:
            self.x = x
            self.y = y
            self.z = z
            d = self.d
            a = self.a
            l1 = self.l1 #arm1 length in meter
            l2 = self.l2 #arm2 length in meter
            l3 = self.l3
            y -= d[2] #end effactor y offset from joint 1
            z += (l3 - d[0]) #end effactor z offset from joint 1
            d = np.sqrt(x**2 + y**2)
            z_offset = self.adjustZ(d)
            # if d < self.previousR:
            #     z_offset += 0.0005
            #z_offset = 0
            print("z_offset: " + str(z_offset))
            z += z_offset

            self.previousR = d
            theta1 = np.arctan2(y, x)

            cos_theta3 = (d**2 + z**2 - l1**2 - l2**2) / (2 * l1 * l2)
            cos_theta3 = np.clip(cos_theta3, -1.0, 1.0)  # Clipping to avoid domain error
            theta3 = np.arccos(cos_theta3)

            theta2 = np.arctan2(z, d) + np.arctan2(l2 * np.sin(theta3), l1 + l2 * np.cos(theta3))
            #theta4 = -1 * (np.degrees(theta2) - np.degrees(theta3)) - 0.5*np.pi
            theta4 = -1*(0.5*np.pi+theta2-theta3)
            theta4 = theta4 % (2*np.pi)
            if theta4 > np.pi:
                theta4 -= 2*np.pi
            theta1 = np.degrees(theta1)
            theta2 = np.degrees(theta2)
            theta3 = np.degrees(theta3)
            theta4 = np.degrees(theta4)
            theta2 = theta2 - 90
            theta3 = theta3 -90
            # if theta4 > 180:
            #     theta4 -= 180  # Subtract 360 to wrap around if above 90
            # elif theta4 < -180:
            #     theta4 += 180  # Add 360 to wrap around if below -90
            print([theta1, theta2, theta3, theta4])
            self.update_joints(theta1, theta2, theta3, theta4)
            self.move_to_angles((theta1, theta2, theta3, theta4))


    def fk(self, theta1, theta2, theta3, theta4):
        theta1 = np.deg2rad(theta1)
        theta2 = np.deg2rad(theta2+90)
        theta3 = np.deg2rad(theta3+90)
        theta4 = np.deg2rad(theta4)

        # DH parameters
        d = self.d
        a = self.a

        # End effector position relative to the last joint
        end_effector_position_relative_to_the_last_joint = np.array([self.l3, 0, 0, 1])
        T1 = np.array([
            [np.cos(theta1), -np.sin(theta1), 0, 0],
            [np.sin(theta1), np.cos(theta1), 0, 0],
            [0, 0, 1, d[0]],
            [0, 0, 0, 1]
        ])
        T2 = np.array([
            [np.cos(theta2), -np.sin(theta2), 0, 0],
            [0, 0, -1, d[2]],
            [np.sin(theta2), np.cos(theta2), 0, 0],
            [0, 0, 0, 1]
        ])
        T3 = np.array([
            [np.cos(theta3), -np.sin(theta3), 0, a[1]],
            [-np.sin(theta3), -np.cos(theta3), 0, 0],
            [0, 0, -1, 0],
            [0, 0, 0, 1]
        ])
        T4 = np.array([
            [np.cos(theta4), -np.sin(theta4), 0, a[2]],
            [-np.sin(theta4), -np.cos(theta4), 0, 0],
            [0, 0, -1, 0],
            [0, 0, 0, 1]
        ])

        T_final = np.matmul(np.matmul(np.matmul(T1, T2), T3),T4)

        coord = np.matmul(T_final, end_effector_position_relative_to_the_last_joint)
        print(coord[:3])

        # Return the x, y, z coordinates
        self.update_coord(coord[1],coord[2],coord[3])
        self.move_to_angles((np.rad2deg(theta1),np.rad2deg(theta2),np.rad2deg(theta3),np.rad2deg(theta4)))
        
    
        
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
                self.Dis = self.Dis/100
                self.correctZ()

    def read_from_port(self):
        while not self.stop_event.is_set():
            try:
                if self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                    self.parse_and_store(response)
                    print(f"Received: {response}")
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

    def wait_done(self, timeout=60):
        start_time = time.time()
        while not self.Done:
            if time.time() - start_time > timeout:
                print("Timeout: Target not reached.")
                break
            time.sleep(0.01)

    def move_to_angles(self, angles):
        #abs_angles = self.absframe(*angles)
        command = "J0,{:.2f},J1,{:.2f},J2,{:.2f},J3,{:.2f};".format(*angles)
        self.send_command(command)
        self.wait_done()

    def resetOrigin(self):
        command = "ZERO;"
        self.send_command(command)

    def correctZ(self):
        self.z = self.Dis - 0.0429

    def close(self):
        self.stop_event.set()
        self.thread.join()
        try:
            self.ser.close()
        except serial.SerialException as e:
            print(f"Error closing serial port: {e}")
        except Exception as e:
            print(f"Unexpected error while closing serial port: {e}")
    
    def adjustZ(self, x):
        return -6.75e-3 + (0.132 * x) + (-0.563 * x**2) + (0.912 * x**3)
    
    
