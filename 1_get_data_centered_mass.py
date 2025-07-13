"""

This file collects data from the 3D printed sensor and writes it down in a csv along with
an estimated wrench for a given mass fixed to the FTS and centered on its z-axis.

For each timestamp, the 8 raw sensor values are collected from the 3D printed sensor (s_0 to s_7)
and the wrench is estimated for the centered mass.

The user has to introduce the direction of gravity (+x / -x / +y / -y / +z / -z)
or what is the same, the direction in which the force is being applied.

The results are stored in a csv file, each row containing the next values:
< Timestamp, Fx, Fy, Fz, Mx, My, Mz, s0, s1, s2, s3, s4, s5, s6, s7 >

"""
import math
import sys
import struct
import time
import collections

import pysoem
import ctypes
import struct

import csv
import os

import serial

print('Starting get_data.')

# Function to get the direction from the user
def get_direction_from_input():
    while True:
        user_input = input("Enter the direction of the mass (+x / -x / +y / -y / +z / -z): ").strip()
        # Check if input starts with '+' or '-' and the rest is a valid number
        if user_input in ['+x', '-x', '+y', '-y', '+z', '-z']:
            print("The direction of the mass is: " + user_input)
            return user_input
        else:
            print("Error: Input must be exactly '+x', '-x', '+y', '-y', '+z' or '-z'. ")

# Function to compute the wrench [Fx, Fy, Fz, Mx, My, Mz], based on the applied force F, its direction
# and torque M (from F being applied at a distance d of the COG to the tool's origin)
def compute_wrench(F, M, direction):
    if direction == '+x':
        return [F, 0.0, 0.0, 0.0, M, 0.0]
    elif direction == '-x':
        return [-F, 0.0, 0.0, 0.0, -M, 0.0]
    elif direction == '+y':
        return [0.0, F, 0.0, -M, 0.0, 0.0]
    elif direction == '-y':
        return [0.0, -F, 0.0, M, 0.0, 0.0]
    elif direction == '+z':
        return [0.0, 0.0, F, 0.0, 0.0, 0.0]
    elif direction == '-z':
        return [0.0, 0.0, -F, 0.0, 0.0, 0.0]

try:
    # Open serial port
    port = 'COM3'
    baudrate = 115200
    ser = serial.Serial(port, baudrate, parity=serial.PARITY_NONE)
    print("Got the serial port.")

    n_sensors = 8
    overload_lower = 50
    overload_upper = 950

    # Get wrench
    m = 0.93  # kg
    d = 0.055  # meters - distance to COG (centered)
    g = 9.81  # m/s2

    F = m * g
    M = F * d
    direction = get_direction_from_input()
    [Fx, Fy, Fz, Mx, My, Mz] = compute_wrench(F, M, direction)

    # Create CSV
    filename = f'data_{direction}.csv'
    csvfile = open(filename, 'a', newline='')
    fieldnames = ['Timestamp', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz', 's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7']
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

        # Print line
        # print('\n')
        # print(f"Fx: {Fx}, Fy: {Fy}, Fz: {Fz}, Mx: {Mx}, My: {My}, Mz: {Mz},\n"
        #      f" s0: {s0}, s1: {s1}, s2: {s2}, s3: {s3}, s4: {s4}, s5: {s5}, s6: {s6}, s7: {s7}")
        # print('\n')

        if datapoints > start_datapoint:
            writer.writerow({'Timestamp': timestamp,
                'Fx': Fx, 'Fy': Fy, 'Fz': Fz, 'Mx': Mx,'My': My, 'Mz': Mz,
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


