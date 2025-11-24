# Advanced Alternator Impedance Calculation Lab

## Overview
A comprehensive Python + Tkinter application for electrical engineering education, specifically designed to solve alternator impedance problems with dynamic simulation and advanced visualization.

## Features

### 1. **Problem Solving**
- **Problem 9.15**: Calculates synchronous impedance, reactance, and no-load voltage for lagging power factor
- **Problem 9.16**: Calculates parameters for leading power factor
- **Custom Mode**: Allows manual parameter adjustment for any alternator configuration

### 2. **User Interface**
- **Main Menu**: Quick access to predefined problems and custom calculations
- **Parameter Controls**: Interactive sliders with real-time value display
- **Organized Tabs**:
  - Parameters (input settings)
  - Simulation (solver configuration)
  - Results (calculated values)

### 3. **Calculation Modules**

#### Mathematical Models:
```python
# Synchronous Impedance
Zs = Eoc / Isc

# Synchronous Reactance
Xs = √(Zs² - Ra²)

# No-Load Voltage (Phasor Equation)
E = Vt + Ia(Ra + jXs)
```

#### Dynamic Simulation:
- **Euler Method**: Fixed time-step integration for first-order electrical dynamics
- **RK45 Method**: Adaptive Runge-Kutta solver for accurate transient analysis
- **ODE Model**: Simulates current buildup and voltage dynamics

### 4. **Visualization**

#### Phasor Diagram
- Terminal voltage (Vt)
- Armature current (Ia)
- Voltage drops (IRa, jIXs)
- Internal EMF (E)
- Phase relationships

#### Time Domain Plots
- Voltage transient response
- Current buildup
- Power variation

#### Operating Characteristics
- V-I characteristics for different power factors
- Power-Current curves
- Efficiency curve
- Voltage regulation

### 5. **Control Features**
- **Start**: Begin dynamic simulation
- **Stop**: Halt running simulation
- **Reset**: Clear all simulation data
- **Calculate**: Compute steady-state values

## Installation

### Requirements
```bash
pip install numpy matplotlib scipy
```

### Standard Library (included):
- tkinter
- threading
- time
- cmath

## Usage

### Running the Lab
```bash
python3 alternator_impedance_lab.py
```

### Solving Problem 9.15
1. Click **"Problem 9.15"** button in menu
2. View auto-populated parameters:
   - Ra = 0.15 Ω
   - Eoc = 60 V
   - Isc = 150 A
   - Vt = 200 V
   - Ia = 90 A
   - pf = 0.8 lagging
3. Click **"Calculate"** to see results
4. Check **"Results"** tab for detailed values

**Expected Results:**
- Synchronous Impedance (Zs): 0.4000 Ω
- Synchronous Reactance (Xs): 0.3708 Ω
- No-Load Voltage (E): ~229.5 V
- Load Angle: ~17.8°

### Solving Problem 9.16
1. Click **"Problem 9.16"** button
2. Auto-populated parameters:
   - Ra = 0.35 Ω
   - Eoc = 500 V
   - Isc = 180 A
   - Vt = 220 V
   - Ia = 60 A
   - pf = 0.85 leading
3. Click **"Calculate"**

**Expected Results:**
- Synchronous Impedance (Zs): 2.7778 Ω
- Synchronous Reactance (Xs): 2.7556 Ω
- No-Load Voltage (E): ~189 V (lower due to leading power factor)

### Custom Calculations
1. Click **"Custom"** button
2. Adjust sliders or type values:
   - Armature Resistance (Ra)
   - Open Circuit Voltage (Eoc)
   - Short Circuit Current (Isc)
   - Terminal Voltage (Vt)
   - Armature Current (Ia)
   - Power Factor (pf)
   - Frequency
3. Select **"Lagging"** or **"Leading"** power factor
4. Click **"Calculate"**

### Running Dynamic Simulation
1. Load a problem or set custom parameters
2. Go to **"Simulation"** tab
3. Select solver:
   - **RK45**: More accurate, adaptive step size
   - **Euler**: Faster, fixed step size
4. Set simulation time (0.1 - 5.0 seconds)
5. Click **"Start Simulation"**
6. Watch **"Time Domain"** tab for transient response
7. Click **"Stop"** to halt or **"Reset"** to clear

## Technical Details

### Phasor Analysis
The lab uses complex number arithmetic to perform phasor calculations:

```python
# Reference: Terminal voltage
Vt_complex = Vt + j0

# Current with power factor angle
Ia_complex = Ia ∠ -φ

# Voltage drops
Z_complex = Ra + jXs
Voltage_drop = Ia_complex × Z_complex

# Internal EMF
E = Vt + Voltage_drop
```

### Differential Equations
First-order electrical dynamics:

```
dI/dt = (I_target - I) / τ

where τ = Xs / (ω × Ra)
```

### Solver Comparison
- **Euler**: `I(t+Δt) = I(t) + (dI/dt)×Δt`
- **RK45**: Adaptive 4th-5th order Runge-Kutta with error control

## Advanced Features

### Auto-Scaling
- Window resize automatically adjusts plot sizes
- Maintains aspect ratio for phasor diagrams
- Optimizes layout for all screen sizes

### Real-Time Updates
- Simulation runs in background thread
- Non-blocking GUI during computation
- Progress visible in time-domain plots

### Professional Visualizations
- Multiple synchronized plots
- Color-coded phasors
- Grid overlays
- Legend annotations
- Tight layout optimization

## Practical Applications

### Educational Use
- Understanding synchronous machine behavior
- Visualizing phasor relationships
- Comparing lagging vs leading power factor effects
- Analyzing voltage regulation

### Engineering Analysis
- Parameter sensitivity studies
- Operating point determination
- Stability margin assessment
- Design validation

## Problem Solutions Explained

### Problem 9.15 Analysis
Given an alternator with:
- Low armature resistance (0.15 Ω)
- Moderate short-circuit capability (150 A)
- Operating at lagging power factor (0.8)

The **lagging current** requires higher excitation voltage because reactive power is absorbed by the load. The phasor diagram shows:
- Voltage drops add constructively with terminal voltage
- Internal EMF is significantly higher than terminal voltage
- Larger load angle indicates more electromagnetic torque

### Problem 9.16 Analysis
Leading power factor scenario:
- Higher armature resistance (0.35 Ω)
- Better short-circuit rating (180 A)
- Leading power factor (0.85)

The **leading current** provides reactive power support:
- Voltage drops partially cancel terminal voltage
- Internal EMF can be lower than terminal voltage
- Smaller load angle indicates easier synchronization
- Better voltage regulation

## Troubleshooting

### Import Errors
If matplotlib or scipy not found:
```bash
pip3 install matplotlib scipy numpy
```

### Tkinter Not Available
On Linux:
```bash
sudo apt-get install python3-tk
```

### Simulation Not Starting
- Check that parameters are within valid ranges
- Ensure no other simulation is running
- Click "Reset" and try again

## Future Enhancements
- 3D visualization of operating surfaces
- Multi-machine parallel operation
- Fault analysis capabilities
- Export results to CSV/PDF
- Animation of rotating phasors

## Author
Created for advanced electrical engineering education

## License
Educational use - Open Source

---

**Note**: This lab combines theoretical calculations with practical visualization to provide comprehensive understanding of alternator behavior under various operating conditions.
