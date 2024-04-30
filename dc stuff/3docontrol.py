import serial
import threading
import time
import numpy as np

J0 = 0.0
J1 = 0.0
J2 = 0.0
J3 = 0.0
Done = False

# Setup serial connection
# Note: Replace 'COM7' with your actual COM port used by the Arduino
ser = serial.Serial('COM7', 115200, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize

# This event signals the thread to stop
stop_event = threading.Event()

def calculate_joint_angles(x, y, z):
    l1 = .18
    l2 = .18
    y = y+0.0355
    z=z-.1021
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

    theta4_deg = -1*(theta2_deg-theta3_deg)
    
    return (theta1_deg, theta2_deg, theta3_deg, theta4_deg)

def parse_and_store(input_string):
    global J0, J1, J2, J3  # Use global keyword to modify global variables
    
    # Split the string by "; " to get each Jn: value pair
    parts = input_string.split("; ")
    
    for part in parts:
        if part:  # Check if part is not empty
            # Split each part by ": " to separate the label from the value
            label, value = part.split(": ")
            # Convert value to float and assign it to the corresponding global variable
            if label == "J0":
                J0 = float(value)
            elif label == "J1":
                J1 = float(value)
            elif label == "J2":
                J2 = float(value)
            elif label == "J3":
                J3 = float(value)

def read_from_port(ser):
    global Done
    while not stop_event.is_set():  # Check if the stop event is signaled
        if ser.in_waiting:
            response = ser.readline().decode().strip()  # Read the response
            parse_and_store(response)
            print(f"Received: {response}")
            Done = True
        else:
            time.sleep(0.1)  # Short delay to prevent busy waiting

def send_command(command):
    global Done
    ser.write((command + '\n').encode())  # Send command
    print(f"Sent: {command}")
    Done = False
    time.sleep(0.1)  # Wait for the Arduino to process the command

def absframe(t0, t1, t2, t3):
    global J0, J1, J2, J3
    t0 = t0 - J0
    t1 = t1 - J1
    t2 = t2 - J2
    t3 = t3 - J3
    return(t0, t1, t2, t3)

tolerance = 0.1

def waitDone():
    global Done
    start_time = time.time()
    timeout = 15  # seconds
    
    while Done == False:
        if time.time() - start_time > timeout:
            print("Timeout: Target not reached.")
            break
        
        time.sleep(0.1)  # Small delay to reduce CPU usage

def send_coords():
    global J0, J1, J2
    theta0, theta1, theta2, theta3 = calculate_joint_angles(0.30, 0, 0.048)
    theta0, theta1, theta2, theta3 = absframe(theta0, theta1, theta2, theta3)
    send_command("J0,{:.2f},J1,{:.2f},J2,{:.2f},J3,{:.2f};".format(theta0, theta1, theta2, theta3))
    waitDone()
    theta0, theta1, theta2, theta3 = calculate_joint_angles(0.20, 0, 0.048)
    theta0, theta1, theta2, theta3 = absframe(theta0, theta1, theta2, theta3)
    send_command("J0,{:.2f},J1,{:.2f},J2,{:.2f},J3,{:.2f};".format(theta0, theta1, theta2, theta3))
    waitDone()
    theta0, theta1, theta2, theta3 = calculate_joint_angles(0.20, 0.05, 0.048)
    theta0, theta1, theta2, theta3 = absframe(theta0, theta1, theta2, theta3)
    send_command("J0,{:.2f},J1,{:.2f},J2,{:.2f},J3,{:.2f};".format(theta0, theta1, theta2, theta3))
    waitDone()
    theta0, theta1, theta2, theta3 = calculate_joint_angles(0.30, 0.05, 0.048)
    theta0, theta1, theta2, theta3 = absframe(theta0, theta1, theta2, theta3)
    send_command("J0,{:.2f},J1,{:.2f},J2,{:.2f},J3,{:.2f};".format(theta0, theta1, theta2, theta3))
    waitDone()
    theta0, theta1, theta2, theta3 = calculate_joint_angles(0.30, 0, 0.048)
    theta0, theta1, theta2, theta3 = absframe(theta0, theta1, theta2, theta3)
    send_command("J0,{:.2f},J1,{:.2f},J2,{:.2f},J3,{:.2f};".format(theta0, theta1, theta2, theta3))
    waitDone()
    send_command("HOME;")

# Start the thread for reading from port
thread = threading.Thread(target=read_from_port, args=(ser,))
thread.start()

try:
    print("Enter your commands below. Type 'exit' to quit.")
    while True:
        cmd = input()
        if cmd.lower() == 'exit':  # Type 'exit' to quit the loop
            break
        elif cmd.lower() == 'run':
            send_coords()
        else:
            send_command(cmd)
finally:
    stop_event.set()  # Signal the thread to stop
    thread.join()  # Wait for the thread to actually stop
    ser.close()  # Ensure the serial port is closed on exit