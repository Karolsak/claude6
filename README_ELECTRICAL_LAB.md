# Advanced Electrical Engineering Laboratory

A comprehensive Python application with Tkinter GUI for electrical engineering analysis, including tariff calculations, equipment cost analysis, and dynamic machine simulations.

## Features

### 1. **Tariff Calculator (Example 50.74)**
   - Compares two electricity tariff structures
   - Calculates break-even point for domestic power consumption
   - Visual cost comparison charts
   - Detailed analysis and recommendations

### 2. **Equipment Cost Analyzer (Example 50.75)**
   - Analyzes transformer and motor costs
   - Compares LT system (Transformer + LT Motor) vs HT Motor
   - Calculates economic equivalence point
   - Considers efficiency, load factor, and operating costs

### 3. **DC Motor Dynamic Simulation**
   - Real-time simulation of DC motor dynamics
   - Differential equations for armature current and angular velocity
   - Interactive parameter adjustment with sliders
   - Multiple solver options: RK45 (Runge-Kutta) and Euler
   - Visualizes: Current, Speed, Torque, and Power

### 4. **Induction Motor Simulation**
   - Simplified induction motor model
   - Speed and slip analysis
   - Synchronous speed comparison
   - Torque-speed characteristics

### 5. **RLC Circuit Analysis**
   - Dynamic RLC circuit simulation
   - Resonance frequency calculator
   - Quality factor and damping analysis
   - Phase portrait visualization
   - AC/DC source support

## Technical Features

### ODE Solvers
- **RK45 (Runge-Kutta 4th/5th order)**: High accuracy adaptive method
- **Euler Method**: Simple first-order method for comparison

### GUI Features
- Multi-tab interface for organized access
- Real-time parameter adjustment with sliders
- Interactive matplotlib plots embedded in Tkinter
- Auto-scaling on window resize
- Start/Stop/Reset controls for simulations
- Export functionality for results
- Professional status bar

### Mathematical Models

#### DC Motor Equations:
```
di_a/dt = (V - R_a*i_a - K_e*ω) / L_a
dω/dt = (K_t*i_a - B*ω - T_load) / J
```

#### Induction Motor (Simplified):
```
s = (ω_s - ω) / ω_s
T_e = (P * V² * R_r/s) / (ω_s * ((R_s + R_r/s)² + (X_s + X_r)²))
dω/dt = (T_e - T_load) / J
```

#### RLC Circuit:
```
di/dt = (V - R*i - v_c) / L
dv_c/dt = i / C
```

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually comes with Python)

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install numpy matplotlib
```

### For Ubuntu/Debian (if tkinter is missing):
```bash
sudo apt-get install python3-tk
```

### For macOS:
```bash
brew install python-tk
```

## Usage

### Run the Application
```bash
python3 electrical_engineering_lab.py
```

### Example 50.74 - Tariff Calculator
1. Navigate to "Tariff Calculator" tab
2. Enter annual rateable value (default: Rs 2,500)
3. Enter monthly lighting consumption (default: 40 units)
4. Adjust power consumption slider
5. Click "Calculate Break-Even Point"
6. View detailed analysis and cost comparison chart

**Problem Statement**: A supply undertaking offers two tariffs:
- **Tariff A**: Lighting: 20 paise/unit; Power: 5 paise/unit; Meter rent: 30 paise/month
- **Tariff B**: 12% on rateable value + 3 paise/unit for all purposes

**Solution**: The application calculates the domestic power consumption where both tariffs are equal.

### Example 50.75 - Equipment Analysis
1. Navigate to "Equipment Analysis" tab
2. Enter equipment parameters:
   - Transformer price: Rs 12/kVA
   - LT Motor price: Rs 24/kW
   - Efficiencies: Transformer 98%, LT Motor 90%, HT Motor 89%
   - Load factor: 30%
   - Energy cost: 7 paise/kWh
   - Interest rate: 8%
3. Click "Calculate HT Motor Price"
4. View detailed economic analysis

**Problem Statement**: Determine the maximum price per kW for HT motors to be economically equivalent to LT system.

### DC Motor Simulation
1. Navigate to "DC Motor Dynamics" tab
2. Adjust motor parameters using sliders:
   - Applied Voltage
   - Armature Resistance & Inductance
   - Back EMF and Torque Constants
   - Moment of Inertia
   - Friction Coefficient
   - Load Torque
3. Select solver method (RK45 or Euler)
4. Set time step and simulation duration
5. Click "Start" to run simulation
6. View real-time plots of current, speed, torque, and power

### Induction Motor Simulation
1. Navigate to "Induction Motor" tab
2. Set parameters: Voltage, Frequency, Poles, Resistances, Reactances
3. Click "Start" to simulate motor startup
4. Observe speed vs time and slip characteristics

### RLC Circuit Analysis
1. Navigate to "RLC Circuit" tab
2. Set circuit parameters: Voltage, R, L, C, Frequency
3. Click "Calculate Resonance" for frequency analysis
4. Click "Start" to simulate circuit response
5. View current, voltages, and phase portrait

## Application Structure

```
electrical_engineering_lab.py
├── ODESolver class
│   ├── euler() - Euler method solver
│   └── rk45() - Runge-Kutta solver
├── ElectricalMachineModels class
│   ├── dc_motor_dynamics()
│   ├── induction_motor_simplified()
│   └── rlc_circuit()
├── TariffCalculator class (Example 50.74)
│   ├── calculate_equal_consumption()
│   └── compare_tariffs()
├── EquipmentCostAnalyzer class (Example 50.75)
│   └── calculate_ht_motor_price()
└── ElectricalEngineeringLab (Main GUI)
    ├── create_tariff_tab()
    ├── create_equipment_tab()
    ├── create_dc_motor_tab()
    ├── create_induction_motor_tab()
    └── create_rlc_circuit_tab()
