from robotarm11 import *
from joystick import Joystick

robot_arm = RobotArm('COM4')

try:
    js = Joystick()
except Exception as e:
        print("Joystick Not Detected:", e)


#cprint(robot_arm.ik(0.4,-0.034,0.07))

def draw_square(robot_arm, start_x, start_y, side_length, z):
    # Calculate the end points of the square based on the starting point and side length
    end_x = start_x + side_length
    end_y = start_y + side_length

    # Draw the bottom edge from left to right
    for x in range(int(start_x*100), int(end_x*100), 2):  # Adjust step size as needed
        robot_arm.ik(x/100, start_y, z)
        robot_arm.wait_done()

    # Draw the right edge from bottom to top
    for y in range(int(start_y*100), int(end_y*100), 2):  # Adjust step size as needed
        robot_arm.ik(end_x, y/100, z)
        robot_arm.wait_done()

    # Draw the top edge from right to left
    for x in range(int(end_x*100), int(start_x*100), -2):  # Adjust step size as needed
        robot_arm.ik(x/100, end_y, z)
        robot_arm.wait_done()

    # Draw the left edge from top to bottom
    for y in range(int(end_y*100), int(start_y*100), -2):  # Adjust step size as needed
        robot_arm.ik(start_x, y/100, z)
        robot_arm.wait_done()

def parse_ik_command(cmd):
    """Parse the 'IK' command to extract x, y, z coordinates."""
    try:
        parts = cmd.split()
        x, y, z = map(float, parts[1].split(','))
        return x, y, z
    except ValueError as e:
        print(f"Error parsing coordinates: {e}")
        return None
    
def parse_fk_command(cmd):
    """Parse the 'IK' command to extract x, y, z coordinates."""
    try:
        parts = cmd.split()
        theta1, theta2, theta3, theta4 = map(float, parts[1].split(','))
        return theta1, theta2, theta3, theta4
    except ValueError as e:
        print(f"Error parsing coordinates: {e}")
        return None
    
def parse_drawik_command(cmd):
    """Parse the 'IK' command to extract x, y, z coordinates."""
    try:
        parts = cmd.split()
        x, y, z = map(float, parts[0:3])  # Adapt to use space as the separator
        return x, y, z
    except ValueError as e:
        print(f"Error parsing coordinates: {e}")
        return None

while True:
        cmd = input()
        if cmd.lower() == 'exit': 
            robot_arm.close() 
            break
        elif cmd.upper().startswith('IK'): 
            coords = parse_ik_command(cmd)
            if coords:
                x, y, z = coords
                robot_arm.ik(x, y, z)
        elif cmd.upper().startswith('FK'): 
            coords = parse_fk_command(cmd)
            if coords:
                theta1, theta2, theta3, theta4 = coords
                robot_arm.fk(theta1, theta2, theta3, theta4)
        elif cmd.lower() == 'home':
            robot_arm.send_command('J0,0,J1,0,J2,0,J3,0;')
        elif cmd.lower() == 'zero':
            robot_arm.resetOrigin()
        elif cmd.lower() == 'dance':
            robot_arm.send_command('J0,90,J1,0,J2,0,J3,0;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,45,J1,0,J2,0,J3,0;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,45,J1,45,J2,0,J3,0;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,45,J1,0,J2,0,J3,0;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,45,J1,0,J2,45,J3,0;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,45,J1,0,J2,0,J3,0;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,45,J1,0,J2,0,J3,-45;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,45,J1,0,J2,0,J3,0;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,45,J1,45,J2,45,J3,-90;')
            robot_arm.wait_done()
            robot_arm.send_command('J0,0,J1,0,J2,0,J3,0;')
            robot_arm.wait_done()
        elif cmd.lower() == 'square':
            draw_square(robot_arm, 0.06, 0.06, 0.13, 0)
        elif cmd.lower() == 'print':
            print(robot_arm.Dis)
            print(robot_arm.z)
        elif cmd.lower() == 'doodle':
            file_name = "output_data.txt"
            try:
                with open(file_name, 'r') as file:
                    for line in file:
                        coords = parse_drawik_command(line.strip())
                        if coords:
                            x, y, z = coords
                            print(coords)
                            robot_arm.ik(x, y, z)
                            robot_arm.wait_done()
            except FileNotFoundError:
                print(f"File not found: {file_name}")
            except Exception as e:
                print(f"An error occurred: {e}")
            robot_arm.send_command('J0,0,J1,0,J2,0,J3,0;')
        elif cmd.lower() == 'js':
            robot_arm.ik(0.05,0.05,0.01)
            robot_arm.z = 0.01
            js_reading = js.get_values()
            button_x = js_reading["buttons"][2]
            while (button_x != 1):
                js_reading = js.get_values()
                button_x = js_reading["buttons"][2]
                #print("hi")
                step = 0.01
                curr_x = robot_arm.x
                curr_y = robot_arm.y
                curr_z = robot_arm.z

                hats_x = js_reading["hats"][0][0]
                hats_y = js_reading["hats"][0][1]

                button_a = js_reading["buttons"][0]
                button_b = js_reading["buttons"][1]
                
                button_y = js_reading["buttons"][3]

                # print("hats_x: ", hats_x)
                # print("hats_y: ", hats_y)
                # print("b_a: ", button_a)
                # print("b_b: ", button_b)
                # print("b_y: ", button_y)

                if (hats_x == 1): # move positive in x direction
                    if curr_x < 0.2:
                        curr_x += step
                        robot_arm.ik(curr_x, curr_y, curr_z)
                        robot_arm.wait_done()
                        #print(curr_x, curr_y, curr_z)
                elif (hats_x == -1): # move negative in x direction
                    if curr_x >0.06:
                        curr_x -= step
                        robot_arm.ik(curr_x, curr_y, curr_z)
                        robot_arm.wait_done()
                        #print(curr_x, curr_y, curr_z)

                elif (hats_y == 1): # move positive in y direction
                    if curr_y < 0.2:
                        curr_y += step
                        robot_arm.ik(curr_x, curr_y, curr_z)
                        robot_arm.wait_done()
                        #print(curr_x, curr_y, curr_z)
                elif (hats_y == -1): # move negative in y direction
                    if curr_y>0.06:
                        curr_y -= step
                        robot_arm.ik(curr_x, curr_y, curr_z)
                        robot_arm.wait_done()
                        #print(curr_x, curr_y, curr_z)

                elif (button_y == 1): # move positive in z direction
                    if curr_z < 0.1:
                        curr_z += 0.002
                        robot_arm.ik(curr_x, curr_y, curr_z)
                        robot_arm.wait_done()
                        #print(curr_x, curr_y, curr_z)
                elif (button_a == 1): # move negative in z direction
                    if curr_z > -0.5:
                        curr_z -= 0.002
                        robot_arm.ik(curr_x, curr_y, curr_z)
                        robot_arm.wait_done()
                        #print(curr_x, curr_y, curr_z)

                robot_arm.x = curr_x
                robot_arm.y = curr_y
                robot_arm.z = curr_z
                #time.sleep(0.1)
            robot_arm.send_command('J0,0,J1,0,J2,0,J3,0;')
            
        else:
            robot_arm.send_command(cmd)