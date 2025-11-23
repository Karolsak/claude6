# Quick Start Guide

## Instant Solutions (No GUI Required)

Run the demo script to see the solutions to both examples:

```bash
python3 example_solutions_demo.py
```

This will display:
- **Example 50.74**: Tariff comparison analysis
- **Example 50.75**: Equipment cost analysis

---

## Full Application (GUI)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. For Ubuntu/Debian (if tkinter is missing):
```bash
sudo apt-get install python3-tk
```

### Run the Application

```bash
python3 electrical_engineering_lab.py
```

---

## Features at a Glance

### 1. Tariff Calculator (Example 50.74)
- **Input**: Rateable value, lighting consumption
- **Output**: Break-even power consumption (895 units)
- **Visual**: Cost comparison chart

### 2. Equipment Analyzer (Example 50.75)
- **Input**: Equipment specs, efficiencies, costs
- **Output**: HT motor maximum price (Rs 61.04/kW)
- **Analysis**: Complete economic breakdown

### 3. DC Motor Simulation
- Adjust voltage, resistance, inductance, torque
- Choose solver: RK45 or Euler
- View: Current, Speed, Torque, Power plots

### 4. Induction Motor Simulation
- Set voltage, frequency, impedances
- Observe startup characteristics
- Analyze slip and speed

### 5. RLC Circuit Analysis
- Configure R, L, C values
- Calculate resonance frequency
- Simulate transient response

---

## Quick Example Solutions

### Example 50.74
**Answer**: 895 units of domestic power consumption

At this consumption level, both tariffs cost Rs 53.05/month

### Example 50.75
**Answer**: HT motor can cost up to Rs 61.04 per kW

This is 62% MORE than the LT system (Rs 37.61/kW) because:
- No transformer needed
- Lower annual energy costs over equipment lifetime

---

## File Structure

```
claude6/
├── electrical_engineering_lab.py    # Main GUI application
├── example_solutions_demo.py        # Terminal-based solutions
├── requirements.txt                 # Python dependencies
├── README_ELECTRICAL_LAB.md        # Full documentation
└── QUICKSTART.md                   # This file
```

---

## Troubleshooting

**"No module named 'tkinter'"**
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- macOS: `brew install python-tk`

**"No module named 'numpy'"**
```bash
pip install numpy matplotlib
```

**Display not working**
- Ensure X11 forwarding if using SSH
- Check GUI support on your system

---

## Next Steps

1. Run `example_solutions_demo.py` to verify calculations
2. Launch the GUI for interactive analysis
3. Experiment with different parameters
4. Export results using File → Export Results

For detailed documentation, see `README_ELECTRICAL_LAB.md`
