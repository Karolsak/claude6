# Advanced Electrical Engineering Lab

## Overview

This comprehensive Python application combines power factor correction analysis with dynamic electrical machine simulations. It features a professional Tkinter GUI with real-time visualization and ODE solvers.

## Features

### 1. Power Factor Correction Calculator
Solves the practical problem:
- **Problem Statement**: A system working at maximum kVA capacity with lagging power factor of 0.71. Analyze two options for meeting increased load:
  - (i) Raising power factor to 0.87 using phase advancers
  - (ii) Installing extra generating plant
- **Calculations Include**:
  - Real and reactive power analysis
  - kVAr compensation requirements
  - Limiting cost per kVA of phase advancing plant
  - Annual cost comparison
  - Economic justification analysis

### 2. Synchronous Machine Dynamic Simulation
- **State Variables**: Rotor angle (δ), angular velocity (ω), transient EMFs (E'q, E'd), stator currents (id, iq)
- **Features**:
  - Swing equation dynamics
  - Transient stability analysis
  - Phase plane trajectories
  - Power balance visualization
  - Adjustable inertia, damping, excitation, and mechanical power

### 3. Induction Motor Dynamic Simulation
- **State Variables**: Rotor speed (ω), stator currents (iqs, ids), rotor currents (iqr, idr)
- **Features**:
  - Starting transients
  - Speed-torque characteristics
  - Current magnitude analysis
  - Electromagnetic torque dynamics
  - Adjustable voltage, load torque, resistance, and inertia

### 4. Advanced ODE Solvers
- **RK45 (Runge-Kutta-Fehlberg)**: Adaptive step-size, high accuracy
- **Euler Method**: Fixed step-size, educational comparison
- Real-time selection between solvers

### 5. GUI Features
- **Auto-scaling**: Responsive design with automatic width/height adjustment
- **Interactive Controls**: Sliders for real-time parameter adjustment
- **Start/Stop/Reset**: Full simulation control
- **Multi-tab Interface**: Organized modules for different analyses
- **Professional Visualization**:
  - Multiple synchronized plots
  - Power triangles
  - Phase plane diagrams
  - Time-domain responses
  - Cost comparisons

## Installation

### Prerequisites
```bash
pip install numpy scipy matplotlib tkinter
```

Note: tkinter usually comes with Python. If not:
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- Fedora: `sudo dnf install python3-tkinter`
- macOS: tkinter is included with Python

## Usage

### Running the Application
```bash
python3 power_factor_advanced_lab.py
```

### Power Factor Calculator Tab
1. Adjust parameters using sliders:
   - System Capacity (kVA)
   - Initial Power Factor
   - Final Power Factor
   - Generator Cost (Rs/kVA)
   - Interest Rate (%)
2. Click "Calculate" to see detailed analysis
3. View results in text panel and visualizations:
   - Power comparison charts
   - Cost analysis
   - Power triangles (before/after)

### Synchronous Machine Tab
1. Set machine parameters:
   - Inertia constant H
   - Damping coefficient D
   - Mechanical power Pm
   - Field voltage Efd
   - Simulation time
2. Select ODE solver (RK45 or Euler)
3. Click "Start" to run simulation
4. Observe dynamic responses:
   - Rotor angle oscillations
   - Speed deviations
   - Transient EMFs
   - Stator currents
   - Phase plane trajectory
   - Power balance

### Induction Motor Tab
1. Configure motor parameters:
   - Stator voltage Vqs
   - Load torque
   - Rotor resistance
   - Moment of inertia
   - Simulation time
2. Choose solver
3. Click "Start" to simulate
4. Analyze startup transients and steady-state operation

## Mathematical Models

### Power Factor Correction

Given:
- Initial PF = 0.71 (lagging)
- Final PF = 0.87
- Generator cost = Rs. 60/kVA
- Interest & depreciation = 1%

**Calculations**:

1. Real power increase:
   ```
   ΔP = S × (PF_final - PF_initial)
   ```

2. Reactive power compensation:
   ```
   ΔQ = S × (sin(φ_initial) - sin(φ_final))
   ```

3. Additional generating capacity needed:
   ```
   Additional_kVA = ΔP / PF_initial
   ```

4. Limiting cost of phase advancers:
   ```
   Cost_limit = (Gen_cost × Additional_kVA) / ΔQ
   ```

**Result**: Phase advancers are economical if cost ≤ Rs. 64.0/kVA (approximately)

### Synchronous Machine Dynamics

Differential equations:
```
dδ/dt = ω
dω/dt = (ωs/2H) × (Pm - Pe - D×ω)
dE'q/dt = (1/T'd0) × (Efd - E'q - (Xd - X'd)×id)
dE'd/dt = (1/T'q0) × (-E'd + (Xq - X'q)×iq)
```

Where:
- δ: Rotor angle
- ω: Speed deviation
- E'q, E'd: Transient EMFs
- H: Inertia constant
- D: Damping
- Pm, Pe: Mechanical and electrical power

### Induction Motor Dynamics

State equations in synchronous reference frame:
```
dω/dt = (1/J) × (Te - Tload - B×ω)
diqs/dt = f(Vqs, Rs, Ls, Lr, Lm, currents)
dids/dt = f(Vds, Rs, Ls, Lr, Lm, currents)
diqr/dt = f(Rotor parameters, slip)
didr/dt = f(Rotor parameters, slip)
```

Electromagnetic torque:
```
Te = (3P/4) × Lm × (idr×iqs - iqr×ids)
```

## Practical Applications

1. **Power Factor Correction**:
   - Economic analysis for industrial installations
   - Capacitor bank sizing
   - Phase advancer justification
   - Energy cost reduction studies

2. **Synchronous Machine Analysis**:
   - Transient stability studies
   - Fault analysis
   - Excitation system design
   - Power system stabilizer tuning

3. **Induction Motor Analysis**:
   - Soft-starter design
   - Motor protection coordination
   - Load matching
   - Energy efficiency studies

## Technical Details

### ODE Solver Comparison

**RK45 (Recommended)**:
- Adaptive step size
- 4th/5th order accuracy
- Error control
- Faster for stiff systems

**Euler Method**:
- Fixed step size
- 1st order accuracy
- Educational value
- Simple implementation

### GUI Architecture

- **Auto-scaling**: Grid weights ensure proper resizing
- **Event-driven**: Responsive to user interactions
- **Modular design**: Separate tabs for different analyses
- **Professional styling**: Dark theme with color-coded plots

## Troubleshooting

### Import Errors
If you get matplotlib backend errors:
```python
# Add at the start of script if needed
import matplotlib
matplotlib.use('TkAgg')
```

### Display Issues
For high-DPI displays, set scaling:
```python
# Add in __init__ method
self.tk.call('tk', 'scaling', 2.0)
```

### Performance
- Use RK45 for accuracy
- Reduce simulation time for faster results
- Close unused tabs to save memory

## Example Problem Solution

**Given Problem**:
- System: 100 kVA, PF = 0.71 (lagging)
- Target: PF = 0.87
- Generator cost: Rs. 60/kVA
- Interest: 1%

**Solution**:
1. Real power at 0.71 PF: 71 kW
2. Real power at 0.87 PF: 87 kW
3. Additional power: 16 kW
4. kVAr compensation: 21.1 kVAr
5. Additional generator capacity: 22.5 kVA
6. **Limiting cost**: Rs. 64.0/kVA

**Conclusion**: If phase advancers cost ≤ Rs. 64/kVA, they are more economical than new generating plant.

## Author

Advanced Electrical Engineering Lab - Developed for practical electrical engineering education and analysis.

## License

Open source - Free for educational and commercial use.
