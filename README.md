# 3D Printed Force-Torque Sensor (FTS) Calibration

## Overview
FTS_Calibration is a Python-based project for calibrating Force/Torque Sensors (FTS) used in robotics.

This repository provides tools and scripts to process sensor data, perform calibration, and validate results, ensuring accurate force and torque measurements.

## Original 3D Printed FTS and code
The original 3D printed FTS is taken from the next paper: https://ieeexplore.ieee.org/document/9133543

The paper comes with its own GitHub repository, which runs the sensor and performs calibration using ROS: https://github.com/TAMS-Group/tams_printed_ft/tree/master

However, I did not find the code for performing the calibration in the original code, so I created this project for doing so, using Python without ROS.

## Calibration approach 0: Using another calibrated FTS (failed)
For this approach, a SensONE FTS (https://www.botasys.com/force-torque-sensors/sensone) was used for computing the estimated wrench, using part of the code from https://gitlab.com/botasys/python_interface (check dependencies there).

The main reason for this approach to fail is that there was a **noticeable jump in wrench values for every time the code was run**.

<span style="color:red">red text</span>

The python script and the collected data showing the jumps is available in:  
- Datasets
  - 0_SensOne_jumps
    - x-axis  
    - y-axis 
    - z-axis 
- 0_get_data_sensONE.py  

## Calibration approach 1: Known mass and orientation
For this approach, a known mass was used, attached to the 3D printed sensor using a jig, and the FTS was attached to a UR3e robotic arm to know the orientation.

Each **Python script** has an explanation of what it does at the top of the file.
They are chronologically ordered from 1 to 5:  

* 1_get_data_centered_mass.py
* 1_get_data_offcentered_mass.py
* 2_merge_data.py
* 2_plot_data.py
* 2_s_plot_data.py
* 3_linearization.py
* 3_linearization_quadratic.py
* 4_validation.py
* 4_validation_quadratic.py
* 5_read_calibrated_values.py
* 5_read_calibrated_values_quadratic.py

**Final results** are saved in the next folder:  
* Datasets
  * 12_final_extra_bounded
    * data  
    * results 
    * train  
    * val  
    * description.txt

## Future work
All the scripts can be put together in one file that makes the entire calibration, communicating with the UR3e to move it and get the orientation at each timestep. This can be done using ROS.
 

