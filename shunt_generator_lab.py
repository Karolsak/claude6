"""
Advanced Shunt Generator Dynamic Simulation Lab
Electrical Engineering Application with Real-time ODE Solver
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from scipy.integrate import solve_ivp

class ShuntGeneratorLab:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Shunt Generator Dynamic Simulation Lab")
        self.root.geometry("1400x900")

        # Generator parameters (default values from problem)
        self.params = {
            'P_rated': 100000,      # Rated power (W)
            'V_rated': 230,         # Rated voltage (V)
            'Ra': 0.05,             # Armature resistance (Ω)
            'Rf': 57.5,             # Field resistance (Ω)
            'La': 0.01,             # Armature inductance (H)
            'Lf': 5.0,              # Field inductance (H)
            'speed': 1800,          # Speed (RPM)
            'load_factor': 1.0,     # Load factor (0-1)
            'Kf': 1.2,              # Field constant
        }

        # Simulation parameters
        self.sim_running = False
        self.sim_paused = False
        self.solver_method = 'RK45'  # 'RK45' or 'Euler'
        self.dt = 0.001  # Time step for Euler method
        self.time_data = []
        self.ia_data = []
        self.if_data = []
        self.ea_data = []
        self.v_terminal_data = []
        self.power_data = []
        self.efficiency_data = []

        # State variables
        self.current_time = 0
        self.state = np.array([0.0, 0.0])  # [Ia, If]

        # Create main container with grid that responds to window resize
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_menu()
        self.create_widgets()

        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def create_menu(self):
        """Create main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset to Defaults", command=self.reset_defaults)
        file_menu.add_command(label="Save Results", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Solver menu
        solver_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Solver", menu=solver_menu)
        solver_menu.add_radiobutton(label="RK45 (Runge-Kutta)",
                                     command=lambda: self.set_solver('RK45'))
        solver_menu.add_radiobutton(label="Euler Method",
                                     command=lambda: self.set_solver('Euler'))

        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Steady-State Analysis",
                                  command=self.steady_state_analysis)
        analysis_menu.add_command(label="Load Characteristics",
                                  command=self.load_characteristics)
        analysis_menu.add_command(label="Voltage Regulation",
                                  command=self.voltage_regulation_analysis)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_widgets(self):
        """Create main GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)

        # Left panel - Controls
        self.create_control_panel(main_frame)

        # Right panel - Visualization
        self.create_visualization_panel(main_frame)

        # Bottom panel - Results
        self.create_results_panel(main_frame)

    def create_control_panel(self, parent):
        """Create control panel with input parameters and sliders"""
        control_frame = ttk.LabelFrame(parent, text="Control Panel", padding=10)
        control_frame.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)

        # Input Parameters Section
        params_frame = ttk.LabelFrame(control_frame, text="Generator Parameters", padding=5)
        params_frame.pack(fill='x', padx=5, pady=5)

        row = 0
        self.param_entries = {}

        # Power Rating
        ttk.Label(params_frame, text="Rated Power (kW):").grid(row=row, column=0, sticky='w', pady=2)
        self.param_entries['P_rated'] = ttk.Entry(params_frame, width=10)
        self.param_entries['P_rated'].insert(0, str(self.params['P_rated']/1000))
        self.param_entries['P_rated'].grid(row=row, column=1, pady=2)
        row += 1

        # Voltage Rating
        ttk.Label(params_frame, text="Rated Voltage (V):").grid(row=row, column=0, sticky='w', pady=2)
        self.param_entries['V_rated'] = ttk.Entry(params_frame, width=10)
        self.param_entries['V_rated'].insert(0, str(self.params['V_rated']))
        self.param_entries['V_rated'].grid(row=row, column=1, pady=2)
        row += 1

        # Armature Resistance
        ttk.Label(params_frame, text="Ra (Ω):").grid(row=row, column=0, sticky='w', pady=2)
        self.param_entries['Ra'] = ttk.Entry(params_frame, width=10)
        self.param_entries['Ra'].insert(0, str(self.params['Ra']))
        self.param_entries['Ra'].grid(row=row, column=1, pady=2)
        row += 1

        # Field Resistance
        ttk.Label(params_frame, text="Rf (Ω):").grid(row=row, column=0, sticky='w', pady=2)
        self.param_entries['Rf'] = ttk.Entry(params_frame, width=10)
        self.param_entries['Rf'].insert(0, str(self.params['Rf']))
        self.param_entries['Rf'].grid(row=row, column=1, pady=2)
        row += 1

        # Armature Inductance
        ttk.Label(params_frame, text="La (H):").grid(row=row, column=0, sticky='w', pady=2)
        self.param_entries['La'] = ttk.Entry(params_frame, width=10)
        self.param_entries['La'].insert(0, str(self.params['La']))
        self.param_entries['La'].grid(row=row, column=1, pady=2)
        row += 1

        # Field Inductance
        ttk.Label(params_frame, text="Lf (H):").grid(row=row, column=0, sticky='w', pady=2)
        self.param_entries['Lf'] = ttk.Entry(params_frame, width=10)
        self.param_entries['Lf'].insert(0, str(self.params['Lf']))
        self.param_entries['Lf'].grid(row=row, column=1, pady=2)
        row += 1

        # Speed
        ttk.Label(params_frame, text="Speed (RPM):").grid(row=row, column=0, sticky='w', pady=2)
        self.param_entries['speed'] = ttk.Entry(params_frame, width=10)
        self.param_entries['speed'].insert(0, str(self.params['speed']))
        self.param_entries['speed'].grid(row=row, column=1, pady=2)
        row += 1

        # Apply button
        ttk.Button(params_frame, text="Apply Parameters",
                  command=self.apply_parameters).grid(row=row, column=0, columnspan=2, pady=5)

        # Control Sliders Section
        sliders_frame = ttk.LabelFrame(control_frame, text="Dynamic Controls", padding=5)
        sliders_frame.pack(fill='x', padx=5, pady=5)

        # Load Factor Slider
        ttk.Label(sliders_frame, text="Load Factor:").pack(anchor='w')
        self.load_scale = ttk.Scale(sliders_frame, from_=0, to=1.5,
                                    orient='horizontal', command=self.update_load_factor)
        self.load_scale.set(self.params['load_factor'])
        self.load_scale.pack(fill='x', pady=2)
        self.load_label = ttk.Label(sliders_frame, text=f"{self.params['load_factor']:.2f}")
        self.load_label.pack(anchor='w')

        # Speed Slider
        ttk.Label(sliders_frame, text="Speed (RPM):").pack(anchor='w', pady=(10,0))
        self.speed_scale = ttk.Scale(sliders_frame, from_=0, to=3600,
                                     orient='horizontal', command=self.update_speed)
        self.speed_scale.set(self.params['speed'])
        self.speed_scale.pack(fill='x', pady=2)
        self.speed_label = ttk.Label(sliders_frame, text=f"{self.params['speed']:.0f} RPM")
        self.speed_label.pack(anchor='w')

        # Field Constant Slider
        ttk.Label(sliders_frame, text="Field Constant (Kf):").pack(anchor='w', pady=(10,0))
        self.kf_scale = ttk.Scale(sliders_frame, from_=0.5, to=2.0,
                                  orient='horizontal', command=self.update_kf)
        self.kf_scale.set(self.params['Kf'])
        self.kf_scale.pack(fill='x', pady=2)
        self.kf_label = ttk.Label(sliders_frame, text=f"{self.params['Kf']:.2f}")
        self.kf_label.pack(anchor='w')

        # Simulation Controls
        sim_frame = ttk.LabelFrame(control_frame, text="Simulation Controls", padding=5)
        sim_frame.pack(fill='x', padx=5, pady=5)

        button_frame = ttk.Frame(sim_frame)
        button_frame.pack(fill='x')

        self.start_btn = ttk.Button(button_frame, text="Start",
                                    command=self.start_simulation, width=12)
        self.start_btn.pack(side='left', padx=2, pady=5)

        self.pause_btn = ttk.Button(button_frame, text="Pause",
                                    command=self.pause_simulation, width=12, state='disabled')
        self.pause_btn.pack(side='left', padx=2, pady=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop",
                                   command=self.stop_simulation, width=12, state='disabled')
        self.stop_btn.pack(side='left', padx=2, pady=5)

        self.reset_btn = ttk.Button(button_frame, text="Reset",
                                    command=self.reset_simulation, width=12)
        self.reset_btn.pack(side='left', padx=2, pady=5)

        # Solver selection
        ttk.Label(sim_frame, text="Solver Method:").pack(anchor='w', pady=(10,2))
        self.solver_var = tk.StringVar(value='RK45')
        ttk.Radiobutton(sim_frame, text="RK45 (Runge-Kutta)",
                       variable=self.solver_var, value='RK45',
                       command=lambda: self.set_solver('RK45')).pack(anchor='w')
        ttk.Radiobutton(sim_frame, text="Euler Method",
                       variable=self.solver_var, value='Euler',
                       command=lambda: self.set_solver('Euler')).pack(anchor='w')

        # Status display
        status_frame = ttk.LabelFrame(control_frame, text="Status", padding=5)
        status_frame.pack(fill='x', padx=5, pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready", foreground='green')
        self.status_label.pack(anchor='w')

        self.time_label = ttk.Label(status_frame, text="Time: 0.000 s")
        self.time_label.pack(anchor='w')

    def create_visualization_panel(self, parent):
        """Create visualization panel with plots"""
        viz_frame = ttk.LabelFrame(parent, text="Real-time Visualization", padding=5)
        viz_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure with subplots
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.fig.subplots_adjust(hspace=0.4, wspace=0.3)

        # Create subplots
        self.ax1 = self.fig.add_subplot(3, 2, 1)
        self.ax2 = self.fig.add_subplot(3, 2, 2)
        self.ax3 = self.fig.add_subplot(3, 2, 3)
        self.ax4 = self.fig.add_subplot(3, 2, 4)
        self.ax5 = self.fig.add_subplot(3, 2, 5)
        self.ax6 = self.fig.add_subplot(3, 2, 6)

        # Initialize plots
        self.line1, = self.ax1.plot([], [], 'b-', linewidth=2)
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Armature Current (A)')
        self.ax1.set_title('Armature Current vs Time')
        self.ax1.grid(True, alpha=0.3)

        self.line2, = self.ax2.plot([], [], 'r-', linewidth=2)
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Field Current (A)')
        self.ax2.set_title('Field Current vs Time')
        self.ax2.grid(True, alpha=0.3)

        self.line3, = self.ax3.plot([], [], 'g-', linewidth=2)
        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Induced EMF (V)')
        self.ax3.set_title('Induced EMF vs Time')
        self.ax3.grid(True, alpha=0.3)

        self.line4, = self.ax4.plot([], [], 'm-', linewidth=2)
        self.ax4.set_xlabel('Time (s)')
        self.ax4.set_ylabel('Terminal Voltage (V)')
        self.ax4.set_title('Terminal Voltage vs Time')
        self.ax4.grid(True, alpha=0.3)

        self.line5, = self.ax5.plot([], [], 'c-', linewidth=2)
        self.ax5.set_xlabel('Time (s)')
        self.ax5.set_ylabel('Output Power (kW)')
        self.ax5.set_title('Output Power vs Time')
        self.ax5.grid(True, alpha=0.3)

        self.line6, = self.ax6.plot([], [], 'orange', linewidth=2)
        self.ax6.set_xlabel('Time (s)')
        self.ax6.set_ylabel('Efficiency (%)')
        self.ax6.set_title('Efficiency vs Time')
        self.ax6.grid(True, alpha=0.3)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def create_results_panel(self, parent):
        """Create results panel with calculated values"""
        results_frame = ttk.LabelFrame(parent, text="Calculated Results", padding=10)
        results_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        # Create text widget for results
        self.results_text = tk.Text(results_frame, height=8, width=80,
                                    font=('Courier', 10))
        self.results_text.pack(fill='both', expand=True)

        # Display initial steady-state calculations
        self.display_steady_state_results()

    def apply_parameters(self):
        """Apply parameter changes from entry fields"""
        try:
            self.params['P_rated'] = float(self.param_entries['P_rated'].get()) * 1000
            self.params['V_rated'] = float(self.param_entries['V_rated'].get())
            self.params['Ra'] = float(self.param_entries['Ra'].get())
            self.params['Rf'] = float(self.param_entries['Rf'].get())
            self.params['La'] = float(self.param_entries['La'].get())
            self.params['Lf'] = float(self.param_entries['Lf'].get())
            self.params['speed'] = float(self.param_entries['speed'].get())

            self.speed_scale.set(self.params['speed'])
            self.display_steady_state_results()
            messagebox.showinfo("Success", "Parameters applied successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid parameter values!")

    def update_load_factor(self, value):
        """Update load factor from slider"""
        self.params['load_factor'] = float(value)
        self.load_label.config(text=f"{self.params['load_factor']:.2f}")

    def update_speed(self, value):
        """Update speed from slider"""
        self.params['speed'] = float(value)
        self.speed_label.config(text=f"{self.params['speed']:.0f} RPM")

    def update_kf(self, value):
        """Update field constant from slider"""
        self.params['Kf'] = float(value)
        self.kf_label.config(text=f"{self.params['Kf']:.2f}")

    def calculate_steady_state(self, load_factor):
        """Calculate steady-state values for given load factor"""
        V = self.params['V_rated']
        P = self.params['P_rated'] * load_factor
        Ra = self.params['Ra']
        Rf = self.params['Rf']

        # Calculate currents
        IL = P / V if V > 0 else 0
        If = V / Rf if Rf > 0 else 0
        Ia = IL + If

        # Calculate induced EMF
        Ea = V + Ia * Ra

        # Calculate power and efficiency
        P_out = V * IL
        P_cu_a = Ia**2 * Ra
        P_cu_f = If**2 * Rf
        P_in = P_out + P_cu_a + P_cu_f
        efficiency = (P_out / P_in * 100) if P_in > 0 else 0

        return {
            'IL': IL,
            'If': If,
            'Ia': Ia,
            'Ea': Ea,
            'V': V,
            'P_out': P_out,
            'P_cu_a': P_cu_a,
            'P_cu_f': P_cu_f,
            'efficiency': efficiency
        }

    def display_steady_state_results(self):
        """Display steady-state calculations in results panel"""
        self.results_text.delete(1.0, tk.END)

        results = []
        results.append("=" * 80)
        results.append("STEADY-STATE ANALYSIS - SHUNT GENERATOR")
        results.append("=" * 80)
        results.append(f"Generator Rating: {self.params['P_rated']/1000:.1f} kW, {self.params['V_rated']:.1f} V")
        results.append(f"Armature Resistance (Ra): {self.params['Ra']:.4f} Ω")
        results.append(f"Field Resistance (Rf): {self.params['Rf']:.2f} Ω")
        results.append("-" * 80)

        # Full load
        results.append("\n(a) FULL LOAD CONDITIONS:")
        full_load = self.calculate_steady_state(1.0)
        results.append(f"    Load Current (IL):        {full_load['IL']:.2f} A")
        results.append(f"    Field Current (If):       {full_load['If']:.2f} A")
        results.append(f"    Armature Current (Ia):    {full_load['Ia']:.2f} A")
        results.append(f"    Induced EMF (Ea):         {full_load['Ea']:.2f} V")
        results.append(f"    Terminal Voltage (V):     {full_load['V']:.2f} V")
        results.append(f"    Output Power:             {full_load['P_out']/1000:.2f} kW")
        results.append(f"    Copper Loss (Armature):   {full_load['P_cu_a']:.2f} W")
        results.append(f"    Copper Loss (Field):      {full_load['P_cu_f']:.2f} W")
        results.append(f"    Efficiency:               {full_load['efficiency']:.2f} %")

        # Half load
        results.append("\n(b) HALF LOAD CONDITIONS:")
        half_load = self.calculate_steady_state(0.5)
        results.append(f"    Load Current (IL):        {half_load['IL']:.2f} A")
        results.append(f"    Field Current (If):       {half_load['If']:.2f} A")
        results.append(f"    Armature Current (Ia):    {half_load['Ia']:.2f} A")
        results.append(f"    Induced EMF (Ea):         {half_load['Ea']:.2f} V")
        results.append(f"    Terminal Voltage (V):     {half_load['V']:.2f} V")
        results.append(f"    Output Power:             {half_load['P_out']/1000:.2f} kW")
        results.append(f"    Copper Loss (Armature):   {half_load['P_cu_a']:.2f} W")
        results.append(f"    Copper Loss (Field):      {half_load['P_cu_f']:.2f} W")
        results.append(f"    Efficiency:               {half_load['efficiency']:.2f} %")

        results.append("\n" + "=" * 80)

        self.results_text.insert(1.0, "\n".join(results))

    def generator_ode(self, t, y):
        """
        Differential equations for shunt generator dynamics
        y[0] = Ia (armature current)
        y[1] = If (field current)
        """
        Ia, If = y

        # Parameters
        Ra = self.params['Ra']
        Rf = self.params['Rf']
        La = self.params['La']
        Lf = self.params['Lf']
        V = self.params['V_rated']
        speed = self.params['speed']
        Kf = self.params['Kf']
        load_factor = self.params['load_factor']

        # Calculate induced EMF (proportional to field current and speed)
        omega = speed * 2 * np.pi / 60  # Convert RPM to rad/s
        Ea = Kf * If * omega / 188.5  # Normalized

        # Load current based on load factor
        IL = (self.params['P_rated'] * load_factor) / V if V > 0 else 0

        # Armature circuit equation: Ea = V + Ia*Ra + La*dIa/dt
        dIa_dt = (Ea - V - Ia * Ra) / La if La > 0 else 0

        # Field circuit equation: V = If*Rf + Lf*dIf/dt
        dIf_dt = (V - If * Rf) / Lf if Lf > 0 else 0

        return [dIa_dt, dIf_dt]

    def euler_step(self, t, y, dt):
        """Euler method integration step"""
        dydt = self.generator_ode(t, y)
        y_new = y + np.array(dydt) * dt
        return y_new

    def simulation_loop(self):
        """Main simulation loop"""
        t_max = 10.0  # Maximum simulation time

        while self.sim_running and self.current_time < t_max:
            if not self.sim_paused:
                if self.solver_method == 'RK45':
                    # RK45 solver step
                    sol = solve_ivp(self.generator_ode,
                                  [self.current_time, self.current_time + 0.01],
                                  self.state, method='RK45', max_step=0.01)
                    self.state = sol.y[:, -1]
                    self.current_time = sol.t[-1]
                else:
                    # Euler method step
                    self.state = self.euler_step(self.current_time, self.state, self.dt)
                    self.current_time += self.dt

                # Extract state variables
                Ia = self.state[0]
                If = self.state[1]

                # Calculate other quantities
                V = self.params['V_rated']
                Ra = self.params['Ra']
                omega = self.params['speed'] * 2 * np.pi / 60
                Kf = self.params['Kf']

                Ea = Kf * If * omega / 188.5
                V_terminal = Ea - Ia * Ra
                IL = Ia - If
                P_out = V_terminal * IL
                P_in = Ea * Ia
                efficiency = (P_out / P_in * 100) if P_in > 0 and P_out > 0 else 0

                # Store data
                self.time_data.append(self.current_time)
                self.ia_data.append(Ia)
                self.if_data.append(If)
                self.ea_data.append(Ea)
                self.v_terminal_data.append(V_terminal)
                self.power_data.append(P_out / 1000)
                self.efficiency_data.append(efficiency)

                # Update plots
                self.update_plots()

                # Update status
                self.time_label.config(text=f"Time: {self.current_time:.3f} s")

                # Control simulation speed
                time.sleep(0.01)

        if self.sim_running:
            self.stop_simulation()

    def update_plots(self):
        """Update all plots with current data"""
        try:
            # Update data
            self.line1.set_data(self.time_data, self.ia_data)
            self.line2.set_data(self.time_data, self.if_data)
            self.line3.set_data(self.time_data, self.ea_data)
            self.line4.set_data(self.time_data, self.v_terminal_data)
            self.line5.set_data(self.time_data, self.power_data)
            self.line6.set_data(self.time_data, self.efficiency_data)

            # Auto-scale axes
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
                ax.relim()
                ax.autoscale_view()

            self.canvas.draw()
            self.canvas.flush_events()
        except:
            pass

    def start_simulation(self):
        """Start dynamic simulation"""
        if not self.sim_running:
            self.sim_running = True
            self.sim_paused = False
            self.status_label.config(text="Running", foreground='blue')
            self.start_btn.config(state='disabled')
            self.pause_btn.config(state='normal')
            self.stop_btn.config(state='normal')

            # Start simulation thread
            self.sim_thread = threading.Thread(target=self.simulation_loop)
            self.sim_thread.daemon = True
            self.sim_thread.start()

    def pause_simulation(self):
        """Pause/resume simulation"""
        if self.sim_running:
            self.sim_paused = not self.sim_paused
            if self.sim_paused:
                self.status_label.config(text="Paused", foreground='orange')
                self.pause_btn.config(text="Resume")
            else:
                self.status_label.config(text="Running", foreground='blue')
                self.pause_btn.config(text="Pause")

    def stop_simulation(self):
        """Stop simulation"""
        self.sim_running = False
        self.sim_paused = False
        self.status_label.config(text="Stopped", foreground='red')
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text="Pause")
        self.stop_btn.config(state='disabled')

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()

        # Clear data
        self.time_data = []
        self.ia_data = []
        self.if_data = []
        self.ea_data = []
        self.v_terminal_data = []
        self.power_data = []
        self.efficiency_data = []

        # Reset state
        self.current_time = 0
        self.state = np.array([0.0, 0.0])

        # Clear plots
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
            ax.clear()

        # Reinitialize plots
        self.line1, = self.ax1.plot([], [], 'b-', linewidth=2)
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Armature Current (A)')
        self.ax1.set_title('Armature Current vs Time')
        self.ax1.grid(True, alpha=0.3)

        self.line2, = self.ax2.plot([], [], 'r-', linewidth=2)
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Field Current (A)')
        self.ax2.set_title('Field Current vs Time')
        self.ax2.grid(True, alpha=0.3)

        self.line3, = self.ax3.plot([], [], 'g-', linewidth=2)
        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Induced EMF (V)')
        self.ax3.set_title('Induced EMF vs Time')
        self.ax3.grid(True, alpha=0.3)

        self.line4, = self.ax4.plot([], [], 'm-', linewidth=2)
        self.ax4.set_xlabel('Time (s)')
        self.ax4.set_ylabel('Terminal Voltage (V)')
        self.ax4.set_title('Terminal Voltage vs Time')
        self.ax4.grid(True, alpha=0.3)

        self.line5, = self.ax5.plot([], [], 'c-', linewidth=2)
        self.ax5.set_xlabel('Time (s)')
        self.ax5.set_ylabel('Output Power (kW)')
        self.ax5.set_title('Output Power vs Time')
        self.ax5.grid(True, alpha=0.3)

        self.line6, = self.ax6.plot([], [], 'orange', linewidth=2)
        self.ax6.set_xlabel('Time (s)')
        self.ax6.set_ylabel('Efficiency (%)')
        self.ax6.set_title('Efficiency vs Time')
        self.ax6.grid(True, alpha=0.3)

        self.canvas.draw()

        self.time_label.config(text="Time: 0.000 s")
        self.status_label.config(text="Ready", foreground='green')

    def set_solver(self, method):
        """Set solver method"""
        self.solver_method = method
        self.solver_var.set(method)
        messagebox.showinfo("Solver", f"Solver method set to: {method}")

    def steady_state_analysis(self):
        """Perform comprehensive steady-state analysis"""
        self.display_steady_state_results()
        messagebox.showinfo("Analysis", "Steady-state analysis complete! Check results panel.")

    def load_characteristics(self):
        """Plot load characteristics"""
        load_factors = np.linspace(0, 1.5, 50)
        voltages = []
        currents = []
        powers = []
        efficiencies = []

        for lf in load_factors:
            results = self.calculate_steady_state(lf)
            voltages.append(results['V'])
            currents.append(results['IL'])
            powers.append(results['P_out'] / 1000)
            efficiencies.append(results['efficiency'])

        # Create new window with plots
        window = tk.Toplevel(self.root)
        window.title("Load Characteristics")
        window.geometry("1000x600")

        fig = Figure(figsize=(10, 6))

        ax1 = fig.add_subplot(2, 2, 1)
        ax1.plot(currents, voltages, 'b-', linewidth=2)
        ax1.set_xlabel('Load Current (A)')
        ax1.set_ylabel('Terminal Voltage (V)')
        ax1.set_title('External Characteristic')
        ax1.grid(True, alpha=0.3)

        ax2 = fig.add_subplot(2, 2, 2)
        ax2.plot(currents, powers, 'r-', linewidth=2)
        ax2.set_xlabel('Load Current (A)')
        ax2.set_ylabel('Output Power (kW)')
        ax2.set_title('Power vs Load Current')
        ax2.grid(True, alpha=0.3)

        ax3 = fig.add_subplot(2, 2, 3)
        ax3.plot(powers, efficiencies, 'g-', linewidth=2)
        ax3.set_xlabel('Output Power (kW)')
        ax3.set_ylabel('Efficiency (%)')
        ax3.set_title('Efficiency vs Power')
        ax3.grid(True, alpha=0.3)

        ax4 = fig.add_subplot(2, 2, 4)
        ax4.plot(load_factors, currents, 'm-', linewidth=2)
        ax4.set_xlabel('Load Factor')
        ax4.set_ylabel('Load Current (A)')
        ax4.set_title('Current vs Load Factor')
        ax4.grid(True, alpha=0.3)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def voltage_regulation_analysis(self):
        """Calculate and display voltage regulation"""
        no_load = self.calculate_steady_state(0.01)
        full_load = self.calculate_steady_state(1.0)

        V_nl = no_load['V']
        V_fl = full_load['V']
        regulation = ((V_nl - V_fl) / V_fl) * 100

        message = f"Voltage Regulation Analysis:\n\n"
        message += f"No-Load Voltage: {V_nl:.2f} V\n"
        message += f"Full-Load Voltage: {V_fl:.2f} V\n"
        message += f"Voltage Regulation: {regulation:.2f} %\n\n"
        message += f"This indicates the voltage stability of the generator.\n"
        message += f"Lower regulation values indicate better voltage stability."

        messagebox.showinfo("Voltage Regulation", message)

    def reset_defaults(self):
        """Reset all parameters to default values"""
        self.params = {
            'P_rated': 100000,
            'V_rated': 230,
            'Ra': 0.05,
            'Rf': 57.5,
            'La': 0.01,
            'Lf': 5.0,
            'speed': 1800,
            'load_factor': 1.0,
            'Kf': 1.2,
        }

        # Update entries
        self.param_entries['P_rated'].delete(0, tk.END)
        self.param_entries['P_rated'].insert(0, str(self.params['P_rated']/1000))

        self.param_entries['V_rated'].delete(0, tk.END)
        self.param_entries['V_rated'].insert(0, str(self.params['V_rated']))

        self.param_entries['Ra'].delete(0, tk.END)
        self.param_entries['Ra'].insert(0, str(self.params['Ra']))

        self.param_entries['Rf'].delete(0, tk.END)
        self.param_entries['Rf'].insert(0, str(self.params['Rf']))

        self.param_entries['La'].delete(0, tk.END)
        self.param_entries['La'].insert(0, str(self.params['La']))

        self.param_entries['Lf'].delete(0, tk.END)
        self.param_entries['Lf'].insert(0, str(self.params['Lf']))

        self.param_entries['speed'].delete(0, tk.END)
        self.param_entries['speed'].insert(0, str(self.params['speed']))

        # Update sliders
        self.load_scale.set(self.params['load_factor'])
        self.speed_scale.set(self.params['speed'])
        self.kf_scale.set(self.params['Kf'])

        self.display_steady_state_results()
        messagebox.showinfo("Reset", "Parameters reset to default values!")

    def save_results(self):
        """Save current results to file"""
        try:
            with open('generator_results.txt', 'w') as f:
                f.write(self.results_text.get(1.0, tk.END))
            messagebox.showinfo("Save", "Results saved to generator_results.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Shunt Generator Dynamic Simulation Lab
Version 1.0

This application provides comprehensive simulation and analysis
of DC shunt generators for electrical engineering applications.

Features:
- Real-time dynamic simulation with ODE solvers (RK45, Euler)
- Steady-state analysis
- Load characteristics
- Voltage regulation analysis
- Interactive parameter adjustment
- Multiple visualization plots

Developed for educational and practical use in electrical engineering.
        """
        messagebox.showinfo("About", about_text)

    def on_window_resize(self, event):
        """Handle window resize events for auto-scaling"""
        try:
            if hasattr(self, 'canvas'):
                self.canvas.draw()
        except:
            pass

def main():
    root = tk.Tk()
    app = ShuntGeneratorLab(root)
    root.mainloop()

if __name__ == "__main__":
    main()
