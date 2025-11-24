# Quick Start Guide - Alternator Impedance Lab

## Installation

1. **Install dependencies:**
```bash
pip3 install numpy matplotlib scipy
```

2. **Run the application:**
```bash
python3 alternator_impedance_lab.py
```

## Quick Usage

### Solve Problem 9.15 (1 minute)
1. Click **"Problem 9.15"** button in top menu
2. Automatically loads:
   - Armature Resistance: 0.15 Ω
   - Open Circuit Voltage: 60 V
   - Short Circuit Current: 150 A
   - Terminal Voltage: 200 V
   - Armature Current: 90 A
   - Power Factor: 0.8 lagging
3. View results in "Results" tab:
   - **Zs = 0.4000 Ω** (Synchronous Impedance)
   - **Xs = 0.3708 Ω** (Synchronous Reactance)
   - **E = 231.57 V** (No-Load Voltage)
4. Check "Phasor Diagram" tab to see voltage and current relationships
5. Check "Characteristics" tab for V-I curves, power curves, efficiency

### Solve Problem 9.16 (1 minute)
1. Click **"Problem 9.16"** button
2. Automatically loads parameters with leading power factor
3. Results:
   - **Zs = 2.7778 Ω**
   - **Xs = 2.7556 Ω**
   - **E = 213.80 V** (note: lower than terminal voltage due to leading pf)

### Run Dynamic Simulation (2 minutes)
1. Load any problem (9.15 or 9.16)
2. Go to "Simulation" tab
3. Select solver: **RK45** (recommended) or **Euler**
4. Set simulation time: 1.0 seconds
5. Click **"Start Simulation"**
6. Switch to "Time Domain" tab to see:
   - Voltage transient response
   - Current buildup dynamics
   - Power variation over time

## Test Calculations

Run the test script to verify all calculations:
```bash
python3 test_alternator_calculations.py
```

Expected output shows detailed step-by-step solutions for both problems.

## Key Features

### 📊 Visualizations
- **Phasor Diagram**: Shows E, Vt, Ia, IRa, jIXs in complex plane
- **Time Domain**: Transient voltage, current, and power
- **Characteristics**: V-I curves, power curves, efficiency, regulation

### 🎛️ Controls
- **Sliders**: Adjust all parameters in real-time
- **Calculate**: Compute steady-state values
- **Start Simulation**: Run dynamic transient analysis
- **Stop/Reset**: Control simulation execution

## Files

- `alternator_impedance_lab.py` - Main application
- `test_alternator_calculations.py` - Verification script
- `ALTERNATOR_LAB_README.md` - Full documentation
- `ALTERNATOR_QUICKSTART.md` - This file

---

**Ready to go!** Start with Problem 9.15, then explore!
