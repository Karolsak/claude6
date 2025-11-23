# DC Machine Analysis Laboratory - Advanced Engineering Tool

A comprehensive Python application with Tkinter GUI for analyzing DC generators and motors, featuring dynamic simulation capabilities with multiple ODE solvers.

## Features

### 1. **DC Compound Generator Analysis (Problem 7.9)**
- Calculate required series turns per pole for compound generators
- Interactive input parameters with sliders
- Open Circuit Characteristic (OCC) curve interpolation
- Comprehensive visualizations:
  - OCC with operating points
  - Load characteristics
  - Field ampere-turns distribution
  - Current distribution diagrams

### 2. **DC Shunt Motor Analysis (Problem 7.10)**
- Calculate full-load speed and developed torque
- Performance analysis with armature reaction effects
- Visualizations include:
  - Speed vs Load characteristic
  - Torque-Speed characteristic
  - Power distribution
  - Efficiency curves

### 3. **Dynamic Simulation Module**
- Real-time ODE solver simulation
- Multiple solver options:
  - **RK45** (Adaptive Runge-Kutta)
  - **Euler** (Fixed-step)
  - **RK4** (Fixed-step Runge-Kutta 4th order)
- Adjustable parameters via sliders:
  - Applied Voltage (0-500V)
  - Load Torque (0-200 Nm)
  - Moment of Inertia (0.01-10 kg·m²)
  - Armature Resistance (0.1-5 Ω)
  - Field Resistance (50-500 Ω)
  - Simulation Time (1-20 s)
- Real-time visualization of:
  - Motor speed response
  - Armature current
  - Motor torque
  - Developed power
- Performance metrics:
  - Rise time (10% to 90%)
  - Settling time
  - Peak overshoot
  - Steady-state error

### 4. **Advanced GUI Features**
- Multi-tab interface for organized workflow
- Automatic window scaling and responsive layout
- Interactive sliders with real-time value display
- Control buttons: Start, Stop, Reset
- High-quality matplotlib visualizations
- Detailed results with formatted output
- Thread-based simulation for non-blocking UI

## Problem Solutions

### Problem 7.9: DC Compound Generator
**Given:**
- 250 kW, 6-pole, lap-connected DC compound generator
- No-load voltage: 500V, Full-load voltage: 550V
- 1080 conductors, Armature resistance: 0.037Ω
- OCC data provided
- Shunt field resistance: 85Ω
- Armature reaction compensation: 10%

**Solution:** The application calculates the required number of series turns per pole using:
- Interpolation of OCC data
- Field ampere-turns calculations
- Armature reaction compensation
- Series field requirements for voltage regulation

### Problem 7.10: DC Shunt Motor
**Given:**
- 10 kW, 250V shunt motor
- Ra = 0.5Ω, Rf = 200Ω
- No-load: 1200 rpm, Ia = 3A
- Full-load: IL = 47A, flux reduced by 4%

**Solution:**
- (a) Full-load speed calculated using speed-flux relationship
- (b) Developed torque using power and angular velocity

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually comes with Python)

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install numpy>=1.21.0 matplotlib>=3.4.0 scipy>=1.7.0
```

### For Ubuntu/Debian (if tkinter is not installed):
```bash
sudo apt-get install python3-tk
```

### For macOS:
Tkinter should be included with Python installation from python.org

### For Windows:
Tkinter comes bundled with Python installation

## Usage

### Running the Application
```bash
python3 dc_machine_analysis_lab.py
```

### Using the Application

#### Tab 1: DC Compound Generator
1. Enter generator parameters in the input fields
2. Provide OCC data (voltage and field AT)
3. Click "Calculate Series Turns"
4. View results and visualizations

#### Tab 2: DC Shunt Motor
1. Enter motor parameters
2. Click "Calculate Motor Performance"
3. View full-load speed, torque, and efficiency
4. Analyze performance curves

#### Tab 3: Dynamic Simulation
1. Select machine type (DC Motor/Generator)
2. Choose ODE solver (RK45/Euler/RK4)
3. Adjust parameters using sliders
4. Click "▶ Start" to run simulation
5. Click "■ Stop" to pause
6. Click "↻ Reset" to clear results
7. View real-time plots and performance metrics

## Technical Details

### Mathematical Models

#### DC Motor Dynamics
The application solves the following differential equations:

**Electrical equation:**
```
L * (di_a/dt) = V - E_b - i_a * R_a
```

**Mechanical equation:**
```
J * (dω/dt) = T_motor - T_load - B * ω
```

Where:
- `i_a`: Armature current
- `ω`: Angular velocity
- `V`: Applied voltage
- `E_b`: Back EMF = K_e * ω
- `T_motor`: Motor torque = K_t * i_a
- `J`: Moment of inertia
- `B`: Friction coefficient
- `R_a`: Armature resistance
- `L`: Armature inductance

### ODE Solvers

1. **RK45 (Runge-Kutta-Fehlberg)**: Adaptive step-size method with 4th and 5th order accuracy
2. **Euler Method**: Simple first-order fixed-step method
3. **RK4 Method**: Classical 4th order Runge-Kutta fixed-step method

### Visualization Features
- Multiple synchronized plots
- Grid overlay for easy reading
- Color-coded operating points
- Legend annotations
- Auto-scaling axes
- Professional formatting

## Code Structure

```
dc_machine_analysis_lab.py
├── DCMachineLabApp (Main Class)
│   ├── __init__: Initialize GUI components
│   ├── create_compound_generator_tab: Generator analysis interface
│   ├── create_shunt_motor_tab: Motor analysis interface
│   ├── create_dynamic_simulation_tab: Simulation interface
│   ├── calculate_compound_generator: Problem 7.9 solver
│   ├── calculate_shunt_motor: Problem 7.10 solver
│   ├── run_simulation: Dynamic simulation engine
│   ├── update_simulation_plot: Real-time visualization
│   └── Performance metric calculators
```

## Features Highlights

✓ Comprehensive electrical engineering calculations
✓ Multiple ODE solvers for dynamic analysis
✓ Real-time interactive visualization
✓ Responsive auto-scaling GUI
✓ Thread-based non-blocking simulations
✓ Professional engineering formatting
✓ Detailed performance metrics
✓ Error handling and validation
✓ Educational tool for electrical engineering students
✓ Practical for motor/generator design analysis

## Performance Metrics Calculated

- **Rise Time**: Time taken for response to go from 10% to 90% of final value
- **Settling Time**: Time for response to settle within 2% of final value
- **Peak Overshoot**: Maximum overshoot as percentage of final value
- **Steady-State Error**: Error between desired and actual final values

## Applications

This tool is useful for:
- Electrical engineering education
- DC machine design and analysis
- Control system verification
- Performance prediction
- Parameter optimization
- Transient response analysis
- Research and development

## Notes

- All calculations use SI units
- Interpolation uses cubic splines for smooth curves
- Thread-safe GUI updates
- Automatic resource cleanup
- Comprehensive error handling

## License

This educational tool is provided for electrical engineering analysis and learning purposes.

## Author

Created as a comprehensive solution for DC machine analysis problems 7.9 and 7.10 with advanced simulation capabilities.
