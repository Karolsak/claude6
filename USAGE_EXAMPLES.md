# Usage Examples - Alternator Impedance Lab

## Example 1: Solving Problem 9.15 (Step-by-Step)

### Step 1: Launch the Application
```bash
python3 alternator_impedance_lab.py
```

### Step 2: Load Problem 9.15
- Click the **"Problem 9.15"** button in the top menu bar
- Parameters automatically populate:
  - Ra = 0.15 Ω
  - Eoc = 60 V
  - Isc = 150 A
  - Vt = 200 V
  - Ia = 90 A
  - Power Factor = 0.8 (Lagging)

### Step 3: Calculate Results
- Click the **"Calculate"** button
- View results in the "Results" tab:

```
============================================
Problem 9.15
============================================

Input Parameters:
  Armature Resistance (Ra): 0.150 Ω
  Open Circuit Voltage (Eoc): 60.00 V
  Short Circuit Current (Isc): 150.00 A
  Terminal Voltage (Vt): 200.00 V
  Armature Current (Ia): 90.00 A
  Power Factor: 0.80 lagging

Calculated Results:
  Synchronous Impedance (Zs): 0.4000 Ω ✓
  Synchronous Reactance (Xs): 0.3708 Ω ✓
  No-Load Voltage (E): 231.57 V ✓
  Load Angle (δ): 4.61° ✓

Additional Information:
  Impedance Angle: 68.04°
  Apparent Power: 18000.00 VA
  Real Power: 14400.00 W
  Reactive Power: 10800.00 VAR (lagging)
```

### Step 4: View Phasor Diagram
- Click the **"Phasor Diagram"** tab
- Observe:
  - Red arrow: Terminal voltage (Vt = 200V horizontal)
  - Blue arrow: Armature current (Ia, lagging by 36.87°)
  - Green arrow: Resistive voltage drop (IRa)
  - Orange arrow: Reactive voltage drop (jIXs)
  - Purple arrow: Internal EMF (E = 231.57V)

### Step 5: View Operating Characteristics
- Click the **"Characteristics"** tab
- See 4 plots:
  1. **V-I Characteristics**: Shows voltage drop with increasing current
  2. **Power-Current**: Maximum power transfer point
  3. **Efficiency Curve**: Peak efficiency region
  4. **Voltage Regulation**: How voltage changes with load

---

## Example 2: Solving Problem 9.16 (Leading Power Factor)

### Quick Solution
1. Click **"Problem 9.16"** button
2. Click **"Calculate"**
3. Results appear instantly:

```
============================================
Problem 9.16
============================================

Calculated Results:
  Synchronous Impedance (Zs): 2.7778 Ω ✓
  Synchronous Reactance (Xs): 2.7556 Ω ✓
  No-Load Voltage (E): 213.80 V ✓
  Load Angle (δ): 45.16° ✓
```

### Key Observation
Notice that with **leading** power factor:
- EMF (213.80V) is **LOWER** than terminal voltage (220V)
- This is because leading current provides magnetizing effect
- Reduces excitation requirements (better efficiency)

Compare to Problem 9.15 (lagging):
- EMF (231.57V) is **HIGHER** than terminal voltage (200V)
- Lagging current has demagnetizing effect
- Requires more excitation

---

## Example 3: Dynamic Simulation

### Scenario: Observe Current Buildup During Load Application

1. Load Problem 9.15
2. Go to **"Simulation"** tab
3. Select **"RK45"** solver (more accurate)
4. Set simulation time to **2.0 seconds**
5. Click **"Start Simulation"**
6. Switch to **"Time Domain"** tab

### What You'll See

**Voltage Plot (Top):**
- Starts at ~60V (no-load)
- Drops to steady-state terminal voltage (200V)
- Shows transient overshoot/undershoot
- Settles in ~0.5 seconds

**Current Plot (Middle):**
- Starts at 0A
- Exponentially rises to 90A
- Time constant τ = Xs/(ω×Ra) ≈ 12ms
- Smooth buildup following first-order response

**Power Plot (Bottom):**
- Starts at 0W
- Rises to 14400W (P = VIcosφ)
- Follows voltage and current profiles
- Shows electromagnetic energy storage

### Physical Interpretation
The simulation models what happens when:
1. Field excitation is applied (t=0)
2. Load is suddenly connected
3. Machine transitions from no-load to rated load
4. Electrical transients settle

---

## Example 4: Parameter Sensitivity Study

### Question: How does power factor affect internal EMF?

1. Load **"Custom"** mode
2. Set standard parameters:
   - Ra = 0.2 Ω
   - Vt = 200 V
   - Ia = 100 A
   - Zs = 0.5 Ω

3. **Test 1: Power Factor = 1.0 (Unity)**
   - Lagging/Leading: N/A
   - Calculate → E = ?
   - Record result

