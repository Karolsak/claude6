"""
Advanced DC Machine Analysis Laboratory
Comprehensive electrical engineering application for DC generator and motor analysis
with dynamic simulation capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.interpolate import interp1d
from scipy.integrate import odeint, solve_ivp
import threading
import time


class DCMachineLabApp:
    """Main application class for DC Machine Analysis Laboratory"""

    def __init__(self, root):
        self.root = root
        self.root.title("DC Machine Analysis Laboratory - Advanced Engineering Tool")
        self.root.geometry("1400x900")

        # Simulation control variables
        self.simulation_running = False
        self.simulation_thread = None
        self.time_data = []
        self.state_data = []

        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create tabs
        self.create_compound_generator_tab()
        self.create_shunt_motor_tab()
        self.create_dynamic_simulation_tab()

        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        """Handle window resize events for responsive layout"""
        if event.widget == self.root:
            # Update canvas sizes
            if hasattr(self, 'canvas1'):
                self.canvas1.get_tk_widget().configure(width=event.width-50, height=event.height//2)
            if hasattr(self, 'canvas2'):
                self.canvas2.get_tk_widget().configure(width=event.width-50, height=event.height//2)
            if hasattr(self, 'canvas3'):
                self.canvas3.get_tk_widget().configure(width=event.width-50, height=event.height//2)

    def create_compound_generator_tab(self):
        """Create tab for DC Compound Generator analysis (Problem 7.9)"""
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="DC Compound Generator")

        # Configure grid weights
        tab1.grid_rowconfigure(1, weight=1)
        tab1.grid_columnconfigure(0, weight=1)
        tab1.grid_columnconfigure(1, weight=2)

        # Input frame
        input_frame = ttk.LabelFrame(tab1, text="Generator Parameters", padding=10)
        input_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Parameters
        params = [
            ("Power Rating (kW):", "250"),
            ("Number of Poles:", "6"),
            ("No-load Voltage (V):", "500"),
            ("Full-load Voltage (V):", "550"),
            ("Number of Conductors:", "1080"),
            ("Armature Resistance (Ω):", "0.037"),
            ("Shunt Field Resistance (Ω):", "85"),
            ("Armature Reaction Compensation (%):", "10")
        ]

        self.gen_entries = {}
        for i, (label, default) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            entry = ttk.Entry(input_frame, width=15)
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky='ew', pady=2, padx=5)
            self.gen_entries[label] = entry

        # OCC Data frame
        occ_frame = ttk.LabelFrame(input_frame, text="Open Circuit Characteristic (OCC)", padding=5)
        occ_frame.grid(row=len(params), column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Label(occ_frame, text="Voltage (V):").grid(row=0, column=0, sticky='w')
        self.gen_occ_voltage = ttk.Entry(occ_frame, width=30)
        self.gen_occ_voltage.insert(0, "500, 535, 560, 580")
        self.gen_occ_voltage.grid(row=0, column=1, sticky='ew', padx=5)

        ttk.Label(occ_frame, text="Field AT/pole:").grid(row=1, column=0, sticky='w')
        self.gen_occ_at = ttk.Entry(occ_frame, width=30)
        self.gen_occ_at.insert(0, "6000, 7000, 8000, 9000")
        self.gen_occ_at.grid(row=1, column=1, sticky='ew', padx=5)

        # Calculate button
        calc_btn = ttk.Button(input_frame, text="Calculate Series Turns",
                             command=self.calculate_compound_generator)
        calc_btn.grid(row=len(params)+2, column=0, columnspan=2, pady=10)

        # Results frame
        results_frame = ttk.LabelFrame(tab1, text="Results & Visualization", padding=10)
        results_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Results text
        self.gen_results = scrolledtext.ScrolledText(results_frame, height=10, width=60)
        self.gen_results.grid(row=0, column=0, sticky='nsew', pady=5)

        # Matplotlib figure
        self.fig1 = Figure(figsize=(8, 6), dpi=100)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, results_frame)
        self.canvas1.get_tk_widget().grid(row=1, column=0, sticky='nsew')

    def create_shunt_motor_tab(self):
        """Create tab for DC Shunt Motor analysis (Problem 7.10)"""
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="DC Shunt Motor")

        # Configure grid weights
        tab2.grid_rowconfigure(1, weight=1)
        tab2.grid_columnconfigure(0, weight=1)
        tab2.grid_columnconfigure(1, weight=2)

        # Input frame
        input_frame = ttk.LabelFrame(tab2, text="Motor Parameters", padding=10)
        input_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Parameters
        params = [
            ("Power Rating (kW):", "10"),
            ("Rated Voltage (V):", "250"),
            ("Armature Resistance (Ω):", "0.5"),
            ("Field Resistance (Ω):", "200"),
            ("No-load Speed (rpm):", "1200"),
            ("No-load Armature Current (A):", "3"),
            ("Full-load Line Current (A):", "47"),
            ("Flux Reduction at Full-load (%):", "4")
        ]

        self.motor_entries = {}
        for i, (label, default) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            entry = ttk.Entry(input_frame, width=15)
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky='ew', pady=2, padx=5)
            self.motor_entries[label] = entry

        # Calculate button
        calc_btn = ttk.Button(input_frame, text="Calculate Motor Performance",
                             command=self.calculate_shunt_motor)
        calc_btn.grid(row=len(params), column=0, columnspan=2, pady=10)

        # Results frame
        results_frame = ttk.LabelFrame(tab2, text="Results & Visualization", padding=10)
        results_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Results text
        self.motor_results = scrolledtext.ScrolledText(results_frame, height=10, width=60)
        self.motor_results.grid(row=0, column=0, sticky='nsew', pady=5)

        # Matplotlib figure
        self.fig2 = Figure(figsize=(8, 6), dpi=100)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, results_frame)
        self.canvas2.get_tk_widget().grid(row=1, column=0, sticky='nsew')

    def create_dynamic_simulation_tab(self):
        """Create tab for dynamic simulation with ODE solvers"""
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="Dynamic Simulation")

        # Configure grid weights
        tab3.grid_rowconfigure(2, weight=1)
        tab3.grid_columnconfigure(0, weight=1)
        tab3.grid_columnconfigure(1, weight=2)

        # Control frame
        control_frame = ttk.LabelFrame(tab3, text="Simulation Controls", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Machine type selection
        ttk.Label(control_frame, text="Machine Type:").grid(row=0, column=0, sticky='w', pady=5)
        self.machine_type = ttk.Combobox(control_frame, values=["DC Motor", "DC Generator"], state='readonly')
        self.machine_type.set("DC Motor")
        self.machine_type.grid(row=0, column=1, sticky='ew', pady=5, padx=5)

        # Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=1, column=0, sticky='w', pady=5)
        self.solver_type = ttk.Combobox(control_frame, values=["RK45 (Adaptive)", "Euler (Fixed)", "RK4 (Fixed)"], state='readonly')
        self.solver_type.set("RK45 (Adaptive)")
        self.solver_type.grid(row=1, column=1, sticky='ew', pady=5, padx=5)

        # Simulation parameters with sliders
        slider_params = [
            ("Applied Voltage (V):", 0, 500, 250),
            ("Load Torque (Nm):", 0, 200, 50),
            ("Moment of Inertia (kg·m²):", 0.01, 10, 1.0),
            ("Armature Resistance (Ω):", 0.1, 5, 0.5),
            ("Field Resistance (Ω):", 50, 500, 200),
            ("Simulation Time (s):", 1, 20, 5)
        ]

        self.sim_sliders = {}
        self.sim_labels = {}

        for i, (label, min_val, max_val, default) in enumerate(slider_params):
            row = i + 2
            ttk.Label(control_frame, text=label).grid(row=row, column=0, sticky='w', pady=2)

            frame = ttk.Frame(control_frame)
            frame.grid(row=row, column=1, sticky='ew', pady=2, padx=5)

            slider = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal',
                             command=lambda val, lbl=label: self.update_slider_label(lbl, val))
            slider.set(default)
            slider.pack(side='left', fill='x', expand=True)

            value_label = ttk.Label(frame, text=f"{default:.2f}", width=8)
            value_label.pack(side='right')

            self.sim_sliders[label] = slider
            self.sim_labels[label] = value_label

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=len(slider_params)+2, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(button_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(button_frame, text="■ Stop", command=self.stop_simulation, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        self.reset_btn = ttk.Button(button_frame, text="↻ Reset", command=self.reset_simulation)
        self.reset_btn.pack(side='left', padx=5)

        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Ready", foreground='green')
        self.status_label.grid(row=len(slider_params)+3, column=0, columnspan=2, pady=5)

        # Visualization frame
        viz_frame = ttk.LabelFrame(tab3, text="Real-Time Visualization", padding=10)
        viz_frame.grid(row=0, column=1, rowspan=3, sticky='nsew', padx=5, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Matplotlib figure for simulation
        self.fig3 = Figure(figsize=(10, 8), dpi=100)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, viz_frame)
        self.canvas3.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Results text
        results_text_frame = ttk.LabelFrame(tab3, text="Simulation Results", padding=5)
        results_text_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        self.sim_results = scrolledtext.ScrolledText(results_text_frame, height=8, width=40)
        self.sim_results.pack(fill='both', expand=True)

    def update_slider_label(self, label, value):
        """Update slider value label"""
        self.sim_labels[label].config(text=f"{float(value):.2f}")

    def calculate_compound_generator(self):
        """Calculate series turns per pole for DC compound generator (Problem 7.9)"""
        try:
            # Get input values
            P_rated = float(self.gen_entries["Power Rating (kW):"].get()) * 1000  # W
            poles = int(self.gen_entries["Number of Poles:"].get())
            V_nl = float(self.gen_entries["No-load Voltage (V):"].get())
            V_fl = float(self.gen_entries["Full-load Voltage (V):"].get())
            Z = int(self.gen_entries["Number of Conductors:"].get())
            Ra = float(self.gen_entries["Armature Resistance (Ω):"].get())
            Rsh = float(self.gen_entries["Shunt Field Resistance (Ω):"].get())
            ar_comp = float(self.gen_entries["Armature Reaction Compensation (%):"].get()) / 100

            # Get OCC data
            occ_voltage = [float(x.strip()) for x in self.gen_occ_voltage.get().split(',')]
            occ_at = [float(x.strip()) for x in self.gen_occ_at.get().split(',')]

            # Create interpolation function for OCC
            occ_interp = interp1d(occ_voltage, occ_at, kind='cubic', fill_value='extrapolate')

            # Calculate full-load current
            I_fl = P_rated / V_fl

            # Calculate shunt field current at full load
            I_sh_fl = V_fl / Rsh

            # Calculate armature current at full load
            Ia_fl = I_fl + I_sh_fl

            # For lap winding, number of parallel paths = number of poles
            A = poles

            # Calculate armature ampere-turns per pole at full load
            AT_armature_per_pole = (Ia_fl * Z) / (2 * A * poles)

            # Armature reaction AT per pole
            AT_ar_per_pole = ar_comp * AT_armature_per_pole

            # Voltage drop at full load
            V_drop = Ia_fl * Ra

            # Induced EMF at full load
            E_fl = V_fl + V_drop

            # Required field AT at full load (from OCC)
            AT_required_fl = occ_interp(E_fl)

            # Shunt field current at no-load
            I_sh_nl = V_nl / Rsh

            # At no-load, armature current is minimal (assume = shunt current)
            Ia_nl = I_sh_nl
            V_drop_nl = Ia_nl * Ra
            E_nl = V_nl + V_drop_nl

            # Required field AT at no-load
            AT_required_nl = occ_interp(E_nl)

            # Series field provides the difference plus compensation for armature reaction
            AT_series = AT_required_fl - AT_required_nl + AT_ar_per_pole

            # Number of series turns per pole
            N_series = AT_series / Ia_fl

            # Display results
            results_text = f"""
