"""

This file reads the CSV file with collected data (the merged one), and then
solves the linear coefficients C and L (not Q) using the OLS method.

It can be easily changed from Linear Regression, to Ridge or Lasso.

"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import GridSearchCV
import joblib

# Load the dataset
directory = 'Datasets/12_final_extra_bounded'
df = pd.read_csv(f'{directory}/train/train_data.csv')

# Features (sensor values, S: 8x1) and targets (wrench values, W: 6x1)
S = df[['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7']].values  # Shape: (12000, 8)
W = df[['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz']].values  # Shape: (12000, 6)

# Fit linear regression model: W = C + LS
# model = LinearRegression()
# model = Ridge()  # Tune alpha
model = Lasso()  # Tune alpha
model.fit(S, W)

# Extract L (6x8 matrix) and C (6x1 vector)
L = model.coef_  # Shape: (6, 8)
C = model.intercept_  # Shape: (6,)

# Save L and C to a CSV file
results = pd.DataFrame({
    'Wrench': ['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz'],
    'C': C,
    'L_s0': L[:, 0], 'L_s1': L[:, 1], 'L_s2': L[:, 2], 'L_s3': L[:, 3],
    'L_s4': L[:, 4], 'L_s5': L[:, 5], 'L_s6': L[:, 6], 'L_s7': L[:, 7]
})
results.to_csv(f'{directory}/results/params/params_lasso.csv', index=False)

# Print results
print("Bias Vector C (6x1):")
print(C)
print("\nCoefficient Matrix L (6x8):")
print(L)