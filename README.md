# Fleet-Managment-Spatial-Data-Imputation


## Description
This project aims to enhance vehicle tracking accuracy in scenarios of GPS signal loss through the application of spatial data imputation techniques. By integrating dead reckoning and Hidden Markov Model (HMM) map matching, the system reliably generates vehicle position points even in the absence of GPS data. The map matching functionality is implemented using the GraphHopper API. This repository includes all the code, documentation, and additional resources needed to comprehend and implement the proposed solution.

## Features
- **Dead Reckoning Implementation:** Utilizes vehicle sensor data to estimate the position when GPS is unavailable.
- **HMM Map Matching:** Enhances the accuracy of the estimated positions by aligning them to a digital map using a probabilistic model.
- **Data Simulation:** Includes scripts for simulating vehicle movement and signal loss scenarios.
- **Visualization Tools:** Tools to visualize vehicle tracks and compare performance of different imputation methods.

## Installation

To get started with this project, clone this repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/vehicle-positioning-system.git
cd vehicle-positioning-system
pip install -r requirements.txt
