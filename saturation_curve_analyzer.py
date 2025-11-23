#!/usr/bin/env python3
"""
Advanced DC Generator Saturation Curve Analyzer
Comprehensive Electrical Engineering Analysis Tool with Dynamic Simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from scipy.interpolate import interp1d, UnivariateSpline
from scipy.integrate import odeint, solve_ivp
import threading
import time


class SaturationCurveAnalyzer:
    """Main application class for DC Generator analysis"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced DC Generator Saturation Curve Analyzer")
        self.root.geometry("1400x900")

        # Original data at 1800 rpm
        self.Eg_1800 = np.array([8, 40, 74, 113, 152, 213, 234, 248, 266, 278])
        self.If_original = np.array([0, 0.5, 1.0, 1.5, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0])
        self.N_original = 1800  # rpm

        # Simulation control variables
        self.simulation_running = False
        self.simulation_thread = None
        self.time_data = []
        self.voltage_data = []
        self.current_data = []

        # Control variables
        self.speed_var = tk.DoubleVar(value=1800)
        self.field_current_var = tk.DoubleVar(value=4.6)
        self.load_resistance_var = tk.DoubleVar(value=100)
        self.field_resistance_var = tk.DoubleVar(value=50)
        self.simulation_time_var = tk.DoubleVar(value=10.0)
        self.solver_var = tk.StringVar(value="RK45")

        # Configure grid weight for auto-scaling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_widgets()
        self.bind_resize_events()

    def bind_resize_events(self):
        """Bind window resize events for auto-scaling"""
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        if hasattr(self, 'canvas'):
            try:
                self.canvas.draw_idle()
            except:
                pass

    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create tabs
        self.tab_saturation = ttk.Frame(self.notebook)
        self.tab_dynamic = ttk.Frame(self.notebook)
        self.tab_analysis = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_saturation, text="Saturation Curve Analysis")
        self.notebook.add(self.tab_dynamic, text="Dynamic Simulation")
        self.notebook.add(self.tab_analysis, text="Advanced Analysis")

        # Configure tab grids
        for tab in [self.tab_saturation, self.tab_dynamic, self.tab_analysis]:
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(1, weight=1)

        # Build each tab
        self.build_saturation_tab()
        self.build_dynamic_tab()
        self.build_analysis_tab()

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky='ew', padx=5, pady=2)

    def build_saturation_tab(self):
        """Build the saturation curve analysis tab"""
        # Control panel (left side)
        control_frame = ttk.LabelFrame(self.tab_saturation, text="Control Parameters", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Speed control
        row = 0
        ttk.Label(control_frame, text="Speed (rpm):", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=5)
        ttk.Label(control_frame, textvariable=self.speed_var, font=('Arial', 10)).grid(row=row, column=1, sticky='e', pady=5)
        row += 1

        speed_slider = ttk.Scale(control_frame, from_=500, to=2500, variable=self.speed_var,
                                orient='horizontal', length=250, command=self.update_saturation_plot)
        speed_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # Field current control
        ttk.Label(control_frame, text="Field Current (A):", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=5)
        ttk.Label(control_frame, textvariable=self.field_current_var, font=('Arial', 10)).grid(row=row, column=1, sticky='e', pady=5)
        row += 1

        field_current_slider = ttk.Scale(control_frame, from_=0, to=6.0, variable=self.field_current_var,
                                        orient='horizontal', length=250, command=self.update_saturation_plot)
        field_current_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1

        # Results display
        ttk.Label(control_frame, text="Results:", font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=5)
        row += 1

        self.result_text = tk.Text(control_frame, width=35, height=15, font=('Courier', 9), wrap=tk.WORD)
        self.result_text.grid(row=row, column=0, columnspan=2, sticky='nsew', pady=5)
        row += 1

        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Calculate All", command=self.calculate_all_parts).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset_saturation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=5)

        # Plot area (right side)
        plot_frame = ttk.LabelFrame(self.tab_saturation, text="Saturation Curves", padding=10)
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig_saturation = Figure(figsize=(10, 7), dpi=100)
        self.ax_saturation = self.fig_saturation.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig_saturation, plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Toolbar
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.grid(row=1, column=0, sticky='ew')
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()

        # Initial plot
        self.update_saturation_plot()

    def build_dynamic_tab(self):
        """Build the dynamic simulation tab"""
        # Control panel (left side)
        control_frame = ttk.LabelFrame(self.tab_dynamic, text="Simulation Parameters", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        row = 0

        # Speed control
        ttk.Label(control_frame, text="Speed (rpm):", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=5)
        ttk.Label(control_frame, textvariable=self.speed_var, font=('Arial', 10)).grid(row=row, column=1, sticky='e', pady=5)
        row += 1

        ttk.Scale(control_frame, from_=500, to=2500, variable=self.speed_var,
                 orient='horizontal', length=250).grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # Field resistance
        ttk.Label(control_frame, text="Field Resistance (Ω):", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=5)
        ttk.Label(control_frame, textvariable=self.field_resistance_var, font=('Arial', 10)).grid(row=row, column=1, sticky='e', pady=5)
        row += 1

        ttk.Scale(control_frame, from_=10, to=200, variable=self.field_resistance_var,
                 orient='horizontal', length=250).grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # Load resistance
        ttk.Label(control_frame, text="Load Resistance (Ω):", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=5)
        ttk.Label(control_frame, textvariable=self.load_resistance_var, font=('Arial', 10)).grid(row=row, column=1, sticky='e', pady=5)
        row += 1

        ttk.Scale(control_frame, from_=10, to=500, variable=self.load_resistance_var,
                 orient='horizontal', length=250).grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # Simulation time
        ttk.Label(control_frame, text="Simulation Time (s):", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=5)
        ttk.Label(control_frame, textvariable=self.simulation_time_var, font=('Arial', 10)).grid(row=row, column=1, sticky='e', pady=5)
        row += 1

        ttk.Scale(control_frame, from_=1, to=50, variable=self.simulation_time_var,
                 orient='horizontal', length=250).grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # ODE Solver selection
        ttk.Label(control_frame, text="ODE Solver:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=5)
        row += 1

        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_var,
                                    values=["RK45", "Euler", "RK23", "DOP853"], state='readonly')
        solver_combo.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1

        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)

        self.btn_start = ttk.Button(btn_frame, text="Start Simulation", command=self.start_simulation)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = ttk.Button(btn_frame, text="Stop", command=self.stop_simulation, state='disabled')
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="Reset", command=self.reset_simulation).pack(side=tk.LEFT, padx=5)
        row += 1

        # Status
        self.sim_status_label = ttk.Label(control_frame, text="Status: Idle", font=('Arial', 9, 'italic'))
        self.sim_status_label.grid(row=row, column=0, columnspan=2, pady=5)

        # Plot area (right side)
        plot_frame = ttk.LabelFrame(self.tab_dynamic, text="Dynamic Response", padding=10)
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure with subplots
        self.fig_dynamic = Figure(figsize=(10, 7), dpi=100)
        self.ax_voltage = self.fig_dynamic.add_subplot(211)
        self.ax_current = self.fig_dynamic.add_subplot(212)

        self.canvas_dynamic = FigureCanvasTkAgg(self.fig_dynamic, plot_frame)
        self.canvas_dynamic.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Toolbar
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.grid(row=1, column=0, sticky='ew')
        toolbar = NavigationToolbar2Tk(self.canvas_dynamic, toolbar_frame)
        toolbar.update()

    def build_analysis_tab(self):
        """Build the advanced analysis tab"""
        # Control panel (left side)
        control_frame = ttk.LabelFrame(self.tab_analysis, text="Analysis Tools", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        row = 0
        ttk.Label(control_frame, text="Advanced Analysis", font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        ttk.Button(control_frame, text="Magnetic Saturation Analysis",
                  command=self.analyze_saturation).grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        ttk.Button(control_frame, text="Critical Speed Analysis",
                  command=self.analyze_critical_speed).grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        ttk.Button(control_frame, text="Voltage Regulation Analysis",
                  command=self.analyze_voltage_regulation).grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        ttk.Button(control_frame, text="Efficiency Curves",
                  command=self.analyze_efficiency).grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1

        # Analysis results
        ttk.Label(control_frame, text="Analysis Results:", font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=5)
        row += 1

        self.analysis_text = tk.Text(control_frame, width=35, height=20, font=('Courier', 9), wrap=tk.WORD)
        self.analysis_text.grid(row=row, column=0, columnspan=2, sticky='nsew', pady=5)

        # Plot area (right side)
        plot_frame = ttk.LabelFrame(self.tab_analysis, text="Analysis Plots", padding=10)
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig_analysis = Figure(figsize=(10, 7), dpi=100)
        self.ax_analysis = self.fig_analysis.add_subplot(111)

        self.canvas_analysis = FigureCanvasTkAgg(self.fig_analysis, plot_frame)
        self.canvas_analysis.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Toolbar
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.grid(row=1, column=0, sticky='ew')
        toolbar = NavigationToolbar2Tk(self.canvas_analysis, toolbar_frame)
        toolbar.update()

    def get_interpolation_function(self, speed):
        """Create interpolation function for given speed"""
        # Voltage is proportional to speed: Eg2 = Eg1 * (N2/N1)
        Eg_adjusted = self.Eg_1800 * (speed / self.N_original)

        # Create spline interpolation for smooth curve
        interpolator = UnivariateSpline(self.If_original, Eg_adjusted, s=0, k=3)
        return interpolator

    def calculate_voltage_at_current(self, field_current, speed):
        """Calculate voltage for given field current and speed"""
        interpolator = self.get_interpolation_function(speed)

        # Ensure field current is within bounds
        if field_current < self.If_original[0]:
            return interpolator(self.If_original[0])
        elif field_current > self.If_original[-1]:
            return interpolator(self.If_original[-1])
        else:
            return interpolator(field_current)

    def calculate_field_current_for_voltage(self, target_voltage, speed):
        """Calculate required field current for target voltage at given speed"""
        interpolator = self.get_interpolation_function(speed)

        # Create inverse function by searching
        If_range = np.linspace(self.If_original[0], self.If_original[-1], 1000)
        Eg_range = interpolator(If_range)

        # Find closest match
        idx = np.argmin(np.abs(Eg_range - target_voltage))
        return If_range[idx]

    def update_saturation_plot(self, event=None):
        """Update the saturation curve plot"""
        self.ax_saturation.clear()

        # Get current speed
        current_speed = self.speed_var.get()
        current_if = self.field_current_var.get()

        # Plot original curve at 1800 rpm
        self.ax_saturation.plot(self.If_original, self.Eg_1800, 'bo-', linewidth=2,
                               markersize=8, label='1800 rpm (Original)', alpha=0.7)

        # Plot curve at current speed
        Eg_current = self.Eg_1800 * (current_speed / self.N_original)
        self.ax_saturation.plot(self.If_original, Eg_current, 'rs-', linewidth=2,
                               markersize=8, label=f'{current_speed:.0f} rpm', alpha=0.7)

        # Plot interpolated curves for smooth visualization
        If_smooth = np.linspace(self.If_original[0], self.If_original[-1], 200)
        interpolator_current = self.get_interpolation_function(current_speed)
        Eg_smooth_current = interpolator_current(If_smooth)
        self.ax_saturation.plot(If_smooth, Eg_smooth_current, 'r--', linewidth=1.5, alpha=0.5)

        # Mark current operating point
        current_voltage = self.calculate_voltage_at_current(current_if, current_speed)
        self.ax_saturation.plot(current_if, current_voltage, 'g*', markersize=20,
                               label=f'Operating Point\n({current_if:.1f}A, {current_voltage:.1f}V)', zorder=5)

        # Also plot some reference speeds
        for speed in [1500, 1000, 900]:
            if speed != current_speed:
                Eg_ref = self.Eg_1800 * (speed / self.N_original)
                self.ax_saturation.plot(self.If_original, Eg_ref, 'o--',
                                       linewidth=1, markersize=4, alpha=0.3, label=f'{speed} rpm')

        self.ax_saturation.set_xlabel('Field Current If (A)', fontsize=11, fontweight='bold')
        self.ax_saturation.set_ylabel('Generated Voltage Eg (V)', fontsize=11, fontweight='bold')
        self.ax_saturation.set_title('DC Generator Saturation Curves at Various Speeds',
                                     fontsize=13, fontweight='bold')
        self.ax_saturation.grid(True, alpha=0.3, linestyle='--')
        self.ax_saturation.legend(loc='best', fontsize=9)

        self.canvas.draw_idle()

    def calculate_all_parts(self):
        """Calculate all parts (a, b, c, d) of the problem"""
        self.result_text.delete(1.0, tk.END)

        result = "=" * 50 + "\n"
        result += "DC GENERATOR SATURATION CURVE ANALYSIS\n"
        result += "=" * 50 + "\n\n"

        # Part (a): Plot at 1500 rpm
        result += "PART (a): Saturation curve at 1500 rpm\n"
        result += "-" * 50 + "\n"
        Eg_1500 = self.Eg_1800 * (1500 / 1800)
        result += "Speed scaling: Eg(1500) = Eg(1800) × (1500/1800)\n\n"
        result += f"{'If (A)':<10} {'Eg @ 1800rpm (V)':<18} {'Eg @ 1500rpm (V)':<18}\n"
        result += "-" * 50 + "\n"
        for i in range(len(self.If_original)):
            result += f"{self.If_original[i]:<10.1f} {self.Eg_1800[i]:<18.1f} {Eg_1500[i]:<18.1f}\n"
        result += "\n"

        # Part (b): Voltage at 1000 rpm with If = 4.6 A
        result += "PART (b): Voltage at 1000 rpm, If = 4.6 A\n"
        result += "-" * 50 + "\n"
        If_b = 4.6
        speed_b = 1000
        voltage_b = self.calculate_voltage_at_current(If_b, speed_b)
        result += f"Field Current: {If_b} A\n"
        result += f"Speed: {speed_b} rpm\n"
        result += f"Generated Voltage: {voltage_b:.2f} V\n\n"

        # Part (c): Field current for 120V at 900 rpm
        result += "PART (c): Field current for 120V at 900 rpm\n"
        result += "-" * 50 + "\n"
        target_voltage_c = 120
        speed_c = 900
        If_c = self.calculate_field_current_for_voltage(target_voltage_c, speed_c)
        result += f"Target Voltage: {target_voltage_c} V\n"
        result += f"Speed: {speed_c} rpm\n"
        result += f"Required Field Current: {If_c:.3f} A\n\n"

        # Part (d): No-load voltage at 1500 rpm (shunt generator with If=4.6A at 1800rpm)
        result += "PART (d): No-load voltage at 1500 rpm\n"
        result += "         (Shunt generator, If = 4.6A at 1800rpm)\n"
        result += "-" * 50 + "\n"
        If_d = 4.6
        speed_d = 1500
        voltage_d = self.calculate_voltage_at_current(If_d, speed_d)
        result += f"Field Current: {If_d} A (constant for shunt)\n"
        result += f"Original Speed: 1800 rpm\n"
        result += f"New Speed: {speed_d} rpm\n"
        result += f"No-load Voltage: {voltage_d:.2f} V\n\n"

        result += "=" * 50 + "\n"
        result += "NOTES:\n"
        result += "- Voltage proportional to speed: Eg ∝ N\n"
        result += "- Cubic spline interpolation used for accuracy\n"
        result += "- Magnetic saturation effects included\n"
        result += "=" * 50 + "\n"

        self.result_text.insert(1.0, result)
        self.status_bar.config(text="Calculation completed successfully")

    def generator_ode_euler(self, state, t, params):
        """
        Differential equations for DC generator using Euler method
        state = [Vt, If, Ia]
        """
        Vt, If, Ia = state
        Rf, Ra, La, Lf, RL, N = params

        # Get generated voltage from saturation curve
        Eg = self.calculate_voltage_at_current(If, N)

        # Differential equations
        # dIf/dt = (Vt - If*Rf) / Lf  (field circuit)
        # dIa/dt = (Eg - Vt - Ia*Ra) / La  (armature circuit)
        # Vt = Ia * RL  (load)

        dIf_dt = (Vt - If * Rf) / Lf if Lf > 0 else 0
        dIa_dt = (Eg - Vt - Ia * Ra) / La if La > 0 else 0
        dVt_dt = (Ia * RL - Vt) / 0.1  # RC time constant

        return [dVt_dt, dIf_dt, dIa_dt]

    def generator_ode_rk45(self, t, state, params):
        """
        Differential equations for DC generator (RK45 format)
        """
        Vt, If, Ia = state
        Rf, Ra, La, Lf, RL, N = params

        # Get generated voltage from saturation curve
        Eg = self.calculate_voltage_at_current(If, N)

        # Armature and field inductances (typical values)
        dIf_dt = (Vt - If * Rf) / Lf if Lf > 0 else 0
        dIa_dt = (Eg - Vt - Ia * Ra) / La if La > 0 else 0
        dVt_dt = (Ia * RL - Vt) / 0.1

        return [dVt_dt, dIf_dt, dIa_dt]

    def simulate_euler(self, t_span, initial_state, params, dt=0.01):
        """Euler method integration"""
        t_start, t_end = t_span
        t = np.arange(t_start, t_end, dt)
        state = np.zeros((len(t), len(initial_state)))
        state[0] = initial_state

        for i in range(1, len(t)):
            derivatives = self.generator_ode_euler(state[i-1], t[i-1], params)
            state[i] = state[i-1] + np.array(derivatives) * dt

            # Update status periodically
            if i % 100 == 0 and self.simulation_running:
                progress = (i / len(t)) * 100
                self.root.after(0, lambda p=progress: self.sim_status_label.config(
                    text=f"Status: Simulating... {p:.1f}%"))

        return t, state

    def run_simulation_thread(self):
        """Run simulation in separate thread"""
        try:
            # Get parameters
            N = self.speed_var.get()
            Rf = self.field_resistance_var.get()
            RL = self.load_resistance_var.get()
            t_end = self.simulation_time_var.get()
            solver = self.solver_var.get()

            # Typical DC generator parameters
            Ra = 0.5  # Armature resistance
            La = 0.01  # Armature inductance
            Lf = 0.1  # Field inductance

            params = (Rf, Ra, La, Lf, RL, N)

            # Initial conditions [Vt, If, Ia]
            initial_state = [10.0, 0.1, 0.1]

            # Clear previous data
            self.time_data = []
            self.voltage_data = []
            self.current_data = []

            # Run simulation based on selected solver
            if solver == "Euler":
                t, state = self.simulate_euler((0, t_end), initial_state, params, dt=0.001)
                self.time_data = t
                self.voltage_data = state[:, 0]
                self.current_data = state[:, 2]
            else:
                # Use scipy's solve_ivp for RK45, RK23, DOP853
                sol = solve_ivp(
                    self.generator_ode_rk45,
                    (0, t_end),
                    initial_state,
                    method=solver,
                    args=(params,),
                    dense_output=True,
                    max_step=0.01
                )

                self.time_data = sol.t
                self.voltage_data = sol.y[0]
                self.current_data = sol.y[2]

            # Update plots
            self.root.after(0, self.update_dynamic_plots)
            self.root.after(0, lambda: self.sim_status_label.config(text="Status: Simulation Complete"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Simulation Error", str(e)))
        finally:
            self.simulation_running = False
            self.root.after(0, lambda: self.btn_start.config(state='normal'))
            self.root.after(0, lambda: self.btn_stop.config(state='disabled'))

    def start_simulation(self):
        """Start the dynamic simulation"""
        if not self.simulation_running:
            self.simulation_running = True
            self.btn_start.config(state='disabled')
            self.btn_stop.config(state='normal')
            self.sim_status_label.config(text="Status: Starting simulation...")

            # Run in separate thread
            self.simulation_thread = threading.Thread(target=self.run_simulation_thread, daemon=True)
            self.simulation_thread.start()

    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_running = False
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.sim_status_label.config(text="Status: Stopped")

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()
        self.time_data = []
        self.voltage_data = []
        self.current_data = []

        self.ax_voltage.clear()
        self.ax_current.clear()

        self.ax_voltage.set_title('Terminal Voltage vs Time', fontweight='bold')
        self.ax_voltage.set_ylabel('Voltage (V)', fontweight='bold')
        self.ax_voltage.grid(True, alpha=0.3)

        self.ax_current.set_title('Armature Current vs Time', fontweight='bold')
        self.ax_current.set_xlabel('Time (s)', fontweight='bold')
        self.ax_current.set_ylabel('Current (A)', fontweight='bold')
        self.ax_current.grid(True, alpha=0.3)

        self.canvas_dynamic.draw()
        self.sim_status_label.config(text="Status: Reset")

    def update_dynamic_plots(self):
        """Update dynamic simulation plots"""
        self.ax_voltage.clear()
        self.ax_current.clear()

        if len(self.time_data) > 0:
            # Voltage plot
            self.ax_voltage.plot(self.time_data, self.voltage_data, 'b-', linewidth=2)
            self.ax_voltage.set_title('Terminal Voltage vs Time', fontweight='bold', fontsize=11)
            self.ax_voltage.set_ylabel('Voltage (V)', fontweight='bold')
            self.ax_voltage.grid(True, alpha=0.3, linestyle='--')

            # Current plot
            self.ax_current.plot(self.time_data, self.current_data, 'r-', linewidth=2)
            self.ax_current.set_title('Armature Current vs Time', fontweight='bold', fontsize=11)
            self.ax_current.set_xlabel('Time (s)', fontweight='bold')
            self.ax_current.set_ylabel('Current (A)', fontweight='bold')
            self.ax_current.grid(True, alpha=0.3, linestyle='--')

        self.fig_dynamic.tight_layout()
        self.canvas_dynamic.draw()

    def analyze_saturation(self):
        """Analyze magnetic saturation characteristics"""
        self.analysis_text.delete(1.0, tk.END)
        self.ax_analysis.clear()

        result = "MAGNETIC SATURATION ANALYSIS\n"
        result += "=" * 45 + "\n\n"

        # Calculate saturation factor
        # Saturation factor = actual voltage / air-gap line voltage

        # Linear region (first two points)
        slope_linear = (self.Eg_1800[1] - self.Eg_1800[0]) / (self.If_original[1] - self.If_original[0])

        If_analysis = np.linspace(0, 6, 100)
        Eg_airgap = slope_linear * If_analysis  # Air-gap line

        interpolator = self.get_interpolation_function(1800)
        Eg_actual = interpolator(If_analysis)

        saturation_factor = Eg_actual / (Eg_airgap + 0.001)  # Avoid division by zero

        # Find knee point (where saturation starts)
        diff_saturation = np.diff(saturation_factor)
        knee_idx = np.argmax(diff_saturation < -0.01) if any(diff_saturation < -0.01) else len(diff_saturation)//2

        result += f"Air-gap line slope: {slope_linear:.2f} V/A\n"
        result += f"Knee point at If ≈ {If_analysis[knee_idx]:.2f} A\n"
        result += f"Voltage at knee: {Eg_actual[knee_idx]:.2f} V\n\n"

        result += "Saturation factors at key points:\n"
        result += "-" * 45 + "\n"
        for i in [10, 25, 50, 75, 99]:
            result += f"If = {If_analysis[i]:.2f} A: SF = {saturation_factor[i]:.3f}\n"

        # Plot
        self.ax_analysis.plot(If_analysis, Eg_actual, 'b-', linewidth=2.5, label='Actual Curve')
        self.ax_analysis.plot(If_analysis, Eg_airgap, 'r--', linewidth=2, label='Air-gap Line')
        self.ax_analysis.plot(If_analysis[knee_idx], Eg_actual[knee_idx], 'go',
                             markersize=12, label='Knee Point', zorder=5)

        self.ax_analysis.set_xlabel('Field Current (A)', fontweight='bold', fontsize=11)
        self.ax_analysis.set_ylabel('Generated Voltage (V)', fontweight='bold', fontsize=11)
        self.ax_analysis.set_title('Magnetic Saturation Characteristics', fontweight='bold', fontsize=12)
        self.ax_analysis.grid(True, alpha=0.3, linestyle='--')
        self.ax_analysis.legend(loc='best', fontsize=10)

        self.canvas_analysis.draw()
        self.analysis_text.insert(1.0, result)

    def analyze_critical_speed(self):
        """Analyze critical speed for self-excitation"""
        self.analysis_text.delete(1.0, tk.END)
        self.ax_analysis.clear()

        result = "CRITICAL SPEED ANALYSIS\n"
        result += "=" * 45 + "\n\n"

        # For self-excitation: Eg > If * Rf (voltage must overcome field resistance)
        # Critical speed is minimum speed for self-excitation

        Rf_values = [25, 50, 75, 100, 150]
        critical_speeds = []

        result += "Critical speeds for different field resistances:\n"
        result += "-" * 45 + "\n"

        for Rf in Rf_values:
            # Find intersection of saturation curve and resistance line
            speeds = np.linspace(500, 2500, 50)
            min_speed = 2500

            for speed in speeds:
                interpolator = self.get_interpolation_function(speed)
                If_test = np.linspace(0.5, 6, 100)
                Eg_test = interpolator(If_test)
                Vf_test = If_test * Rf

                # Find if curves intersect (besides origin)
                diff = Eg_test - Vf_test
                if any(diff > 0):
                    min_speed = speed
                    break

            critical_speeds.append(min_speed)
            result += f"Rf = {Rf:3d} Ω: Critical speed = {min_speed:4.0f} rpm\n"

        # Plot saturation curves at various speeds with resistance lines
        speeds_plot = [1000, 1500, 1800, 2000]
        If_plot = np.linspace(0, 6, 100)

        for speed in speeds_plot:
            interpolator = self.get_interpolation_function(speed)
            Eg_plot = interpolator(If_plot)
            self.ax_analysis.plot(If_plot, Eg_plot, linewidth=2, label=f'{speed} rpm', alpha=0.7)

        # Plot resistance lines
        for Rf in [50, 100, 150]:
            Vf_line = If_plot * Rf
            self.ax_analysis.plot(If_plot, Vf_line, '--', linewidth=1.5,
                                 label=f'Rf = {Rf}Ω', alpha=0.6)

        self.ax_analysis.set_xlabel('Field Current (A)', fontweight='bold', fontsize=11)
        self.ax_analysis.set_ylabel('Voltage (V)', fontweight='bold', fontsize=11)
        self.ax_analysis.set_title('Critical Speed Analysis for Self-Excitation',
                                   fontweight='bold', fontsize=12)
        self.ax_analysis.grid(True, alpha=0.3, linestyle='--')
        self.ax_analysis.legend(loc='best', fontsize=8, ncol=2)
        self.ax_analysis.set_xlim([0, 6])
        self.ax_analysis.set_ylim([0, 400])

        self.canvas_analysis.draw()
        self.analysis_text.insert(1.0, result)

    def analyze_voltage_regulation(self):
        """Analyze voltage regulation characteristics"""
        self.analysis_text.delete(1.0, tk.END)
        self.ax_analysis.clear()

        result = "VOLTAGE REGULATION ANALYSIS\n"
        result += "=" * 45 + "\n\n"

        # Voltage regulation = (Vnl - Vfl) / Vfl × 100%
        # where Vnl = no-load voltage, Vfl = full-load voltage

        If_fixed = 4.0
        speed = 1800
        Ra = 0.5  # Armature resistance

        # No-load voltage
        Vnl = self.calculate_voltage_at_current(If_fixed, speed)

        # Calculate voltage at various loads
        Ia_range = np.linspace(0, 50, 100)
        Vt_range = []

        for Ia in Ia_range:
            # Terminal voltage = Eg - Ia*Ra - armature reaction drop
            # Armature reaction approximated as equivalent field current reduction
            If_effective = If_fixed - 0.02 * Ia  # Approximation
            If_effective = max(If_effective, 0.5)

            Eg_load = self.calculate_voltage_at_current(If_effective, speed)
            Vt = Eg_load - Ia * Ra
            Vt = max(Vt, 0)
            Vt_range.append(Vt)

        Vt_range = np.array(Vt_range)

        # Calculate regulation at different load points
        result += f"No-load voltage: {Vnl:.2f} V\n"
        result += f"Field current: {If_fixed} A\n"
        result += f"Speed: {speed} rpm\n\n"

        result += "Voltage regulation at various loads:\n"
        result += "-" * 45 + "\n"
        result += f"{'Load (A)':<12} {'Vt (V)':<12} {'Reg (%)':<12}\n"
        result += "-" * 45 + "\n"

        for i in [10, 25, 50, 75, 90]:
            Ia = Ia_range[i]
            Vt = Vt_range[i]
            reg = ((Vnl - Vt) / Vt * 100) if Vt > 0 else 0
            result += f"{Ia:<12.1f} {Vt:<12.1f} {reg:<12.1f}\n"

        # Plot external characteristic
        self.ax_analysis.plot(Ia_range, Vt_range, 'b-', linewidth=2.5, label='Terminal Voltage')
        self.ax_analysis.axhline(y=Vnl, color='r', linestyle='--', linewidth=2, label='No-load Voltage')

        # Mark rated point (typically at 70% of max current)
        rated_idx = int(0.7 * len(Ia_range))
        self.ax_analysis.plot(Ia_range[rated_idx], Vt_range[rated_idx], 'go',
                             markersize=12, label='Rated Point', zorder=5)

        self.ax_analysis.set_xlabel('Armature Current (A)', fontweight='bold', fontsize=11)
        self.ax_analysis.set_ylabel('Terminal Voltage (V)', fontweight='bold', fontsize=11)
        self.ax_analysis.set_title('External Characteristic Curve (Voltage Regulation)',
                                   fontweight='bold', fontsize=12)
        self.ax_analysis.grid(True, alpha=0.3, linestyle='--')
        self.ax_analysis.legend(loc='best', fontsize=10)

        self.canvas_analysis.draw()
        self.analysis_text.insert(1.0, result)

    def analyze_efficiency(self):
        """Analyze efficiency curves"""
        self.analysis_text.delete(1.0, tk.END)
        self.ax_analysis.clear()

        result = "EFFICIENCY ANALYSIS\n"
        result += "=" * 45 + "\n\n"

        # Efficiency = Pout / Pin = Pout / (Pout + Losses)
        # Losses = Fixed losses + Variable losses (I²R)

        If_fixed = 4.0
        speed = 1800
        Ra = 0.5
        Rf = 50

        # Fixed losses (core, friction, windage)
        P_fixed = 500  # Watts

        # Field loss
        Vf = self.calculate_voltage_at_current(If_fixed, speed)
        P_field = Vf * If_fixed

        Ia_range = np.linspace(1, 50, 100)
        efficiency = []
        power_out = []

        for Ia in Ia_range:
            If_effective = If_fixed - 0.02 * Ia
            If_effective = max(If_effective, 0.5)

            Eg = self.calculate_voltage_at_current(If_effective, speed)
            Vt = Eg - Ia * Ra
            Vt = max(Vt, 0)

            Pout = Vt * Ia
            P_armature_loss = Ia**2 * Ra
            P_total_loss = P_fixed + P_field + P_armature_loss

            Pin = Pout + P_total_loss
            eff = (Pout / Pin * 100) if Pin > 0 else 0

            efficiency.append(eff)
            power_out.append(Pout / 1000)  # Convert to kW

        efficiency = np.array(efficiency)
        power_out = np.array(power_out)

        # Find maximum efficiency
        max_eff_idx = np.argmax(efficiency)
        max_eff = efficiency[max_eff_idx]
        Ia_max_eff = Ia_range[max_eff_idx]

        result += f"Operating conditions:\n"
        result += f"  Speed: {speed} rpm\n"
        result += f"  Field current: {If_fixed} A\n"
        result += f"  Fixed losses: {P_fixed} W\n\n"

        result += f"Maximum efficiency: {max_eff:.2f}%\n"
        result += f"  at Ia = {Ia_max_eff:.2f} A\n"
        result += f"  Power output = {power_out[max_eff_idx]:.2f} kW\n\n"

        result += "Efficiency at various loads:\n"
        result += "-" * 45 + "\n"
        result += f"{'Ia (A)':<12} {'Pout (kW)':<12} {'Eff (%)':<12}\n"
        result += "-" * 45 + "\n"

        for i in [10, 25, 50, 75, 90]:
            result += f"{Ia_range[i]:<12.1f} {power_out[i]:<12.2f} {efficiency[i]:<12.2f}\n"

        # Plot efficiency curve
        ax2 = self.ax_analysis.twinx()

        line1 = self.ax_analysis.plot(Ia_range, efficiency, 'b-', linewidth=2.5, label='Efficiency')
        self.ax_analysis.plot(Ia_max_eff, max_eff, 'ro', markersize=12,
                             label=f'Max Eff: {max_eff:.1f}%', zorder=5)

        line2 = ax2.plot(Ia_range, power_out, 'g--', linewidth=2, label='Output Power')

        self.ax_analysis.set_xlabel('Armature Current (A)', fontweight='bold', fontsize=11)
        self.ax_analysis.set_ylabel('Efficiency (%)', fontweight='bold', fontsize=11, color='b')
        ax2.set_ylabel('Output Power (kW)', fontweight='bold', fontsize=11, color='g')

        self.ax_analysis.set_title('Efficiency and Power Output Curves', fontweight='bold', fontsize=12)
        self.ax_analysis.grid(True, alpha=0.3, linestyle='--')

        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        self.ax_analysis.legend(lines, labels, loc='best', fontsize=10)

        self.ax_analysis.tick_params(axis='y', labelcolor='b')
        ax2.tick_params(axis='y', labelcolor='g')

        self.canvas_analysis.draw()
        self.analysis_text.insert(1.0, result)

    def reset_saturation(self):
        """Reset saturation curve analysis"""
        self.speed_var.set(1800)
        self.field_current_var.set(4.6)
        self.result_text.delete(1.0, tk.END)
        self.update_saturation_plot()
        self.status_bar.config(text="Reset to default values")

    def export_data(self):
        """Export data to file"""
        try:
            with open('saturation_data.txt', 'w') as f:
                f.write("DC Generator Saturation Curve Data\n")
                f.write("=" * 50 + "\n\n")
                f.write("Original Data (1800 rpm):\n")
                f.write(f"{'If (A)':<10} {'Eg (V)':<10}\n")
                f.write("-" * 20 + "\n")
                for i in range(len(self.If_original)):
                    f.write(f"{self.If_original[i]:<10.1f} {self.Eg_1800[i]:<10.1f}\n")

            messagebox.showinfo("Export", "Data exported to saturation_data.txt")
            self.status_bar.config(text="Data exported successfully")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SaturationCurveAnalyzer(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()