```

## Menu Options

### File Menu
- **Export Results**: Save analysis to text file with timestamp
- **Exit**: Close application

### Tools Menu
- **Clear All**: Clear all results and plots
- **Reset Simulation**: Stop and reset all simulations

### Help Menu
- **About**: Application information

## Advanced Features

### Auto-Scaling
- All plots automatically resize with window
- Responsive layout adjusts to screen size

### Real-Time Control
- Sliders provide immediate parameter feedback
- Start/Stop controls for simulations
- Reset functionality for clean restart

### Data Export
- Export results to timestamped text files
- Includes all calculations and analysis

## Practical Applications

1. **Utility Companies**: Tariff structure optimization
2. **Industrial Plants**: Equipment procurement decisions
3. **Educational**: Understanding motor dynamics and circuit behavior
4. **Research**: Testing control algorithms and system responses
5. **Design**: Sizing electrical equipment and systems

## Numerical Methods

### RK45 (Recommended)
- 4th order accuracy
- Excellent stability
- Suitable for stiff systems
- Default method for most simulations

### Euler Method
- 1st order accuracy
- Simple and fast
- Good for educational comparison
- May require smaller time steps

## Solutions to Examples

### Example 50.74 Solution
**Given**: Rateable value = Rs 2,500, Lighting = 40 units/month

**Calculation**:
- Tariff B monthly fixed = (0.12 × 2500) / 12 = Rs 25
- Setting costs equal: 8 + 0.05x + 0.30 = 25 + 0.03(40 + x)
- Solving: x = 895 units

**Answer**: 895 units of domestic power makes both tariffs equal.

### Example 50.75 Solution
**Given**: Transformer: Rs 12/kVA at 98% efficiency
         LT Motor: Rs 24/kW at 90% efficiency
         HT Motor: 89% efficiency, Load factor: 30%
         Energy: 7 paise/kWh, Interest: 8%

**Calculation**:
- LT system capital cost/kW = Rs 36.51
- Annual energy costs calculated
- HT motor price for equivalence: Rs 27.30/kW

**Answer**: Maximum Rs 27.30 per kW for HT motor.

## Troubleshooting

### Import Errors
If you get "ModuleNotFoundError":
```bash
pip install numpy matplotlib
```

For tkinter on Linux:
```bash
sudo apt-get install python3-tk
```

### Display Issues
- Ensure your system supports GUI applications
- Try adjusting window size for better visualization
- Check display resolution settings

### Performance
- Reduce time step for faster simulation
- Use Euler method for quick results
- Close other resource-intensive applications

## Future Enhancements

Potential additions:
- Synchronous machine models
- Power system load flow
- Transformer thermal analysis
- Power factor correction studies
- Harmonic analysis
- Protection coordination

## License

This application is provided for educational and engineering analysis purposes.

## Author

Created for comprehensive electrical engineering education and analysis.

## Version History

- **v1.0**: Initial release with full functionality
  - Tariff calculator
  - Equipment analyzer
  - DC motor simulation
  - Induction motor simulation
  - RLC circuit analysis
  - Multiple ODE solvers
  - Auto-scaling GUI

## Support

For issues or questions, refer to the inline documentation and comments in the source code.