═══════════════════════════════════════════════════════════
           DC COMPOUND GENERATOR CALCULATION RESULTS
═══════════════════════════════════════════════════════════

GIVEN PARAMETERS:
├─ Power Rating: {P_rated/1000:.1f} kW
├─ Number of Poles: {poles}
├─ No-load Voltage: {V_nl:.1f} V
├─ Full-load Voltage: {V_fl:.1f} V
├─ Number of Conductors: {Z}
├─ Armature Resistance: {Ra:.4f} Ω
└─ Shunt Field Resistance: {Rsh:.1f} Ω

CALCULATED VALUES:
├─ Full-load Current (IL): {I_fl:.2f} A
├─ Shunt Field Current (FL): {I_sh_fl:.2f} A
├─ Armature Current (FL): {Ia_fl:.2f} A
├─ Armature AT per pole: {AT_armature_per_pole:.2f} AT
├─ Armature Reaction AT per pole: {AT_ar_per_pole:.2f} AT
├─ Voltage Drop (FL): {V_drop:.3f} V
├─ Induced EMF (FL): {E_fl:.2f} V
├─ Induced EMF (NL): {E_nl:.2f} V
├─ Required Field AT (FL): {AT_required_fl:.2f} AT/pole
├─ Required Field AT (NL): {AT_required_nl:.2f} AT/pole
└─ Series Field AT needed: {AT_series:.2f} AT/pole

