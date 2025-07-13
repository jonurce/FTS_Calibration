"""

This file collects data from the 3D printed sensor (s_0 to s_7),
and uses the calibration matrices C and L to obtain the wrench W=C+LS

The wrench is printed on screen in real time

"""
import math
import sys
import struct
import time

import numpy as np
import serial
import pandas as pd

print('Starting...')

# Function to compute the wrench W = [Fx, Fy, Fz, Mx, My, Mz], based on C, L and S (W=C+LS)
def compute_wrench(C, L, S):
    W = [0, 0, 0, 0, 0, 0]
    # W = C + np.dot(L,S)
    for i in range(len(W)):
        W[i] += C[i]
        for j in range(len(S)):
            W[i] += L[i,j] * S[j]
    return W

try:
    # Open serial port
    port = 'COM3'
    baudrate = 115200
    ser = serial.Serial(port, baudrate, parity=serial.PARITY_NONE)
    print("Got the serial port.")

    n_sensors = 8
    overload_lower = 50
    overload_upper = 950

    # Load calibrated C and L
    df = pd.read_csv('Datasets/7_offcenter_mass_1_and_3/params_ridge.csv')
    C = df[['C']].values # Shape: (6, 1)
    L = df[['L_s0','L_s1','L_s2','L_s3','L_s4','L_s5','L_s6','L_s7']].values # Shape: (6, 8)

    while True:
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

        # Compute wrench
        [Fx, Fy, Fz, Mx, My, Mz] = compute_wrench(C, L, s)

        # Print line
        print('\n')
        print(f"Fx: {Fx}, Fy: {Fy}, Fz: {Fz}, Mx: {Mx}, My: {My}, Mz: {Mz},\n"
             f" s0: {s0}, s1: {s1}, s2: {s2}, s3: {s3}, s4: {s4}, s5: {s5}, s6: {s6}, s7: {s7}")
        print('\n')

        time.sleep(1/200)

except KeyboardInterrupt:
    # ctrl-C abort handling
    print('Stopped.')
except Exception as exp:
    print("Exception. Something went wrong.")
    sys.exit(1)
finally:
    print('Finished.')


