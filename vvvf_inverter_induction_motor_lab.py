"""
VVVF Inverter-Fed Three-Phase Induction Motor Laboratory
Advanced simulation with dynamic modeling and real-time visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from scipy.integrate import solve_ivp
import math

class VVVFInductionMotorLab:
    """Comprehensive VVVF Inverter-Fed Induction Motor Laboratory"""

    def __init__(self, root):
        self.root = root
        self.root.title("VVVF Inverter-Fed Induction Motor Laboratory")
        self.root.geometry("1400x900")

        # Simulation parameters
        self.is_running = False
        self.simulation_time = 0.0
        self.dt = 0.001  # Time step for Euler method
        self.current_solver = "RK45"

        # Motor parameters (default values)
        self.motor_params = {
            'VL_rated': 380.0,      # Line-to-line voltage (V)
            'f_rated': 50.0,        # Rated frequency (Hz)
            'n_rated': 1450.0,      # Rated speed (rpm)
            'poles': 4,             # Number of poles
            'Rs': 1.5,              # Stator resistance (Ohm)
            'Rr': 1.2,              # Rotor resistance (Ohm)
            'Ls': 0.15,             # Stator inductance (H)
            'Lr': 0.15,             # Rotor inductance (H)
            'Lm': 0.14,             # Magnetizing inductance (H)
            'J': 0.05,              # Moment of inertia (kg.m^2)
            'B': 0.01,              # Friction coefficient (N.m.s)
            'speed_ratio': 10.0,    # Max to min speed ratio
        }

        # Rectifier parameters
        self.rectifier_params = {
            'VL_input': 380.0,      # Rectifier input voltage (V)
            'f_input': 50.0,        # Input frequency (Hz)
        }

        # Control parameters
        self.control_params = {
            'frequency': 50.0,      # Output frequency (Hz)
            'voltage': 380.0,       # Output voltage (V)
            'firing_angle': 0.0,    # Rectifier firing angle (degrees)
            'load_torque': 0.0,     # Load torque (N.m)
        }

        # State variables [ids, iqs, idr, iqr, omega_r, theta_r]
        self.state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Data storage for plotting
        self.time_data = []
        self.speed_data = []
        self.torque_data = []
        self.current_data = []
        self.voltage_dc_data = []
        self.slip_data = []

        # Calculate theoretical values
        self.calculate_theoretical_values()

        # Setup GUI
        self.setup_gui()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def calculate_theoretical_values(self):
        """Calculate maximum and minimum DC link voltage and firing angles"""
        VL = self.rectifier_params['VL_input']

        # Maximum DC voltage (firing angle = 0°)
        self.Vdc_max = (3 * math.sqrt(2) / math.pi) * VL
        self.alpha_max = 0.0

        # V/f ratio
        self.vf_ratio = self.motor_params['VL_rated'] / self.motor_params['f_rated']

        # Minimum frequency
        self.f_min = self.motor_params['f_rated'] / self.motor_params['speed_ratio']

        # Minimum voltage (line-to-line RMS)
        VL_min = self.f_min * self.vf_ratio

        # Minimum DC voltage needed (for space vector modulation)
        # Vdc = sqrt(2) * VL for SVM
        self.Vdc_min = math.sqrt(2) * VL_min

        # Calculate firing angle for minimum DC voltage
        # Vdc = Vdc_max * cos(alpha)
        cos_alpha_min = self.Vdc_min / self.Vdc_max
        if cos_alpha_min <= 1.0:
            self.alpha_min = math.degrees(math.acos(cos_alpha_min))
        else:
            self.alpha_min = 0.0
            self.Vdc_min = self.Vdc_max

    def motor_equations(self, t, x, params):
        """
        Induction motor dynamic equations in d-q reference frame
        State vector: x = [ids, iqs, idr, iqr, omega_r, theta_r]
        """
        ids, iqs, idr, iqr, omega_r, theta_r = x

        # Extract parameters
        Rs = params['Rs']
        Rr = params['Rr']
        Ls = params['Ls']
        Lr = params['Lr']
        Lm = params['Lm']
        J = params['J']
        B = params['B']
        poles = params['poles']

        # Calculate transient inductances
        Lls = Ls - Lm
        Llr = Lr - Lm

        # Leakage coefficient
        sigma = 1 - (Lm**2) / (Ls * Lr)

        # Electrical angular velocity
        omega_e = 2 * math.pi * self.control_params['frequency']

        # Slip angular velocity
        omega_slip = omega_e - (poles / 2) * omega_r

        # Supply voltages (d-q components in synchronous reference frame)
        Vds = self.control_params['voltage'] * math.sqrt(2/3)
        Vqs = 0.0

        # Voltage equations
        dids_dt = (1 / (sigma * Ls)) * (
            Vds - Rs * ids + omega_e * sigma * Ls * iqs +
            (Lm / Lr) * (Rr * idr - omega_slip * Lr * iqr)
        )

        diqs_dt = (1 / (sigma * Ls)) * (
            Vqs - Rs * iqs - omega_e * sigma * Ls * ids +
            (Lm / Lr) * (Rr * iqr + omega_slip * Lr * idr)
        )

        didr_dt = (1 / (sigma * Lr)) * (
            -Rr * idr + omega_slip * sigma * Lr * iqr +
            (Lm / Ls) * (Rs * ids - omega_e * Ls * iqs)
        )

        diqr_dt = (1 / (sigma * Lr)) * (
            -Rr * iqr - omega_slip * sigma * Lr * idr +
            (Lm / Ls) * (Rs * iqs + omega_e * Ls * ids)
        )

        # Electromagnetic torque
        Te = (3 / 2) * (poles / 2) * Lm * (iqs * idr - ids * iqr)

        # Load torque
        TL = self.control_params['load_torque']

        # Mechanical equation
        domega_r_dt = (1 / J) * (Te - TL - B * omega_r)

        # Rotor angle
        dtheta_r_dt = omega_r

        return [dids_dt, diqs_dt, didr_dt, diqr_dt, domega_r_dt, dtheta_r_dt]

    def euler_step(self):
        """Perform one Euler integration step"""
        derivatives = self.motor_equations(self.simulation_time, self.state, self.motor_params)
        self.state = self.state + self.dt * np.array(derivatives)
        self.simulation_time += self.dt

    def rk45_step(self):
        """Perform one RK45 integration step"""
        t_span = [self.simulation_time, self.simulation_time + self.dt]
        sol = solve_ivp(
            self.motor_equations,
            t_span,
            self.state,
            method='RK45',
            args=(self.motor_params,),
            dense_output=False,
            max_step=self.dt
        )
        if sol.success:
            self.state = sol.y[:, -1]
            self.simulation_time = sol.t[-1]

    def simulate_step(self):
        """Perform one simulation step based on selected solver"""
        if self.current_solver == "RK45":
            self.rk45_step()
        else:  # Euler
            self.euler_step()

        # Calculate derived quantities
        omega_r = self.state[4]
        speed_rpm = omega_r * 60 / (2 * math.pi)

        # Electromagnetic torque
        Lm = self.motor_params['Lm']
        poles = self.motor_params['poles']
        Te = (3 / 2) * (poles / 2) * Lm * (
            self.state[1] * self.state[2] - self.state[0] * self.state[3]
        )

        # Stator current magnitude
        Is = math.sqrt(self.state[0]**2 + self.state[1]**2)

        # DC link voltage
        alpha_rad = math.radians(self.control_params['firing_angle'])
        Vdc = self.Vdc_max * math.cos(alpha_rad)

        # Slip
        omega_e = 2 * math.pi * self.control_params['frequency']
        omega_sync = omega_e / (poles / 2)
        slip = (omega_sync - omega_r) / omega_sync if omega_sync != 0 else 0

        # Store data
        self.time_data.append(self.simulation_time)
        self.speed_data.append(speed_rpm)
        self.torque_data.append(Te)
        self.current_data.append(Is)
        self.voltage_dc_data.append(Vdc)
        self.slip_data.append(slip * 100)

        # Limit data storage
        max_points = 2000
        if len(self.time_data) > max_points:
            self.time_data = self.time_data[-max_points:]
            self.speed_data = self.speed_data[-max_points:]
            self.torque_data = self.torque_data[-max_points:]
            self.current_data = self.current_data[-max_points:]
            self.voltage_dc_data = self.voltage_dc_data[-max_points:]
            self.slip_data = self.slip_data[-max_points:]

    def setup_gui(self):
        """Setup the complete GUI"""
        # Create main container with grid layout
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=0, column=0, sticky='nsew')

        # Configure root grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Configure main container grid weights
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(1, weight=3)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create sections
        self.create_header()
        self.create_control_panel()
        self.create_visualization_panel()
        self.create_status_bar()

    def create_header(self):
        """Create header with title and theoretical results"""
        header_frame = ttk.LabelFrame(self.main_container, text="VVVF Inverter-Fed Induction Motor Laboratory", padding=10)
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Theoretical calculations display
        theory_text = f"""Theoretical Analysis:
Maximum DC Voltage: {self.Vdc_max:.2f} V (α = {self.alpha_max:.2f}°)
Minimum DC Voltage: {self.Vdc_min:.2f} V (α = {self.alpha_min:.2f}°)
V/f Ratio: {self.vf_ratio:.2f} V/Hz
Frequency Range: {self.f_min:.2f} Hz - {self.motor_params['f_rated']:.2f} Hz
Speed Ratio: {self.motor_params['speed_ratio']:.1f}:1"""

        theory_label = ttk.Label(header_frame, text=theory_text, font=('Courier', 9))
        theory_label.pack()

    def create_control_panel(self):
        """Create control panel with input parameters and controls"""
        control_frame = ttk.Frame(self.main_container)
        control_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Motor Parameters
        motor_frame = ttk.LabelFrame(control_frame, text="Motor Parameters", padding=10)
        motor_frame.pack(fill='x', padx=5, pady=5)

        self.create_parameter_entry(motor_frame, "Rated Voltage (V):", 'VL_rated', 0)
        self.create_parameter_entry(motor_frame, "Rated Frequency (Hz):", 'f_rated', 1)
        self.create_parameter_entry(motor_frame, "Rated Speed (rpm):", 'n_rated', 2)
        self.create_parameter_entry(motor_frame, "Stator Resistance (Ω):", 'Rs', 3)
        self.create_parameter_entry(motor_frame, "Rotor Resistance (Ω):", 'Rr', 4)
        self.create_parameter_entry(motor_frame, "Inertia (kg.m²):", 'J', 5)

        # Control Sliders
        slider_frame = ttk.LabelFrame(control_frame, text="Control Adjustments", padding=10)
        slider_frame.pack(fill='x', padx=5, pady=5)

        self.create_slider(slider_frame, "Frequency (Hz):", 'frequency',
                          self.f_min, self.motor_params['f_rated'], 0)
        self.create_slider(slider_frame, "Voltage (V):", 'voltage',
                          self.vf_ratio * self.f_min, self.motor_params['VL_rated'], 1)
        self.create_slider(slider_frame, "Firing Angle (°):", 'firing_angle',
                          0, 90, 2)
        self.create_slider(slider_frame, "Load Torque (N.m):", 'load_torque',
                          0, 50, 3)

        # Simulation Settings
        sim_frame = ttk.LabelFrame(control_frame, text="Simulation Settings", padding=10)
        sim_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(sim_frame, text="ODE Solver:").grid(row=0, column=0, sticky='w', pady=2)
        self.solver_var = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(sim_frame, textvariable=self.solver_var,
                                     values=["RK45", "Euler"], state='readonly', width=15)
        solver_combo.grid(row=0, column=1, sticky='ew', pady=2)
        solver_combo.bind('<<ComboboxSelected>>', self.on_solver_change)

        ttk.Label(sim_frame, text="Time Step (s):").grid(row=1, column=0, sticky='w', pady=2)
        self.dt_var = tk.StringVar(value="0.001")
        dt_entry = ttk.Entry(sim_frame, textvariable=self.dt_var, width=15)
        dt_entry.grid(row=1, column=1, sticky='ew', pady=2)
        dt_entry.bind('<Return>', self.on_dt_change)

        sim_frame.columnconfigure(1, weight=1)

        # Control Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', padx=5, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side='left', padx=2, expand=True, fill='x')

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_simulation, state='disabled')
        self.stop_button.pack(side='left', padx=2, expand=True, fill='x')

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side='left', padx=2, expand=True, fill='x')

        # Real-time Display
        display_frame = ttk.LabelFrame(control_frame, text="Real-time Measurements", padding=10)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.display_labels = {}
        measurements = [
            ('Speed (rpm):', 'speed'),
            ('Torque (N.m):', 'torque'),
            ('Current (A):', 'current'),
            ('DC Voltage (V):', 'vdc'),
            ('Slip (%):', 'slip'),
            ('Time (s):', 'time')
        ]

        for i, (label, key) in enumerate(measurements):
            ttk.Label(display_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            value_label = ttk.Label(display_frame, text="0.00", font=('Courier', 10, 'bold'))
            value_label.grid(row=i, column=1, sticky='e', pady=2)
            self.display_labels[key] = value_label

        display_frame.columnconfigure(1, weight=1)

    def create_parameter_entry(self, parent, label, param_key, row):
        """Create parameter entry field"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', pady=2)
        var = tk.StringVar(value=str(self.motor_params[param_key]))
        entry = ttk.Entry(parent, textvariable=var, width=12)
        entry.grid(row=row, column=1, sticky='ew', pady=2)
        entry.bind('<Return>', lambda e, k=param_key: self.on_parameter_change(k, var))
        parent.columnconfigure(1, weight=1)

    def create_slider(self, parent, label, param_key, min_val, max_val, row):
        """Create control slider"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)

        ttk.Label(frame, text=label).pack(anchor='w')

        value_label = ttk.Label(frame, text=f"{self.control_params[param_key]:.2f}")
        value_label.pack(anchor='e')

        slider = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal',
                          command=lambda v, k=param_key, lbl=value_label: self.on_slider_change(k, v, lbl))
        slider.set(self.control_params[param_key])
        slider.pack(fill='x')

        parent.columnconfigure(0, weight=1)

    def create_visualization_panel(self):
        """Create visualization panel with plots"""
        viz_frame = ttk.Frame(self.main_container)
        viz_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.fig.subplots_adjust(hspace=0.3, left=0.1, right=0.95, top=0.95, bottom=0.08)

        # Create subplots
        self.ax1 = self.fig.add_subplot(3, 2, 1)
        self.ax2 = self.fig.add_subplot(3, 2, 2)
        self.ax3 = self.fig.add_subplot(3, 2, 3)
        self.ax4 = self.fig.add_subplot(3, 2, 4)
        self.ax5 = self.fig.add_subplot(3, 2, 5)
        self.ax6 = self.fig.add_subplot(3, 2, 6)

        # Initialize plots
        self.line1, = self.ax1.plot([], [], 'b-', linewidth=2)
        self.line2, = self.ax2.plot([], [], 'r-', linewidth=2)
        self.line3, = self.ax3.plot([], [], 'g-', linewidth=2)
        self.line4, = self.ax4.plot([], [], 'm-', linewidth=2)
        self.line5, = self.ax5.plot([], [], 'c-', linewidth=2)
        self.line6, = self.ax6.plot([], [], 'orange', linewidth=2)

        # Set labels
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Speed (rpm)')
        self.ax1.set_title('Motor Speed')
        self.ax1.grid(True, alpha=0.3)

        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Torque (N.m)')
        self.ax2.set_title('Electromagnetic Torque')
        self.ax2.grid(True, alpha=0.3)

        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Current (A)')
        self.ax3.set_title('Stator Current')
        self.ax3.grid(True, alpha=0.3)

        self.ax4.set_xlabel('Time (s)')
        self.ax4.set_ylabel('DC Voltage (V)')
        self.ax4.set_title('DC Link Voltage')
        self.ax4.grid(True, alpha=0.3)

        self.ax5.set_xlabel('Time (s)')
        self.ax5.set_ylabel('Slip (%)')
        self.ax5.set_title('Motor Slip')
        self.ax5.grid(True, alpha=0.3)

        self.ax6.set_xlabel('Speed (rpm)')
        self.ax6.set_ylabel('Torque (N.m)')
        self.ax6.set_title('Torque-Speed Characteristic')
        self.ax6.grid(True, alpha=0.3)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Label(self.main_container, text="Ready", relief='sunken', anchor='w')
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky='ew')

    def on_parameter_change(self, key, var):
        """Handle parameter change"""
        try:
            value = float(var.get())
            self.motor_params[key] = value
            self.calculate_theoretical_values()
            self.status_bar.config(text=f"Parameter {key} updated to {value}")
        except ValueError:
            messagebox.showerror("Error", "Invalid parameter value")

    def on_slider_change(self, key, value, label):
        """Handle slider change"""
        val = float(value)
        self.control_params[key] = val
        label.config(text=f"{val:.2f}")

        # Maintain V/f ratio if frequency changes
        if key == 'frequency':
            new_voltage = val * self.vf_ratio
            # Update voltage slider and control param
            self.control_params['voltage'] = new_voltage

    def on_solver_change(self, event):
        """Handle solver change"""
        self.current_solver = self.solver_var.get()
        self.status_bar.config(text=f"Solver changed to {self.current_solver}")

    def on_dt_change(self, event):
        """Handle time step change"""
        try:
            self.dt = float(self.dt_var.get())
            self.status_bar.config(text=f"Time step updated to {self.dt} s")
        except ValueError:
            messagebox.showerror("Error", "Invalid time step value")
            self.dt_var.set(str(self.dt))

    def start_simulation(self):
        """Start the simulation"""
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_bar.config(text="Simulation running...")
        self.run_simulation()

    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_bar.config(text="Simulation stopped")

    def reset_simulation(self):
        """Reset the simulation"""
        self.stop_simulation()
        self.simulation_time = 0.0
        self.state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.time_data = []
        self.speed_data = []
        self.torque_data = []
        self.current_data = []
        self.voltage_dc_data = []
        self.slip_data = []
        self.update_plots()
        self.status_bar.config(text="Simulation reset")

    def run_simulation(self):
        """Run simulation loop"""
        if self.is_running:
            # Perform multiple steps per update for smoother simulation
            for _ in range(10):
                self.simulate_step()

            # Update display
            self.update_display()
            self.update_plots()

            # Schedule next update
            self.root.after(20, self.run_simulation)

    def update_display(self):
        """Update real-time display"""
        if len(self.speed_data) > 0:
            self.display_labels['speed'].config(text=f"{self.speed_data[-1]:.2f}")
            self.display_labels['torque'].config(text=f"{self.torque_data[-1]:.2f}")
            self.display_labels['current'].config(text=f"{self.current_data[-1]:.2f}")
            self.display_labels['vdc'].config(text=f"{self.voltage_dc_data[-1]:.2f}")
            self.display_labels['slip'].config(text=f"{self.slip_data[-1]:.2f}")
            self.display_labels['time'].config(text=f"{self.time_data[-1]:.3f}")

    def update_plots(self):
        """Update all plots"""
        if len(self.time_data) > 0:
            # Update data
            self.line1.set_data(self.time_data, self.speed_data)
            self.line2.set_data(self.time_data, self.torque_data)
            self.line3.set_data(self.time_data, self.current_data)
            self.line4.set_data(self.time_data, self.voltage_dc_data)
            self.line5.set_data(self.time_data, self.slip_data)
            self.line6.set_data(self.speed_data, self.torque_data)

            # Auto-scale axes
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
            self.ax3.relim()
            self.ax3.autoscale_view()
            self.ax4.relim()
            self.ax4.autoscale_view()
            self.ax5.relim()
            self.ax5.autoscale_view()
            self.ax6.relim()
            self.ax6.autoscale_view()

            # Redraw canvas
            self.canvas.draw_idle()

    def on_window_resize(self, event):
        """Handle window resize event"""
        if event.widget == self.root:
            # Update figure size based on window size
            try:
                self.canvas.draw_idle()
            except:
                pass


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = VVVFInductionMotorLab(root)
    root.mainloop()


if __name__ == "__main__":
    main()