═══════════════════════════════════════════════════════════
FINAL ANSWER:
Required Number of Series Turns per Pole: {N_series:.2f} turns
═══════════════════════════════════════════════════════════
"""

            self.gen_results.delete(1.0, tk.END)
            self.gen_results.insert(1.0, results_text)

            # Plot OCC and operating points
            self.fig1.clear()

            # Create subplots
            ax1 = self.fig1.add_subplot(2, 2, 1)
            ax2 = self.fig1.add_subplot(2, 2, 2)
            ax3 = self.fig1.add_subplot(2, 2, 3)
            ax4 = self.fig1.add_subplot(2, 2, 4)

            # Plot 1: OCC with operating points
            voltage_range = np.linspace(min(occ_voltage), max(occ_voltage)*1.1, 100)
            at_range = occ_interp(voltage_range)

            ax1.plot(occ_at, occ_voltage, 'bo-', label='OCC Data', linewidth=2, markersize=8)
            ax1.plot(voltage_range, at_range, 'b--', label='Interpolated OCC', alpha=0.6)
            ax1.plot(AT_required_nl, E_nl, 'go', markersize=12, label=f'No-load: {E_nl:.1f}V', zorder=5)
            ax1.plot(AT_required_fl, E_fl, 'ro', markersize=12, label=f'Full-load: {E_fl:.1f}V', zorder=5)
            ax1.set_xlabel('Field AT per pole', fontsize=10, fontweight='bold')
            ax1.set_ylabel('Voltage (V)', fontsize=10, fontweight='bold')
            ax1.set_title('Open Circuit Characteristic', fontsize=11, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=8)

            # Plot 2: Load characteristics
            load_current = np.linspace(0, I_fl*1.2, 50)
            terminal_voltage = []

            for Il in load_current:
                I_sh = V_fl / Rsh  # Approximate
                Ia = Il + I_sh
                Vdrop = Ia * Ra
                # For compound generator, voltage increases with load (within range)
                Vt = V_nl + (V_fl - V_nl) * (Il / I_fl) if Il <= I_fl else V_fl
                terminal_voltage.append(Vt)

            ax2.plot(load_current, terminal_voltage, 'b-', linewidth=2)
            ax2.axvline(I_fl, color='r', linestyle='--', label=f'Full Load ({I_fl:.1f}A)')
            ax2.axhline(V_nl, color='g', linestyle='--', label=f'No Load ({V_nl:.0f}V)')
            ax2.axhline(V_fl, color='orange', linestyle='--', label=f'Full Load ({V_fl:.0f}V)')
            ax2.set_xlabel('Load Current (A)', fontsize=10, fontweight='bold')
            ax2.set_ylabel('Terminal Voltage (V)', fontsize=10, fontweight='bold')
            ax2.set_title('Load Characteristic', fontsize=11, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=8)

            # Plot 3: Field ampere-turns distribution
            labels = ['Shunt Field\n(No-load)', 'Shunt Field\n(Full-load)', 'Series Field', 'AR Comp.']
            values = [AT_required_nl, AT_required_nl, AT_series-AT_ar_per_pole, AT_ar_per_pole]
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']

            bars = ax3.bar(labels, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
            ax3.set_ylabel('Ampere-Turns per Pole', fontsize=10, fontweight='bold')
            ax3.set_title('Field AT Distribution', fontsize=11, fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

            # Plot 4: Current distribution
            pie_labels = ['Load Current', 'Shunt Field Current']
            pie_values = [I_fl, I_sh_fl]
            pie_colors = ['#3498db', '#2ecc71']

            wedges, texts, autotexts = ax4.pie(pie_values, labels=pie_labels, colors=pie_colors,
                                                autopct='%1.1f%%', startangle=90,
                                                textprops={'fontsize': 9, 'fontweight': 'bold'})
            ax4.set_title(f'Current Distribution\nTotal Armature: {Ia_fl:.2f}A',
                         fontsize=11, fontweight='bold')

            self.fig1.tight_layout()
            self.canvas1.draw()

        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred:\n{str(e)}")

    def calculate_shunt_motor(self):
        """Calculate motor performance (Problem 7.10)"""
        try:
            # Get input values
            P_rated = float(self.motor_entries["Power Rating (kW):"].get()) * 1000  # W
            V = float(self.motor_entries["Rated Voltage (V):"].get())
            Ra = float(self.motor_entries["Armature Resistance (Ω):"].get())
            Rf = float(self.motor_entries["Field Resistance (Ω):"].get())
            N_nl = float(self.motor_entries["No-load Speed (rpm):"].get())
            Ia_nl = float(self.motor_entries["No-load Armature Current (A):"].get())
            IL_fl = float(self.motor_entries["Full-load Line Current (A):"].get())
            flux_reduction = float(self.motor_entries["Flux Reduction at Full-load (%)"].get()) / 100

            # Calculate field current (constant for shunt motor)
            If = V / Rf

            # No-load calculations
            Eb_nl = V - Ia_nl * Ra  # Back EMF at no-load

            # Full-load calculations
            Ia_fl = IL_fl - If  # Armature current at full load
            Eb_fl = V - Ia_fl * Ra  # Back EMF at full load

            # Flux at full load relative to no-load
            phi_fl_ratio = 1 - flux_reduction

            # Speed relationship: N ∝ Eb/φ
            # N_fl / N_nl = (Eb_fl / Eb_nl) * (phi_nl / phi_fl)
            N_fl = N_nl * (Eb_fl / Eb_nl) * (1 / phi_fl_ratio)

            # Developed torque at full load
            # T = (Eb * Ia) / ω, where ω is in rad/s
            omega_fl = (2 * np.pi * N_fl) / 60  # rad/s
            T_dev_fl = (Eb_fl * Ia_fl) / omega_fl

            # Also calculate using power
            P_dev_fl = Eb_fl * Ia_fl
            T_dev_fl_alt = P_dev_fl / omega_fl

            # Efficiency
            P_input_fl = V * IL_fl
            P_losses_fl = (Ia_fl**2 * Ra) + (If**2 * Rf)
            P_output_fl = P_input_fl - P_losses_fl
            efficiency_fl = (P_output_fl / P_input_fl) * 100

            # Display results
            results_text = f"""
