"""
Advanced Power Factor Billing Calculator and Electrical System Simulator
Includes:
- Power Factor Correction Analysis
- Dynamic Motor Simulation with ODE Solvers
- Real-time Visualization
- Professional Tkinter GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import math
from scipy.integrate import solve_ivp
import threading
import time


class PowerFactorCalculator:
    """Calculate power factor correction savings"""

    def __init__(self):
        self.reset_values()

    def reset_values(self):
        """Reset all calculation values"""
        self.voltage = 460.0  # Volts
        self.power_rate = 7.50  # Rs per kVA per month
        self.original_pf = 0.745
        self.original_kva = 611.0  # kVA
        self.capacitor_kvar = 210.0  # kVAR
        self.installation_cost = 11600.0  # Rs
        self.fixed_charges_rate = 0.15  # 15% per year

    def calculate_savings(self):
        """Calculate yearly savings from power factor correction"""
        # Original real power (kW)
        original_kw = self.original_kva * self.original_pf

        # Original reactive power (kVAR)
        original_angle = math.acos(self.original_pf)
        original_kvar = self.original_kva * math.sin(original_angle)

        # New reactive power after capacitor installation
        new_kvar = original_kvar - self.capacitor_kvar

        # New apparent power (kVA)
        new_kva = math.sqrt(original_kw**2 + new_kvar**2)

        # New power factor
        new_pf = original_kw / new_kva if new_kva > 0 else 1.0

        # Monthly costs
        original_monthly_cost = self.original_kva * self.power_rate
        new_monthly_cost = new_kva * self.power_rate
        monthly_savings = original_monthly_cost - new_monthly_cost

        # Yearly savings from reduced demand
        yearly_savings = monthly_savings * 12

        # Annual fixed charges for capacitor equipment
        annual_fixed_charges = self.installation_cost * self.fixed_charges_rate

        # Net yearly savings
        net_yearly_savings = yearly_savings - annual_fixed_charges

        # Payback period
        payback_period = self.installation_cost / yearly_savings if yearly_savings > 0 else 0

        return {
            'original_kw': original_kw,
            'original_kvar': original_kvar,
            'original_kva': self.original_kva,
            'original_pf': self.original_pf,
            'new_kvar': new_kvar,
            'new_kva': new_kva,
            'new_pf': new_pf,
            'original_monthly_cost': original_monthly_cost,
            'new_monthly_cost': new_monthly_cost,
            'monthly_savings': monthly_savings,
            'yearly_savings': yearly_savings,
            'annual_fixed_charges': annual_fixed_charges,
            'net_yearly_savings': net_yearly_savings,
            'payback_period': payback_period
        }


class MotorDynamicsSimulator:
    """Simulate induction motor dynamics using differential equations"""

    def __init__(self):
        self.reset_parameters()

    def reset_parameters(self):
        """Reset motor parameters to default values"""
        # Motor parameters
        self.Rs = 0.5  # Stator resistance (Ohms)
        self.Rr = 0.3  # Rotor resistance (Ohms)
        self.Ls = 0.05  # Stator inductance (H)
        self.Lr = 0.05  # Rotor inductance (H)
        self.Lm = 0.045  # Mutual inductance (H)
        self.J = 0.05  # Moment of inertia (kg·m²)
        self.B = 0.01  # Friction coefficient
        self.P = 2  # Number of pole pairs
        self.Vs = 400  # Supply voltage (V)
        self.frequency = 50  # Supply frequency (Hz)
        self.load_torque = 5.0  # Load torque (N·m)

    def motor_equations(self, t, y):
        """
        Differential equations for induction motor dynamics
        State variables: [ids, iqs, idr, iqr, omega]
        ids, iqs: d-q axis stator currents
        idr, iqr: d-q axis rotor currents
        omega: rotor angular velocity
        """
        ids, iqs, idr, iqr, omega = y

        # Angular frequency
        omega_s = 2 * math.pi * self.frequency

        # Voltage equations (simplified d-q model)
        Vds = self.Vs * math.cos(omega_s * t)
        Vqs = self.Vs * math.sin(omega_s * t)

        # Electromagnetic torque
        Te = (3/2) * self.P * self.Lm * (iqs * idr - ids * iqr)

        # Differential equations
        Ls_sigma = self.Ls - (self.Lm**2 / self.Lr)
        Lr_sigma = self.Lr - (self.Lm**2 / self.Ls)

        dids_dt = (Vds - self.Rs * ids - self.Lm * (self.Rr * idr / self.Lr)) / Ls_sigma
        diqs_dt = (Vqs - self.Rs * iqs - self.Lm * (self.Rr * iqr / self.Lr)) / Ls_sigma
        didr_dt = (self.Lm * self.Rs * ids / self.Ls - self.Rr * idr - (omega_s - omega) * self.Lr * iqr) / Lr_sigma
        diqr_dt = (self.Lm * self.Rs * iqs / self.Ls - self.Rr * iqr + (omega_s - omega) * self.Lr * idr) / Lr_sigma
        domega_dt = (Te - self.load_torque - self.B * omega) / self.J

        return [dids_dt, diqs_dt, didr_dt, diqr_dt, domega_dt]

    def euler_method(self, t_span, y0, dt=0.001):
        """Euler method for solving ODEs"""
        t0, tf = t_span
        t = np.arange(t0, tf, dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(1, len(t)):
            dydt = self.motor_equations(t[i-1], y[i-1])
            y[i] = y[i-1] + dt * np.array(dydt)

        return t, y

    def rk45_method(self, t_span, y0):
        """RK45 (Runge-Kutta 4-5) method using scipy"""
        sol = solve_ivp(self.motor_equations, t_span, y0, method='RK45',
                       dense_output=True, max_step=0.001)
        return sol.t, sol.y.T


class ElectricalEngineeringGUI:
    """Main GUI Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Electrical Engineering Analysis Tool")
        self.root.geometry("1400x900")

        # Initialize calculators
        self.pf_calc = PowerFactorCalculator()
        self.motor_sim = MotorDynamicsSimulator()

        # Simulation control
        self.is_simulating = False
        self.simulation_thread = None

        # Setup GUI
        self.setup_styles()
        self.create_widgets()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'), foreground='#34495e')
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))

    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Power Factor Calculator
        self.create_pf_tab()

        # Tab 2: Motor Dynamics Simulation
        self.create_motor_sim_tab()

        # Tab 3: About
        self.create_about_tab()

    def create_pf_tab(self):
        """Create Power Factor Calculator tab"""
        pf_frame = ttk.Frame(self.notebook)
        self.notebook.add(pf_frame, text='Power Factor Correction')

        # Left panel - Inputs
        left_frame = ttk.Frame(pf_frame)
        left_frame.pack(side='left', fill='both', expand=False, padx=10, pady=10)

        ttk.Label(left_frame, text="Power Factor Correction Calculator",
                 style='Title.TLabel').pack(pady=10)

        # Input fields
        input_frame = ttk.LabelFrame(left_frame, text="Input Parameters", padding=10)
        input_frame.pack(fill='x', pady=5)

        self.pf_inputs = {}

        params = [
            ('Voltage (V):', 'voltage', 460.0, 100, 1000),
            ('Power Rate (Rs/kVA/month):', 'power_rate', 7.50, 1.0, 20.0),
            ('Original Power Factor:', 'original_pf', 0.745, 0.5, 1.0),
            ('Original Demand (kVA):', 'original_kva', 611.0, 100, 2000),
            ('Capacitor Rating (kVAR):', 'capacitor_kvar', 210.0, 50, 500),
            ('Installation Cost (Rs):', 'installation_cost', 11600.0, 1000, 100000),
            ('Fixed Charges Rate (%):', 'fixed_charges_rate', 15.0, 1, 30)
        ]

        for i, (label, key, default, min_val, max_val) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)

            var = tk.DoubleVar(value=default)
            self.pf_inputs[key] = var

            slider = ttk.Scale(input_frame, from_=min_val, to=max_val,
                              variable=var, orient='horizontal', length=200)
            slider.grid(row=i, column=1, padx=5, pady=5)

            entry = ttk.Entry(input_frame, textvariable=var, width=10)
            entry.grid(row=i, column=2, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Calculate", command=self.calculate_pf,
                  style='Action.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_pf).pack(side='left', padx=5)

        # Right panel - Results
        right_frame = ttk.Frame(pf_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Analysis Results",
                 style='Title.TLabel').pack(pady=10)

        # Results text area
        self.pf_results = scrolledtext.ScrolledText(right_frame, width=60, height=20,
                                                    font=('Courier', 10))
        self.pf_results.pack(fill='both', expand=True, pady=5)

        # Visualization
        viz_frame = ttk.LabelFrame(right_frame, text="Power Triangle Comparison", padding=5)
        viz_frame.pack(fill='both', expand=True, pady=5)

        self.pf_fig = Figure(figsize=(8, 4), dpi=80)
        self.pf_canvas = FigureCanvasTkAgg(self.pf_fig, viz_frame)
        self.pf_canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_motor_sim_tab(self):
        """Create Motor Dynamics Simulation tab"""
        motor_frame = ttk.Frame(self.notebook)
        self.notebook.add(motor_frame, text='Motor Dynamics Simulation')

        # Control panel
        control_frame = ttk.Frame(motor_frame)
        control_frame.pack(side='top', fill='x', padx=10, pady=5)

        ttk.Label(control_frame, text="Induction Motor Dynamic Simulation",
                 style='Title.TLabel').pack(pady=5)

        # Parameters
        param_frame = ttk.LabelFrame(control_frame, text="Motor Parameters", padding=10)
        param_frame.pack(fill='x', pady=5)

        self.motor_inputs = {}

        motor_params = [
            ('Stator Resistance Rs (Ω):', 'Rs', 0.5, 0.1, 5.0),
            ('Rotor Resistance Rr (Ω):', 'Rr', 0.3, 0.1, 5.0),
            ('Stator Inductance Ls (H):', 'Ls', 0.05, 0.01, 0.2),
            ('Rotor Inductance Lr (H):', 'Lr', 0.05, 0.01, 0.2),
            ('Mutual Inductance Lm (H):', 'Lm', 0.045, 0.01, 0.2),
            ('Inertia J (kg·m²):', 'J', 0.05, 0.01, 1.0),
            ('Friction B:', 'B', 0.01, 0.001, 0.1),
            ('Supply Voltage Vs (V):', 'Vs', 400, 100, 1000),
            ('Frequency (Hz):', 'frequency', 50, 25, 100),
            ('Load Torque (N·m):', 'load_torque', 5.0, 0, 50)
        ]

        for i, (label, key, default, min_val, max_val) in enumerate(motor_params):
            row = i // 2
            col = (i % 2) * 3

            ttk.Label(param_frame, text=label).grid(row=row, column=col, sticky='w', padx=5, pady=3)

            var = tk.DoubleVar(value=default)
            self.motor_inputs[key] = var

            slider = ttk.Scale(param_frame, from_=min_val, to=max_val,
                              variable=var, orient='horizontal', length=150)
            slider.grid(row=row, column=col+1, padx=5, pady=3)

            entry = ttk.Entry(param_frame, textvariable=var, width=8)
            entry.grid(row=row, column=col+2, padx=5, pady=3)

        # Simulation controls
        sim_control_frame = ttk.Frame(control_frame)
        sim_control_frame.pack(pady=10)

        ttk.Label(sim_control_frame, text="Solver Method:").pack(side='left', padx=5)
        self.solver_method = tk.StringVar(value='RK45')
        ttk.Radiobutton(sim_control_frame, text="RK45 (Adaptive)",
                       variable=self.solver_method, value='RK45').pack(side='left', padx=5)
        ttk.Radiobutton(sim_control_frame, text="Euler (Fixed Step)",
                       variable=self.solver_method, value='Euler').pack(side='left', padx=5)

        ttk.Label(sim_control_frame, text="Simulation Time (s):").pack(side='left', padx=5)
        self.sim_time = tk.DoubleVar(value=2.0)
        ttk.Entry(sim_control_frame, textvariable=self.sim_time, width=8).pack(side='left', padx=5)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=5)

        self.start_btn = ttk.Button(button_frame, text="▶ Start",
                                    command=self.start_simulation, style='Action.TButton')
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏸ Stop",
                                   command=self.stop_simulation, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        ttk.Button(button_frame, text="↻ Reset",
                  command=self.reset_motor_sim).pack(side='left', padx=5)

        # Visualization
        plot_frame = ttk.Frame(motor_frame)
        plot_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.motor_fig = Figure(figsize=(12, 8), dpi=100)
        self.motor_canvas = FigureCanvasTkAgg(self.motor_fig, plot_frame)
        self.motor_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.motor_canvas, plot_frame)
        toolbar.update()

    def create_about_tab(self):
        """Create About tab"""
        about_frame = ttk.Frame(self.notebook)
        self.notebook.add(about_frame, text='About')

        about_text = """
        Advanced Electrical Engineering Analysis Tool
        ============================================

        This application provides professional-grade tools for electrical engineering analysis:

        1. POWER FACTOR CORRECTION CALCULATOR
           - Analyzes billing savings from power factor improvement
           - Calculates optimal capacitor sizing
           - Determines payback period for capacitor investment
           - Visualizes power triangle before and after correction

        2. MOTOR DYNAMICS SIMULATION
           - Simulates three-phase induction motor behavior
           - Solves differential equations using multiple methods:
             * RK45 (Runge-Kutta 4-5): Adaptive step size, high accuracy
             * Euler Method: Fixed step size, educational purposes
           - Visualizes:
             * Rotor speed vs time
             * Electromagnetic torque
             * Stator and rotor currents (d-q components)
             * Phase portraits

        FEATURES:
        ✓ Real-time ODE solver visualization
        ✓ Adjustable parameters with sliders
        ✓ Auto-scaling plots
        ✓ Professional matplotlib integration
        ✓ Responsive window resizing
        ✓ Comprehensive electrical engineering calculations

        TECHNICAL DETAILS:
        - D-Q axis transformation for motor modeling
        - Three-phase induction motor dynamic equations
        - Economic analysis of power factor correction
        - Real-time numerical integration

        VERSION: 1.0
        CREATED: 2025

        For educational and professional use in electrical engineering.
        """

        text_widget = scrolledtext.ScrolledText(about_frame, wrap=tk.WORD,
                                               font=('Arial', 10), padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', about_text)
        text_widget.config(state='disabled')

    def calculate_pf(self):
        """Calculate power factor correction savings"""
        try:
            # Update calculator parameters
            self.pf_calc.voltage = self.pf_inputs['voltage'].get()
            self.pf_calc.power_rate = self.pf_inputs['power_rate'].get()
            self.pf_calc.original_pf = self.pf_inputs['original_pf'].get()
            self.pf_calc.original_kva = self.pf_inputs['original_kva'].get()
            self.pf_calc.capacitor_kvar = self.pf_inputs['capacitor_kvar'].get()
            self.pf_calc.installation_cost = self.pf_inputs['installation_cost'].get()
            self.pf_calc.fixed_charges_rate = self.pf_inputs['fixed_charges_rate'].get() / 100

            # Calculate
            results = self.pf_calc.calculate_savings()

            # Display results
            self.pf_results.delete('1.0', tk.END)

            output = f"""
{'='*70}
           POWER FACTOR CORRECTION ANALYSIS REPORT
{'='*70}

ORIGINAL SYSTEM (Before Capacitor Installation):
{'─'*70}
  Real Power (kW)           : {results['original_kw']:.2f} kW
  Reactive Power (kVAR)     : {results['original_kvar']:.2f} kVAR
  Apparent Power (kVA)      : {results['original_kva']:.2f} kVA
  Power Factor              : {results['original_pf']:.4f} ({results['original_pf']*100:.2f}%)
  Monthly Demand Cost       : Rs. {results['original_monthly_cost']:.2f}

IMPROVED SYSTEM (After Capacitor Installation):
{'─'*70}
  Capacitor Rating          : {self.pf_calc.capacitor_kvar:.2f} kVAR
  New Reactive Power (kVAR) : {results['new_kvar']:.2f} kVAR
  New Apparent Power (kVA)  : {results['new_kva']:.2f} kVA
  New Power Factor          : {results['new_pf']:.4f} ({results['new_pf']*100:.2f}%)
  New Monthly Demand Cost   : Rs. {results['new_monthly_cost']:.2f}

FINANCIAL ANALYSIS:
{'─'*70}
  Monthly Savings           : Rs. {results['monthly_savings']:.2f}
  Yearly Savings (Billing)  : Rs. {results['yearly_savings']:.2f}
  Annual Fixed Charges      : Rs. {results['annual_fixed_charges']:.2f}

  NET YEARLY SAVINGS        : Rs. {results['net_yearly_savings']:.2f}

  Installation Cost         : Rs. {self.pf_calc.installation_cost:.2f}
  Payback Period            : {results['payback_period']:.2f} years

IMPROVEMENTS:
{'─'*70}
  kVA Reduction             : {results['original_kva'] - results['new_kva']:.2f} kVA ({((results['original_kva'] - results['new_kva'])/results['original_kva']*100):.2f}%)
  Power Factor Improvement  : {(results['new_pf'] - results['original_pf'])*100:.2f}%
  Monthly Cost Reduction    : {(results['monthly_savings']/results['original_monthly_cost']*100):.2f}%

{'='*70}
CONCLUSION: The capacitor installation provides a net yearly saving of
Rs. {results['net_yearly_savings']:.2f} and will pay for itself in
{results['payback_period']:.2f} years.
{'='*70}
            """

            self.pf_results.insert('1.0', output)

            # Visualize power triangles
            self.plot_power_triangles(results)

        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error in calculation:\n{str(e)}")

    def plot_power_triangles(self, results):
        """Plot power triangles before and after correction"""
        self.pf_fig.clear()

        # Create subplots
        ax1 = self.pf_fig.add_subplot(121)
        ax2 = self.pf_fig.add_subplot(122)

        # Original power triangle
        kw_orig = results['original_kw']
        kvar_orig = results['original_kvar']
        kva_orig = results['original_kva']

        ax1.arrow(0, 0, kw_orig, 0, head_width=20, head_length=15, fc='blue', ec='blue', linewidth=2)
        ax1.arrow(kw_orig, 0, 0, kvar_orig, head_width=20, head_length=15, fc='red', ec='red', linewidth=2)
        ax1.plot([0, kw_orig], [0, kvar_orig], 'g-', linewidth=2)

        ax1.text(kw_orig/2, -30, f'P = {kw_orig:.1f} kW', ha='center', fontsize=10, fontweight='bold')
        ax1.text(kw_orig+20, kvar_orig/2, f'Q = {kvar_orig:.1f} kVAR', ha='left', fontsize=10, fontweight='bold')
        ax1.text(kw_orig/2-50, kvar_orig/2+20, f'S = {kva_orig:.1f} kVA', ha='center', fontsize=10, fontweight='bold', color='green')
        ax1.text(kw_orig/2, kvar_orig+50, f'PF = {results["original_pf"]:.4f}', ha='center', fontsize=11, fontweight='bold', color='darkred')

        ax1.set_xlim(-50, kva_orig + 100)
        ax1.set_ylim(-50, kvar_orig + 100)
        ax1.set_xlabel('Real Power (kW)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Reactive Power (kVAR)', fontsize=10, fontweight='bold')
        ax1.set_title('BEFORE Correction', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')

        # New power triangle
        kw_new = kw_orig  # Real power unchanged
        kvar_new = results['new_kvar']
        kva_new = results['new_kva']

        ax2.arrow(0, 0, kw_new, 0, head_width=20, head_length=15, fc='blue', ec='blue', linewidth=2)
        ax2.arrow(kw_new, 0, 0, kvar_new, head_width=20, head_length=15, fc='orange', ec='orange', linewidth=2)
        ax2.plot([0, kw_new], [0, kvar_new], 'g-', linewidth=2)

        ax2.text(kw_new/2, -30, f'P = {kw_new:.1f} kW', ha='center', fontsize=10, fontweight='bold')
        ax2.text(kw_new+20, kvar_new/2, f'Q = {kvar_new:.1f} kVAR', ha='left', fontsize=10, fontweight='bold')
        ax2.text(kw_new/2-50, kvar_new/2+20, f'S = {kva_new:.1f} kVA', ha='center', fontsize=10, fontweight='bold', color='green')
        ax2.text(kw_new/2, kvar_new+50, f'PF = {results["new_pf"]:.4f}', ha='center', fontsize=11, fontweight='bold', color='darkgreen')

        # Show capacitor contribution
        ax2.arrow(kw_new, kvar_new, 0, -(kvar_orig - kvar_new), head_width=20, head_length=15,
                 fc='purple', ec='purple', linewidth=2, linestyle='--', alpha=0.7)
        ax2.text(kw_new+40, (kvar_orig+kvar_new)/2, f'Qc = {self.pf_calc.capacitor_kvar:.1f} kVAR',
                ha='left', fontsize=9, fontweight='bold', color='purple')

        ax2.set_xlim(-50, kva_orig + 100)
        ax2.set_ylim(-50, kvar_orig + 100)
        ax2.set_xlabel('Real Power (kW)', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Reactive Power (kVAR)', fontsize=10, fontweight='bold')
        ax2.set_title('AFTER Correction', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')

        self.pf_fig.tight_layout()
        self.pf_canvas.draw()

    def reset_pf(self):
        """Reset power factor calculator"""
        self.pf_calc.reset_values()

        self.pf_inputs['voltage'].set(self.pf_calc.voltage)
        self.pf_inputs['power_rate'].set(self.pf_calc.power_rate)
        self.pf_inputs['original_pf'].set(self.pf_calc.original_pf)
        self.pf_inputs['original_kva'].set(self.pf_calc.original_kva)
        self.pf_inputs['capacitor_kvar'].set(self.pf_calc.capacitor_kvar)
        self.pf_inputs['installation_cost'].set(self.pf_calc.installation_cost)
        self.pf_inputs['fixed_charges_rate'].set(self.pf_calc.fixed_charges_rate * 100)

        self.pf_results.delete('1.0', tk.END)
        self.pf_fig.clear()
        self.pf_canvas.draw()

    def start_simulation(self):
        """Start motor dynamics simulation"""
        if not self.is_simulating:
            self.is_simulating = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')

            # Run simulation in separate thread
            self.simulation_thread = threading.Thread(target=self.run_motor_simulation)
            self.simulation_thread.start()

    def stop_simulation(self):
        """Stop simulation"""
        self.is_simulating = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def run_motor_simulation(self):
        """Run motor simulation"""
        try:
            # Update motor parameters
            self.motor_sim.Rs = self.motor_inputs['Rs'].get()
            self.motor_sim.Rr = self.motor_inputs['Rr'].get()
            self.motor_sim.Ls = self.motor_inputs['Ls'].get()
            self.motor_sim.Lr = self.motor_inputs['Lr'].get()
            self.motor_sim.Lm = self.motor_inputs['Lm'].get()
            self.motor_sim.J = self.motor_inputs['J'].get()
            self.motor_sim.B = self.motor_inputs['B'].get()
            self.motor_sim.Vs = self.motor_inputs['Vs'].get()
            self.motor_sim.frequency = self.motor_inputs['frequency'].get()
            self.motor_sim.load_torque = self.motor_inputs['load_torque'].get()

            # Initial conditions [ids, iqs, idr, iqr, omega]
            y0 = [0.0, 0.0, 0.0, 0.0, 0.0]

            # Time span
            t_span = (0, self.sim_time.get())

            # Solve using selected method
            if self.solver_method.get() == 'RK45':
                t, y = self.motor_sim.rk45_method(t_span, y0)
            else:
                t, y = self.motor_sim.euler_method(t_span, y0, dt=0.0001)

            # Calculate derived quantities
            ids = y[:, 0]
            iqs = y[:, 1]
            idr = y[:, 2]
            iqr = y[:, 3]
            omega = y[:, 4]

            # Electromagnetic torque
            Te = (3/2) * self.motor_sim.P * self.motor_sim.Lm * (iqs * idr - ids * iqr)

            # Stator current magnitude
            Is = np.sqrt(ids**2 + iqs**2)

            # Speed in RPM
            n_rpm = omega * 60 / (2 * np.pi)

            # Plot results
            self.root.after(0, self.plot_motor_results, t, omega, Te, ids, iqs, idr, iqr, Is, n_rpm)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Simulation Error",
                                                            f"Error in simulation:\n{str(e)}"))
        finally:
            self.is_simulating = False
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))

    def plot_motor_results(self, t, omega, Te, ids, iqs, idr, iqr, Is, n_rpm):
        """Plot motor simulation results"""
        self.motor_fig.clear()

        # Create subplots
        gs = self.motor_fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Speed vs time
        ax1 = self.motor_fig.add_subplot(gs[0, :])
        ax1.plot(t, n_rpm, 'b-', linewidth=2, label='Rotor Speed')
        ax1.set_xlabel('Time (s)', fontweight='bold')
        ax1.set_ylabel('Speed (RPM)', fontweight='bold')
        ax1.set_title('Rotor Speed vs Time', fontweight='bold', fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Torque vs time
        ax2 = self.motor_fig.add_subplot(gs[1, 0])
        ax2.plot(t, Te, 'r-', linewidth=2, label='Electromagnetic Torque')
        ax2.axhline(y=self.motor_sim.load_torque, color='g', linestyle='--',
                   linewidth=2, label='Load Torque')
        ax2.set_xlabel('Time (s)', fontweight='bold')
        ax2.set_ylabel('Torque (N·m)', fontweight='bold')
        ax2.set_title('Torque vs Time', fontweight='bold', fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # Stator currents
        ax3 = self.motor_fig.add_subplot(gs[1, 1])
        ax3.plot(t, ids, 'b-', linewidth=1.5, label='ids (d-axis)', alpha=0.8)
        ax3.plot(t, iqs, 'r-', linewidth=1.5, label='iqs (q-axis)', alpha=0.8)
        ax3.plot(t, Is, 'g-', linewidth=2, label='|Is| (magnitude)')
        ax3.set_xlabel('Time (s)', fontweight='bold')
        ax3.set_ylabel('Current (A)', fontweight='bold')
        ax3.set_title('Stator Currents', fontweight='bold', fontsize=11)
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # Rotor currents
        ax4 = self.motor_fig.add_subplot(gs[2, 0])
        ax4.plot(t, idr, 'c-', linewidth=1.5, label='idr (d-axis)', alpha=0.8)
        ax4.plot(t, iqr, 'm-', linewidth=1.5, label='iqr (q-axis)', alpha=0.8)
        Ir = np.sqrt(idr**2 + iqr**2)
        ax4.plot(t, Ir, 'y-', linewidth=2, label='|Ir| (magnitude)')
        ax4.set_xlabel('Time (s)', fontweight='bold')
        ax4.set_ylabel('Current (A)', fontweight='bold')
        ax4.set_title('Rotor Currents', fontweight='bold', fontsize=11)
        ax4.grid(True, alpha=0.3)
        ax4.legend()

        # Phase portrait: Torque vs Speed
        ax5 = self.motor_fig.add_subplot(gs[2, 1])
        ax5.plot(n_rpm, Te, 'purple', linewidth=2)
        ax5.scatter(n_rpm[0], Te[0], c='green', s=100, marker='o',
                   label='Start', zorder=5)
        ax5.scatter(n_rpm[-1], Te[-1], c='red', s=100, marker='s',
                   label='End', zorder=5)
        ax5.set_xlabel('Speed (RPM)', fontweight='bold')
        ax5.set_ylabel('Torque (N·m)', fontweight='bold')
        ax5.set_title('Phase Portrait (Torque-Speed)', fontweight='bold', fontsize=11)
        ax5.grid(True, alpha=0.3)
        ax5.legend()

        self.motor_fig.suptitle(f'Induction Motor Dynamic Simulation - Solver: {self.solver_method.get()}',
                               fontsize=13, fontweight='bold')

        self.motor_canvas.draw()

    def reset_motor_sim(self):
        """Reset motor simulation"""
        self.stop_simulation()

        self.motor_sim.reset_parameters()

        self.motor_inputs['Rs'].set(self.motor_sim.Rs)
        self.motor_inputs['Rr'].set(self.motor_sim.Rr)
        self.motor_inputs['Ls'].set(self.motor_sim.Ls)
        self.motor_inputs['Lr'].set(self.motor_sim.Lr)
        self.motor_inputs['Lm'].set(self.motor_sim.Lm)
        self.motor_inputs['J'].set(self.motor_sim.J)
        self.motor_inputs['B'].set(self.motor_sim.B)
        self.motor_inputs['Vs'].set(self.motor_sim.Vs)
        self.motor_inputs['frequency'].set(self.motor_sim.frequency)
        self.motor_inputs['load_torque'].set(self.motor_sim.load_torque)

        self.motor_fig.clear()
        self.motor_canvas.draw()

    def on_window_resize(self, event):
        """Handle window resize events"""
        # Auto-scale canvases
        if hasattr(self, 'pf_canvas'):
            self.pf_canvas.draw()
        if hasattr(self, 'motor_canvas'):
            self.motor_canvas.draw()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ElectricalEngineeringGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
