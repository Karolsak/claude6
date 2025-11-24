# VVVF Inverter-Fed Three-Phase Induction Motor Laboratory

## Problem Solution

### Given Parameters:
- **Three-phase Y-connected cage induction motor**
  - Line-to-line voltage: 380 V
  - Frequency: 50 Hz
  - Speed: 1450 rpm
- **VVVF Inverter specifications**
  - Maximum input frequency: 50 Hz
  - Speed ratio (max:min): 10:1
- **Three-phase rectifier**
  - Input voltage: 380 V (three-phase)
  - Fully controlled (thyristor-based)

### Theoretical Solution:

#### 1. Maximum DC Link Voltage
For a fully controlled three-phase rectifier:
```
Vdc = (3√2/π) × VL × cos(α)
```

**Maximum DC voltage** occurs at firing angle α = 0°:
```
Vdc_max = (3√2/π) × 380 V = 513.37 V
α_max = 0°
```

#### 2. Minimum DC Link Voltage
**V/f ratio** (constant for VVVF control):
```
V/f = 380V / 50Hz = 7.6 V/Hz
```

**Minimum frequency** (from speed ratio 10:1):
```
f_min = 50Hz / 10 = 5 Hz
```

**Minimum voltage** (line-to-line RMS):
```
VL_min = 5 Hz × 7.6 V/Hz = 38 V
```

**Minimum DC voltage** (for Space Vector Modulation):
```
Vdc_min = √2 × VL_min = √2 × 38 V = 53.74 V
```

**Firing angle for minimum DC voltage**:
```
Vdc_min = Vdc_max × cos(α)
cos(α) = 53.74 / 513.37 = 0.1047
α_min = 84.0°
```

### Summary of Results:
| Parameter | Value |
|-----------|-------|
| **Maximum DC Voltage** | **513.37 V** |
| **Maximum Firing Angle** | **0°** |
| **Minimum DC Voltage** | **53.74 V** |
| **Minimum Firing Angle** | **84.0°** |
| **V/f Ratio** | **7.6 V/Hz** |
| **Frequency Range** | **5 Hz - 50 Hz** |
| **Speed Ratio** | **10:1** |

---

## Application Features

### 1. **Mathematical Modeling**
- Complete induction motor dynamic model in d-q reference frame
- Differential equations for electrical and mechanical dynamics
- State variables: [ids, iqs, idr, iqr, ωr, θr]

### 2. **ODE Solvers**
- **RK45 (Runge-Kutta 4th/5th order)**: High accuracy, adaptive step size
- **Euler Method**: Simple, fixed step size
- Real-time comparison of solver performance

### 3. **User Interface Components**

#### Control Panel:
- **Motor Parameters**: Voltage, frequency, speed, resistances, inductances, inertia
- **Control Sliders**:
  - Frequency (Hz): Adjusts output frequency
  - Voltage (V): Adjusts output voltage (maintains V/f ratio)
  - Firing Angle (°): Controls rectifier DC output
  - Load Torque (N.m): Applies mechanical load

#### Visualization:
Six real-time plots:
1. **Motor Speed** (rpm vs time)
2. **Electromagnetic Torque** (N.m vs time)
3. **Stator Current** (A vs time)
4. **DC Link Voltage** (V vs time)
5. **Motor Slip** (% vs time)
6. **Torque-Speed Characteristic** (torque vs speed)

#### Real-time Measurements:
- Speed (rpm)
- Torque (N.m)
- Current (A)
- DC Voltage (V)
- Slip (%)
- Simulation Time (s)

### 4. **Advanced Features**
- Auto-scaling plots when window resizes
- Adjustable time step for simulation accuracy
- Start/Stop/Reset controls
- Status bar with real-time feedback
- Maintains V/f ratio automatically
- Dynamic parameter updates

---

## Installation & Requirements

### Required Libraries:
```bash
pip install numpy scipy matplotlib
```

### Standard Libraries (included with Python):
- tkinter
- math

---

## How to Run

```bash
python3 vvvf_inverter_induction_motor_lab.py
```

---

## Usage Guide

### 1. Starting a Simulation:
1. Review motor parameters (modify if needed)
2. Adjust control sliders to desired values
3. Select ODE solver (RK45 recommended for accuracy)
4. Click **Start** button
5. Observe real-time plots and measurements

