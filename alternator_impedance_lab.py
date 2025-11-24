#!/usr/bin/env python3
"""
Advanced Alternator Impedance Calculation Lab
Solves problems 9.15 and 9.16 with dynamic simulation and visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import cmath
from scipy.integrate import solve_ivp
import threading
import time


class AlternatorSimulator:
    """Mathematical model for alternator dynamic simulation"""

    def __init__(self):
        # Machine parameters (default values)
        self.Ra = 0.15  # Armature resistance (Ω)
        self.Xs = 0.371  # Synchronous reactance (Ω)
        self.Zs = 0.4  # Synchronous impedance (Ω)
        self.Eoc = 60  # Open circuit voltage (V)
        self.Isc = 150  # Short circuit current (A)
        self.Vt = 200  # Terminal voltage (V)
        self.Ia = 90  # Armature current (A)
        self.pf = 0.8  # Power factor
        self.freq = 50  # Frequency (Hz)
        self.omega = 2 * np.pi * self.freq  # Angular frequency

        # Simulation state
        self.time_history = []
        self.voltage_history = []
        self.current_history = []
        self.power_history = []
        self.running = False

    def calculate_impedances(self, Ra, Eoc, Isc):
        """Calculate synchronous impedance and reactance"""
        Zs = Eoc / Isc
        Xs = np.sqrt(Zs**2 - Ra**2)
        return Zs, Xs

    def calculate_no_load_voltage(self, Vt, Ia, Ra, Xs, pf, leading=False):
        """Calculate internal EMF using phasor diagram"""
        # Power factor angle
        phi = np.arccos(pf)

        if leading:
            phi = -phi  # Leading current

        # Terminal voltage (reference phasor)
        Vt_complex = complex(Vt, 0)

        # Current phasor
        Ia_complex = Ia * complex(np.cos(-phi), np.sin(-phi))

        # Impedance drop
        Z_complex = complex(Ra, Xs)
        voltage_drop = Ia_complex * Z_complex

        # Internal EMF
        E_complex = Vt_complex + voltage_drop
        E_magnitude = abs(E_complex)
        E_angle = np.angle(E_complex, deg=True)

        return E_magnitude, E_angle, E_complex

    def solve_problem_9_15(self):
        """Solve problem 9.15"""
        Ra = 0.15
        Eoc = 60
        Isc = 150
        Ia = 90
        Vt = 200
        pf = 0.8

        # Calculate impedances
        Zs, Xs = self.calculate_impedances(Ra, Eoc, Isc)

        # Calculate no-load voltage
        E, E_angle, E_complex = self.calculate_no_load_voltage(Vt, Ia, Ra, Xs, pf, leading=False)

        results = {
            'problem': '9.15',
            'Ra': Ra,
            'Zs': Zs,
            'Xs': Xs,
            'E': E,
            'E_angle': E_angle,
            'E_complex': E_complex,
            'Vt': Vt,
            'Ia': Ia,
            'pf': pf,
            'leading': False
        }

        return results

    def solve_problem_9_16(self):
        """Solve problem 9.16"""
        Ra = 0.35
        Eoc = 500
        Isc = 180
        Ia = 60
        Vt = 220
        pf = 0.85

        # Calculate impedances
        Zs, Xs = self.calculate_impedances(Ra, Eoc, Isc)

        # Calculate no-load voltage
        E, E_angle, E_complex = self.calculate_no_load_voltage(Vt, Ia, Ra, Xs, pf, leading=True)

        results = {
            'problem': '9.16',
            'Ra': Ra,
            'Zs': Zs,
            'Xs': Xs,
            'E': E,
            'E_angle': E_angle,
            'E_complex': E_complex,
            'Vt': Vt,
            'Ia': Ia,
            'pf': pf,
            'leading': True
        }

        return results

    def alternator_ode_euler(self, dt, T_total):
        """Euler method for dynamic simulation"""
        self.time_history = [0]
        self.voltage_history = [self.Vt]
        self.current_history = [0]
        self.power_history = [0]

        t = 0
        V = self.Vt
        I = 0

        # Target current
        I_target = self.Ia

        # Time constant (electrical)
        tau = self.Xs / (self.omega * self.Ra)

        while t < T_total and self.running:
            # Simple first-order electrical dynamics
            dI_dt = (I_target - I) / tau
            I = I + dI_dt * dt

            # Voltage equation
            V = abs(self.Eoc - I * (self.Ra + 1j * self.Xs))

            # Power
            P = V * I * self.pf

            # Store history
            self.time_history.append(t)
            self.voltage_history.append(V)
            self.current_history.append(I)
            self.power_history.append(P)

            t += dt
            time.sleep(dt / 10)  # Real-time factor

    def alternator_ode_rk45(self, T_total):
        """RK45 method for dynamic simulation"""

        def electrical_dynamics(t, y):
            """Differential equations for alternator"""
            I, delta = y

            # Target current
            I_target = self.Ia

            # Time constant
            tau = self.Xs / (self.omega * self.Ra) if self.Ra > 0 else 0.01

            # Current dynamics (first-order)
            dI_dt = (I_target - I) / tau

            # Load angle dynamics (simplified)
            d_delta_dt = self.omega * 0.01 * (I_target - I)

            return [dI_dt, d_delta_dt]

        # Initial conditions
        y0 = [0, 0]  # [current, load_angle]

        # Time span
        t_span = (0, T_total)
        t_eval = np.linspace(0, T_total, 500)

        # Solve ODE
        sol = solve_ivp(electrical_dynamics, t_span, y0, method='RK45',
                       t_eval=t_eval, rtol=1e-6)

        # Extract results
        self.time_history = sol.t.tolist()
        self.current_history = sol.y[0].tolist()

        # Calculate voltage and power
        self.voltage_history = []
        self.power_history = []

        for I in self.current_history:
            V = abs(self.Eoc - I * (self.Ra + 1j * self.Xs))
            P = V * I * self.pf
            self.voltage_history.append(V)
            self.power_history.append(P)


class AlternatorLab:
    """Main application class for Alternator Lab"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Alternator Impedance Calculation Lab")
        self.root.geometry("1400x900")

        # Simulator instance
        self.simulator = AlternatorSimulator()

        # Simulation control
        self.sim_thread = None

        # Current problem
        self.current_problem = None

        # Setup GUI
        self.setup_gui()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def setup_gui(self):
        """Setup the GUI layout"""

        # Main container with grid
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Top menu frame
        self.setup_menu()

        # Main content frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)

        # Left panel - Controls
        self.setup_control_panel()

        # Right panel - Visualization
        self.setup_visualization_panel()

    def setup_menu(self):
        """Setup menu bar"""
        menu_frame = ttk.Frame(self.root, relief='raised', borderwidth=1)
        menu_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        ttk.Label(menu_frame, text="Alternator Impedance Lab",
                 font=('Arial', 16, 'bold')).pack(side='left', padx=10)

        ttk.Button(menu_frame, text="Problem 9.15",
                  command=self.load_problem_9_15).pack(side='left', padx=5)

        ttk.Button(menu_frame, text="Problem 9.16",
                  command=self.load_problem_9_16).pack(side='left', padx=5)

        ttk.Button(menu_frame, text="Custom",
                  command=self.load_custom).pack(side='left', padx=5)

        ttk.Button(menu_frame, text="About",
                  command=self.show_about).pack(side='right', padx=5)

    def setup_control_panel(self):
        """Setup control panel with inputs and sliders"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Control Panel", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create notebook for organized controls
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill='both', expand=True)

        # Tab 1: Parameters
        params_frame = ttk.Frame(notebook, padding=10)
        notebook.add(params_frame, text="Parameters")

        # Parameters with sliders
        self.param_vars = {}
        params = [
            ('Ra', 'Armature Resistance (Ω)', 0.01, 2.0, 0.15),
            ('Eoc', 'Open Circuit Voltage (V)', 10, 500, 60),
            ('Isc', 'Short Circuit Current (A)', 10, 300, 150),
            ('Vt', 'Terminal Voltage (V)', 50, 500, 200),
            ('Ia', 'Armature Current (A)', 10, 200, 90),
            ('pf', 'Power Factor', 0.5, 1.0, 0.8),
            ('freq', 'Frequency (Hz)', 25, 100, 50),
        ]

        row = 0
        for param, label, min_val, max_val, default in params:
            ttk.Label(params_frame, text=label).grid(row=row, column=0, sticky='w', pady=5)

            var = tk.DoubleVar(value=default)
            self.param_vars[param] = var

            scale = ttk.Scale(params_frame, from_=min_val, to=max_val,
                            variable=var, orient='horizontal', length=200)
            scale.grid(row=row, column=1, sticky='ew', padx=5)

            entry = ttk.Entry(params_frame, textvariable=var, width=10)
            entry.grid(row=row, column=2, padx=5)

            row += 1

        params_frame.grid_columnconfigure(1, weight=1)

        # Leading/Lagging selection
        ttk.Label(params_frame, text="Power Factor Type:").grid(row=row, column=0, sticky='w', pady=5)
        self.pf_type_var = tk.StringVar(value="Lagging")
        ttk.Radiobutton(params_frame, text="Lagging", variable=self.pf_type_var,
                       value="Lagging").grid(row=row, column=1, sticky='w')
        ttk.Radiobutton(params_frame, text="Leading", variable=self.pf_type_var,
                       value="Leading").grid(row=row, column=2, sticky='w')

        # Tab 2: Simulation Settings
        sim_frame = ttk.Frame(notebook, padding=10)
        notebook.add(sim_frame, text="Simulation")

        ttk.Label(sim_frame, text="Solver Method:").grid(row=0, column=0, sticky='w', pady=5)
        self.solver_var = tk.StringVar(value="RK45")
        ttk.Radiobutton(sim_frame, text="RK45 (Adaptive)", variable=self.solver_var,
                       value="RK45").grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(sim_frame, text="Euler (Fixed)", variable=self.solver_var,
                       value="Euler").grid(row=1, column=1, sticky='w')

        ttk.Label(sim_frame, text="Simulation Time (s):").grid(row=2, column=0, sticky='w', pady=5)
        self.sim_time_var = tk.DoubleVar(value=1.0)
        ttk.Scale(sim_frame, from_=0.1, to=5.0, variable=self.sim_time_var,
                 orient='horizontal', length=200).grid(row=2, column=1, sticky='ew', padx=5)
        ttk.Entry(sim_frame, textvariable=self.sim_time_var, width=10).grid(row=2, column=2)

        # Tab 3: Results
        results_frame = ttk.Frame(notebook, padding=10)
        notebook.add(results_frame, text="Results")

        self.results_text = tk.Text(results_frame, height=15, width=40, wrap='word')
        self.results_text.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_text.config(yscrollcommand=scrollbar.set)

        # Control buttons at bottom
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Calculate",
                  command=self.calculate).pack(side='left', padx=5, fill='x', expand=True)

        ttk.Button(button_frame, text="Start Simulation",
                  command=self.start_simulation,
                  style='Accent.TButton').pack(side='left', padx=5, fill='x', expand=True)

        ttk.Button(button_frame, text="Stop",
                  command=self.stop_simulation).pack(side='left', padx=5, fill='x', expand=True)

        ttk.Button(button_frame, text="Reset",
                  command=self.reset).pack(side='left', padx=5, fill='x', expand=True)

    def setup_visualization_panel(self):
        """Setup visualization panel with plots"""
        viz_frame = ttk.LabelFrame(self.main_frame, text="Visualization", padding=10)
        viz_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create notebook for multiple plots
        self.viz_notebook = ttk.Notebook(viz_frame)
        self.viz_notebook.pack(fill='both', expand=True)

        # Tab 1: Phasor Diagram
        self.phasor_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.phasor_frame, text="Phasor Diagram")

        self.phasor_fig = Figure(figsize=(6, 6), dpi=100)
        self.phasor_ax = self.phasor_fig.add_subplot(111)
        self.phasor_canvas = FigureCanvasTkAgg(self.phasor_fig, self.phasor_frame)
        self.phasor_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Tab 2: Time Domain
        self.time_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.time_frame, text="Time Domain")

        self.time_fig = Figure(figsize=(8, 6), dpi=100)
        self.time_canvas = FigureCanvasTkAgg(self.time_fig, self.time_frame)
        self.time_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Tab 3: Operating Characteristics
        self.char_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.char_frame, text="Characteristics")

        self.char_fig = Figure(figsize=(8, 6), dpi=100)
        self.char_canvas = FigureCanvasTkAgg(self.char_fig, self.char_frame)
        self.char_canvas.get_tk_widget().pack(fill='both', expand=True)

    def load_problem_9_15(self):
        """Load problem 9.15 parameters"""
        self.param_vars['Ra'].set(0.15)
        self.param_vars['Eoc'].set(60)
        self.param_vars['Isc'].set(150)
        self.param_vars['Vt'].set(200)
        self.param_vars['Ia'].set(90)
        self.param_vars['pf'].set(0.8)
        self.pf_type_var.set("Lagging")
        self.current_problem = "9.15"
        self.calculate()

    def load_problem_9_16(self):
        """Load problem 9.16 parameters"""
        self.param_vars['Ra'].set(0.35)
        self.param_vars['Eoc'].set(500)
        self.param_vars['Isc'].set(180)
        self.param_vars['Vt'].set(220)
        self.param_vars['Ia'].set(60)
        self.param_vars['pf'].set(0.85)
        self.pf_type_var.set("Leading")
        self.current_problem = "9.16"
        self.calculate()

    def load_custom(self):
        """Load custom mode"""
        self.current_problem = "Custom"
        messagebox.showinfo("Custom Mode", "Adjust parameters and click Calculate")

    def calculate(self):
        """Calculate impedances and voltages"""
        # Get parameters
        Ra = self.param_vars['Ra'].get()
        Eoc = self.param_vars['Eoc'].get()
        Isc = self.param_vars['Isc'].get()
        Vt = self.param_vars['Vt'].get()
        Ia = self.param_vars['Ia'].get()
        pf = self.param_vars['pf'].get()
        leading = (self.pf_type_var.get() == "Leading")

        # Update simulator parameters
        self.simulator.Ra = Ra
        self.simulator.Eoc = Eoc
        self.simulator.Isc = Isc
        self.simulator.Vt = Vt
        self.simulator.Ia = Ia
        self.simulator.pf = pf
        self.simulator.freq = self.param_vars['freq'].get()
        self.simulator.omega = 2 * np.pi * self.simulator.freq

        # Calculate
        Zs, Xs = self.simulator.calculate_impedances(Ra, Eoc, Isc)
        E, E_angle, E_complex = self.simulator.calculate_no_load_voltage(
            Vt, Ia, Ra, Xs, pf, leading)

        # Update simulator
        self.simulator.Zs = Zs
        self.simulator.Xs = Xs

        # Display results
        self.results_text.delete(1.0, tk.END)

        problem_text = f"Problem {self.current_problem}\n" if self.current_problem else "Custom Calculation\n"
        self.results_text.insert(tk.END, "=" * 40 + "\n")
        self.results_text.insert(tk.END, problem_text)
        self.results_text.insert(tk.END, "=" * 40 + "\n\n")

        self.results_text.insert(tk.END, "Input Parameters:\n")
        self.results_text.insert(tk.END, f"  Armature Resistance (Ra): {Ra:.3f} Ω\n")
        self.results_text.insert(tk.END, f"  Open Circuit Voltage (Eoc): {Eoc:.2f} V\n")
        self.results_text.insert(tk.END, f"  Short Circuit Current (Isc): {Isc:.2f} A\n")
        self.results_text.insert(tk.END, f"  Terminal Voltage (Vt): {Vt:.2f} V\n")
        self.results_text.insert(tk.END, f"  Armature Current (Ia): {Ia:.2f} A\n")
        self.results_text.insert(tk.END, f"  Power Factor: {pf:.2f} {'leading' if leading else 'lagging'}\n\n")

        self.results_text.insert(tk.END, "Calculated Results:\n")
        self.results_text.insert(tk.END, f"  Synchronous Impedance (Zs): {Zs:.4f} Ω\n")
        self.results_text.insert(tk.END, f"  Synchronous Reactance (Xs): {Xs:.4f} Ω\n")
        self.results_text.insert(tk.END, f"  No-Load Voltage (E): {E:.2f} V\n")
        self.results_text.insert(tk.END, f"  Load Angle (δ): {E_angle:.2f}°\n\n")

        # Additional calculations
        Z_magnitude = np.sqrt(Ra**2 + Xs**2)
        Z_angle = np.arctan2(Xs, Ra) * 180 / np.pi
        apparent_power = Vt * Ia
        real_power = Vt * Ia * pf
        reactive_power = Vt * Ia * np.sqrt(1 - pf**2)

        self.results_text.insert(tk.END, "Additional Information:\n")
        self.results_text.insert(tk.END, f"  Impedance Angle: {Z_angle:.2f}°\n")
        self.results_text.insert(tk.END, f"  Apparent Power: {apparent_power:.2f} VA\n")
        self.results_text.insert(tk.END, f"  Real Power: {real_power:.2f} W\n")
        self.results_text.insert(tk.END, f"  Reactive Power: {reactive_power:.2f} VAR {'(leading)' if leading else '(lagging)'}\n")

        # Draw phasor diagram
        self.draw_phasor_diagram(Vt, Ia, Ra, Xs, pf, leading, E_complex)

        # Draw characteristics
        self.draw_characteristics(Ra, Xs, Eoc, Isc)

    def draw_phasor_diagram(self, Vt, Ia, Ra, Xs, pf, leading, E_complex):
        """Draw phasor diagram"""
        self.phasor_ax.clear()

        # Power factor angle
        phi = np.arccos(pf)
        if leading:
            phi = -phi

        # Phasors (Vt is reference)
        V_phasor = np.array([Vt, 0])
        I_phasor = Ia * np.array([np.cos(-phi), np.sin(-phi)])

        # Voltage drops
        IXs_phasor = Ia * Xs * np.array([-np.sin(-phi), np.cos(-phi)])
        IRa_phasor = Ia * Ra * np.array([np.cos(-phi), np.sin(-phi)])

        # Plot phasors
        origin = [0, 0]

        # Terminal voltage (red)
        self.phasor_ax.quiver(*origin, V_phasor[0], V_phasor[1],
                             angles='xy', scale_units='xy', scale=1,
                             color='red', width=0.006, label='Vt (Terminal Voltage)')

        # Current (blue)
        I_scale = Vt / (2 * Ia)  # Scale current for visibility
        self.phasor_ax.quiver(*origin, I_phasor[0] * I_scale, I_phasor[1] * I_scale,
                             angles='xy', scale_units='xy', scale=1,
                             color='blue', width=0.006, label=f'Ia (Current, scaled)')

        # IRa drop (green)
        self.phasor_ax.quiver(V_phasor[0], V_phasor[1], IRa_phasor[0], IRa_phasor[1],
                             angles='xy', scale_units='xy', scale=1,
                             color='green', width=0.005, label='IRa')

        # IXs drop (orange)
        self.phasor_ax.quiver(V_phasor[0] + IRa_phasor[0], V_phasor[1] + IRa_phasor[1],
                             IXs_phasor[0], IXs_phasor[1],
                             angles='xy', scale_units='xy', scale=1,
                             color='orange', width=0.005, label='jIXs')

        # EMF (purple)
        E_x = E_complex.real
        E_y = E_complex.imag
        self.phasor_ax.quiver(*origin, E_x, E_y,
                             angles='xy', scale_units='xy', scale=1,
                             color='purple', width=0.007, label='E (EMF)')

        # Formatting
        max_val = max(abs(E_complex), Vt) * 1.2
        self.phasor_ax.set_xlim(-max_val * 0.2, max_val)
        self.phasor_ax.set_ylim(-max_val * 0.6, max_val * 0.6)
        self.phasor_ax.set_aspect('equal')
        self.phasor_ax.grid(True, alpha=0.3)
        self.phasor_ax.axhline(y=0, color='k', linewidth=0.5)
        self.phasor_ax.axvline(x=0, color='k', linewidth=0.5)
        self.phasor_ax.set_xlabel('Real Axis (V)')
        self.phasor_ax.set_ylabel('Imaginary Axis (V)')
        self.phasor_ax.set_title('Phasor Diagram')
        self.phasor_ax.legend(loc='best', fontsize=8)

        self.phasor_fig.tight_layout()
        self.phasor_canvas.draw()

    def draw_characteristics(self, Ra, Xs, Eoc, Isc):
        """Draw operating characteristics"""
        self.char_fig.clear()

        # Create subplots
        ax1 = self.char_fig.add_subplot(221)
        ax2 = self.char_fig.add_subplot(222)
        ax3 = self.char_fig.add_subplot(223)
        ax4 = self.char_fig.add_subplot(224)

        # Current range
        I_range = np.linspace(0, Isc, 100)

        # 1. V-I Characteristic
        pf_values = [1.0, 0.8, 0.6]
        for pf in pf_values:
            V_values = []
            for I in I_range:
                phi = np.arccos(pf)
                I_complex = I * np.exp(-1j * phi)
                Z_complex = Ra + 1j * Xs
                V = abs(Eoc - I_complex * Z_complex)
                V_values.append(V)
            ax1.plot(I_range, V_values, label=f'pf={pf}')

        ax1.set_xlabel('Current (A)')
        ax1.set_ylabel('Terminal Voltage (V)')
        ax1.set_title('V-I Characteristics')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 2. Power-Current Characteristic
        for pf in pf_values:
            P_values = []
            for I in I_range:
                phi = np.arccos(pf)
                I_complex = I * np.exp(-1j * phi)
                Z_complex = Ra + 1j * Xs
                V = abs(Eoc - I_complex * Z_complex)
                P = V * I * pf
                P_values.append(P)
            ax2.plot(I_range, P_values, label=f'pf={pf}')

        ax2.set_xlabel('Current (A)')
        ax2.set_ylabel('Power (W)')
        ax2.set_title('Power-Current Characteristics')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # 3. Efficiency curve (simplified)
        eta_values = []
        for I in I_range:
            if I > 0:
                P_out = Eoc * I * 0.8  # Assuming 0.8 pf
                P_loss = I**2 * Ra
                P_in = P_out + P_loss
                eta = (P_out / P_in) * 100 if P_in > 0 else 0
                eta_values.append(min(eta, 100))
            else:
                eta_values.append(0)

        ax3.plot(I_range, eta_values, 'g-', linewidth=2)
        ax3.set_xlabel('Current (A)')
        ax3.set_ylabel('Efficiency (%)')
        ax3.set_title('Efficiency Curve')
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(0, 100)

        # 4. Regulation curve
        reg_values = []
        Vt_rated = Eoc - Isc * 0.5 * (Ra + Xs)  # Approximate rated voltage
        for I in I_range:
            V_no_load = Eoc
            V_load = abs(Eoc - I * (Ra + 1j * Xs) * 0.8)  # 0.8 pf
            reg = ((V_no_load - V_load) / V_load) * 100 if V_load > 0 else 0
            reg_values.append(reg)

        ax4.plot(I_range, reg_values, 'r-', linewidth=2)
        ax4.set_xlabel('Current (A)')
        ax4.set_ylabel('Voltage Regulation (%)')
        ax4.set_title('Voltage Regulation')
        ax4.grid(True, alpha=0.3)

        self.char_fig.tight_layout()
        self.char_canvas.draw()

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.sim_thread and self.sim_thread.is_alive():
            messagebox.showwarning("Warning", "Simulation already running!")
            return

        self.simulator.running = True

        # Run simulation in separate thread
        self.sim_thread = threading.Thread(target=self.run_simulation)
        self.sim_thread.daemon = True
        self.sim_thread.start()

    def run_simulation(self):
        """Run the simulation"""
        solver = self.solver_var.get()
        T_total = self.sim_time_var.get()

        try:
            if solver == "RK45":
                self.simulator.alternator_ode_rk45(T_total)
            else:  # Euler
                dt = 0.001  # Fixed time step
                self.simulator.alternator_ode_euler(dt, T_total)

            # Update plot after simulation
            self.root.after(100, self.update_time_plots)

        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")
        finally:
            self.simulator.running = False

    def update_time_plots(self):
        """Update time domain plots"""
        self.time_fig.clear()

        if not self.simulator.time_history:
            return

        # Create subplots
        ax1 = self.time_fig.add_subplot(311)
        ax2 = self.time_fig.add_subplot(312)
        ax3 = self.time_fig.add_subplot(313)

        t = self.simulator.time_history
        V = self.simulator.voltage_history
        I = self.simulator.current_history
        P = self.simulator.power_history

        # Plot voltage
        ax1.plot(t, V, 'r-', linewidth=2)
        ax1.set_ylabel('Voltage (V)')
        ax1.set_title('Transient Response')
        ax1.grid(True, alpha=0.3)

        # Plot current
        ax2.plot(t, I, 'b-', linewidth=2)
        ax2.set_ylabel('Current (A)')
        ax2.grid(True, alpha=0.3)

        # Plot power
        ax3.plot(t, P, 'g-', linewidth=2)
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Power (W)')
        ax3.grid(True, alpha=0.3)

        self.time_fig.tight_layout()
        self.time_canvas.draw()

    def stop_simulation(self):
        """Stop the simulation"""
        self.simulator.running = False

    def reset(self):
        """Reset simulation"""
        self.stop_simulation()
        self.simulator.time_history = []
        self.simulator.voltage_history = []
        self.simulator.current_history = []
        self.simulator.power_history = []

        # Clear time plot
        self.time_fig.clear()
        self.time_canvas.draw()

    def on_window_resize(self, event):
        """Handle window resize for autoscaling"""
        # Trigger canvas redraw on resize
        if hasattr(self, 'phasor_canvas'):
            self.phasor_canvas.draw_idle()
        if hasattr(self, 'time_canvas'):
            self.time_canvas.draw_idle()
        if hasattr(self, 'char_canvas'):
            self.char_canvas.draw_idle()

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Alternator Impedance Calculation Lab
Version 1.0

Features:
• Solves alternator impedance problems (9.15, 9.16)
• Dynamic simulation with RK45 and Euler solvers
• Phasor diagram visualization
• Operating characteristics curves
• Real-time parameter adjustment
• Professional electrical engineering tool

Developed for educational purposes in electrical machines.
"""
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()

    # Configure style
    style = ttk.Style()
    style.theme_use('clam')

    # Create application
    app = AlternatorLab(root)

    # Run main loop
    root.mainloop()


if __name__ == "__main__":
    main()
