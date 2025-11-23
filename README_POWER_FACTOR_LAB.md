# Advanced Electrical Engineering Laboratory

A comprehensive Python + Tkinter application for electrical engineering calculations and dynamic simulations.

## Features

### 1. ★ Generator Station Power Factor Problem (NEW!)
Solves the generator station power factor problem with:
- **Problem Statement**: Calculate the required power factor of a rotary converter to achieve unity power factor at the generator station
- **Given Loads**:
  - Lighting: 100 kW
  - Induction Motor: 400 HP (298.4 kW), PF = 0.8, Efficiency = 0.92
  - Rotary Converter: 800V, 100A, Efficiency = 0.94
- **Solution**: Required PF = **0.3302 (leading)**
- **Features**:
  - Step-by-step mathematical solution
  - Interactive parameter adjustment with sliders
  - Power triangle diagrams for each load
  - Real-time visualization
  - Comprehensive verification

### 2. Tariff Calculator (Example 50.74)
Compares two electricity tariff structures:
- Tariff A: Separate rates for lighting and power with meter rent
- Tariff B: Fixed charge based on rateable value plus per-unit charge
- Calculates break-even consumption point
- Visual cost comparison graphs

### 3. Equipment Cost Analyzer (Example 50.75)
Economic analysis of HT vs LT motor systems:
- Compares transformer + LT motor vs direct HT motor
- Considers capital costs and energy consumption
- Calculates maximum economical price for HT motor
- Detailed cost breakdown and analysis

### 4. DC Motor Dynamic Simulation
Real-time simulation of DC motor behavior:
- Differential equation solver (Euler & RK45 methods)
- Adjustable parameters: voltage, resistance, inductance, torque constant, etc.
- Real-time load torque and voltage control via sliders
- Visualization of:
  - Armature current
  - Motor speed (RPM)
  - Electromagnetic torque
  - Mechanical power

### 5. Induction Motor Simulation
Three-phase induction motor analysis:
- Simplified dynamic model
- Slip calculation
- Speed vs time response
- Torque characteristics
- Adjustable motor parameters

### 6. RLC Circuit Transient Analysis
Series RLC circuit simulation:
- Transient response analysis
- Resonance frequency calculation
- Quality factor (Q) and damping ratio
- Phase portrait visualization
- Component voltage analysis

## Mathematical Foundation

### Generator Station Power Factor Problem

**Step 1: Lighting Load Analysis**
```
P_lighting = 100 kW
Q_lighting = 0 kVAR (unity power factor)
```

**Step 2: Induction Motor Analysis**
```
Motor Output = 400 HP × 0.746 = 298.4 kW
Motor Input = 298.4 / 0.92 = 324.35 kW
Apparent Power = 324.35 / 0.8 = 405.43 kVA
Reactive Power = 405.43 × sin(arccos(0.8)) = 243.26 kVAR (lagging)
```

**Step 3: Rotary Converter Analysis**
```
Converter Output = 800V × 100A / 1000 = 80 kW
Converter Input = 80 / 0.94 = 85.11 kW
```

**Step 4: Unity Power Factor Requirement**
```
For Unity PF at station: Q_total = 0
Q_converter = -(Q_lighting + Q_motor)
Q_converter = -(0 + 243.26) = -243.26 kVAR (leading)
```

**Step 5: Converter Power Factor**
```
S_converter = √(85.11² + (-243.26)²) = 257.72 kVA
PF_converter = 85.11 / 257.72 = 0.3302 (leading)
```

## ODE Solvers

### Euler Method
Simple first-order method:
```python
y[i+1] = y[i] + h × f(t[i], y[i])
```

### Runge-Kutta 4th Order (RK45)
Higher accuracy method:
```python
k1 = f(t, y)
k2 = f(t + h/2, y + h×k1/2)
k3 = f(t + h/2, y + h×k2/2)
k4 = f(t + h, y + h×k3)
y[i+1] = y[i] + (h/6) × (k1 + 2×k2 + 2×k3 + k4)
```

## Requirements

### Python Dependencies
```bash
pip install numpy matplotlib
```

### System Requirements
- Python 3.6+
- Tkinter (usually included with Python)
- NumPy
- Matplotlib

## Installation & Usage

### Option 1: Run the Full GUI Application
```bash
python3 electrical_engineering_lab.py
```

### Option 2: Run the Power Factor Test (CLI)
```bash
python3 test_power_factor.py
```

## Application Structure

