# 3D Printed Force-Torque Sensor (FTS) Calibration

## Overview
FTS_Calibration is a Python-based project for calibrating Force/Torque Sensors (FTS) used in robotics.

This repository provides tools and scripts to process sensor data, perform calibration, and validate results, ensuring accurate force and torque measurements.

## Original 3D Printed FTS and code
The original 3D printed FTS is taken from the next paper: https://ieeexplore.ieee.org/document/9133543

The paper comes with its own GitHub repository, which runs the sensor and performs calibration using ROS: https://github.com/TAMS-Group/tams_printed_ft/tree/master

However, I did not find the code for performing the calibration in the original code, so I created this project for doing so, using Python without ROS.

# Python scripts
Each Python script has an explanation of what it does at the top of the file.
They are chronologically ordered from 0 to 5:  
├──0_get_data_sensONE.py  
├──1_get_data_centered_mass.py  
├──1_get_data_offcentered_mass.py  
├──2_merge_data.py    
├──2_plot_data.py  
├──2_s_plot_data.py   
├──3_linearization.py   
├──3_linearization_quadratic.py    
├──4_validation.py   
├──4_validation_quadratic.py   
├──5_read_calibrated_values.py   
└──5_read_calibrated_values_quadratic.py

# Example results
Explain example results

├──Datasets
│  └──12_final_extra_bounded  