═══════════════════════════════════════════════════════════
              DC SHUNT MOTOR CALCULATION RESULTS
═══════════════════════════════════════════════════════════

GIVEN PARAMETERS:
├─ Power Rating: {P_rated/1000:.1f} kW
├─ Rated Voltage: {V:.1f} V
├─ Armature Resistance: {Ra:.2f} Ω
├─ Field Resistance: {Rf:.1f} Ω
├─ No-load Speed: {N_nl:.1f} rpm
├─ No-load Armature Current: {Ia_nl:.2f} A
├─ Full-load Line Current: {IL_fl:.2f} A
└─ Flux Reduction at Full-load: {flux_reduction*100:.1f}%

NO-LOAD CONDITIONS:
├─ Field Current: {If:.3f} A
├─ Armature Current: {Ia_nl:.2f} A
└─ Back EMF: {Eb_nl:.2f} V

FULL-LOAD CONDITIONS:
├─ Field Current: {If:.3f} A
├─ Armature Current: {Ia_fl:.2f} A
├─ Back EMF: {Eb_fl:.2f} V
└─ Flux Ratio (φ_fl/φ_nl): {phi_fl_ratio:.4f}

═══════════════════════════════════════════════════════════
FINAL ANSWERS:

(a) FULL-LOAD SPEED: {N_fl:.2f} rpm

