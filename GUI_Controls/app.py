from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import json

app = Flask(__name__)
CORS(app)


@app.route('/api/upload_drawing', methods=['POST'])
def upload_drawing():
    data = request.get_json()  # Retrieve JSON data sent from the client
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Save the received data to a file
    try:
        with open('drawing_data.json', 'w') as file:
            json.dump(data, file, indent=4)
        return jsonify({"message": "Drawing data saved successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error saving drawing data: {str(e)}")
        return jsonify({"error": "Failed to save data"}), 500

class Kinematics:
    @staticmethod
    def forward_kinematics(theta1, theta2, theta3, theta4):
        d = np.array([0.17, 0.0, -0.034])
        a = np.array([0, 0.2, 0.2])

        # End effector position relative to the last joint
        end_effector_position_relative_to_the_last_joint = np.array([0.1, 0, 0, 1])
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

        coord[0] = round(coord[0], 4) * 10
        coord[1] = round(coord[1], 4) * 10
        coord[2] = round(coord[2], 4) * 10

        return coord[:3]

    @staticmethod
    def inverse_kinematics(x, y, z):
        d = np.array([0.17, 0.0, -0.034])
        l1 = 0.2 #arm1 length in meter
        l2 = 0.2 #arm2 length in meter
        l3 = 0.1
        y -= d[2] #end effactor y offset from joint 1
        z += (l3 - d[0]) #end effactor z offset from joint 1
        d = np.sqrt(x**2 + y**2)
        theta1 = np.arctan2(y, x)

        cos_theta3 = (d**2 + z**2 - l1**2 - l2**2) / (2 * l1 * l2)
        cos_theta3 = np.clip(cos_theta3, -1.0, 1.0)  # Clipping to avoid domain error
        theta3 = np.arccos(cos_theta3)

        theta2 = np.arctan2(z, d) + np.arctan2(l2 * np.sin(theta3), l1 + l2 * np.cos(theta3))
        theta4 = -1 * (np.degrees(theta2) - np.degrees(theta3)) - 0.5*np.pi
        theta4 = theta4 % (2*np.pi)
        if theta4 > np.pi:
            theta4 -= 2*np.pi
        return  [round(theta1, 3), round(theta2, 3), round(theta3, 3), round(theta4, 3)]

@app.route('/api/forward', methods=['POST'])
def calculate_forward():
    data = request.get_json()
    if not data or 'parameters' not in data:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        theta1 = float(data['parameters']['theta1'])
        theta2 = float(data['parameters']['theta2'])
        theta3 = float(data['parameters']['theta3'])
        theta4 = float(data['parameters']['theta4'])
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid parameters"}), 400

    try:
        result = Kinematics.forward_kinematics(theta1, theta2, theta3, theta4)
        return jsonify({"position": result.tolist()})  # Convert ndarray to list
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/inverse', methods=['POST'])
def calculate_inverse():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if 'x' not in data or 'y' not in data or 'z' not in data:
        return jsonify({"error": "Missing one or more required parameters: x, y, z"}), 400

    try:
        x, y, z = float(data['x']), float(data['y']), float(data['z'])
    except ValueError:
        return jsonify({"error": "x, y, z must be numbers"}), 400

    try:
        result = Kinematics.inverse_kinematics(x, y, z)
        return jsonify({"theta1": result[0], "theta2": result[1], "theta3": result[2], "theta4": result[3]})
    except Exception as e:
        app.logger.error(f"Error computing inverse kinematics: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)