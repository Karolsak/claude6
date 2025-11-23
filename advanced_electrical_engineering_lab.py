#!/usr/bin/env python3
"""
Advanced Electrical Engineering Analysis Laboratory
Includes:
- Transformer Cost Analysis
- Dynamic Circuit Simulation (RLC, Transformers, Motors)
- Real-time ODE Solvers (RK45, Euler)
- Interactive Tkinter GUI with Auto-scaling
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from scipy.integrate import solve_ivp
import math


class TransformerCostAnalysis:
    """Analyzes transformer purchase costs including losses and depreciation"""

    def __init__(self, price, no_load_loss, full_load_loss, hours_on_load=12,
                 hours_total=24, energy_cost=0.05, fixed_charge=125, depreciation_rate=0.10):
        self.price = price
        self.no_load_loss = no_load_loss
        self.full_load_loss = full_load_loss
        self.hours_on_load = hours_on_load
        self.hours_total = hours_total
        self.hours_no_load = hours_total - hours_on_load
        self.energy_cost = energy_cost  # Rs per kWh
        self.fixed_charge = fixed_charge  # Rs per kW per annum
        self.depreciation_rate = depreciation_rate

    def calculate_annual_energy_loss_cost(self):
        """Calculate annual cost of energy losses"""
        # No-load loss operates 24 hours
        no_load_energy = self.no_load_loss * self.hours_total * 365  # kWh per year
        # Full-load loss operates only during load hours
        full_load_energy = self.full_load_loss * self.hours_on_load * 365  # kWh per year
        total_energy_loss = no_load_energy + full_load_energy
        return total_energy_loss * self.energy_cost

    def calculate_annual_fixed_charges(self):
        """Calculate annual fixed charges on losses"""
        total_loss = self.no_load_loss + self.full_load_loss
        return total_loss * self.fixed_charge

    def calculate_annual_depreciation(self):
        """Calculate annual depreciation"""
        return self.price * self.depreciation_rate

    def calculate_total_annual_cost(self):
        """Calculate total annual operating cost"""
        energy_cost = self.calculate_annual_energy_loss_cost()
        fixed_cost = self.calculate_annual_fixed_charges()
        depreciation = self.calculate_annual_depreciation()
        return {
            'energy_loss_cost': energy_cost,
            'fixed_charges': fixed_cost,
            'depreciation': depreciation,
            'total': energy_cost + fixed_cost + depreciation
        }


class ODESolver:
    """Base class for ODE solvers"""

    @staticmethod
    def euler(f, y0, t_span, t_eval):
        """Euler method for solving ODEs"""
        t0, tf = t_span
        y = np.array(y0)
        t = t0
        dt = t_eval[1] - t_eval[0] if len(t_eval) > 1 else 0.01

        solution = [y.copy()]
        time_points = [t0]

        for t_next in t_eval[1:]:
            while t < t_next:
                step = min(dt, t_next - t)
                y = y + step * np.array(f(t, y))
                t += step
            solution.append(y.copy())
            time_points.append(t)

        return np.array(time_points), np.array(solution).T

    @staticmethod
    def rk45(f, y0, t_span, t_eval):
        """Runge-Kutta 45 method using scipy"""
        sol = solve_ivp(f, t_span, y0, method='RK45', t_eval=t_eval,
                       dense_output=True, max_step=0.01)
        return sol.t, sol.y


class ElectricalCircuitModels:
    """Collection of electrical engineering differential equation models"""

    @staticmethod
    def rlc_circuit(t, y, R, L, C, V_source_func):
        """
        RLC Circuit differential equations
        y[0] = i (current)
        y[1] = v_c (capacitor voltage)
        """
        i, v_c = y
        V_in = V_source_func(t)

        # di/dt = (V_in - v_c - R*i) / L
        di_dt = (V_in - v_c - R * i) / L
        # dv_c/dt = i / C
        dv_c_dt = i / C

        return [di_dt, dv_c_dt]

    @staticmethod
    def transformer_model(t, y, R1, L1, R2, L2, M, V_in_func, R_load):
        """
        Transformer model with mutual inductance
        y[0] = i1 (primary current)
        y[1] = i2 (secondary current)
        """
        i1, i2 = y
        V_in = V_in_func(t)

        # Transformer equations:
        # V_in = R1*i1 + L1*di1/dt + M*di2/dt
        # 0 = R2*i2 + L2*di2/dt + M*di1/dt + R_load*i2

        # Solving for derivatives:
        det = L1 * L2 - M * M
        di1_dt = (L2 * (V_in - R1 * i1) - M * (-(R2 + R_load) * i2)) / det
        di2_dt = (L1 * (-(R2 + R_load) * i2) - M * (V_in - R1 * i1)) / det

        return [di1_dt, di2_dt]

    @staticmethod
    def dc_motor(t, y, R_a, L_a, K_e, K_t, J, B, V_in_func, T_load):
        """
        DC Motor model
        y[0] = i_a (armature current)
        y[1] = omega (angular velocity)
        """
        i_a, omega = y
        V_in = V_in_func(t)

        # di_a/dt = (V_in - R_a*i_a - K_e*omega) / L_a
        di_a_dt = (V_in - R_a * i_a - K_e * omega) / L_a

        # d_omega/dt = (K_t*i_a - B*omega - T_load) / J
        d_omega_dt = (K_t * i_a - B * omega - T_load) / J

        return [di_a_dt, d_omega_dt]

    @staticmethod
    def rc_charging(t, y, R, C, V_source):
        """Simple RC charging circuit"""
        v_c = y[0]
        dv_c_dt = (V_source - v_c) / (R * C)
        return [dv_c_dt]


class AdvancedElectricalEngineeringLab:
    """Main application class with Tkinter GUI"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Electrical Engineering Analysis Laboratory")
        self.root.geometry("1200x800")

        # Simulation state
        self.simulation_running = False
        self.current_time = 0
        self.animation_id = None

        # Configure grid weight for auto-scaling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main container
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create tabs
        self.create_transformer_cost_tab()
        self.create_rlc_circuit_tab()
        self.create_transformer_simulation_tab()
        self.create_motor_simulation_tab()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        # This will be called on resize - matplotlib canvas will auto-adjust
        pass

    def create_transformer_cost_tab(self):
        """Tab 1: Transformer Cost Analysis"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Transformer Cost Analysis")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Title
        title = ttk.Label(tab, text="Transformer Purchase Cost Analysis",
                         font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, pady=10)

        # Create frames
        input_frame = ttk.LabelFrame(tab, text="Input Parameters", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        results_frame = ttk.LabelFrame(tab, text="Cost Analysis Results", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Input parameters with sliders
        self.transformer_params = {}

        params = [
            ("Hours on Load (per day)", "hours_load", 12, 0, 24, 1),
            ("Energy Cost (Rs/kWh)", "energy_cost", 0.05, 0.01, 1.0, 0.01),
            ("Fixed Charge (Rs/kW/year)", "fixed_charge", 125, 50, 500, 5),
            ("Depreciation Rate (%)", "depreciation_rate", 10, 0, 30, 1)
        ]

        for idx, (label, key, default, min_val, max_val, resolution) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=idx, column=0, sticky=tk.W, pady=5)

            var = tk.DoubleVar(value=default)
            self.transformer_params[key] = var

            slider = ttk.Scale(input_frame, from_=min_val, to=max_val,
                             orient=tk.HORIZONTAL, variable=var, length=300)
            slider.grid(row=idx, column=1, padx=10, pady=5)

            value_label = ttk.Label(input_frame, text=f"{default}")
            value_label.grid(row=idx, column=2, pady=5)

            # Update label on slider change
            slider.configure(command=lambda v, lbl=value_label, res=resolution:
                           lbl.config(text=f"{float(v):.2f}"))

        # Calculate button
        calc_btn = ttk.Button(input_frame, text="Calculate Costs",
                             command=self.calculate_transformer_costs)
        calc_btn.grid(row=len(params), column=0, columnspan=3, pady=10)

        # Results display
        self.transformer_results = scrolledtext.ScrolledText(results_frame, width=100, height=20)
        self.transformer_results.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Initial calculation
        self.calculate_transformer_costs()

    def calculate_transformer_costs(self):
        """Calculate and display transformer costs"""
        hours_load = self.transformer_params['hours_load'].get()
        energy_cost = self.transformer_params['energy_cost'].get()
        fixed_charge = self.transformer_params['fixed_charge'].get()
        depreciation_rate = self.transformer_params['depreciation_rate'].get() / 100

        # Define transformers
        transformers = {
            'A': {'price': 41000, 'no_load': 16, 'full_load': 50},
            'B': {'price': 45000, 'no_load': 14, 'full_load': 45},
            'C': {'price': 38000, 'no_load': 19, 'full_load': 60}
        }

        results = []
        for name, params in transformers.items():
            analyzer = TransformerCostAnalysis(
                price=params['price'],
                no_load_loss=params['no_load'],
                full_load_loss=params['full_load'],
                hours_on_load=hours_load,
                energy_cost=energy_cost,
                fixed_charge=fixed_charge,
                depreciation_rate=depreciation_rate
            )
            costs = analyzer.calculate_total_annual_cost()
            results.append((name, params, costs))

        # Display results
        self.transformer_results.delete(1.0, tk.END)
        self.transformer_results.insert(tk.END, "="*100 + "\n")
        self.transformer_results.insert(tk.END, "TRANSFORMER COST ANALYSIS REPORT\n")
        self.transformer_results.insert(tk.END, "="*100 + "\n\n")

        self.transformer_results.insert(tk.END, f"Operating Conditions:\n")
        self.transformer_results.insert(tk.END, f"  - Hours on Load: {hours_load} hours/day\n")
        self.transformer_results.insert(tk.END, f"  - Hours on No-Load: {24-hours_load} hours/day\n")
        self.transformer_results.insert(tk.END, f"  - Energy Cost: Rs. {energy_cost:.2f}/kWh\n")
        self.transformer_results.insert(tk.END, f"  - Fixed Charge: Rs. {fixed_charge}/kW/year\n")
        self.transformer_results.insert(tk.END, f"  - Depreciation Rate: {depreciation_rate*100:.1f}%\n\n")

        for name, params, costs in results:
            self.transformer_results.insert(tk.END, f"\n{'='*100}\n")
            self.transformer_results.insert(tk.END, f"TRANSFORMER {name}\n")
            self.transformer_results.insert(tk.END, f"{'='*100}\n")
            self.transformer_results.insert(tk.END, f"Purchase Price: Rs. {params['price']:,}\n")
            self.transformer_results.insert(tk.END, f"No-load Loss: {params['no_load']} kW\n")
            self.transformer_results.insert(tk.END, f"Full-load Loss: {params['full_load']} kW\n\n")

            self.transformer_results.insert(tk.END, f"Annual Cost Breakdown:\n")
            self.transformer_results.insert(tk.END, f"  1. Energy Loss Cost:    Rs. {costs['energy_loss_cost']:,.2f}\n")
            self.transformer_results.insert(tk.END, f"  2. Fixed Charges:       Rs. {costs['fixed_charges']:,.2f}\n")
            self.transformer_results.insert(tk.END, f"  3. Depreciation:        Rs. {costs['depreciation']:,.2f}\n")
            self.transformer_results.insert(tk.END, f"  {'─'*50}\n")
            self.transformer_results.insert(tk.END, f"  TOTAL ANNUAL COST:      Rs. {costs['total']:,.2f}\n")

        # Find most economical
        min_cost = min(results, key=lambda x: x[2]['total'])
        self.transformer_results.insert(tk.END, f"\n\n{'='*100}\n")
        self.transformer_results.insert(tk.END, f"RECOMMENDATION\n")
        self.transformer_results.insert(tk.END, f"{'='*100}\n")
        self.transformer_results.insert(tk.END, f"Most Economical Transformer: {min_cost[0]}\n")
        self.transformer_results.insert(tk.END, f"Total Annual Cost: Rs. {min_cost[2]['total']:,.2f}\n\n")

        # Cost comparison
        self.transformer_results.insert(tk.END, f"Cost Comparison:\n")
        sorted_results = sorted(results, key=lambda x: x[2]['total'])
        for rank, (name, params, costs) in enumerate(sorted_results, 1):
            self.transformer_results.insert(tk.END, f"  {rank}. Transformer {name}: Rs. {costs['total']:,.2f}")
            if rank == 1:
                self.transformer_results.insert(tk.END, " ← BEST CHOICE\n")
            else:
                diff = costs['total'] - sorted_results[0][2]['total']
                self.transformer_results.insert(tk.END, f" (Rs. {diff:,.2f} more expensive)\n")

    def create_rlc_circuit_tab(self):
        """Tab 2: RLC Circuit Simulation"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="RLC Circuit Simulation")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        # Title
        title = ttk.Label(tab, text="RLC Circuit Dynamic Simulation",
                         font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)

        # Control panel
        control_frame = ttk.LabelFrame(tab, text="Circuit Parameters", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Parameters
        self.rlc_params = {}
        params = [
            ("Resistance R (Ω)", "R", 10, 1, 100, 1),
            ("Inductance L (H)", "L", 0.1, 0.01, 1.0, 0.01),
            ("Capacitance C (F)", "C", 0.001, 0.0001, 0.01, 0.0001),
            ("Input Voltage (V)", "V", 10, 1, 100, 1),
            ("Frequency (Hz)", "freq", 50, 1, 200, 1),
            ("Simulation Time (s)", "t_max", 1.0, 0.1, 10.0, 0.1)
        ]

        for idx, (label, key, default, min_val, max_val, resolution) in enumerate(params):
            ttk.Label(control_frame, text=label).grid(row=idx, column=0, sticky=tk.W, pady=5)

            var = tk.DoubleVar(value=default)
            self.rlc_params[key] = var

            slider = ttk.Scale(control_frame, from_=min_val, to=max_val,
                             orient=tk.HORIZONTAL, variable=var, length=250)
            slider.grid(row=idx, column=1, padx=10, pady=5)

            value_label = ttk.Label(control_frame, text=f"{default}")
            value_label.grid(row=idx, column=2, pady=5)

            slider.configure(command=lambda v, lbl=value_label:
                           lbl.config(text=f"{float(v):.4f}"))

        # Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=len(params), column=0, sticky=tk.W, pady=5)
        self.rlc_solver = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.rlc_solver,
                                   values=["RK45", "Euler"], state="readonly", width=20)
        solver_combo.grid(row=len(params), column=1, pady=5, sticky=tk.W)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=len(params)+1, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="▶ Start", command=self.start_rlc_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏸ Stop", command=self.stop_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="↻ Reset", command=self.reset_rlc_simulation).pack(side=tk.LEFT, padx=5)

        # Plot area
        plot_frame = ttk.LabelFrame(tab, text="Visualization", padding="10")
        plot_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.rlc_fig = Figure(figsize=(8, 6), dpi=100)
        self.rlc_canvas = FigureCanvasTkAgg(self.rlc_fig, master=plot_frame)
        self.rlc_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Initial plot
        self.reset_rlc_simulation()

    def start_rlc_simulation(self):
        """Start RLC circuit simulation"""
        self.simulation_running = True
        self.run_rlc_simulation()

    def stop_simulation(self):
        """Stop current simulation"""
        self.simulation_running = False
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None

    def reset_rlc_simulation(self):
        """Reset RLC simulation"""
        self.stop_simulation()
        self.current_time = 0
        self.run_rlc_simulation()

    def run_rlc_simulation(self):
        """Run RLC circuit simulation"""
        # Get parameters
        R = self.rlc_params['R'].get()
        L = self.rlc_params['L'].get()
        C = self.rlc_params['C'].get()
        V = self.rlc_params['V'].get()
        freq = self.rlc_params['freq'].get()
        t_max = self.rlc_params['t_max'].get()
        solver_method = self.rlc_solver.get()

        # Define source voltage
        omega = 2 * np.pi * freq
        V_source_func = lambda t: V * np.sin(omega * t)

        # Initial conditions [i0, v_c0]
        y0 = [0, 0]
        t_span = (0, t_max)
        t_eval = np.linspace(0, t_max, 500)

        # Solve ODE
        ode_func = lambda t, y: ElectricalCircuitModels.rlc_circuit(t, y, R, L, C, V_source_func)

        if solver_method == "RK45":
            t, y = ODESolver.rk45(ode_func, y0, t_span, t_eval)
        else:  # Euler
            t, y = ODESolver.euler(ode_func, y0, t_span, t_eval)

        current = y[0]
        v_capacitor = y[1]
        v_source = np.array([V_source_func(ti) for ti in t])
        v_resistor = R * current
        v_inductor = v_source - v_capacitor - v_resistor

        # Plot results
        self.rlc_fig.clear()

        ax1 = self.rlc_fig.add_subplot(2, 2, 1)
        ax1.plot(t, current * 1000, 'b-', linewidth=2, label='Current')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Current (mA)')
        ax1.set_title('Circuit Current')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax2 = self.rlc_fig.add_subplot(2, 2, 2)
        ax2.plot(t, v_source, 'r-', linewidth=2, label='Source')
        ax2.plot(t, v_capacitor, 'g-', linewidth=2, label='Capacitor')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Voltage (V)')
        ax2.set_title('Voltages')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        ax3 = self.rlc_fig.add_subplot(2, 2, 3)
        power = v_source * current
        ax3.plot(t, power, 'm-', linewidth=2)
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Power (W)')
        ax3.set_title('Instantaneous Power')
        ax3.grid(True, alpha=0.3)

        ax4 = self.rlc_fig.add_subplot(2, 2, 4)
        ax4.plot(t, v_resistor, 'r-', linewidth=1.5, label='V_R')
        ax4.plot(t, v_inductor, 'b-', linewidth=1.5, label='V_L')
        ax4.plot(t, v_capacitor, 'g-', linewidth=1.5, label='V_C')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Voltage (V)')
        ax4.set_title('Component Voltages')
        ax4.grid(True, alpha=0.3)
        ax4.legend()

        self.rlc_fig.tight_layout()
        self.rlc_canvas.draw()

    def create_transformer_simulation_tab(self):
        """Tab 3: Transformer Dynamic Simulation"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Transformer Simulation")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        # Title
        title = ttk.Label(tab, text="Transformer Dynamic Model",
                         font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)

        # Control panel
        control_frame = ttk.LabelFrame(tab, text="Transformer Parameters", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Parameters
        self.trans_params = {}
        params = [
            ("Primary Resistance R1 (Ω)", "R1", 1.0, 0.1, 10, 0.1),
            ("Primary Inductance L1 (H)", "L1", 0.1, 0.01, 1.0, 0.01),
            ("Secondary Resistance R2 (Ω)", "R2", 0.5, 0.1, 10, 0.1),
            ("Secondary Inductance L2 (H)", "L2", 0.05, 0.01, 1.0, 0.01),
            ("Mutual Inductance M (H)", "M", 0.07, 0.01, 0.5, 0.01),
            ("Load Resistance (Ω)", "R_load", 10, 1, 100, 1),
            ("Input Voltage (V)", "V_in", 100, 10, 500, 10),
            ("Frequency (Hz)", "freq", 50, 10, 200, 10),
            ("Simulation Time (s)", "t_max", 0.5, 0.1, 5.0, 0.1)
        ]

        for idx, (label, key, default, min_val, max_val, resolution) in enumerate(params):
            ttk.Label(control_frame, text=label).grid(row=idx, column=0, sticky=tk.W, pady=3)

            var = tk.DoubleVar(value=default)
            self.trans_params[key] = var

            slider = ttk.Scale(control_frame, from_=min_val, to=max_val,
                             orient=tk.HORIZONTAL, variable=var, length=200)
            slider.grid(row=idx, column=1, padx=10, pady=3)

            value_label = ttk.Label(control_frame, text=f"{default:.3f}")
            value_label.grid(row=idx, column=2, pady=3)

            slider.configure(command=lambda v, lbl=value_label:
                           lbl.config(text=f"{float(v):.3f}"))

        # Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=len(params), column=0, sticky=tk.W, pady=5)
        self.trans_solver = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.trans_solver,
                                   values=["RK45", "Euler"], state="readonly", width=15)
        solver_combo.grid(row=len(params), column=1, pady=5, sticky=tk.W)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=len(params)+1, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="▶ Start", command=self.start_transformer_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏸ Stop", command=self.stop_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="↻ Reset", command=self.reset_transformer_simulation).pack(side=tk.LEFT, padx=5)

        # Plot area
        plot_frame = ttk.LabelFrame(tab, text="Visualization", padding="10")
        plot_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.trans_fig = Figure(figsize=(8, 6), dpi=100)
        self.trans_canvas = FigureCanvasTkAgg(self.trans_fig, master=plot_frame)
        self.trans_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Initial plot
        self.reset_transformer_simulation()

    def start_transformer_simulation(self):
        """Start transformer simulation"""
        self.simulation_running = True
        self.run_transformer_simulation()

    def reset_transformer_simulation(self):
        """Reset transformer simulation"""
        self.stop_simulation()
        self.current_time = 0
        self.run_transformer_simulation()

    def run_transformer_simulation(self):
        """Run transformer simulation"""
        # Get parameters
        R1 = self.trans_params['R1'].get()
        L1 = self.trans_params['L1'].get()
        R2 = self.trans_params['R2'].get()
        L2 = self.trans_params['L2'].get()
        M = self.trans_params['M'].get()
        R_load = self.trans_params['R_load'].get()
        V_in = self.trans_params['V_in'].get()
        freq = self.trans_params['freq'].get()
        t_max = self.trans_params['t_max'].get()
        solver_method = self.trans_solver.get()

        # Define source voltage
        omega = 2 * np.pi * freq
        V_in_func = lambda t: V_in * np.sin(omega * t)

        # Initial conditions [i1_0, i2_0]
        y0 = [0, 0]
        t_span = (0, t_max)
        t_eval = np.linspace(0, t_max, 500)

        # Solve ODE
        ode_func = lambda t, y: ElectricalCircuitModels.transformer_model(
            t, y, R1, L1, R2, L2, M, V_in_func, R_load)

        if solver_method == "RK45":
            t, y = ODESolver.rk45(ode_func, y0, t_span, t_eval)
        else:  # Euler
            t, y = ODESolver.euler(ode_func, y0, t_span, t_eval)

        i1 = y[0]
        i2 = y[1]
        v_in = np.array([V_in_func(ti) for ti in t])
        v_out = -i2 * R_load
        power_in = v_in * i1
        power_out = v_out * i2
        efficiency = np.where(np.abs(power_in) > 1e-6,
                             (power_out / power_in) * 100, 0)

        # Plot results
        self.trans_fig.clear()

        ax1 = self.trans_fig.add_subplot(2, 2, 1)
        ax1.plot(t, i1 * 1000, 'b-', linewidth=2, label='Primary')
        ax1.plot(t, i2 * 1000, 'r-', linewidth=2, label='Secondary')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Current (mA)')
        ax1.set_title('Transformer Currents')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax2 = self.trans_fig.add_subplot(2, 2, 2)
        ax2.plot(t, v_in, 'b-', linewidth=2, label='Input')
        ax2.plot(t, v_out, 'r-', linewidth=2, label='Output')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Voltage (V)')
        ax2.set_title('Transformer Voltages')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        ax3 = self.trans_fig.add_subplot(2, 2, 3)
        ax3.plot(t, power_in, 'b-', linewidth=2, label='Input')
        ax3.plot(t, power_out, 'r-', linewidth=2, label='Output')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Power (W)')
        ax3.set_title('Power Transfer')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        ax4 = self.trans_fig.add_subplot(2, 2, 4)
        ax4.plot(t, efficiency, 'g-', linewidth=2)
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Efficiency (%)')
        ax4.set_title('Instantaneous Efficiency')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim([0, 120])

        self.trans_fig.tight_layout()
        self.trans_canvas.draw()

    def create_motor_simulation_tab(self):
        """Tab 4: DC Motor Simulation"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="DC Motor Simulation")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        # Title
        title = ttk.Label(tab, text="DC Motor Dynamic Simulation",
                         font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)

        # Control panel
        control_frame = ttk.LabelFrame(tab, text="Motor Parameters", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Parameters
        self.motor_params = {}
        params = [
            ("Armature Resistance R_a (Ω)", "R_a", 2.0, 0.1, 10, 0.1),
            ("Armature Inductance L_a (H)", "L_a", 0.05, 0.01, 0.5, 0.01),
            ("Back-EMF Constant K_e (V·s/rad)", "K_e", 0.1, 0.01, 1.0, 0.01),
            ("Torque Constant K_t (N·m/A)", "K_t", 0.1, 0.01, 1.0, 0.01),
            ("Moment of Inertia J (kg·m²)", "J", 0.01, 0.001, 0.1, 0.001),
            ("Friction Coefficient B (N·m·s)", "B", 0.001, 0.0001, 0.01, 0.0001),
            ("Applied Voltage (V)", "V_in", 12, 1, 100, 1),
            ("Load Torque (N·m)", "T_load", 0.05, 0, 1.0, 0.01),
            ("Simulation Time (s)", "t_max", 2.0, 0.5, 10.0, 0.5)
        ]

        for idx, (label, key, default, min_val, max_val, resolution) in enumerate(params):
            ttk.Label(control_frame, text=label).grid(row=idx, column=0, sticky=tk.W, pady=3)

            var = tk.DoubleVar(value=default)
            self.motor_params[key] = var

            slider = ttk.Scale(control_frame, from_=min_val, to=max_val,
                             orient=tk.HORIZONTAL, variable=var, length=200)
            slider.grid(row=idx, column=1, padx=10, pady=3)

            value_label = ttk.Label(control_frame, text=f"{default:.4f}")
            value_label.grid(row=idx, column=2, pady=3)

            slider.configure(command=lambda v, lbl=value_label:
                           lbl.config(text=f"{float(v):.4f}"))

        # Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=len(params), column=0, sticky=tk.W, pady=5)
        self.motor_solver = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.motor_solver,
                                   values=["RK45", "Euler"], state="readonly", width=15)
        solver_combo.grid(row=len(params), column=1, pady=5, sticky=tk.W)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=len(params)+1, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="▶ Start", command=self.start_motor_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏸ Stop", command=self.stop_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="↻ Reset", command=self.reset_motor_simulation).pack(side=tk.LEFT, padx=5)

        # Plot area
        plot_frame = ttk.LabelFrame(tab, text="Visualization", padding="10")
        plot_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.motor_fig = Figure(figsize=(8, 6), dpi=100)
        self.motor_canvas = FigureCanvasTkAgg(self.motor_fig, master=plot_frame)
        self.motor_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Initial plot
        self.reset_motor_simulation()

    def start_motor_simulation(self):
        """Start motor simulation"""
        self.simulation_running = True
        self.run_motor_simulation()

    def reset_motor_simulation(self):
        """Reset motor simulation"""
        self.stop_simulation()
        self.current_time = 0
        self.run_motor_simulation()

    def run_motor_simulation(self):
        """Run DC motor simulation"""
        # Get parameters
        R_a = self.motor_params['R_a'].get()
        L_a = self.motor_params['L_a'].get()
        K_e = self.motor_params['K_e'].get()
        K_t = self.motor_params['K_t'].get()
        J = self.motor_params['J'].get()
        B = self.motor_params['B'].get()
        V_in = self.motor_params['V_in'].get()
        T_load = self.motor_params['T_load'].get()
        t_max = self.motor_params['t_max'].get()
        solver_method = self.motor_solver.get()

        # Constant voltage source
        V_in_func = lambda t: V_in

        # Initial conditions [i_a0, omega0]
        y0 = [0, 0]
        t_span = (0, t_max)
        t_eval = np.linspace(0, t_max, 500)

        # Solve ODE
        ode_func = lambda t, y: ElectricalCircuitModels.dc_motor(
            t, y, R_a, L_a, K_e, K_t, J, B, V_in_func, T_load)

        if solver_method == "RK45":
            t, y = ODESolver.rk45(ode_func, y0, t_span, t_eval)
        else:  # Euler
            t, y = ODESolver.euler(ode_func, y0, t_span, t_eval)

        i_a = y[0]
        omega = y[1]
        rpm = omega * 60 / (2 * np.pi)
        torque = K_t * i_a
        power = torque * omega

        # Plot results
        self.motor_fig.clear()

        ax1 = self.motor_fig.add_subplot(2, 2, 1)
        ax1.plot(t, i_a, 'b-', linewidth=2)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Armature Current (A)')
        ax1.set_title('Motor Current')
        ax1.grid(True, alpha=0.3)

        ax2 = self.motor_fig.add_subplot(2, 2, 2)
        ax2.plot(t, rpm, 'r-', linewidth=2)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Speed (RPM)')
        ax2.set_title('Motor Speed')
        ax2.grid(True, alpha=0.3)

        ax3 = self.motor_fig.add_subplot(2, 2, 3)
        ax3.plot(t, torque, 'g-', linewidth=2)
        ax3.axhline(y=T_load, color='k', linestyle='--', label='Load Torque')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Torque (N·m)')
        ax3.set_title('Motor Torque')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        ax4 = self.motor_fig.add_subplot(2, 2, 4)
        ax4.plot(t, power, 'm-', linewidth=2)
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Mechanical Power (W)')
        ax4.set_title('Output Power')
        ax4.grid(True, alpha=0.3)

        self.motor_fig.tight_layout()
        self.motor_canvas.draw()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = AdvancedElectricalEngineeringLab(root)
    root.mainloop()


if __name__ == "__main__":
    main()