### 2. Adjusting Parameters During Simulation:
- Move **Frequency slider** to change motor speed
- Move **Load Torque slider** to apply mechanical load
- Move **Firing Angle slider** to change DC link voltage
- The system responds dynamically to changes

### 3. Observing Transient Response:
- Start with low frequency and gradually increase
- Apply step changes in load torque
- Observe overshoot, settling time, and steady-state error

### 4. Comparing Solvers:
1. Run simulation with RK45
2. Note the results
3. Reset simulation
4. Change solver to Euler
5. Compare accuracy and computation time

### 5. Testing VVVF Operation:
- Set frequency to minimum (5 Hz) and observe low-speed operation
- Set frequency to maximum (50 Hz) and observe rated operation
- Verify V/f ratio is maintained
- Check DC link voltage matches theoretical calculations

---

## Practical Applications in Electrical Engineering

### 1. **Motor Drive Design**
- Understand transient behavior during startup
- Optimize V/f ratio for different load characteristics
- Design protection schemes based on current and torque limits

### 2. **Speed Control**
- Implement closed-loop speed control strategies
- Analyze stability margins
- Tune controller parameters

### 3. **Energy Efficiency**
- Minimize losses during light load operation
- Optimize flux level for efficiency
- Analyze power factor correction

### 4. **Industrial Applications**
- **Pumps & Fans**: Variable speed for energy savings
- **Conveyors**: Precise speed control
- **Machine Tools**: Wide speed range operation
- **Electric Vehicles**: Traction motor control

### 5. **Education & Research**
- Learn induction motor dynamic behavior
- Understand field-oriented control concepts
- Experiment with different control strategies
- Validate theoretical calculations

---

## Technical Details

### Induction Motor Equations (d-q Reference Frame)

**Voltage Equations:**
```
Vds = Rs·ids + Ls·(dids/dt) - ωe·Ls·iqs
Vqs = Rs·iqs + Ls·(diqs/dt) + ωe·Ls·ids
0 = Rr·idr + Lr·(didr/dt) - ωslip·Lr·iqr
0 = Rr·iqr + Lr·(diqr/dt) + ωslip·Lr·idr
```

**Electromagnetic Torque:**
```
Te = (3/2)·(P/2)·Lm·(iqs·idr - ids·iqr)
```

**Mechanical Equation:**
```
J·(dωr/dt) = Te - TL - B·ωr
```

**Where:**
- Rs, Rr: Stator and rotor resistances
- Ls, Lr, Lm: Stator, rotor, and magnetizing inductances
- ids, iqs, idr, iqr: d-q axis currents
- ωe: Electrical angular frequency
- ωr: Rotor angular velocity
- ωslip: Slip angular frequency
- P: Number of poles
- J: Moment of inertia
- B: Friction coefficient
- Te, TL: Electromagnetic and load torques

---

## Tips for Best Results

1. **Start slowly**: Begin with low frequency and gradually increase
2. **Monitor stability**: Watch for oscillations in torque and current
3. **Load ramping**: Apply load torque gradually to avoid large transients
4. **Solver selection**: Use RK45 for high accuracy, Euler for faster simulation
5. **Time step**: Smaller time steps (0.001s) give better accuracy but slower simulation

---

## Troubleshooting

### Issue: Simulation runs too slowly
- **Solution**: Increase time step or use Euler solver

### Issue: Unstable oscillations
- **Solution**: Reduce time step, check parameter values

### Issue: Plots not updating
- **Solution**: Check that simulation is running (Start button pressed)

### Issue: Window not resizing properly
- **Solution**: Restart application, resize window after startup

---

## Future Enhancements

- [ ] Closed-loop speed control with PI/PID controller
- [ ] Field-oriented control (FOC) implementation
- [ ] Space vector PWM visualization
- [ ] Harmonic analysis
- [ ] Efficiency calculations
- [ ] Temperature modeling
- [ ] Multiple motor comparison
- [ ] Save/load parameter sets
- [ ] Export data to CSV
- [ ] 3D visualization of flux

---

## Author
Created for electrical engineering education and practical motor control applications.

## License
Open source - Free to use and modify for educational purposes.