(b) DEVELOPED TORQUE AT FULL LOAD: {T_dev_fl:.2f} Nm
═══════════════════════════════════════════════════════════

ADDITIONAL CALCULATIONS:
├─ Angular Velocity (ω): {omega_fl:.2f} rad/s
├─ Developed Power: {P_dev_fl:.2f} W ({P_dev_fl/1000:.2f} kW)
├─ Input Power: {P_input_fl:.2f} W ({P_input_fl/1000:.2f} kW)
├─ Total Losses: {P_losses_fl:.2f} W
├─ Armature Copper Loss: {Ia_fl**2 * Ra:.2f} W
├─ Field Copper Loss: {If**2 * Rf:.2f} W
└─ Efficiency: {efficiency_fl:.2f}%
"""

            self.motor_results.delete(1.0, tk.END)
            self.motor_results.insert(1.0, results_text)

            # Create visualizations
            self.fig2.clear()

            # Create subplots
            ax1 = self.fig2.add_subplot(2, 2, 1)
            ax2 = self.fig2.add_subplot(2, 2, 2)
            ax3 = self.fig2.add_subplot(2, 2, 3)
            ax4 = self.fig2.add_subplot(2, 2, 4)

            # Plot 1: Speed vs Load Current
            load_range = np.linspace(Ia_nl, Ia_fl*1.2, 50)
            speed_range = []

            for Ia in load_range:
                Eb = V - Ia * Ra
                # Approximate flux reduction (linear assumption)
                flux_ratio = 1 - (flux_reduction * (Ia - Ia_nl) / (Ia_fl - Ia_nl)) if Ia <= Ia_fl else phi_fl_ratio
                N = N_nl * (Eb / Eb_nl) * (1 / flux_ratio)
                speed_range.append(N)

            ax1.plot(load_range, speed_range, 'b-', linewidth=2)
            ax1.axvline(Ia_nl, color='g', linestyle='--', label=f'No Load ({Ia_nl:.1f}A)', alpha=0.7)
            ax1.axvline(Ia_fl, color='r', linestyle='--', label=f'Full Load ({Ia_fl:.1f}A)', alpha=0.7)
            ax1.axhline(N_nl, color='g', linestyle=':', alpha=0.5)
            ax1.axhline(N_fl, color='r', linestyle=':', alpha=0.5)
            ax1.set_xlabel('Armature Current (A)', fontsize=10, fontweight='bold')
            ax1.set_ylabel('Speed (rpm)', fontsize=10, fontweight='bold')
            ax1.set_title('Speed vs Load Characteristic', fontsize=11, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=8)

            # Plot 2: Torque vs Speed
            torque_range = []
            speed_range2 = []

            for Ia in load_range:
                Eb = V - Ia * Ra
                flux_ratio = 1 - (flux_reduction * (Ia - Ia_nl) / (Ia_fl - Ia_nl)) if Ia <= Ia_fl else phi_fl_ratio
                N = N_nl * (Eb / Eb_nl) * (1 / flux_ratio)
                omega = (2 * np.pi * N) / 60
                T = (Eb * Ia) / omega if omega > 0 else 0
                torque_range.append(T)
                speed_range2.append(N)

            ax2.plot(torque_range, speed_range2, 'g-', linewidth=2)
            ax2.axhline(N_fl, color='r', linestyle='--', label=f'Full Load Speed ({N_fl:.0f} rpm)', alpha=0.7)
            ax2.axvline(T_dev_fl, color='r', linestyle='--', label=f'Full Load Torque ({T_dev_fl:.1f} Nm)', alpha=0.7)
            ax2.set_xlabel('Torque (Nm)', fontsize=10, fontweight='bold')
            ax2.set_ylabel('Speed (rpm)', fontsize=10, fontweight='bold')
            ax2.set_title('Torque-Speed Characteristic', fontsize=11, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=8)

            # Plot 3: Power distribution
            labels = ['Output\nPower', 'Armature\nLoss', 'Field\nLoss']
            values = [P_output_fl, Ia_fl**2 * Ra, If**2 * Rf]
            colors = ['#2ecc71', '#e74c3c', '#f39c12']

            bars = ax3.bar(labels, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
            ax3.set_ylabel('Power (W)', fontsize=10, fontweight='bold')
            ax3.set_title(f'Power Distribution (Input: {P_input_fl:.0f}W)', fontsize=11, fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')

            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}W',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

            # Plot 4: Efficiency vs Load
            eff_range = []
            current_range = np.linspace(Ia_nl, Ia_fl*1.2, 50)

            for Ia in current_range:
                Il = Ia + If
                P_in = V * Il
                P_loss = Ia**2 * Ra + If**2 * Rf
                P_out = P_in - P_loss
                eff = (P_out / P_in) * 100 if P_in > 0 else 0
                eff_range.append(eff)

            ax4.plot(current_range, eff_range, 'b-', linewidth=2)
            ax4.axvline(Ia_fl, color='r', linestyle='--',
                       label=f'Full Load\n({efficiency_fl:.1f}%)', alpha=0.7)
            ax4.set_xlabel('Armature Current (A)', fontsize=10, fontweight='bold')
            ax4.set_ylabel('Efficiency (%)', fontsize=10, fontweight='bold')
            ax4.set_title('Efficiency vs Load', fontsize=11, fontweight='bold')
            ax4.grid(True, alpha=0.3)
            ax4.legend(fontsize=8)
            ax4.set_ylim([0, 100])

            self.fig2.tight_layout()
            self.canvas2.draw()

        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred:\n{str(e)}")

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.simulation_running:
            messagebox.showwarning("Simulation Running", "Simulation is already running!")
            return

        self.simulation_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Status: Simulating...", foreground='orange')

        # Run simulation in separate thread
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()

    def stop_simulation(self):
        """Stop dynamic simulation"""
        self.simulation_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Stopped", foreground='red')

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()
        self.time_data = []
        self.state_data = []
        self.fig3.clear()
        self.canvas3.draw()
        self.sim_results.delete(1.0, tk.END)
        self.status_label.config(text="Status: Ready", foreground='green')

    def run_simulation(self):
        """Run dynamic simulation with selected ODE solver"""
        try:
            # Get parameters from sliders
            V_applied = self.sim_sliders["Applied Voltage (V):"].get()
            T_load = self.sim_sliders["Load Torque (Nm):"].get()
            J = self.sim_sliders["Moment of Inertia (kg·m²):"].get()
            Ra = self.sim_sliders["Armature Resistance (Ω):"].get()
            Rf = self.sim_sliders["Field Resistance (Ω):"].get()
            sim_time = self.sim_sliders["Simulation Time (s):"].get()

            machine_type = self.machine_type.get()
            solver = self.solver_type.get()

            # Motor constants
            Kt = 0.5  # Torque constant (Nm/A)
            Ke = 0.5  # Back-EMF constant (V·s/rad)
            B = 0.1   # Friction coefficient

            # Define differential equations for DC motor
            def dc_motor_dynamics(t, y):
                """
                State variables: y = [omega, ia]
                omega: angular velocity (rad/s)
                ia: armature current (A)
                """
                omega, ia = y

                # Back EMF
                Eb = Ke * omega

                # Current dynamics: L*(dia/dt) = V - Eb - ia*Ra
                # Assuming small inductance, approximate as: dia/dt ≈ (V - Eb - ia*Ra) / (0.01)
                L = 0.01  # Small inductance
                dia_dt = (V_applied - Eb - ia * Ra) / L

                # Speed dynamics: J*(domega/dt) = T_motor - T_load - B*omega
                T_motor = Kt * ia
                domega_dt = (T_motor - T_load - B * omega) / J

                return [domega_dt, dia_dt]

            # Initial conditions
            y0 = [0.0, 0.0]  # Initial speed and current

            # Time parameters
            t_span = (0, sim_time)

            # Solve based on selected solver
            if "RK45" in solver:
                # Adaptive RK45 solver
                sol = solve_ivp(dc_motor_dynamics, t_span, y0, method='RK45',
                               max_step=0.01, rtol=1e-6, atol=1e-8)
                t = sol.t
                omega = sol.y[0]
                ia = sol.y[1]

            elif "Euler" in solver:
                # Fixed-step Euler method
                dt = 0.001  # Time step
                t = np.arange(0, sim_time, dt)
                y = np.zeros((2, len(t)))
                y[:, 0] = y0

                for i in range(1, len(t)):
                    dy = dc_motor_dynamics(t[i-1], y[:, i-1])
                    y[:, i] = y[:, i-1] + np.array(dy) * dt

                omega = y[0]
                ia = y[1]

            else:  # RK4
                # Fixed-step RK4 method
                dt = 0.001
                t = np.arange(0, sim_time, dt)
                y = np.zeros((2, len(t)))
                y[:, 0] = y0

                for i in range(1, len(t)):
                    k1 = np.array(dc_motor_dynamics(t[i-1], y[:, i-1]))
                    k2 = np.array(dc_motor_dynamics(t[i-1] + dt/2, y[:, i-1] + k1*dt/2))
                    k3 = np.array(dc_motor_dynamics(t[i-1] + dt/2, y[:, i-1] + k2*dt/2))
                    k4 = np.array(dc_motor_dynamics(t[i-1] + dt, y[:, i-1] + k3*dt))
                    y[:, i] = y[:, i-1] + (k1 + 2*k2 + 2*k3 + k4) * dt / 6

                omega = y[0]
                ia = y[1]

            # Convert angular velocity to RPM
            speed_rpm = omega * 60 / (2 * np.pi)

            # Calculate other quantities
            Eb = Ke * omega
            T_motor = Kt * ia
            power = Eb * ia

            # Store data
            self.time_data = t
            self.state_data = {
                'speed_rpm': speed_rpm,
                'current': ia,
                'torque': T_motor,
                'power': power,
                'back_emf': Eb
            }

            # Update visualization
            self.root.after(0, self.update_simulation_plot)

            # Final values
            final_speed = speed_rpm[-1]
            final_current = ia[-1]
            final_torque = T_motor[-1]
            final_power = power[-1]

            # Update results
            results_text = f"""