```
electrical_engineering_lab.py
│
├── ODESolver
│   ├── euler()         # Euler method solver
│   └── rk45()          # Runge-Kutta solver
│
├── ElectricalMachineModels
│   ├── dc_motor_dynamics()
│   ├── induction_motor_simplified()
│   └── rlc_circuit()
│
├── GeneratorStationPFCalculator
│   └── calculate_rotary_converter_pf()
│
├── TariffCalculator
│   ├── calculate_equal_consumption()
│   └── compare_tariffs()
│
├── EquipmentCostAnalyzer
│   └── calculate_ht_motor_price()
│
└── ElectricalEngineeringLab (Main GUI)
    ├── create_generator_pf_tab()
    ├── create_tariff_tab()
    ├── create_equipment_tab()
    ├── create_dc_motor_tab()
    ├── create_induction_motor_tab()
    └── create_rlc_circuit_tab()
```

## GUI Features

### Interactive Controls
- **Sliders**: Real-time parameter adjustment
- **Entry Fields**: Precise value input
- **Start/Stop/Reset**: Simulation control
- **Auto-scaling**: Responsive window resizing

### Visualization
- **Power Triangles**: Visual representation of P, Q, S
- **Time-domain Plots**: Dynamic response curves
- **Phase Portraits**: State-space visualization
- **Comparison Charts**: Cost and performance analysis

### Results Display
- **Detailed Solutions**: Step-by-step calculations
- **Formatted Output**: Professional report generation
- **Export Functionality**: Save results to text files

## Example Problems Solved

### Generator Station Power Factor
**Given**: Lighting (100 kW), Motor (400 HP, PF=0.8, eff=0.92), Converter (800V, 100A, eff=0.94)
**Find**: Converter PF for unity station PF
**Answer**: **0.3302 leading**

### Tariff Comparison (Example 50.74)
**Given**: Rateable value Rs 2500, Lighting 40 units/month
**Find**: Domestic power consumption for equal tariff costs
**Answer**: Break-even point calculation with cost graphs

### Equipment Analysis (Example 50.75)
**Given**: Transformer (Rs 12/kVA, 98% eff), LT Motor (Rs 24/kW, 90% eff)
**Find**: Maximum HT motor price for economic parity
**Answer**: Detailed cost-benefit analysis

## Advanced Features

### Real-time Dynamic Simulation
- Continuous parameter updates during simulation
- Immediate visual feedback
- Multiple solver options for accuracy vs speed

### Auto-scaling Graphics
- Window resize handling
- Automatic plot rescaling
- Responsive layout

### Educational Value
- Step-by-step solutions
- Visual learning aids
- Multiple test cases
- Verification checks

## Technical Specifications

### DC Motor Model
```
di/dt = (V - R×i - K_e×ω) / L
dω/dt = (K_t×i - B×ω - T_L) / J
```

### Induction Motor Model (Simplified)
```
s = (ω_s - ω) / ω_s
T = (3×P×V²×R_r/s) / (ω_s×((R_s + R_r/s)² + (X_s + X_r)²))
dω/dt = (T - T_L) / J
```

### RLC Circuit Model
```
di/dt = (V - R×i - v_c) / L
dv_c/dt = i / C
```

## Testing

The application includes comprehensive testing:
```bash
python3 test_power_factor.py
```

This validates:
- Power factor calculations
- Unity PF verification
- Multiple test cases
- Numerical accuracy

## Output Examples

### Console Output
```
================================================================================
★ REQUIRED POWER FACTOR OF ROTARY CONVERTER: 0.330230 (leading)
================================================================================

VERIFICATION:
  Total Real Power (P):       509.4542 kW
  Total Reactive Power (Q):   0.0000 kVAR
  Station Power Factor:       1.0000 (Unity) ✓
```

### GUI Features
- 6 dedicated tabs for different calculations
- Interactive sliders for real-time parameter adjustment
- Professional formatted results
- Multiple synchronized visualizations
- Export to text files

## Practical Applications

### Educational Use
- Understanding power factor correction
- Learning motor dynamics
- Circuit transient analysis
- ODE solver comparison

### Engineering Analysis
- Generator station design
- Power system optimization
- Equipment selection
- Cost-benefit analysis

### Research & Development
- Algorithm testing
- Parameter sensitivity analysis
- Model validation
- Performance comparison

## Development

**Language**: Python 3
**GUI Framework**: Tkinter
**Plotting**: Matplotlib
**Numerical**: NumPy
**Architecture**: Object-oriented, modular design

## Author Notes

This comprehensive laboratory application combines:
- **Theoretical rigor**: Complete mathematical solutions
- **Practical utility**: Real-world engineering problems
- **Educational value**: Step-by-step explanations
- **Professional quality**: Publication-ready visualizations

All calculations have been verified against standard electrical engineering textbooks and industry practices.

## License

This software is provided for educational and professional engineering use.

## Version

**Version 1.0** - Advanced Electrical Engineering Laboratory with comprehensive power factor analysis

---

**For questions or issues, please refer to the inline code documentation.**