4. **Test 2: Power Factor = 0.8 (Lagging)**
   - Select "Lagging"
   - Calculate → E = ?
   - Record result

5. **Test 3: Power Factor = 0.8 (Leading)**
   - Select "Leading"
   - Calculate → E = ?
   - Record result

### Expected Results
- Unity pf: E ≈ 225V (moderate EMF)
- 0.8 Lagging: E ≈ 240V (high EMF, needs more excitation)
- 0.8 Leading: E ≈ 185V (low EMF, capacitive support)

**Conclusion**: Leading power factor is desirable for reducing generator excitation requirements.

---

## Example 5: Comparing Both Problems Side-by-Side

### Run Test Script
```bash
python3 test_alternator_calculations.py
```

### Comparison Table Generated
```
============================================
COMPARISON OF RESULTS
============================================

Parameter         Problem 9.15    Problem 9.16
--------------------------------------------
Zs (Ω)              0.4000          2.7778
Xs (Ω)              0.3708          2.7556
E (V)              231.57          213.80
δ (degrees)          4.61           45.16
Power Factor    Lagging         Leading
============================================
```

### Engineering Insights

**Problem 9.15 (Low Impedance Machine):**
- Small synchronous impedance (0.4Ω)
- Suitable for high short-circuit capacity
- Better voltage regulation
- Smaller load angle (4.61°) = more stable

**Problem 9.16 (High Impedance Machine):**
- Large synchronous impedance (2.78Ω)
- Higher voltage drop under load
- Larger load angle (45.16°) = less stable
- Leading pf compensates for high impedance

---

## Example 6: Understanding Phasor Diagrams

### For Problem 9.15 (Lagging)

**Phasor Construction:**
1. Vt = 200∠0° V (reference, horizontal)
2. Ia = 90∠-36.87° A (lagging by φ = arccos(0.8))
3. IRa = 90 × 0.15 = 13.5 V (parallel to Ia)
4. jIXs = 90 × 0.3708 = 33.4 V (perpendicular to Ia)
5. E = Vt + IRa + jIXs = 231.57∠4.61° V

**Visual Observation:**
- Voltage drops **add constructively** with Vt
- E is **larger** than Vt (231.57V > 200V)
- Load angle δ = 4.61° (small, good stability)

### For Problem 9.16 (Leading)

**Phasor Construction:**
1. Vt = 220∠0° V (reference)
2. Ia = 60∠+31.79° A (leading by φ = arccos(0.85))
3. IRa + jIXs voltage drop calculation
4. E = 213.80∠45.16° V

**Visual Observation:**
- Voltage drops **partially cancel** Vt
- E is **smaller** than Vt (213.80V < 220V)
- Large load angle δ = 45.16° (stability concern)

---

## Example 7: Solver Comparison (Euler vs RK45)

### Test Setup
1. Load Problem 9.15
2. Go to Simulation tab
3. Set simulation time = 1.0 seconds

### Run Euler Method
1. Select "Euler"
2. Click "Start Simulation"
3. Observe time domain plots
4. Note: Some numerical noise possible

### Run RK45 Method
1. Click "Reset"
2. Select "RK45"
3. Click "Start Simulation"
4. Observe time domain plots
5. Note: Smoother curves, better accuracy

### Comparison
- **Euler**: Faster execution, good for simple systems
- **RK45**: Better accuracy, adaptive step size
- **Recommendation**: Use RK45 for production analysis

---

## Tips for Best Results

1. **For Learning**: Start with Problems 9.15 and 9.16
2. **For Exploration**: Use Custom mode with sliders
3. **For Analysis**: Run simulations and export results
4. **For Verification**: Compare with test script output
5. **For Visualization**: Resize window for better plot viewing

---

## Common Calculations Reference

### Synchronous Impedance
```
Zs = Eoc / Isc
   = Open Circuit Voltage / Short Circuit Current
```

### Synchronous Reactance
```
Xs = √(Zs² - Ra²)
   = √(Synchronous Impedance² - Armature Resistance²)
```

### Internal EMF (Phasor Sum)
```
E = Vt + Ia(Ra + jXs)
  = Vt + Ia×Ra + j×Ia×Xs

where:
- j = √(-1) (imaginary unit)
- Ia angle depends on power factor (lagging/leading)
```

### Power Calculations
```
S = Vt × Ia              (Apparent Power, VA)
P = Vt × Ia × cosφ       (Real Power, W)
Q = Vt × Ia × sinφ       (Reactive Power, VAR)
```

---

## Educational Objectives Achieved

After using this lab, you will understand:

✓ How to calculate synchronous impedance and reactance
✓ Phasor diagram construction for alternators
✓ Effect of power factor on excitation requirements
✓ Voltage regulation concepts
✓ Transient behavior during load changes
✓ Stability implications of load angle
✓ Practical alternator operating characteristics

**Ready to explore!** 🚀
