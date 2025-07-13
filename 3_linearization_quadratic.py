import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import joblib

# Load dataset
directory = 'Datasets/12_final_extra_bounded'
df = pd.read_csv(f'{directory}/train/train_data.csv')
# Features (S: 8x1) and targets (W: 6x1)
S = df[['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7']].values  # Shape: (datapoints, 8)
W = df[['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz']].values  # Shape: (datapoints, 6)

# Create pipeline with quadratic terms
poly = PolynomialFeatures(degree=2, include_bias=False)  # Linear + quadratic terms
estimator = 'lasso' #estimator = 'ridge' #estimator = 'linearregression'
if estimator == 'linearregression':
    model = make_pipeline(poly, LinearRegression())
elif estimator == 'ridge':
    model = make_pipeline(poly, Ridge())
elif estimator == 'lasso':
    model = make_pipeline(poly, Lasso())
else:
    print('Invalid estimator')
model.fit(S, W)

# Extract coefficients
L = model.named_steps[estimator].coef_[:, :8]  # Linear terms (6x8)
Q = model.named_steps[estimator].coef_[:, 8:]  # Quadratic terms (6x36 for 8 sensors)
C = model.named_steps[estimator].intercept_  # Bias (6x1)

# Save results
results = pd.DataFrame({
    'Wrench': ['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz'],
    'C': C,
    **{f'L_s{i}': L[:, i] for i in range(8)},
    **{f'Q_s{i}s{j}': Q[:, i*8 + j - i*(i+1)//2] for i in range(8) for j in range(i, 8)}  # Quadratic terms
})
results.to_csv(f'{directory}/results/params/params_{estimator}_quadratic.csv', index=False)

# Print results
print("Bias Vector C (6x1):", C)
print("\nLinear Matrix L (6x8):", L)
print("\nQuadratic Coefficients Q (6x36):", Q)

# Evaluate
from sklearn.metrics import r2_score
W_pred = model.predict(S)
print("\nR² Score:", r2_score(W, W_pred))