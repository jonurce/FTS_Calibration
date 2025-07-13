"""

This file collects data from the 3D printed sensor and writes it down in a csv along with
an estimated wrench for a given mass fixed to the FTS and off-centered on its z-axis.

For each timestamp, the 8 raw sensor values are collected from the 3D printed sensor (s_0 to s_7)
and the wrench is estimated for the off-centered mass.

The user has to introduce the position in which the mass is placed (0 / 1 / 2 / 3 / 4),
as well as the RPY angles from the test orientation (in radians).

The results are stored in a csv file, each row containing the next values:
< Timestamp, Fx, Fy, Fz, Mx, My, Mz, s0, s1, s2, s3, s4, s5, s6, s7 >

"""
import math
import sys
import struct
import time
import collections
import numpy as np
import pysoem
import ctypes
import struct
import csv
import os
import serial

print('Starting get_data.')

def get_r_and_m_from_user():
    while True:
        user_input = input("Enter the position of the mass (0 / 1 / 2 / 3 / 4): ").strip()
        # Check if input starts with '+' or '-' and the rest is a valid number
        if user_input in ['0', '1', '2', '3', '4']:
            print(f"The position of the mass is: {user_input}")
            break
        else:
            print("Error: Input must be exactly '1', '2', '3', '4'. ")
    pos = float(user_input)
    m_total = 1.028  # kg
    m_holder = 0.309 # kg
    if pos == 0.0:
        return [[0.0, 0.0, 0.045], pos, m_holder]  # meters [x, y, z]
    if pos == 1.0:
        return [[0.02937, 0.02937, 0.05394], pos, m_total]
    elif pos == 2.0:
        return [[-0.02937, 0.02937, 0.05394], pos, m_total]
    elif pos == 3.0:
        return [[-0.02937, -0.02937, 0.05394], pos, m_total]
    elif pos == 4.0:
        return [[0.02937, -0.02937, 0.05394], pos, m_total]


# Function to get angle from user from prompt
def get_angle(prompt):
    while True:
        try:
            angle = float(input(prompt).strip())
            if angle < -np.pi or angle > np.pi:
                print("Error: Input value must be between -π and π.")
            else:
                return angle
        except ValueError:
            print("Error: Please enter a valid number.")

# Function to get euler angles from user
def euler_angles_from_user():
    roll = get_angle("Enter roll (x-axis) in radians: ")
    pitch = get_angle("Enter pitch (y-axis) in radians: ")
    yaw = get_angle("Enter yaw (z-axis) in radians: ")
    return [roll, pitch, yaw]

# Function to compute rotation matrix from the Euler angles
# Rotation matrix for ZYX Euler angles = RPY
def rotation_matrix_from_euler_angles(roll, pitch, yaw):
    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    R = np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr]
    ])
    return R

try:
    # Open serial port
    port = 'COM3'
    baudrate = 115200
    ser = serial.Serial(port, baudrate, parity=serial.PARITY_NONE)
    print("Got the serial port.")

    # Define sensor values
    n_sensors = 8
    overload_lower = 50
    overload_upper = 950

    # Get wrench
    [r, pos, m] = get_r_and_m_from_user() # meters [x, y, z] and kg
    g = 9.81  # m/s2
    F_w = [0, 0, - m * g]
    [roll, pitch, yaw] = euler_angles_from_user()
    R_ws = rotation_matrix_from_euler_angles(roll, pitch, yaw)
    F_s = np.dot(np.linalg.inv(R_ws), F_w)
    M_s = np.cross(r, F_s)

    # Create CSV
    filename = f'Datasets/11_final_extra/data/data_{pos}_R{roll}_P{pitch}_Y{yaw}.csv'
    csvfile = open(filename, 'a', newline='')
    fieldnames = ['Timestamp', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz',
                  's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header only if file is empty
    if os.path.getsize(filename) == 0:
        writer.writeheader()

    datapoints = 0
    start_datapoint = 10
    total_datapoints = 2000 + start_datapoint
    time_step = 1 / 200
    start_time = time.time()

    #while True:
    while datapoints < total_datapoints:
        datapoints += 1

        # Get timestamp
        timestamp = (time.time() - start_time)

        # Get raw sensor values
        try:
            data = ser.readline()
            (str_D, seq_number, error_mask, s0, s1, s2, s3, s4, s5, s6, s7) = \
                [t(s) for t, s in zip((str, int, int, int, int, int, int, int, int, int, int), data.split())]
        except ValueError:
            print("parsing input data failed, data='", data, "'")
            continue
        except IndexError:  # probably wrong formatted string...
            print("could not parse message/data:", data)
            continue

        s = [s0, s1, s2, s3, s4, s5, s6, s7]
        for i in range(n_sensors):
            if (s[i] < overload_lower) or (s[i] > overload_upper):
                print(f"Force overload channel {i}")
                continue

        if datapoints > start_datapoint:
            writer.writerow({'Timestamp': timestamp,
                'Fx': F_s[0], 'Fy': F_s[1], 'Fz': F_s[2], 'Mx': M_s[0],'My': M_s[1], 'Mz': M_s[2],
                's0': s0, 's1': s1, 's2': s2, 's3': s3, 's4': s4, 's5': s5, 's6': s6, 's7': s7
             })

        csvfile.flush()
        time.sleep(time_step)
        print(f"Saved {datapoints} datapoints")

except KeyboardInterrupt:
    # ctrl-C abort handling
    print('Stopped.')
except Exception as exp:
    print("Exception. Something went wrong.")
    sys.exit(1)
finally:
    csvfile.close()
    print('The csv file is closed.')


