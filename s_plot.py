import pandas as pd
import matplotlib.pyplot as plt

# Read data
directory = 'Datasets/11_final_extra'
df = pd.read_csv(f'{directory}/data/data.csv')

# Create subplots
fig, axes = plt.subplots(2, 4, figsize=(15, 8), sharey=True)
axes = axes.flatten()

# Plot each sensor value
for i, sensor in enumerate(['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7']):
    sorted_data = df[sensor].sort_values()
    axes[i].plot(range(len(sorted_data)), sorted_data, 'b-')
    axes[i].set_title(f'{sensor}')
    axes[i].set_xlabel('Index')
    axes[i].set_ylabel('Sensor Value')
    axes[i].grid(True)
    axes[i].axhline(y=50, color='k', linewidth=1, linestyle='--')
    axes[i].axhline(y=950, color='k', linewidth=1, linestyle='--')

plt.tight_layout()
plt.savefig(f'{directory}/data/sensor_plots.png')
plt.close()