# Advanced Electrical Engineering Analysis Tool

A comprehensive Python application for power factor correction analysis and induction motor dynamics simulation.

## Features

### 1. Power Factor Correction Calculator
- **Billing Analysis**: Calculate savings from power factor improvement
- **Economic Evaluation**: Determine payback period for capacitor investment
- **Visual Comparison**: Side-by-side power triangle visualization
- **Interactive Controls**: Real-time parameter adjustment with sliders

### 2. Motor Dynamics Simulation
- **Real-time ODE Solver**: Choose between RK45 (adaptive) and Euler (fixed-step) methods
- **Comprehensive Visualization**:
  - Rotor speed vs time
  - Electromagnetic torque dynamics
  - Stator and rotor currents (d-q components)
  - Phase portraits (torque-speed curves)
- **Adjustable Parameters**:
  - Motor electrical parameters (resistances, inductances)
  - Mechanical parameters (inertia, friction)
  - Operating conditions (voltage, frequency, load)

## Installation

### Requirements
```bash
pip install numpy scipy matplotlib
```

### Running the Application
```bash
python3 power_factor_calculator.py
```

## Usage Guide

### Power Factor Correction Tab

1. **Input Parameters**:
   - Voltage (V): System voltage level
   - Power Rate (Rs/kVA/month): Monthly billing rate
   - Original Power Factor: Current power factor (0-1)
   - Original Demand (kVA): Current apparent power demand
   - Capacitor Rating (kVAR): Reactive power compensation
   - Installation Cost (Rs): Capital investment
   - Fixed Charges Rate (%): Annual maintenance/depreciation

2. **Actions**:
   - Click **Calculate** to analyze savings
   - Click **Reset** to restore default values

3. **Results**:
   - Detailed financial analysis
   - Power factor improvement metrics
   - Payback period calculation
   - Visual power triangle comparison

### Motor Dynamics Simulation Tab

1. **Motor Parameters**:
   - **Electrical**: Stator/rotor resistances (Rs, Rr), inductances (Ls, Lr, Lm)
   - **Mechanical**: Moment of inertia (J), friction coefficient (B)
   - **Operating**: Supply voltage (Vs), frequency, load torque

2. **Simulation Controls**:
   - **Solver Method**:
     - RK45: High accuracy, adaptive step size
     - Euler: Educational, fixed step size
   - **Simulation Time**: Duration in seconds

3. **Actions**:
   - Click **▶ Start** to run simulation
   - Click **⏸ Stop** to halt simulation
   - Click **↻ Reset** to restore defaults

4. **Results**:
   - Real-time plots of motor behavior
   - Transient response analysis
   - Current waveforms
   - Dynamic torque-speed characteristics

## Problem Solved

### Example: Mill Power Factor Correction

**Given**:
- Three-phase 50 Hz power supply
- Voltage: 460V
- Monthly power rate: Rs. 7.50/kVA
- Original power factor: 0.745
- Monthly demand: 611 kVA
- Capacitor installation: 210 kVAR
- Installation cost: Rs. 11,600
- Fixed charges: 15% per year

**Solution**:
The application calculates:
- **Original System**: 611 kVA @ 0.745 PF
  - Real Power: 455.2 kW
  - Reactive Power: 407.5 kVAR
  - Monthly Cost: Rs. 4,582.50

- **Improved System**: 485.6 kVA @ 0.937 PF
  - Real Power: 455.2 kW (unchanged)
  - Reactive Power: 197.5 kVAR
  - Monthly Cost: Rs. 3,642.00

- **Financial Analysis**:
  - Monthly Savings: Rs. 940.50
  - Yearly Savings: Rs. 11,286.00
  - Annual Fixed Charges: Rs. 1,740.00
  - **NET YEARLY SAVINGS: Rs. 9,546.00**
  - **Payback Period: 1.03 years**

## Technical Details

### Mathematical Models

#### Power Factor Correction
```
kW = kVA × PF
kVAR = kVA × sin(acos(PF))
New kVA = √(kW² + (kVAR - Qc)²)
New PF = kW / New kVA
```

#### Induction Motor Dynamics (d-q Model)
```
State variables: [ids, iqs, idr, iqr, ω]

dids/dt = (Vds - Rs·ids - Lm·(Rr·idr/Lr)) / Lσs
diqs/dt = (Vqs - Rs·iqs - Lm·(Rr·iqr/Lr)) / Lσs
didr/dt = (Lm·Rs·ids/Ls - Rr·idr - (ωs-ω)·Lr·iqr) / Lσr
diqr/dt = (Lm·Rs·iqs/Ls - Rr·iqr + (ωs-ω)·Lr·idr) / Lσr
dω/dt = (Te - TL - B·ω) / J

Te = (3/2)·P·Lm·(iqs·idr - ids·iqr)
```

### ODE Solvers

**RK45 (Runge-Kutta-Fehlberg)**:
- Adaptive step size control
- 4th/5th order accuracy
- Error estimation
- Optimal for stiff systems

**Euler Method**:
- Fixed step size (dt = 0.0001s)
- 1st order accuracy
- Simple implementation
- Educational purposes

## Features Implemented

✅ **User Interface**:
- Professional Tkinter GUI with tabs
- Input parameter sliders with real-time updates
- Control buttons (Start, Stop, Reset)
- Responsive design with auto-scaling

✅ **Calculations**:
- Power factor correction economics
- Dynamic motor simulation
- Differential equation solving
- Real-time numerical integration

✅ **Visualization**:
- Matplotlib integration
- Multiple synchronized plots
- Power triangle diagrams
- Dynamic waveforms
- Phase portraits

✅ **Advanced Features**:
- Multi-threaded simulation
- Automatic window resizing
- Professional styling
- Comprehensive error handling
- Educational documentation

## Applications

- **Industrial Power Systems**: Optimize power factor for billing reduction
- **Motor Analysis**: Study transient behavior and starting characteristics
- **Educational**: Learn differential equations and numerical methods
- **Design**: Size capacitors and analyze motor performance
- **Research**: Experiment with different parameters and configurations

## Version

**Version 1.0** - Complete implementation with all requested features

## License

Educational and professional use in electrical engineering.

---

**Created for**: Advanced electrical engineering analysis and education
**Technologies**: Python, Tkinter, NumPy, SciPy, Matplotlib
