import math
import sys
import struct
import time
import numpy as np
import serial
import pandas as pd

print('Starting...')

# Function to compute W = C + LS + QS^2
def compute_wrench(C, L, Q, S):
    W = np.zeros(6)
    S = np.array(S)
    # Linear terms: C + LS
    W += C.flatten() + L @ S
    # Quadratic terms: QS^2
    quad_terms = np.array([S[i] * S[j] for i in range(len(S)) for j in range(i, len(S))])
    W += Q @ quad_terms
    return W.tolist()

try:
    # Open serial port
    port = 'COM3'
    baudrate = 115200
    ser = serial.Serial(port, baudrate, parity=serial.PARITY_NONE)
    print("Got the serial port.")

    n_sensors = 8
    overload_lower = 50
    overload_upper = 950

    # Load calibrated C, L, and Q
    df = pd.read_csv('Datasets/7_offcenter_mass_1_and_3/linearization_params_with_quadratic.csv')
    C = df['C'].values  # Shape: (6,)
    L = df[['L_s0', 'L_s1', 'L_s2', 'L_s3', 'L_s4', 'L_s5', 'L_s6', 'L_s7']].values  # Shape: (6, 8)
    Q_cols = [f'Q_s{i}s{j}' for i in range(n_sensors) for j in range(i, n_sensors)]
    Q = df[Q_cols].values  # Shape: (6, 36)

    while True:
        # Get raw sensor values
        try:
            data = ser.readline()
            (str_D, seq_number, error_mask, s0, s1, s2, s3, s4, s5, s6, s7) = \
                [t(s) for t, s in zip((str, int, int, int, int, int, int, int, int, int, int), data.split())]
        except (ValueError, IndexError):
            print("Error parsing data:", data)
            continue

        s = [s0, s1, s2, s3, s4, s5, s6, s7]
        for i in range(n_sensors):
            if (s[i] < overload_lower) or (s[i] > overload_upper):
                print(f"Force overload channel {i}")
                continue

        # Compute wrench
        [Fx, Fy, Fz, Mx, My, Mz] = compute_wrench(C, L, Q, s)

        # Print line
        print('\n')
        print(f"Fx: {Fx:.3f}, Fy: {Fy:.3f}, Fz: {Fz:.3f}, Mx: {Mx:.3f}, My: {My:.3f}, Mz: {Mz:.3f},\n"
              f"s0: {s0}, s1: {s1}, s2: {s2}, s3: {s3}, s4: {s4}, s5: {s5}, s6: {s6}, s7: {s7}")
        print('\n')

        time.sleep(1/200)

except KeyboardInterrupt:
    print('Stopped.')
except Exception as exp:
    print("Exception:", exp)
    sys.exit(1)
finally:
    print('Finished.')
    ser.close()