═══════════════════════════════════════════════════════════
          DYNAMIC SIMULATION RESULTS
═══════════════════════════════════════════════════════════

SIMULATION PARAMETERS:
├─ Machine Type: {machine_type}
├─ ODE Solver: {solver}
├─ Applied Voltage: {V_applied:.2f} V
├─ Load Torque: {T_load:.2f} Nm
├─ Moment of Inertia: {J:.3f} kg·m²
├─ Armature Resistance: {Ra:.2f} Ω
└─ Simulation Time: {sim_time:.2f} s

STEADY-STATE VALUES:
├─ Final Speed: {final_speed:.2f} rpm
├─ Final Current: {final_current:.2f} A
├─ Final Torque: {final_torque:.2f} Nm
├─ Final Power: {final_power:.2f} W
└─ Back EMF: {Eb[-1]:.2f} V

PERFORMANCE METRICS:
├─ Rise Time (90%): {self.calculate_rise_time(t, speed_rpm):.3f} s
├─ Settling Time: {self.calculate_settling_time(t, speed_rpm):.3f} s
├─ Peak Overshoot: {self.calculate_overshoot(speed_rpm):.2f}%
└─ Steady-State Error: {abs(final_torque - T_load)/T_load*100:.2f}%
"""

            self.root.after(0, lambda: self.sim_results.delete(1.0, tk.END))
            self.root.after(0, lambda: self.sim_results.insert(1.0, results_text))

            self.simulation_running = False
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
            self.root.after(0, lambda: self.status_label.config(text="Status: Complete", foreground='green'))

        except Exception as e:
            self.simulation_running = False
            self.root.after(0, lambda: messagebox.showerror("Simulation Error", f"An error occurred:\n{str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="Status: Error", foreground='red'))

    def update_simulation_plot(self):
        """Update simulation plots in real-time"""
        self.fig3.clear()

        # Create 4 subplots
        ax1 = self.fig3.add_subplot(2, 2, 1)
        ax2 = self.fig3.add_subplot(2, 2, 2)
        ax3 = self.fig3.add_subplot(2, 2, 3)
        ax4 = self.fig3.add_subplot(2, 2, 4)

        t = self.time_data

        # Plot 1: Speed vs Time
        ax1.plot(t, self.state_data['speed_rpm'], 'b-', linewidth=2)
        ax1.set_xlabel('Time (s)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Speed (rpm)', fontsize=10, fontweight='bold')
        ax1.set_title('Motor Speed Response', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Current vs Time
        ax2.plot(t, self.state_data['current'], 'r-', linewidth=2)
        ax2.set_xlabel('Time (s)', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Current (A)', fontsize=10, fontweight='bold')
        ax2.set_title('Armature Current', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Torque vs Time
        ax3.plot(t, self.state_data['torque'], 'g-', linewidth=2)
        T_load = self.sim_sliders["Load Torque (Nm):"].get()
        ax3.axhline(T_load, color='r', linestyle='--', label=f'Load Torque ({T_load:.1f} Nm)', alpha=0.7)
        ax3.set_xlabel('Time (s)', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Torque (Nm)', fontsize=10, fontweight='bold')
        ax3.set_title('Motor Torque', fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend(fontsize=8)

        # Plot 4: Power vs Time
        ax4.plot(t, self.state_data['power'], 'm-', linewidth=2)
        ax4.set_xlabel('Time (s)', fontsize=10, fontweight='bold')
        ax4.set_ylabel('Power (W)', fontsize=10, fontweight='bold')
        ax4.set_title('Developed Power', fontsize=11, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        self.fig3.tight_layout()
        self.canvas3.draw()

    def calculate_rise_time(self, t, signal):
        """Calculate rise time (10% to 90%)"""
        try:
            final_value = signal[-1]
            idx_10 = np.where(signal >= 0.1 * final_value)[0][0]
            idx_90 = np.where(signal >= 0.9 * final_value)[0][0]
            return t[idx_90] - t[idx_10]
        except:
            return 0.0

    def calculate_settling_time(self, t, signal, tolerance=0.02):
        """Calculate settling time (within 2% of final value)"""
        try:
            final_value = signal[-1]
            settled = np.abs(signal - final_value) <= tolerance * final_value
            for i in range(len(settled)-1, -1, -1):
                if not settled[i]:
                    return t[i]
            return t[0]
        except:
            return 0.0

    def calculate_overshoot(self, signal):
        """Calculate percentage overshoot"""
        try:
            final_value = signal[-1]
            max_value = np.max(signal)
            overshoot = ((max_value - final_value) / final_value) * 100
            return max(0, overshoot)
        except:
            return 0.0


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = DCMachineLabApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
