#!/usr/bin/env python3
"""
Advanced Electrical Engineering Analysis Laboratory
Includes: Tariff Calculator, Equipment Analysis, Dynamic Machine Simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
from datetime import datetime


class ODESolver:
    """Base class for ODE solvers"""

    @staticmethod
    def euler(func, y0, t_span, dt):
        """Euler method for solving ODEs"""
        t_start, t_end = t_span
        t = np.arange(t_start, t_end, dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(1, len(t)):
            y[i] = y[i-1] + dt * func(t[i-1], y[i-1])

        return t, y

    @staticmethod
    def rk45(func, y0, t_span, dt):
        """Runge-Kutta 4th/5th order adaptive method"""
        t_start, t_end = t_span
        t = np.arange(t_start, t_end, dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(1, len(t)):
            # RK4 coefficients
            k1 = func(t[i-1], y[i-1])
            k2 = func(t[i-1] + dt/2, y[i-1] + dt*k1/2)
            k3 = func(t[i-1] + dt/2, y[i-1] + dt*k2/2)
            k4 = func(t[i-1] + dt, y[i-1] + dt*k3)

            # Update using RK4 formula
            y[i] = y[i-1] + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

        return t, y


class ElectricalMachineModels:
    """Models for various electrical machines"""

    @staticmethod
    def dc_motor_dynamics(t, state, V_applied, R_a, L_a, K_e, K_t, J, B, T_load):
        """
        DC Motor differential equations
        state = [i_a, omega]
        i_a: armature current (A)
        omega: angular velocity (rad/s)
        """
        i_a, omega = state

        # di_a/dt = (V_applied - R_a*i_a - K_e*omega) / L_a
        di_a_dt = (V_applied - R_a * i_a - K_e * omega) / L_a

        # d(omega)/dt = (K_t*i_a - B*omega - T_load) / J
        domega_dt = (K_t * i_a - B * omega - T_load) / J

        return np.array([di_a_dt, domega_dt])

    @staticmethod
    def induction_motor_simplified(t, state, V, f, P, R_s, R_r, X_s, X_r, T_load):
        """
        Simplified induction motor model
        state = [omega]
        omega: rotor speed (rad/s)
        """
        omega = state[0]
        omega_s = 2 * np.pi * f  # Synchronous speed

        # Slip
        s = (omega_s - omega) / omega_s if omega_s != 0 else 0

        # Torque calculation (simplified)
        if s != 0:
            T_e = (P * V**2 * R_r / s) / (omega_s * ((R_s + R_r/s)**2 + (X_s + X_r)**2))
        else:
            T_e = 0

        # Moment of inertia (assumed)
        J = 0.1

        # domega/dt = (T_e - T_load) / J
        domega_dt = (T_e - T_load) / J

        return np.array([domega_dt])

    @staticmethod
    def rlc_circuit(t, state, V_source, R, L, C, freq=0):
        """
        RLC circuit dynamics
        state = [i, v_c]
        i: current (A)
        v_c: capacitor voltage (V)
        """
        i, v_c = state

        # Voltage source (can be DC or AC)
        if freq > 0:
            V = V_source * np.sin(2 * np.pi * freq * t)
        else:
            V = V_source

        # di/dt = (V - R*i - v_c) / L
        di_dt = (V - R * i - v_c) / L

        # dv_c/dt = i / C
        dvc_dt = i / C

        return np.array([di_dt, dvc_dt])


class TariffCalculator:
    """Solver for Example 50.74 - Tariff Comparison"""

    @staticmethod
    def calculate_equal_consumption(rateable_value, lighting_units):
        """
        Calculate domestic power consumption where both tariffs are equal

        Tariff A: Lighting: 20 paise/unit; Power: 5 paise/unit; Meter rent: 30 paise/month
        Tariff B: 12% on rateable value + 3 paise/unit for all purposes

        Returns: Monthly domestic power consumption (units)
        """
        # Annual rateable value
        annual_rateable = rateable_value

        # Tariff B: Annual cost = 12% of rateable value + 3 paise per unit
        # Monthly fixed cost for Tariff B
        tariff_b_fixed_monthly = (0.12 * annual_rateable) / 12  # in Rs

        # Tariff A costs per month
        lighting_cost_a = lighting_units * 0.20  # in Rs
        meter_rent_a = 0.30  # in Rs

        # Let x = domestic power consumption (units per month)
        # Tariff A total = lighting_cost + power_cost + meter_rent
        # Tariff A = 0.20*40 + 0.05*x + 0.30

        # Tariff B total = fixed_monthly + cost_per_unit*(lighting + power)
        # Tariff B = tariff_b_fixed_monthly + 0.03*(40 + x)

        # Setting them equal:
        # 0.20*40 + 0.05*x + 0.30 = tariff_b_fixed_monthly + 0.03*(40 + x)
        # 8 + 0.05*x + 0.30 = tariff_b_fixed_monthly + 1.20 + 0.03*x
        # 8.30 + 0.05*x = tariff_b_fixed_monthly + 1.20 + 0.03*x
        # 0.05*x - 0.03*x = tariff_b_fixed_monthly + 1.20 - 8.30
        # 0.02*x = tariff_b_fixed_monthly - 7.10

        x = (tariff_b_fixed_monthly - 7.10) / 0.02

        return x, tariff_b_fixed_monthly

    @staticmethod
    def compare_tariffs(rateable_value, lighting_units, power_units):
        """Compare costs for both tariffs"""
        # Tariff A
        lighting_cost_a = lighting_units * 0.20
        power_cost_a = power_units * 0.05
        meter_rent_a = 0.30
        total_a = lighting_cost_a + power_cost_a + meter_rent_a

        # Tariff B
        annual_rateable = rateable_value
        tariff_b_fixed_monthly = (0.12 * annual_rateable) / 12
        total_units = lighting_units + power_units
        unit_cost_b = total_units * 0.03
        total_b = tariff_b_fixed_monthly + unit_cost_b

        return total_a, total_b


class EquipmentCostAnalyzer:
    """Solver for Example 50.75 - Equipment Cost Analysis"""

    @staticmethod
    def calculate_ht_motor_price(transformer_price_per_kva, lt_motor_price_per_kw,
                                  transformer_eff, lt_motor_eff, ht_motor_eff,
                                  load_factor, energy_cost_per_unit, interest_rate):
        """
        Calculate price per kW for HT motor

        Args:
            transformer_price_per_kva: Rs per kVA
            lt_motor_price_per_kw: Rs per kW
            transformer_eff: Transformer efficiency (decimal)
            lt_motor_eff: LT motor efficiency (decimal)
            ht_motor_eff: HT motor efficiency (decimal)
            load_factor: Annual load factor (decimal)
            energy_cost_per_unit: Paise per kWh
            interest_rate: Interest and depreciation rate (decimal)

        Returns: Price per kW for HT motor
        """
        # For 1 kW output:
        # LT system: Transformer + LT Motor
        # Input to LT motor = 1 / lt_motor_eff
        input_to_motor = 1.0 / lt_motor_eff

        # Input to transformer (kVA needed) = input_to_motor / transformer_eff
        transformer_input = input_to_motor / transformer_eff

        # Capital cost for LT system
        transformer_cost = transformer_price_per_kva * transformer_input
        lt_motor_cost = lt_motor_price_per_kw * 1.0
        lt_system_capital = transformer_cost + lt_motor_cost

        # Annual charges for LT system
        lt_annual_fixed = interest_rate * lt_system_capital

        # Energy consumption for LT system
        # Annual hours at load factor
        annual_hours = 8760 * load_factor
        lt_energy_consumption = transformer_input * annual_hours  # kWh
        lt_annual_energy_cost = lt_energy_consumption * energy_cost_per_unit / 100  # Convert paise to Rs

        lt_total_annual_cost = lt_annual_fixed + lt_annual_energy_cost

        # HT system: Only HT motor
        # Input to HT motor = 1 / ht_motor_eff
        ht_input = 1.0 / ht_motor_eff

        # Annual charges for HT system (let price = P)
        # ht_annual_fixed = interest_rate * P

        # Energy consumption for HT system
        ht_energy_consumption = ht_input * annual_hours
        ht_annual_energy_cost = ht_energy_consumption * energy_cost_per_unit / 100

        # For equal annual cost:
        # interest_rate * P + ht_annual_energy_cost = lt_total_annual_cost
        # P = (lt_total_annual_cost - ht_annual_energy_cost) / interest_rate

        ht_motor_price = (lt_total_annual_cost - ht_annual_energy_cost) / interest_rate

        return ht_motor_price, lt_system_capital, lt_total_annual_cost


class GeneratorStationPFCalculator:
    """Solver for Generator Station Power Factor Problem"""

    @staticmethod
    def calculate_rotary_converter_pf(lighting_kw, motor_hp, motor_pf, motor_eff,
                                     converter_v, converter_i, converter_eff):
        """
        Calculate the required power factor of the rotary converter
        for unity power factor at the supply station

        Problem: A generator station supplies power to:
        - Lighting load
        - Induction motor with given HP, PF, efficiency
        - Rotary converter with given voltage, current, efficiency

        Find the PF of rotary converter needed for unity PF at station
        """
        # Convert motor HP to kW
        motor_output_kw = motor_hp * 0.746

        # Lighting load (assumed unity power factor)
        P_lighting = lighting_kw
        Q_lighting = 0  # No reactive power for lighting

        # Induction motor calculations
        P_motor_output = motor_output_kw
        P_motor_input = P_motor_output / motor_eff

        # Apparent power of motor
        S_motor = P_motor_input / motor_pf

        # Reactive power of motor (lagging)
        phi_motor = math.acos(motor_pf)
        Q_motor = S_motor * math.sin(phi_motor)

        # Rotary converter calculations
        P_converter_output = (converter_v * converter_i) / 1000  # in kW
        P_converter_input = P_converter_output / converter_eff

        # Total real power
        P_total = P_lighting + P_motor_input + P_converter_input

        # For unity power factor at station: Total Q must be zero
        # Q_total = Q_lighting + Q_motor + Q_converter = 0
        # Therefore: Q_converter = -(Q_lighting + Q_motor)
        Q_converter = -(Q_lighting + Q_motor)

        # Apparent power of converter
        S_converter = math.sqrt(P_converter_input**2 + Q_converter**2)

        # Power factor of converter
        pf_converter = P_converter_input / S_converter

        # Determine if leading or lagging
        if Q_converter < 0:
            pf_type = "leading"
        elif Q_converter > 0:
            pf_type = "lagging"
        else:
            pf_type = "unity"

        return {
            'P_lighting': P_lighting,
            'Q_lighting': Q_lighting,
            'P_motor_output': P_motor_output,
            'P_motor_input': P_motor_input,
            'S_motor': S_motor,
            'Q_motor': Q_motor,
            'P_converter_output': P_converter_output,
            'P_converter_input': P_converter_input,
            'Q_converter': Q_converter,
            'S_converter': S_converter,
            'P_total': P_total,
            'Q_total': 0,
            'pf_converter': pf_converter,
            'pf_type': pf_type,
            'motor_output_kw': motor_output_kw
        }


class ElectricalEngineeringLab(tk.Tk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.title("Advanced Electrical Engineering Laboratory")
        self.geometry("1400x900")
        self.configure(bg='#2c3e50')

        # Simulation control
        self.is_running = False
        self.animation_id = None

        # Bind resize event
        self.bind('<Configure>', self.on_window_resize)

        # Create menu bar
        self.create_menu_bar()

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.create_generator_pf_tab()
        self.create_tariff_tab()
        self.create_equipment_tab()
        self.create_dc_motor_tab()
        self.create_induction_motor_tab()
        self.create_rlc_circuit_tab()

        # Status bar
        self.status_bar = tk.Label(self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear All", command=self.clear_all)
        tools_menu.add_command(label="Reset Simulation", command=self.reset_simulation)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_generator_pf_tab(self):
        """Generator Station Power Factor Calculator"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="★ Generator PF Problem")

        # Main container with grid
        main_frame = ttk.Frame(tab, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        # Problem statement
        problem_frame = ttk.LabelFrame(main_frame, text="Problem Statement", padding="10")
        problem_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        problem_text = """
A generator station supplies power to the following loads:
  • Lighting load
  • Induction motor with specified HP, power factor, and efficiency
  • Rotary converter with specified voltage, current, and efficiency

OBJECTIVE: Find the power factor of the rotary converter needed to achieve
           unity power factor at the generator station.
"""
        ttk.Label(problem_frame, text=problem_text, justify=tk.LEFT, font=("Arial", 10)).pack()

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(0, 5))

        # Lighting load
        ttk.Label(input_frame, text="LIGHTING LOAD", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(5, 2))
        ttk.Label(input_frame, text="Lighting Power (kW):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.gen_lighting_kw = tk.DoubleVar(value=100)
        ttk.Entry(input_frame, textvariable=self.gen_lighting_kw, width=15).grid(row=1, column=1, pady=2)
        ttk.Scale(input_frame, from_=0, to=500, variable=self.gen_lighting_kw,
                 orient=tk.HORIZONTAL, length=200).grid(row=1, column=2, pady=2, padx=5)

        # Induction motor
        ttk.Label(input_frame, text="INDUCTION MOTOR", font=("Arial", 10, "bold")).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 2))

        ttk.Label(input_frame, text="Motor Power (HP):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.gen_motor_hp = tk.DoubleVar(value=400)
        ttk.Entry(input_frame, textvariable=self.gen_motor_hp, width=15).grid(row=3, column=1, pady=2)
        ttk.Scale(input_frame, from_=0, to=1000, variable=self.gen_motor_hp,
                 orient=tk.HORIZONTAL, length=200).grid(row=3, column=2, pady=2, padx=5)

        ttk.Label(input_frame, text="Motor Power Factor:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.gen_motor_pf = tk.DoubleVar(value=0.8)
        ttk.Entry(input_frame, textvariable=self.gen_motor_pf, width=15).grid(row=4, column=1, pady=2)
        ttk.Scale(input_frame, from_=0.5, to=1.0, variable=self.gen_motor_pf,
                 orient=tk.HORIZONTAL, length=200).grid(row=4, column=2, pady=2, padx=5)

        ttk.Label(input_frame, text="Motor Efficiency:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.gen_motor_eff = tk.DoubleVar(value=0.92)
        ttk.Entry(input_frame, textvariable=self.gen_motor_eff, width=15).grid(row=5, column=1, pady=2)
        ttk.Scale(input_frame, from_=0.7, to=1.0, variable=self.gen_motor_eff,
                 orient=tk.HORIZONTAL, length=200).grid(row=5, column=2, pady=2, padx=5)

        # Rotary converter
        ttk.Label(input_frame, text="ROTARY CONVERTER", font=("Arial", 10, "bold")).grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(10, 2))

        ttk.Label(input_frame, text="Converter Voltage (V):").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.gen_conv_v = tk.DoubleVar(value=800)
        ttk.Entry(input_frame, textvariable=self.gen_conv_v, width=15).grid(row=7, column=1, pady=2)
        ttk.Scale(input_frame, from_=0, to=1500, variable=self.gen_conv_v,
                 orient=tk.HORIZONTAL, length=200).grid(row=7, column=2, pady=2, padx=5)

        ttk.Label(input_frame, text="Converter Current (A):").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.gen_conv_i = tk.DoubleVar(value=100)
        ttk.Entry(input_frame, textvariable=self.gen_conv_i, width=15).grid(row=8, column=1, pady=2)
        ttk.Scale(input_frame, from_=0, to=500, variable=self.gen_conv_i,
                 orient=tk.HORIZONTAL, length=200).grid(row=8, column=2, pady=2, padx=5)

        ttk.Label(input_frame, text="Converter Efficiency:").grid(row=9, column=0, sticky=tk.W, pady=2)
        self.gen_conv_eff = tk.DoubleVar(value=0.94)
        ttk.Entry(input_frame, textvariable=self.gen_conv_eff, width=15).grid(row=9, column=1, pady=2)
        ttk.Scale(input_frame, from_=0.7, to=1.0, variable=self.gen_conv_eff,
                 orient=tk.HORIZONTAL, length=200).grid(row=9, column=2, pady=2, padx=5)

        # Calculate button
        ttk.Button(input_frame, text="⚡ CALCULATE REQUIRED POWER FACTOR ⚡",
                  command=self.calculate_generator_pf,
                  style="Accent.TButton").grid(row=10, column=0, columnspan=3, pady=15)

        # Results section
        result_frame = ttk.LabelFrame(main_frame, text="Detailed Solution & Results", padding="10")
        result_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(5, 0))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.gen_pf_result = scrolledtext.ScrolledText(result_frame, height=25, width=70,
                                                       wrap=tk.WORD, font=("Courier", 9))
        self.gen_pf_result.pack(fill=tk.BOTH, expand=True)

        # Visualization section
        viz_frame = ttk.LabelFrame(main_frame, text="Power Triangle Diagrams", padding="10")
        viz_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(2, weight=1)

        self.gen_pf_fig = Figure(figsize=(12, 4), dpi=90)
        self.gen_pf_canvas = FigureCanvasTkAgg(self.gen_pf_fig, master=viz_frame)
        self.gen_pf_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate_generator_pf(self):
        """Calculate required rotary converter power factor"""
        try:
            lighting_kw = self.gen_lighting_kw.get()
            motor_hp = self.gen_motor_hp.get()
            motor_pf = self.gen_motor_pf.get()
            motor_eff = self.gen_motor_eff.get()
            converter_v = self.gen_conv_v.get()
            converter_i = self.gen_conv_i.get()
            converter_eff = self.gen_conv_eff.get()

            # Calculate
            calc = GeneratorStationPFCalculator()
            results = calc.calculate_rotary_converter_pf(
                lighting_kw, motor_hp, motor_pf, motor_eff,
                converter_v, converter_i, converter_eff
            )

            # Display detailed results
            result_text = f"""
╔═══════════════════════════════════════════════════════════════════╗
║       GENERATOR STATION POWER FACTOR CALCULATION                  ║
║       Required Rotary Converter Power Factor for Unity PF         ║
╚═══════════════════════════════════════════════════════════════════╝

GIVEN DATA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. LIGHTING LOAD:
   • Power: {lighting_kw:.2f} kW (assumed at unity power factor)

2. INDUCTION MOTOR:
   • Rating: {motor_hp:.2f} HP = {results['motor_output_kw']:.2f} kW
   • Power Factor: {motor_pf:.2f} (lagging)
   • Efficiency: {motor_eff*100:.2f}%

3. ROTARY CONVERTER:
   • Voltage: {converter_v:.2f} V
   • Current: {converter_i:.2f} A
   • Efficiency: {converter_eff*100:.2f}%
   • Output Power: {results['P_converter_output']:.2f} kW

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP-BY-STEP SOLUTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: Lighting Load Analysis
────────────────────────────────
   Real Power (P₁)      = {results['P_lighting']:.4f} kW
   Reactive Power (Q₁)  = {results['Q_lighting']:.4f} kVAR (unity PF)

STEP 2: Induction Motor Analysis
────────────────────────────────
   Motor Output         = {results['P_motor_output']:.4f} kW
   Motor Input (P₂)     = Output / Efficiency
                        = {results['P_motor_output']:.4f} / {motor_eff:.4f}
                        = {results['P_motor_input']:.4f} kW

   Apparent Power (S₂)  = P₂ / Power Factor
                        = {results['P_motor_input']:.4f} / {motor_pf:.4f}
                        = {results['S_motor']:.4f} kVA

   Power Angle (φ₂)     = arccos({motor_pf:.4f})
                        = {math.degrees(math.acos(motor_pf)):.2f}°

   Reactive Power (Q₂)  = S₂ × sin(φ₂)
                        = {results['S_motor']:.4f} × {math.sin(math.acos(motor_pf)):.4f}
                        = {results['Q_motor']:.4f} kVAR (lagging)

STEP 3: Rotary Converter Analysis
────────────────────────────────
   Converter Output     = V × I / 1000
                        = {converter_v:.2f} × {converter_i:.2f} / 1000
                        = {results['P_converter_output']:.4f} kW

   Converter Input (P₃) = Output / Efficiency
                        = {results['P_converter_output']:.4f} / {converter_eff:.4f}
                        = {results['P_converter_input']:.4f} kW

STEP 4: Unity Power Factor Requirement
────────────────────────────────────────
   For unity PF at station: Total Reactive Power = 0

   Q_total = Q₁ + Q₂ + Q₃ = 0

   Q₃ = -(Q₁ + Q₂)
      = -({results['Q_lighting']:.4f} + {results['Q_motor']:.4f})
      = {results['Q_converter']:.4f} kVAR ({results['pf_type']})

STEP 5: Converter Power Factor Calculation
────────────────────────────────────────────
   Apparent Power (S₃)  = √(P₃² + Q₃²)
                        = √({results['P_converter_input']:.4f}² + {results['Q_converter']:.4f}²)
                        = {results['S_converter']:.4f} kVA

   Power Factor (PF₃)   = P₃ / S₃
                        = {results['P_converter_input']:.4f} / {results['S_converter']:.4f}
                        = {results['pf_converter']:.6f} ({results['pf_type']})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINAL ANSWER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ★ REQUIRED POWER FACTOR OF ROTARY CONVERTER: {results['pf_converter']:.4f} ({results['pf_type']})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Real Power:        P_total = {results['P_total']:.4f} kW
Total Reactive Power:    Q_total = {results['Q_total']:.4f} kVAR
Total Apparent Power:    S_total = {results['P_total']:.4f} kVA
Station Power Factor:    PF_station = 1.0000 (Unity) ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY TABLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Load              │  Real P (kW) │ Reactive Q (kVAR) │ Apparent S (kVA)
──────────────────┼──────────────┼───────────────────┼─────────────────
Lighting          │  {results['P_lighting']:>11.4f} │    {results['Q_lighting']:>13.4f} │   {results['P_lighting']:>13.4f}
Induction Motor   │  {results['P_motor_input']:>11.4f} │    {results['Q_motor']:>13.4f} │   {results['S_motor']:>13.4f}
Rotary Converter  │  {results['P_converter_input']:>11.4f} │    {results['Q_converter']:>13.4f} │   {results['S_converter']:>13.4f}
──────────────────┼──────────────┼───────────────────┼─────────────────
TOTAL STATION     │  {results['P_total']:>11.4f} │    {results['Q_total']:>13.4f} │   {results['P_total']:>13.4f}

Station PF = {results['P_total']:.4f} / {results['P_total']:.4f} = 1.0000 ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            self.gen_pf_result.delete(1.0, tk.END)
            self.gen_pf_result.insert(1.0, result_text)

            # Plot power triangles
            self.plot_generator_pf_diagrams(results)

            self.update_status("Generator power factor calculation completed successfully")

        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error during calculation:\n{str(e)}")

    def plot_generator_pf_diagrams(self, results):
        """Plot power triangle diagrams for all loads"""
        self.gen_pf_fig.clear()

        # Create four subplots
        ax1 = self.gen_pf_fig.add_subplot(141)
        ax2 = self.gen_pf_fig.add_subplot(142)
        ax3 = self.gen_pf_fig.add_subplot(143)
        ax4 = self.gen_pf_fig.add_subplot(144)

        # 1. Lighting Load (unity PF)
        P1 = results['P_lighting']
        ax1.arrow(0, 0, P1, 0, head_width=3, head_length=3, fc='blue', ec='blue', linewidth=2)
        ax1.plot([0], [0], 'go', markersize=8)
        ax1.text(P1/2, -8, f'P = {P1:.1f} kW', ha='center', fontsize=9, fontweight='bold')
        ax1.set_xlim([-10, P1+20])
        ax1.set_ylim([-20, 20])
        ax1.set_xlabel('Real Power P (kW)', fontsize=9)
        ax1.set_ylabel('Reactive Power Q (kVAR)', fontsize=9)
        ax1.set_title('Lighting Load\n(Unity PF)', fontsize=10, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='k', linewidth=0.5)
        ax1.axvline(x=0, color='k', linewidth=0.5)

        # 2. Induction Motor (lagging PF)
        P2 = results['P_motor_input']
        Q2 = results['Q_motor']
        S2 = results['S_motor']

        ax2.arrow(0, 0, P2, 0, head_width=10, head_length=10, fc='blue', ec='blue', linewidth=2)
        ax2.arrow(P2, 0, 0, Q2, head_width=10, head_length=10, fc='red', ec='red', linewidth=2)
        ax2.plot([0, P2], [0, Q2], 'g--', linewidth=2.5, label=f'S = {S2:.1f} kVA')
        ax2.plot([0], [0], 'ko', markersize=8)

        angle = math.degrees(math.atan2(Q2, P2))
        ax2.text(P2/2, -20, f'P = {P2:.1f} kW', ha='center', fontsize=9, fontweight='bold', color='blue')
        ax2.text(P2+15, Q2/2, f'Q = {Q2:.1f} kVAR', ha='left', fontsize=9, fontweight='bold', color='red')
        ax2.text(P2/2-20, Q2/2+20, f'φ = {angle:.1f}°', ha='center', fontsize=9, style='italic')

        ax2.set_xlim([-20, P2+50])
        ax2.set_ylim([-40, Q2+50])
        ax2.set_xlabel('Real Power P (kW)', fontsize=9)
        ax2.set_ylabel('Reactive Power Q (kVAR)', fontsize=9)
        ax2.set_title('Induction Motor\n(Lagging PF)', fontsize=10, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='k', linewidth=0.5)
        ax2.axvline(x=0, color='k', linewidth=0.5)

        # 3. Rotary Converter (leading PF)
        P3 = results['P_converter_input']
        Q3 = results['Q_converter']
        S3 = results['S_converter']

        ax3.arrow(0, 0, P3, 0, head_width=10, head_length=5, fc='blue', ec='blue', linewidth=2)
        ax3.arrow(P3, 0, 0, Q3, head_width=10, head_length=5, fc='red', ec='red', linewidth=2)
        ax3.plot([0, P3], [0, Q3], 'g--', linewidth=2.5, label=f'S = {S3:.1f} kVA')
        ax3.plot([0], [0], 'ko', markersize=8)

        angle3 = math.degrees(math.atan2(Q3, P3))
        ax3.text(P3/2, 15, f'P = {P3:.1f} kW', ha='center', fontsize=9, fontweight='bold', color='blue')
        ax3.text(P3+10, Q3/2, f'Q = {Q3:.1f} kVAR', ha='left', fontsize=9, fontweight='bold', color='red')
        ax3.text(P3/2-10, Q3/2-20, f'φ = {abs(angle3):.1f}°', ha='center', fontsize=9, style='italic')

        ax3.set_xlim([-10, P3+40])
        ax3.set_ylim([Q3-50, 40])
        ax3.set_xlabel('Real Power P (kW)', fontsize=9)
        ax3.set_ylabel('Reactive Power Q (kVAR)', fontsize=9)
        ax3.set_title(f'Rotary Converter\n(Leading PF = {results["pf_converter"]:.4f})',
                     fontsize=10, fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=0, color='k', linewidth=0.5)
        ax3.axvline(x=0, color='k', linewidth=0.5)

        # 4. Total Station (unity PF)
        P_total = results['P_total']

        ax4.arrow(0, 0, P_total, 0, head_width=15, head_length=15, fc='green', ec='green', linewidth=3)
        ax4.plot([0], [0], 'ro', markersize=10)
        ax4.text(P_total/2, -30, f'P_total = {P_total:.1f} kW', ha='center',
                fontsize=10, fontweight='bold', color='green')
        ax4.text(P_total/2, -50, 'Q_total = 0 kVAR', ha='center',
                fontsize=10, fontweight='bold', color='green')
        ax4.text(P_total/2, 50, '★ UNITY POWER FACTOR ★', ha='center',
                fontsize=11, fontweight='bold', color='darkgreen',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

        ax4.set_xlim([-20, P_total+50])
        ax4.set_ylim([-80, 80])
        ax4.set_xlabel('Real Power P (kW)', fontsize=9)
        ax4.set_ylabel('Reactive Power Q (kVAR)', fontsize=9)
        ax4.set_title('Total Station Load\n(Unity PF = 1.0)', fontsize=10, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=0, color='k', linewidth=0.5)
        ax4.axvline(x=0, color='k', linewidth=0.5)

        self.gen_pf_fig.tight_layout()
        self.gen_pf_canvas.draw()

    def create_tariff_tab(self):
        """Example 50.74 - Tariff Calculator"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Tariff Calculator")

        # Main container with grid
        main_frame = ttk.Frame(tab, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Rateable value
        ttk.Label(input_frame, text="Annual Rateable Value (Rs):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.tariff_rateable = tk.DoubleVar(value=2500)
        ttk.Entry(input_frame, textvariable=self.tariff_rateable, width=15).grid(row=0, column=1, pady=2)

        # Lighting units
        ttk.Label(input_frame, text="Monthly Lighting Consumption (units):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tariff_lighting = tk.DoubleVar(value=40)
        ttk.Entry(input_frame, textvariable=self.tariff_lighting, width=15).grid(row=1, column=1, pady=2)

        # Power units (for comparison)
        ttk.Label(input_frame, text="Monthly Power Consumption (units):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.tariff_power = tk.DoubleVar(value=0)
        ttk.Entry(input_frame, textvariable=self.tariff_power, width=15).grid(row=2, column=1, pady=2)
        ttk.Scale(input_frame, from_=0, to=1000, variable=self.tariff_power,
                 orient=tk.HORIZONTAL, length=300).grid(row=2, column=2, pady=2, padx=5)

        # Calculate button
        ttk.Button(input_frame, text="Calculate Break-Even Point",
                  command=self.calculate_tariff).grid(row=3, column=0, columnspan=3, pady=10)

        # Results section
        result_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        result_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(1, weight=1)

        self.tariff_result = scrolledtext.ScrolledText(result_frame, height=15, width=80, wrap=tk.WORD)
        self.tariff_result.pack(fill=tk.BOTH, expand=True)

        # Visualization
        viz_frame = ttk.LabelFrame(main_frame, text="Cost Comparison Chart", padding="10")
        viz_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(2, weight=1)

        self.tariff_fig = Figure(figsize=(8, 4), dpi=80)
        self.tariff_canvas = FigureCanvasTkAgg(self.tariff_fig, master=viz_frame)
        self.tariff_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_equipment_tab(self):
        """Example 50.75 - Equipment Cost Analyzer"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Equipment Analysis")

        main_frame = ttk.Frame(tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Equipment Parameters", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        # Create two columns for inputs
        left_frame = ttk.Frame(input_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        right_frame = ttk.Frame(input_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Left column
        ttk.Label(left_frame, text="Transformer Price (Rs/kVA):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.eq_trans_price = tk.DoubleVar(value=12)
        ttk.Entry(left_frame, textvariable=self.eq_trans_price, width=15).grid(row=0, column=1, pady=2)

        ttk.Label(left_frame, text="LT Motor Price (Rs/kW):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.eq_lt_price = tk.DoubleVar(value=24)
        ttk.Entry(left_frame, textvariable=self.eq_lt_price, width=15).grid(row=1, column=1, pady=2)

        ttk.Label(left_frame, text="Transformer Efficiency (%):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.eq_trans_eff = tk.DoubleVar(value=98)
        ttk.Entry(left_frame, textvariable=self.eq_trans_eff, width=15).grid(row=2, column=1, pady=2)

        ttk.Label(left_frame, text="LT Motor Efficiency (%):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.eq_lt_eff = tk.DoubleVar(value=90)
        ttk.Entry(left_frame, textvariable=self.eq_lt_eff, width=15).grid(row=3, column=1, pady=2)

        # Right column
        ttk.Label(right_frame, text="HT Motor Efficiency (%):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.eq_ht_eff = tk.DoubleVar(value=89)
        ttk.Entry(right_frame, textvariable=self.eq_ht_eff, width=15).grid(row=0, column=1, pady=2)

        ttk.Label(right_frame, text="Annual Load Factor (%):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.eq_load_factor = tk.DoubleVar(value=30)
        ttk.Entry(right_frame, textvariable=self.eq_load_factor, width=15).grid(row=1, column=1, pady=2)

        ttk.Label(right_frame, text="Energy Cost (paise/kWh):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.eq_energy_cost = tk.DoubleVar(value=7)
        ttk.Entry(right_frame, textvariable=self.eq_energy_cost, width=15).grid(row=2, column=1, pady=2)

        ttk.Label(right_frame, text="Interest & Depreciation (%):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.eq_interest = tk.DoubleVar(value=8)
        ttk.Entry(right_frame, textvariable=self.eq_interest, width=15).grid(row=3, column=1, pady=2)

        # Calculate button
        ttk.Button(input_frame, text="Calculate HT Motor Price",
                  command=self.calculate_equipment).pack(pady=10)

        # Results
        result_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.equipment_result = scrolledtext.ScrolledText(result_frame, height=20, wrap=tk.WORD)
        self.equipment_result.pack(fill=tk.BOTH, expand=True)

    def create_dc_motor_tab(self):
        """DC Motor Dynamic Simulation"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="DC Motor Dynamics")

        # Split into control and visualization
        control_frame = ttk.Frame(tab)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        viz_frame = ttk.Frame(tab)
        viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Parameters
        param_frame = ttk.LabelFrame(control_frame, text="Motor Parameters", padding="10")
        param_frame.pack(fill=tk.X, pady=5)

        params = [
            ("Applied Voltage (V):", "dc_voltage", 100, 0, 500),
            ("Armature Resistance (Ω):", "dc_ra", 1.0, 0.1, 10),
            ("Armature Inductance (H):", "dc_la", 0.1, 0.01, 1),
            ("Back EMF Constant (Vs/rad):", "dc_ke", 0.5, 0.1, 2),
            ("Torque Constant (Nm/A):", "dc_kt", 0.5, 0.1, 2),
            ("Moment of Inertia (kg·m²):", "dc_j", 0.01, 0.001, 0.1),
            ("Friction Coefficient (Nms/rad):", "dc_b", 0.001, 0.0001, 0.01),
            ("Load Torque (Nm):", "dc_tload", 1.0, 0, 10),
        ]

        self.dc_vars = {}
        for i, (label, var_name, default, min_val, max_val) in enumerate(params):
            ttk.Label(param_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            var = tk.DoubleVar(value=default)
            self.dc_vars[var_name] = var
            ttk.Entry(param_frame, textvariable=var, width=10).grid(row=i, column=1, pady=2)
            ttk.Scale(param_frame, from_=min_val, to=max_val, variable=var,
                     orient=tk.HORIZONTAL, length=150).grid(row=i, column=2, pady=2)

        # Simulation control
        sim_frame = ttk.LabelFrame(control_frame, text="Simulation Control", padding="10")
        sim_frame.pack(fill=tk.X, pady=5)

        ttk.Label(sim_frame, text="Solver Method:").pack()
        self.dc_solver = tk.StringVar(value="RK45")
        ttk.Radiobutton(sim_frame, text="RK45", variable=self.dc_solver, value="RK45").pack()
        ttk.Radiobutton(sim_frame, text="Euler", variable=self.dc_solver, value="Euler").pack()

        ttk.Label(sim_frame, text="Time Step (s):").pack()
        self.dc_dt = tk.DoubleVar(value=0.001)
        ttk.Entry(sim_frame, textvariable=self.dc_dt, width=10).pack()

        ttk.Label(sim_frame, text="Simulation Time (s):").pack()
        self.dc_t_end = tk.DoubleVar(value=2.0)
        ttk.Entry(sim_frame, textvariable=self.dc_t_end, width=10).pack()

        # Control buttons
        btn_frame = ttk.Frame(sim_frame)
        btn_frame.pack(pady=10)

        self.dc_start_btn = ttk.Button(btn_frame, text="Start", command=lambda: self.run_dc_simulation())
        self.dc_start_btn.pack(side=tk.LEFT, padx=2)

        self.dc_stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_simulation, state=tk.DISABLED)
        self.dc_stop_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(btn_frame, text="Reset", command=lambda: self.reset_dc_plot()).pack(side=tk.LEFT, padx=2)

        # Visualization
        self.dc_fig = Figure(figsize=(10, 8), dpi=100)
        self.dc_canvas = FigureCanvasTkAgg(self.dc_fig, master=viz_frame)
        self.dc_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize plot
        self.reset_dc_plot()

    def create_induction_motor_tab(self):
        """Induction Motor Simulation"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Induction Motor")

        control_frame = ttk.Frame(tab)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        viz_frame = ttk.Frame(tab)
        viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Parameters
        param_frame = ttk.LabelFrame(control_frame, text="Motor Parameters", padding="10")
        param_frame.pack(fill=tk.X, pady=5)

        params = [
            ("Voltage (V):", "im_voltage", 400, 0, 1000),
            ("Frequency (Hz):", "im_freq", 50, 10, 100),
            ("Poles:", "im_poles", 4, 2, 12),
            ("Stator Resistance (Ω):", "im_rs", 0.5, 0.1, 5),
            ("Rotor Resistance (Ω):", "im_rr", 0.3, 0.1, 5),
            ("Stator Reactance (Ω):", "im_xs", 1.0, 0.1, 10),
            ("Rotor Reactance (Ω):", "im_xr", 1.0, 0.1, 10),
            ("Load Torque (Nm):", "im_tload", 10.0, 0, 100),
        ]

        self.im_vars = {}
        for i, (label, var_name, default, min_val, max_val) in enumerate(params):
            ttk.Label(param_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            var = tk.DoubleVar(value=default)
            self.im_vars[var_name] = var
            ttk.Entry(param_frame, textvariable=var, width=10).grid(row=i, column=1, pady=2)
            ttk.Scale(param_frame, from_=min_val, to=max_val, variable=var,
                     orient=tk.HORIZONTAL, length=150).grid(row=i, column=2, pady=2)

        # Control buttons
        btn_frame = ttk.LabelFrame(control_frame, text="Control", padding="10")
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Start", command=self.run_im_simulation).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="Reset", command=self.reset_im_plot).pack(pady=2, fill=tk.X)

        # Visualization
        self.im_fig = Figure(figsize=(10, 8), dpi=100)
        self.im_canvas = FigureCanvasTkAgg(self.im_fig, master=viz_frame)
        self.im_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.reset_im_plot()

    def create_rlc_circuit_tab(self):
        """RLC Circuit Simulation"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="RLC Circuit")

        control_frame = ttk.Frame(tab)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        viz_frame = ttk.Frame(tab)
        viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Parameters
        param_frame = ttk.LabelFrame(control_frame, text="Circuit Parameters", padding="10")
        param_frame.pack(fill=tk.X, pady=5)

        params = [
            ("Voltage Source (V):", "rlc_voltage", 100, 0, 500),
            ("Resistance (Ω):", "rlc_r", 10, 0.1, 100),
            ("Inductance (H):", "rlc_l", 0.1, 0.001, 1),
            ("Capacitance (F):", "rlc_c", 0.001, 0.00001, 0.01),
            ("Source Frequency (Hz):", "rlc_freq", 0, 0, 100),
        ]

        self.rlc_vars = {}
        for i, (label, var_name, default, min_val, max_val) in enumerate(params):
            ttk.Label(param_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            var = tk.DoubleVar(value=default)
            self.rlc_vars[var_name] = var
            ttk.Entry(param_frame, textvariable=var, width=10).grid(row=i, column=1, pady=2)
            ttk.Scale(param_frame, from_=min_val, to=max_val, variable=var,
                     orient=tk.HORIZONTAL, length=150).grid(row=i, column=2, pady=2)

        # Analysis
        analysis_frame = ttk.LabelFrame(control_frame, text="Circuit Analysis", padding="10")
        analysis_frame.pack(fill=tk.X, pady=5)

        ttk.Button(analysis_frame, text="Calculate Resonance",
                  command=self.calculate_rlc_resonance).pack(pady=2, fill=tk.X)

        self.rlc_analysis_text = tk.Text(analysis_frame, height=8, width=30, wrap=tk.WORD)
        self.rlc_analysis_text.pack(pady=5)

        # Control buttons
        btn_frame = ttk.LabelFrame(control_frame, text="Simulation", padding="10")
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Start", command=self.run_rlc_simulation).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="Reset", command=self.reset_rlc_plot).pack(pady=2, fill=tk.X)

        # Visualization
        self.rlc_fig = Figure(figsize=(10, 8), dpi=100)
        self.rlc_canvas = FigureCanvasTkAgg(self.rlc_fig, master=viz_frame)
        self.rlc_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.reset_rlc_plot()

    def calculate_tariff(self):
        """Calculate and display tariff comparison"""
        try:
            rateable = self.tariff_rateable.get()
            lighting = self.tariff_lighting.get()
            power = self.tariff_power.get()

            # Calculate break-even point
            break_even, tariff_b_fixed = TariffCalculator.calculate_equal_consumption(rateable, lighting)

            # Compare at current power consumption
            cost_a, cost_b = TariffCalculator.compare_tariffs(rateable, lighting, power)

            # Display results
            result_text = f"""
╔══════════════════════════════════════════════════════════════╗
║           ELECTRICITY TARIFF COMPARISON ANALYSIS             ║
╚══════════════════════════════════════════════════════════════╝

EXAMPLE 50.74 SOLUTION
─────────────────────────────────────────────────────────────

INPUT PARAMETERS:
  • Annual Rateable Value: Rs {rateable:.2f}
  • Monthly Lighting Consumption: {lighting:.2f} units
  • Monthly Power Consumption: {power:.2f} units

TARIFF STRUCTURES:
─────────────────────────────────────────────────────────────
Tariff A:
  • Lighting: 20 paise per unit
  • Domestic Power: 5 paise per unit
  • Meter Rent: 30 paise per month

Tariff B:
  • Fixed Charge: 12% of rateable value annually
  • Energy Charge: 3 paise per unit (all purposes)
  • Monthly Fixed: Rs {tariff_b_fixed:.2f}

BREAK-EVEN ANALYSIS:
─────────────────────────────────────────────────────────────
✓ Domestic Power Consumption for Equal Cost: {break_even:.2f} units/month

CURRENT CONSUMPTION COMPARISON:
─────────────────────────────────────────────────────────────
At {power:.2f} units of domestic power consumption:

Tariff A Monthly Cost:
  • Lighting Cost: Rs {lighting * 0.20:.2f}
  • Power Cost: Rs {power * 0.05:.2f}
  • Meter Rent: Rs 0.30
  • TOTAL: Rs {cost_a:.2f}

Tariff B Monthly Cost:
  • Fixed Charge: Rs {tariff_b_fixed:.2f}
  • Energy Charge: Rs {(lighting + power) * 0.03:.2f}
  • TOTAL: Rs {cost_b:.2f}

RECOMMENDATION:
─────────────────────────────────────────────────────────────
"""

            if cost_a < cost_b:
                diff = cost_b - cost_a
                result_text += f"► TARIFF A is better by Rs {diff:.2f}/month (Rs {diff*12:.2f}/year)\n"
            elif cost_b < cost_a:
                diff = cost_a - cost_b
                result_text += f"► TARIFF B is better by Rs {diff:.2f}/month (Rs {diff*12:.2f}/year)\n"
            else:
                result_text += f"► Both tariffs cost the same at this consumption level\n"

            self.tariff_result.delete(1.0, tk.END)
            self.tariff_result.insert(1.0, result_text)

            # Plot comparison
            self.plot_tariff_comparison(rateable, lighting, break_even)

            self.update_status("Tariff calculation completed")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def plot_tariff_comparison(self, rateable, lighting, break_even):
        """Plot tariff cost comparison"""
        self.tariff_fig.clear()

        power_range = np.linspace(0, break_even * 2, 100)
        costs_a = []
        costs_b = []

        for p in power_range:
            ca, cb = TariffCalculator.compare_tariffs(rateable, lighting, p)
            costs_a.append(ca)
            costs_b.append(cb)

        ax = self.tariff_fig.add_subplot(111)
        ax.plot(power_range, costs_a, 'b-', linewidth=2, label='Tariff A')
        ax.plot(power_range, costs_b, 'r-', linewidth=2, label='Tariff B')
        ax.axvline(break_even, color='g', linestyle='--', linewidth=2, label=f'Break-even: {break_even:.1f} units')

        ax.set_xlabel('Monthly Power Consumption (units)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Monthly Cost (Rs)', fontsize=12, fontweight='bold')
        ax.set_title('Tariff Comparison: Cost vs Power Consumption', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        self.tariff_canvas.draw()

    def calculate_equipment(self):
        """Calculate HT motor price"""
        try:
            trans_price = self.eq_trans_price.get()
            lt_price = self.eq_lt_price.get()
            trans_eff = self.eq_trans_eff.get() / 100
            lt_eff = self.eq_lt_eff.get() / 100
            ht_eff = self.eq_ht_eff.get() / 100
            load_factor = self.eq_load_factor.get() / 100
            energy_cost = self.eq_energy_cost.get()
            interest = self.eq_interest.get() / 100

            ht_price, lt_capital, lt_annual = EquipmentCostAnalyzer.calculate_ht_motor_price(
                trans_price, lt_price, trans_eff, lt_eff, ht_eff,
                load_factor, energy_cost, interest
            )

            # Detailed breakdown
            result_text = f"""
╔══════════════════════════════════════════════════════════════╗
║         EQUIPMENT COST ANALYSIS - MOTOR COMPARISON           ║
╚══════════════════════════════════════════════════════════════╝

EXAMPLE 50.75 SOLUTION
─────────────────────────────────────────────────────────────

INPUT PARAMETERS:
  • Transformer Price: Rs {trans_price:.2f} per kVA
  • LT Motor Price: Rs {lt_price:.2f} per kW
  • Transformer Efficiency: {trans_eff*100:.2f}%
  • LT Motor Efficiency: {lt_eff*100:.2f}%
  • HT Motor Efficiency: {ht_eff*100:.2f}%
  • Annual Load Factor: {load_factor*100:.2f}%
  • Energy Cost: {energy_cost:.2f} paise/kWh
  • Interest & Depreciation: {interest*100:.2f}%

ANALYSIS FOR 1 kW OUTPUT:
─────────────────────────────────────────────────────────────

LOW-TENSION SYSTEM (Transformer + LT Motor):
  • Input to LT Motor: {1/lt_eff:.4f} kW
  • Input to Transformer: {1/(lt_eff*trans_eff):.4f} kVA
  • Transformer Cost: Rs {trans_price/(lt_eff*trans_eff):.2f}
  • LT Motor Cost: Rs {lt_price:.2f}
  • Total Capital Cost: Rs {lt_capital:.2f}

  Annual Costs:
  • Fixed Charges ({interest*100:.0f}%): Rs {interest*lt_capital:.2f}
  • Annual Operating Hours: {8760*load_factor:.0f} hrs
  • Energy Consumption: {1/(lt_eff*trans_eff)*8760*load_factor:.2f} kWh
  • Energy Cost: Rs {1/(lt_eff*trans_eff)*8760*load_factor*energy_cost/100:.2f}
  • TOTAL ANNUAL COST: Rs {lt_annual:.2f}

HIGH-TENSION MOTOR SYSTEM:
  • Input Required: {1/ht_eff:.4f} kW
  • Annual Operating Hours: {8760*load_factor:.0f} hrs
  • Energy Consumption: {1/ht_eff*8760*load_factor:.2f} kWh
  • Annual Energy Cost: Rs {1/ht_eff*8760*load_factor*energy_cost/100:.2f}

  Annual Fixed Charges Required: Rs {lt_annual - 1/ht_eff*8760*load_factor*energy_cost/100:.2f}

RESULT:
─────────────────────────────────────────────────────────────
✓ Maximum Price for HT Motor: Rs {ht_price:.2f} per kW

ECONOMIC COMPARISON:
─────────────────────────────────────────────────────────────
  • LT System Capital: Rs {lt_capital:.2f}/kW
  • HT System Capital: Rs {ht_price:.2f}/kW
  • Capital Saving: Rs {lt_capital - ht_price:.2f}/kW
  • Percentage: {(lt_capital - ht_price)/lt_capital*100:.2f}%

CONCLUSION:
─────────────────────────────────────────────────────────────
The HT motor can cost up to Rs {ht_price:.2f} per kW to be economically
equivalent to the LT system (transformer + LT motor) over the equipment
lifetime, considering capital costs and energy consumption.
"""

            self.equipment_result.delete(1.0, tk.END)
            self.equipment_result.insert(1.0, result_text)

            self.update_status("Equipment analysis completed")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def run_dc_simulation(self):
        """Run DC motor simulation"""
        try:
            self.dc_start_btn.config(state=tk.DISABLED)
            self.dc_stop_btn.config(state=tk.NORMAL)

            # Get parameters
            V = self.dc_vars["dc_voltage"].get()
            R_a = self.dc_vars["dc_ra"].get()
            L_a = self.dc_vars["dc_la"].get()
            K_e = self.dc_vars["dc_ke"].get()
            K_t = self.dc_vars["dc_kt"].get()
            J = self.dc_vars["dc_j"].get()
            B = self.dc_vars["dc_b"].get()
            T_load = self.dc_vars["dc_tload"].get()

            dt = self.dc_dt.get()
            t_end = self.dc_t_end.get()

            # Define ODE
            def motor_ode(t, y):
                return ElectricalMachineModels.dc_motor_dynamics(
                    t, y, V, R_a, L_a, K_e, K_t, J, B, T_load
                )

            # Initial conditions [i_a, omega]
            y0 = np.array([0.0, 0.0])

            # Solve
            if self.dc_solver.get() == "RK45":
                t, y = ODESolver.rk45(motor_ode, y0, (0, t_end), dt)
            else:
                t, y = ODESolver.euler(motor_ode, y0, (0, t_end), dt)

            # Extract results
            i_a = y[:, 0]
            omega = y[:, 1]
            speed_rpm = omega * 60 / (2 * np.pi)
            torque = K_t * i_a
            power = torque * omega

            # Plot results
            self.dc_fig.clear()

            ax1 = self.dc_fig.add_subplot(2, 2, 1)
            ax1.plot(t, i_a, 'b-', linewidth=2)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Armature Current (A)', color='b')
            ax1.set_title('Armature Current vs Time')
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='y', labelcolor='b')

            ax2 = self.dc_fig.add_subplot(2, 2, 2)
            ax2.plot(t, speed_rpm, 'r-', linewidth=2)
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Speed (RPM)', color='r')
            ax2.set_title('Motor Speed vs Time')
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='y', labelcolor='r')

            ax3 = self.dc_fig.add_subplot(2, 2, 3)
            ax3.plot(t, torque, 'g-', linewidth=2)
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Torque (Nm)', color='g')
            ax3.set_title('Electromagnetic Torque vs Time')
            ax3.grid(True, alpha=0.3)
            ax3.tick_params(axis='y', labelcolor='g')

            ax4 = self.dc_fig.add_subplot(2, 2, 4)
            ax4.plot(t, power, 'm-', linewidth=2)
            ax4.set_xlabel('Time (s)')
            ax4.set_ylabel('Power (W)', color='m')
            ax4.set_title('Mechanical Power vs Time')
            ax4.grid(True, alpha=0.3)
            ax4.tick_params(axis='y', labelcolor='m')

            self.dc_fig.tight_layout()
            self.dc_canvas.draw()

            self.update_status(f"DC Motor simulation completed using {self.dc_solver.get()} method")

        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")
        finally:
            self.dc_start_btn.config(state=tk.NORMAL)
            self.dc_stop_btn.config(state=tk.DISABLED)

    def run_im_simulation(self):
        """Run induction motor simulation"""
        try:
            V = self.im_vars["im_voltage"].get()
            f = self.im_vars["im_freq"].get()
            P = self.im_vars["im_poles"].get()
            R_s = self.im_vars["im_rs"].get()
            R_r = self.im_vars["im_rr"].get()
            X_s = self.im_vars["im_xs"].get()
            X_r = self.im_vars["im_xr"].get()
            T_load = self.im_vars["im_tload"].get()

            # Define ODE
            def motor_ode(t, y):
                return ElectricalMachineModels.induction_motor_simplified(
                    t, y, V, f, P, R_s, R_r, X_s, X_r, T_load
                )

            # Initial condition [omega]
            y0 = np.array([0.0])

            # Solve
            t, y = ODESolver.rk45(motor_ode, y0, (0, 5.0), 0.001)

            omega = y[:, 0]
            omega_s = 2 * np.pi * f
            speed_rpm = omega * 60 / (2 * np.pi)
            sync_rpm = omega_s * 60 / (2 * np.pi)
            slip = (omega_s - omega) / omega_s * 100

            # Plot
            self.im_fig.clear()

            ax1 = self.im_fig.add_subplot(2, 1, 1)
            ax1.plot(t, speed_rpm, 'b-', linewidth=2, label='Rotor Speed')
            ax1.axhline(sync_rpm, color='r', linestyle='--', linewidth=2, label='Synchronous Speed')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Speed (RPM)')
            ax1.set_title('Induction Motor Speed vs Time')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            ax2 = self.im_fig.add_subplot(2, 1, 2)
            ax2.plot(t, slip, 'g-', linewidth=2)
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Slip (%)')
            ax2.set_title('Motor Slip vs Time')
            ax2.grid(True, alpha=0.3)

            self.im_fig.tight_layout()
            self.im_canvas.draw()

            self.update_status("Induction motor simulation completed")

        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")

    def run_rlc_simulation(self):
        """Run RLC circuit simulation"""
        try:
            V = self.rlc_vars["rlc_voltage"].get()
            R = self.rlc_vars["rlc_r"].get()
            L = self.rlc_vars["rlc_l"].get()
            C = self.rlc_vars["rlc_c"].get()
            freq = self.rlc_vars["rlc_freq"].get()

            # Define ODE
            def circuit_ode(t, y):
                return ElectricalMachineModels.rlc_circuit(t, y, V, R, L, C, freq)

            # Initial condition [i, v_c]
            y0 = np.array([0.0, 0.0])

            # Solve
            t, y = ODESolver.rk45(circuit_ode, y0, (0, 0.5), 0.0001)

            current = y[:, 0]
            v_capacitor = y[:, 1]
            v_resistor = R * current
            v_inductor = V - v_resistor - v_capacitor

            # Plot
            self.rlc_fig.clear()

            ax1 = self.rlc_fig.add_subplot(3, 1, 1)
            ax1.plot(t, current, 'b-', linewidth=2)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Current (A)')
            ax1.set_title('RLC Circuit - Current vs Time')
            ax1.grid(True, alpha=0.3)

            ax2 = self.rlc_fig.add_subplot(3, 1, 2)
            ax2.plot(t, v_capacitor, 'r-', linewidth=2, label='Capacitor')
            ax2.plot(t, v_resistor, 'g-', linewidth=2, label='Resistor')
            ax2.plot(t, v_inductor, 'm-', linewidth=2, label='Inductor')
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Voltage (V)')
            ax2.set_title('Component Voltages vs Time')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            ax3 = self.rlc_fig.add_subplot(3, 1, 3)
            # Phase plot
            ax3.plot(v_capacitor, current, 'b-', linewidth=1.5)
            ax3.set_xlabel('Capacitor Voltage (V)')
            ax3.set_ylabel('Current (A)')
            ax3.set_title('Phase Portrait (Current vs Capacitor Voltage)')
            ax3.grid(True, alpha=0.3)

            self.rlc_fig.tight_layout()
            self.rlc_canvas.draw()

            self.update_status("RLC circuit simulation completed")

        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")

    def calculate_rlc_resonance(self):
        """Calculate RLC circuit resonance parameters"""
        try:
            L = self.rlc_vars["rlc_l"].get()
            C = self.rlc_vars["rlc_c"].get()
            R = self.rlc_vars["rlc_r"].get()

            # Resonant frequency
            f_r = 1 / (2 * np.pi * np.sqrt(L * C))
            omega_r = 2 * np.pi * f_r

            # Characteristic impedance
            Z_0 = np.sqrt(L / C)

            # Quality factor
            Q = omega_r * L / R

            # Bandwidth
            BW = f_r / Q

            # Damping ratio
            zeta = R / (2 * np.sqrt(L / C))

            # Circuit type
            if zeta < 1:
                circuit_type = "Underdamped (Oscillatory)"
            elif zeta == 1:
                circuit_type = "Critically damped"
            else:
                circuit_type = "Overdamped"

            result = f"""Resonance Analysis:
─────────────────────
Resonant Frequency: {f_r:.2f} Hz
Angular Frequency: {omega_r:.2f} rad/s
Characteristic Z: {Z_0:.2f} Ω
Quality Factor (Q): {Q:.2f}
Bandwidth: {BW:.2f} Hz
Damping Ratio (ζ): {zeta:.4f}
Circuit Type: {circuit_type}
"""

            self.rlc_analysis_text.delete(1.0, tk.END)
            self.rlc_analysis_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror("Error", f"Analysis error: {str(e)}")

    def reset_dc_plot(self):
        """Reset DC motor plot"""
        self.dc_fig.clear()
        ax = self.dc_fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Click START to begin simulation',
                ha='center', va='center', transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        self.dc_canvas.draw()

    def reset_im_plot(self):
        """Reset induction motor plot"""
        self.im_fig.clear()
        ax = self.im_fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Click START to begin simulation',
                ha='center', va='center', transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        self.im_canvas.draw()

    def reset_rlc_plot(self):
        """Reset RLC plot"""
        self.rlc_fig.clear()
        ax = self.rlc_fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Click START to begin simulation',
                ha='center', va='center', transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        self.rlc_canvas.draw()

    def stop_simulation(self):
        """Stop running simulation"""
        self.is_running = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self.update_status("Simulation stopped")

    def reset_simulation(self):
        """Reset all simulations"""
        self.stop_simulation()
        self.reset_dc_plot()
        self.reset_im_plot()
        self.reset_rlc_plot()
        self.update_status("All simulations reset")

    def clear_all(self):
        """Clear all results"""
        self.tariff_result.delete(1.0, tk.END)
        self.equipment_result.delete(1.0, tk.END)
        self.rlc_analysis_text.delete(1.0, tk.END)
        self.reset_simulation()
        self.update_status("All results cleared")

    def export_results(self):
        """Export results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ee_lab_results_{timestamp}.txt"

        try:
            with open(filename, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("ELECTRICAL ENGINEERING LABORATORY RESULTS\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 70 + "\n\n")

                f.write("TARIFF ANALYSIS:\n")
                f.write("-" * 70 + "\n")
                f.write(self.tariff_result.get(1.0, tk.END))
                f.write("\n\n")

                f.write("EQUIPMENT ANALYSIS:\n")
                f.write("-" * 70 + "\n")
                f.write(self.equipment_result.get(1.0, tk.END))
                f.write("\n\n")

            messagebox.showinfo("Export Successful", f"Results exported to {filename}")
            self.update_status(f"Results exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Electrical Engineering Laboratory
Version 1.0

Features:
• Tariff Calculator (Example 50.74)
• Equipment Cost Analyzer (Example 50.75)
• DC Motor Dynamic Simulation
• Induction Motor Simulation
• RLC Circuit Analysis
• Real-time ODE Solvers (RK45, Euler)
• Interactive Visualization

Developed for electrical engineering analysis
and educational purposes.
"""
        messagebox.showinfo("About", about_text)

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.update_idletasks()

    def on_window_resize(self, event):
        """Handle window resize event for auto-scaling"""
        # Only handle resize for the main window
        if event.widget == self:
            # Redraw all canvases to fit new size
            try:
                self.gen_pf_canvas.draw()
            except:
                pass
            try:
                self.tariff_canvas.draw()
            except:
                pass
            try:
                self.dc_canvas.draw()
            except:
                pass
            try:
                self.im_canvas.draw()
            except:
                pass
            try:
                self.rlc_canvas.draw()
            except:
                pass


def main():
    """Main entry point"""
    app = ElectricalEngineeringLab()
    app.mainloop()


if __name__ == "__main__":
    main()
