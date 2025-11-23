"""
Advanced Electrical Engineering Lab - Power Factor & Dynamic Machine Simulation
Features:
- Power Factor Correction Calculator
- Dynamic Electrical Machine Simulation with ODE Solvers (RK45, Euler)
- Real-time visualization and control
- Auto-scaling GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
from scipy.integrate import solve_ivp
from datetime import datetime


class PowerFactorCalculator:
    """Solves power factor correction problems"""

    @staticmethod
    def calculate_phase_advancer_cost(pf_initial, pf_final, gen_cost_per_kva,
                                     interest_rate=0.01, base_kva=100):
        """
        Calculate limiting cost per kVA of phase advancing plant

        Parameters:
        - pf_initial: Initial power factor (lagging)
        - pf_final: Final power factor after correction
        - gen_cost_per_kva: Cost of generating plant per kVA
        - interest_rate: Interest and depreciation rate
        - base_kva: Base system capacity in kVA

        Returns:
        - Dictionary with detailed calculations
        """
        # Calculate angles
        phi_initial = math.acos(pf_initial)
        phi_final = math.acos(pf_final)

        # Real power at initial PF
        P_initial = base_kva * pf_initial

        # Real power at improved PF (same kVA capacity)
        P_final = base_kva * pf_final

        # Additional real power available
        P_increase = P_final - P_initial

        # Additional kVA needed if using new generating plant at initial PF
        additional_kva_gen = P_increase / pf_initial

        # Reactive power at initial PF
        Q_initial = base_kva * math.sin(phi_initial)

        # Reactive power at final PF
        Q_final = base_kva * math.sin(phi_final)

        # kVAr to be compensated by phase advancers
        kvar_compensation = Q_initial - Q_final

        # Annual cost of generating plant option
        annual_cost_gen = gen_cost_per_kva * additional_kva_gen * interest_rate

        # Limiting cost per kVA of phase advancers
        limiting_cost_per_kva = (gen_cost_per_kva * additional_kva_gen) / kvar_compensation

        return {
            'base_kva': base_kva,
            'pf_initial': pf_initial,
            'pf_final': pf_final,
            'P_initial': P_initial,
            'P_final': P_final,
            'P_increase': P_increase,
            'Q_initial': Q_initial,
            'Q_final': Q_final,
            'kvar_compensation': kvar_compensation,
            'additional_kva_gen': additional_kva_gen,
            'gen_cost_per_kva': gen_cost_per_kva,
            'limiting_cost_per_kva': limiting_cost_per_kva,
            'annual_cost_gen': annual_cost_gen,
            'annual_cost_phase_advancer': limiting_cost_per_kva * kvar_compensation * interest_rate,
            'interest_rate': interest_rate
        }


class DynamicMachineSimulator:
    """Simulates dynamic behavior of electrical machines using ODE solvers"""

    def __init__(self):
        self.reset_state()

    def reset_state(self):
        """Reset simulation state"""
        self.t_span = [0, 10]  # Time span
        self.t_eval = np.linspace(0, 10, 1000)
        self.current_time = 0
        self.solution = None

    def synchronous_machine_model(self, t, y, params):
        """
        Differential equations for synchronous machine dynamics
        State variables: [delta, omega, E_q', E_d', i_d, i_q]

        delta: Rotor angle (electrical radians)
        omega: Angular velocity deviation from synchronous speed
        E_q': q-axis transient EMF
        E_d': d-axis transient EMF
        i_d: d-axis current
        i_q: q-axis current
        """
        delta, omega, E_q_prime, E_d_prime, i_d, i_q = y

        # Machine parameters
        H = params.get('H', 5.0)  # Inertia constant (seconds)
        D = params.get('D', 2.0)  # Damping coefficient
        X_d = params.get('X_d', 1.8)  # d-axis reactance
        X_q = params.get('X_q', 1.7)  # q-axis reactance
        X_d_prime = params.get('X_d_prime', 0.3)  # d-axis transient reactance
        X_q_prime = params.get('X_q_prime', 0.55)  # q-axis transient reactance
        T_d0_prime = params.get('T_d0_prime', 8.0)  # d-axis time constant
        T_q0_prime = params.get('T_q0_prime', 1.0)  # q-axis time constant
        omega_s = params.get('omega_s', 2 * np.pi * 60)  # Synchronous speed

        # Mechanical power (constant)
        P_m = params.get('P_m', 0.8)

        # Electrical power
        P_e = E_q_prime * i_q + E_d_prime * i_d + (X_q - X_d) * i_d * i_q

        # Load voltage (simplified)
        V_d = E_d_prime - X_q_prime * i_q
        V_q = E_q_prime + X_d_prime * i_d
        V_t = np.sqrt(V_d**2 + V_q**2)

        # Field voltage (constant excitation)
        E_fd = params.get('E_fd', 1.0)

        # Differential equations
        d_delta = omega  # Rotor angle dynamics
        d_omega = (omega_s / (2 * H)) * (P_m - P_e - D * omega)  # Swing equation
        d_E_q_prime = (1 / T_d0_prime) * (E_fd - E_q_prime - (X_d - X_d_prime) * i_d)
        d_E_d_prime = (1 / T_q0_prime) * (-E_d_prime + (X_q - X_q_prime) * i_q)

        # Stator currents (algebraic approximation)
        # Simplified: assume load impedance
        Z_load = params.get('Z_load', 5.0)
        d_i_d = -i_d + V_d / Z_load
        d_i_q = -i_q + V_q / Z_load

        return [d_delta, d_omega, d_E_q_prime, d_E_d_prime, d_i_d, d_i_q]

    def induction_motor_model(self, t, y, params):
        """
        Differential equations for induction motor dynamics
        State variables: [omega, i_qs, i_ds, i_qr, i_dr]
        """
        omega, i_qs, i_ds, i_qr, i_dr = y

        # Motor parameters
        Rs = params.get('Rs', 0.1)  # Stator resistance
        Rr = params.get('Rr', 0.08)  # Rotor resistance
        Ls = params.get('Ls', 0.05)  # Stator inductance
        Lr = params.get('Lr', 0.05)  # Rotor inductance
        Lm = params.get('Lm', 0.045)  # Mutual inductance
        J = params.get('J', 0.1)  # Moment of inertia
        B = params.get('B', 0.01)  # Friction coefficient
        P = params.get('P', 4)  # Number of poles
        omega_e = params.get('omega_e', 2 * np.pi * 60)  # Electrical frequency

        # Applied voltages
        V_qs = params.get('V_qs', 100)
        V_ds = params.get('V_ds', 0)

        # Load torque
        T_load = params.get('T_load', 5.0)

        # Electrical torque
        T_e = (3 * P / 4) * Lm * (i_dr * i_qs - i_qr * i_ds)

        # Slip speed
        omega_slip = omega_e - (P / 2) * omega

        # Differential equations
        d_omega = (1 / J) * (T_e - T_load - B * omega)

        # Stator currents
        sigma = 1 - (Lm**2 / (Ls * Lr))
        d_i_qs = (1 / (sigma * Ls)) * (V_qs - Rs * i_qs - omega_e * sigma * Ls * i_ds - (Lm / Lr) * Rr * i_qr + omega_slip * (Lm / Lr) * Lr * i_dr)
        d_i_ds = (1 / (sigma * Ls)) * (V_ds - Rs * i_ds + omega_e * sigma * Ls * i_qs - (Lm / Lr) * Rr * i_dr - omega_slip * (Lm / Lr) * Lr * i_qr)

        # Rotor currents
        d_i_qr = (1 / (sigma * Lr)) * (-(Lm / Ls) * Rs * i_qs - Rr * i_qr - omega_slip * sigma * Lr * i_dr + (Lm / Ls) * omega_e * sigma * Ls * i_ds)
        d_i_dr = (1 / (sigma * Lr)) * (-(Lm / Ls) * Rs * i_ds - Rr * i_dr + omega_slip * sigma * Lr * i_qr - (Lm / Ls) * omega_e * sigma * Ls * i_qs)

        return [d_omega, d_i_qs, d_i_ds, d_i_qr, d_i_dr]

    def euler_method(self, f, t_span, y0, params, dt=0.01):
        """Euler method for ODE solution"""
        t = np.arange(t_span[0], t_span[1], dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(1, len(t)):
            dy = f(t[i-1], y[i-1], params)
            y[i] = y[i-1] + dt * np.array(dy)

        return t, y

    def rk45_method(self, f, t_span, y0, params):
        """RK45 (Runge-Kutta-Fehlberg) method using scipy"""
        sol = solve_ivp(
            lambda t, y: f(t, y, params),
            t_span,
            y0,
            method='RK45',
            dense_output=True,
            max_step=0.01
        )
        return sol.t, sol.y.T

    def simulate(self, model_type='synchronous', solver='rk45', params=None, t_span=None, y0=None):
        """
        Run simulation

        Parameters:
        - model_type: 'synchronous' or 'induction'
        - solver: 'rk45' or 'euler'
        - params: Dictionary of machine parameters
        - t_span: [t_start, t_end]
        - y0: Initial conditions
        """
        if params is None:
            params = {}

        if t_span is None:
            t_span = self.t_span

        # Default initial conditions
        if y0 is None:
            if model_type == 'synchronous':
                y0 = [0.1, 0.0, 1.0, 0.0, 0.5, 0.5]  # [delta, omega, E_q', E_d', i_d, i_q]
            else:  # induction
                y0 = [0.0, 0.0, 0.0, 0.0, 0.0]  # [omega, i_qs, i_ds, i_qr, i_dr]

        # Select model
        if model_type == 'synchronous':
            model_func = self.synchronous_machine_model
        else:
            model_func = self.induction_motor_model

        # Select solver
        if solver == 'euler':
            t, y = self.euler_method(model_func, t_span, y0, params)
        else:  # rk45
            t, y = self.rk45_method(model_func, t_span, y0, params)

        self.solution = {'t': t, 'y': y, 'model_type': model_type}
        return t, y


class AdvancedElectricalLab(tk.Tk):
    """Main application class"""

    def __init__(self):
        super().__init__()

        self.title("Advanced Electrical Engineering Lab")
        self.geometry("1200x800")
        self.configure(bg='#2b2b2b')

        # Initialize calculators
        self.pf_calculator = PowerFactorCalculator()
        self.machine_simulator = DynamicMachineSimulator()

        # Simulation control
        self.simulation_running = False
        self.animation_id = None

        # Create main menu
        self.create_menu()

        # Create notebook for different modules
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Create tabs
        self.create_power_factor_tab()
        self.create_synchronous_machine_tab()
        self.create_induction_motor_tab()

        # Bind resize event
        self.bind('<Configure>', self.on_resize)

        # Status bar
        self.status_bar = tk.Label(self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg='#3c3c3c', fg='white')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        """Create main menu bar"""
        menubar = tk.Menu(self, bg='#2b2b2b', fg='white')
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2b2b2b', fg='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Calculation", command=self.reset_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#2b2b2b', fg='white')
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Reset All", command=self.reset_all)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2b2b2b', fg='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_power_factor_tab(self):
        """Create power factor calculator tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Power Factor Calculator")

        # Configure grid weights for auto-scaling
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)

        # Left panel - Input parameters
        left_frame = tk.LabelFrame(tab, text="Input Parameters", bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # System capacity
        tk.Label(left_frame, text="System Capacity (kVA):", bg='#3c3c3c', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.pf_kva_var = tk.DoubleVar(value=100)
        tk.Scale(left_frame, from_=10, to=1000, orient=tk.HORIZONTAL, variable=self.pf_kva_var,
                bg='#3c3c3c', fg='white', highlightthickness=0, length=200).grid(row=0, column=1, padx=5, pady=5)

        # Initial power factor
        tk.Label(left_frame, text="Initial Power Factor:", bg='#3c3c3c', fg='white').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.pf_initial_var = tk.DoubleVar(value=0.71)
        tk.Scale(left_frame, from_=0.5, to=0.95, resolution=0.01, orient=tk.HORIZONTAL,
                variable=self.pf_initial_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=200).grid(row=1, column=1, padx=5, pady=5)

        # Final power factor
        tk.Label(left_frame, text="Final Power Factor:", bg='#3c3c3c', fg='white').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.pf_final_var = tk.DoubleVar(value=0.87)
        tk.Scale(left_frame, from_=0.5, to=1.0, resolution=0.01, orient=tk.HORIZONTAL,
                variable=self.pf_final_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=200).grid(row=2, column=1, padx=5, pady=5)

        # Generator cost
        tk.Label(left_frame, text="Gen. Cost (Rs/kVA):", bg='#3c3c3c', fg='white').grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.pf_gen_cost_var = tk.DoubleVar(value=60)
        tk.Entry(left_frame, textvariable=self.pf_gen_cost_var, bg='#4c4c4c', fg='white', insertbackground='white').grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        # Interest rate
        tk.Label(left_frame, text="Interest Rate (%):", bg='#3c3c3c', fg='white').grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.pf_interest_var = tk.DoubleVar(value=1.0)
        tk.Entry(left_frame, textvariable=self.pf_interest_var, bg='#4c4c4c', fg='white', insertbackground='white').grid(row=4, column=1, sticky='ew', padx=5, pady=5)

        # Calculate button
        tk.Button(left_frame, text="Calculate", command=self.calculate_power_factor,
                 bg='#0078d7', fg='white', font=('Arial', 10, 'bold')).grid(row=5, column=0, columnspan=2, pady=10)

        # Right panel - Results
        right_frame = tk.LabelFrame(tab, text="Results & Visualization", bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Results text
        self.pf_results_text = tk.Text(right_frame, height=10, bg='#4c4c4c', fg='white', insertbackground='white', font=('Courier', 9))
        self.pf_results_text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Scrollbar
        scrollbar = tk.Scrollbar(right_frame, command=self.pf_results_text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.pf_results_text.config(yscrollcommand=scrollbar.set)

        # Visualization area
        self.pf_fig = Figure(figsize=(8, 4), facecolor='#2b2b2b')
        self.pf_canvas = FigureCanvasTkAgg(self.pf_fig, right_frame)
        self.pf_canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        right_frame.grid_rowconfigure(1, weight=1)

    def create_synchronous_machine_tab(self):
        """Create synchronous machine simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Synchronous Machine Dynamics")

        # Configure grid
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)

        # Left panel - Controls
        left_frame = tk.LabelFrame(tab, text="Control Panel", bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Machine parameters
        tk.Label(left_frame, text="Inertia Constant H (s):", bg='#3c3c3c', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.sync_H_var = tk.DoubleVar(value=5.0)
        tk.Scale(left_frame, from_=1, to=10, resolution=0.1, orient=tk.HORIZONTAL,
                variable=self.sync_H_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=150).grid(row=0, column=1, padx=5, pady=3)

        tk.Label(left_frame, text="Damping D:", bg='#3c3c3c', fg='white').grid(row=1, column=0, sticky='w', padx=5, pady=3)
        self.sync_D_var = tk.DoubleVar(value=2.0)
        tk.Scale(left_frame, from_=0, to=5, resolution=0.1, orient=tk.HORIZONTAL,
                variable=self.sync_D_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=150).grid(row=1, column=1, padx=5, pady=3)

        tk.Label(left_frame, text="Mechanical Power Pm:", bg='#3c3c3c', fg='white').grid(row=2, column=0, sticky='w', padx=5, pady=3)
        self.sync_Pm_var = tk.DoubleVar(value=0.8)
        tk.Scale(left_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL,
                variable=self.sync_Pm_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=150).grid(row=2, column=1, padx=5, pady=3)

        tk.Label(left_frame, text="Field Voltage Efd:", bg='#3c3c3c', fg='white').grid(row=3, column=0, sticky='w', padx=5, pady=3)
        self.sync_Efd_var = tk.DoubleVar(value=1.0)
        tk.Scale(left_frame, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL,
                variable=self.sync_Efd_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=150).grid(row=3, column=1, padx=5, pady=3)

        tk.Label(left_frame, text="Simulation Time (s):", bg='#3c3c3c', fg='white').grid(row=4, column=0, sticky='w', padx=5, pady=3)
        self.sync_time_var = tk.DoubleVar(value=10)
        tk.Entry(left_frame, textvariable=self.sync_time_var, bg='#4c4c4c', fg='white', insertbackground='white').grid(row=4, column=1, sticky='ew', padx=5, pady=3)

        # Solver selection
        tk.Label(left_frame, text="ODE Solver:", bg='#3c3c3c', fg='white').grid(row=5, column=0, sticky='w', padx=5, pady=3)
        self.sync_solver_var = tk.StringVar(value='rk45')
        solver_combo = ttk.Combobox(left_frame, textvariable=self.sync_solver_var, values=['rk45', 'euler'], state='readonly')
        solver_combo.grid(row=5, column=1, sticky='ew', padx=5, pady=3)

        # Control buttons
        button_frame = tk.Frame(left_frame, bg='#3c3c3c')
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.sync_start_btn = tk.Button(button_frame, text="Start", command=lambda: self.run_simulation('synchronous'),
                                       bg='#28a745', fg='white', font=('Arial', 9, 'bold'), width=8)
        self.sync_start_btn.pack(side=tk.LEFT, padx=5)

        self.sync_stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_simulation,
                                      bg='#dc3545', fg='white', font=('Arial', 9, 'bold'), width=8, state=tk.DISABLED)
        self.sync_stop_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Reset", command=lambda: self.reset_simulation('synchronous'),
                 bg='#ffc107', fg='black', font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT, padx=5)

        # Right panel - Visualization
        right_frame = tk.LabelFrame(tab, text="Dynamic Response", bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.sync_fig = Figure(figsize=(10, 8), facecolor='#2b2b2b')
        self.sync_canvas = FigureCanvasTkAgg(self.sync_fig, right_frame)
        self.sync_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

    def create_induction_motor_tab(self):
        """Create induction motor simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Induction Motor Dynamics")

        # Configure grid
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)

        # Left panel - Controls
        left_frame = tk.LabelFrame(tab, text="Control Panel", bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Motor parameters
        tk.Label(left_frame, text="Stator Voltage Vqs (V):", bg='#3c3c3c', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.ind_Vqs_var = tk.DoubleVar(value=100)
        tk.Scale(left_frame, from_=0, to=200, resolution=10, orient=tk.HORIZONTAL,
                variable=self.ind_Vqs_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=150).grid(row=0, column=1, padx=5, pady=3)

        tk.Label(left_frame, text="Load Torque (Nm):", bg='#3c3c3c', fg='white').grid(row=1, column=0, sticky='w', padx=5, pady=3)
        self.ind_Tload_var = tk.DoubleVar(value=5.0)
        tk.Scale(left_frame, from_=0, to=20, resolution=0.5, orient=tk.HORIZONTAL,
                variable=self.ind_Tload_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=150).grid(row=1, column=1, padx=5, pady=3)

        tk.Label(left_frame, text="Rotor Resistance Rr:", bg='#3c3c3c', fg='white').grid(row=2, column=0, sticky='w', padx=5, pady=3)
        self.ind_Rr_var = tk.DoubleVar(value=0.08)
        tk.Scale(left_frame, from_=0.01, to=0.5, resolution=0.01, orient=tk.HORIZONTAL,
                variable=self.ind_Rr_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=150).grid(row=2, column=1, padx=5, pady=3)

        tk.Label(left_frame, text="Moment of Inertia J:", bg='#3c3c3c', fg='white').grid(row=3, column=0, sticky='w', padx=5, pady=3)
        self.ind_J_var = tk.DoubleVar(value=0.1)
        tk.Scale(left_frame, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL,
                variable=self.ind_J_var, bg='#3c3c3c', fg='white', highlightthickness=0, length=150).grid(row=3, column=1, padx=5, pady=3)

        tk.Label(left_frame, text="Simulation Time (s):", bg='#3c3c3c', fg='white').grid(row=4, column=0, sticky='w', padx=5, pady=3)
        self.ind_time_var = tk.DoubleVar(value=5)
        tk.Entry(left_frame, textvariable=self.ind_time_var, bg='#4c4c4c', fg='white', insertbackground='white').grid(row=4, column=1, sticky='ew', padx=5, pady=3)

        # Solver selection
        tk.Label(left_frame, text="ODE Solver:", bg='#3c3c3c', fg='white').grid(row=5, column=0, sticky='w', padx=5, pady=3)
        self.ind_solver_var = tk.StringVar(value='rk45')
        solver_combo = ttk.Combobox(left_frame, textvariable=self.ind_solver_var, values=['rk45', 'euler'], state='readonly')
        solver_combo.grid(row=5, column=1, sticky='ew', padx=5, pady=3)

        # Control buttons
        button_frame = tk.Frame(left_frame, bg='#3c3c3c')
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.ind_start_btn = tk.Button(button_frame, text="Start", command=lambda: self.run_simulation('induction'),
                                       bg='#28a745', fg='white', font=('Arial', 9, 'bold'), width=8)
        self.ind_start_btn.pack(side=tk.LEFT, padx=5)

        self.ind_stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_simulation,
                                      bg='#dc3545', fg='white', font=('Arial', 9, 'bold'), width=8, state=tk.DISABLED)
        self.ind_stop_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Reset", command=lambda: self.reset_simulation('induction'),
                 bg='#ffc107', fg='black', font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT, padx=5)

        # Right panel - Visualization
        right_frame = tk.LabelFrame(tab, text="Dynamic Response", bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.ind_fig = Figure(figsize=(10, 8), facecolor='#2b2b2b')
        self.ind_canvas = FigureCanvasTkAgg(self.ind_fig, right_frame)
        self.ind_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

    def calculate_power_factor(self):
        """Calculate power factor correction"""
        try:
            # Get input values
            base_kva = self.pf_kva_var.get()
            pf_initial = self.pf_initial_var.get()
            pf_final = self.pf_final_var.get()
            gen_cost = self.pf_gen_cost_var.get()
            interest_rate = self.pf_interest_var.get() / 100

            # Validate inputs
            if pf_final <= pf_initial:
                messagebox.showerror("Error", "Final power factor must be greater than initial power factor!")
                return

            # Calculate
            results = self.pf_calculator.calculate_phase_advancer_cost(
                pf_initial, pf_final, gen_cost, interest_rate, base_kva
            )

            # Display results
            self.pf_results_text.delete(1.0, tk.END)
            self.pf_results_text.insert(tk.END, "=" * 70 + "\n")
            self.pf_results_text.insert(tk.END, "POWER FACTOR CORRECTION ANALYSIS\n")
            self.pf_results_text.insert(tk.END, "=" * 70 + "\n\n")

            self.pf_results_text.insert(tk.END, f"System Capacity: {results['base_kva']:.2f} kVA\n")
            self.pf_results_text.insert(tk.END, f"Initial Power Factor: {results['pf_initial']:.3f} (lagging)\n")
            self.pf_results_text.insert(tk.END, f"Final Power Factor: {results['pf_final']:.3f}\n\n")

            self.pf_results_text.insert(tk.END, f"Real Power at Initial PF: {results['P_initial']:.2f} kW\n")
            self.pf_results_text.insert(tk.END, f"Real Power at Final PF: {results['P_final']:.2f} kW\n")
            self.pf_results_text.insert(tk.END, f"Additional Power Available: {results['P_increase']:.2f} kW\n\n")

            self.pf_results_text.insert(tk.END, f"Reactive Power (Initial): {results['Q_initial']:.2f} kVAr\n")
            self.pf_results_text.insert(tk.END, f"Reactive Power (Final): {results['Q_final']:.2f} kVAr\n")
            self.pf_results_text.insert(tk.END, f"kVAr to be Compensated: {results['kvar_compensation']:.2f} kVAr\n\n")

            self.pf_results_text.insert(tk.END, "OPTION 1: Phase Advancers\n")
            self.pf_results_text.insert(tk.END, f"  Phase Advancer Rating: {results['kvar_compensation']:.2f} kVAr\n")
            self.pf_results_text.insert(tk.END, f"  Limiting Cost: Rs. {results['limiting_cost_per_kva']:.2f} per kVA\n")
            self.pf_results_text.insert(tk.END, f"  Annual Cost: Rs. {results['annual_cost_phase_advancer']:.2f}\n\n")

            self.pf_results_text.insert(tk.END, "OPTION 2: New Generating Plant\n")
            self.pf_results_text.insert(tk.END, f"  Additional Capacity Needed: {results['additional_kva_gen']:.2f} kVA\n")
            self.pf_results_text.insert(tk.END, f"  Cost per kVA: Rs. {results['gen_cost_per_kva']:.2f}\n")
            self.pf_results_text.insert(tk.END, f"  Annual Cost: Rs. {results['annual_cost_gen']:.2f}\n\n")

            self.pf_results_text.insert(tk.END, "=" * 70 + "\n")
            self.pf_results_text.insert(tk.END, f"CONCLUSION:\n")
            self.pf_results_text.insert(tk.END, f"Phase advancers are economical if their cost is\n")
            self.pf_results_text.insert(tk.END, f"Rs. {results['limiting_cost_per_kva']:.2f} per kVA or less.\n")
            self.pf_results_text.insert(tk.END, "=" * 70 + "\n")

            # Visualize results
            self.visualize_power_factor(results)

            self.status_bar.config(text=f"Calculation completed at {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def visualize_power_factor(self, results):
        """Create visualization for power factor results"""
        self.pf_fig.clear()

        # Create subplots
        gs = self.pf_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Plot 1: Power comparison
        ax1 = self.pf_fig.add_subplot(gs[0, 0])
        categories = ['Initial', 'Final']
        real_power = [results['P_initial'], results['P_final']]
        reactive_power = [results['Q_initial'], results['Q_final']]

        x = np.arange(len(categories))
        width = 0.35

        ax1.bar(x - width/2, real_power, width, label='Real Power (kW)', color='#28a745')
        ax1.bar(x + width/2, reactive_power, width, label='Reactive Power (kVAr)', color='#dc3545')
        ax1.set_xlabel('Power Factor State', color='white')
        ax1.set_ylabel('Power (kW / kVAr)', color='white')
        ax1.set_title('Power Comparison', color='white', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend()
        ax1.tick_params(colors='white')
        ax1.set_facecolor('#2b2b2b')
        ax1.spines['bottom'].set_color('white')
        ax1.spines['top'].set_color('white')
        ax1.spines['left'].set_color('white')
        ax1.spines['right'].set_color('white')

        # Plot 2: Cost comparison
        ax2 = self.pf_fig.add_subplot(gs[0, 1])
        options = ['Phase\nAdvancers', 'New\nGenerating\nPlant']
        annual_costs = [results['annual_cost_phase_advancer'], results['annual_cost_gen']]
        colors = ['#0078d7', '#ffc107']

        bars = ax2.bar(options, annual_costs, color=colors, edgecolor='white', linewidth=2)
        ax2.set_ylabel('Annual Cost (Rs.)', color='white')
        ax2.set_title('Cost Comparison', color='white', fontweight='bold')
        ax2.tick_params(colors='white')
        ax2.set_facecolor('#2b2b2b')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['top'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.spines['right'].set_color('white')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'Rs. {height:.2f}',
                    ha='center', va='bottom', color='white', fontweight='bold')

        # Plot 3: Power triangle (initial)
        ax3 = self.pf_fig.add_subplot(gs[1, 0])
        P_init = results['P_initial']
        Q_init = results['Q_initial']
        S_init = results['base_kva']

        ax3.arrow(0, 0, P_init, 0, head_width=2, head_length=3, fc='#28a745', ec='#28a745', linewidth=2)
        ax3.arrow(P_init, 0, 0, Q_init, head_width=2, head_length=3, fc='#dc3545', ec='#dc3545', linewidth=2)
        ax3.plot([0, P_init], [0, Q_init], 'w--', linewidth=2, label=f'S = {S_init:.2f} kVA')

        ax3.text(P_init/2, -5, f'P = {P_init:.2f} kW', ha='center', color='white', fontweight='bold')
        ax3.text(P_init+5, Q_init/2, f'Q = {Q_init:.2f} kVAr', ha='left', color='white', fontweight='bold')
        ax3.text(P_init/2-5, Q_init/2+5, f'PF = {results["pf_initial"]:.3f}', ha='center', color='white', fontweight='bold')

        ax3.set_xlabel('Real Power (kW)', color='white')
        ax3.set_ylabel('Reactive Power (kVAr)', color='white')
        ax3.set_title('Power Triangle (Initial)', color='white', fontweight='bold')
        ax3.grid(True, alpha=0.3, color='white')
        ax3.set_facecolor('#2b2b2b')
        ax3.tick_params(colors='white')
        ax3.spines['bottom'].set_color('white')
        ax3.spines['top'].set_color('white')
        ax3.spines['left'].set_color('white')
        ax3.spines['right'].set_color('white')

        # Plot 4: Power triangle (final)
        ax4 = self.pf_fig.add_subplot(gs[1, 1])
        P_final = results['P_final']
        Q_final = results['Q_final']

        ax4.arrow(0, 0, P_final, 0, head_width=2, head_length=3, fc='#28a745', ec='#28a745', linewidth=2)
        ax4.arrow(P_final, 0, 0, Q_final, head_width=2, head_length=3, fc='#dc3545', ec='#dc3545', linewidth=2)
        ax4.plot([0, P_final], [0, Q_final], 'w--', linewidth=2, label=f'S = {S_init:.2f} kVA')

        ax4.text(P_final/2, -5, f'P = {P_final:.2f} kW', ha='center', color='white', fontweight='bold')
        ax4.text(P_final+5, Q_final/2, f'Q = {Q_final:.2f} kVAr', ha='left', color='white', fontweight='bold')
        ax4.text(P_final/2-5, Q_final/2+5, f'PF = {results["pf_final"]:.3f}', ha='center', color='white', fontweight='bold')

        ax4.set_xlabel('Real Power (kW)', color='white')
        ax4.set_ylabel('Reactive Power (kVAr)', color='white')
        ax4.set_title('Power Triangle (Final)', color='white', fontweight='bold')
        ax4.grid(True, alpha=0.3, color='white')
        ax4.set_facecolor('#2b2b2b')
        ax4.tick_params(colors='white')
        ax4.spines['bottom'].set_color('white')
        ax4.spines['top'].set_color('white')
        ax4.spines['left'].set_color('white')
        ax4.spines['right'].set_color('white')

        self.pf_canvas.draw()

    def run_simulation(self, machine_type):
        """Run dynamic simulation"""
        try:
            self.simulation_running = True

            if machine_type == 'synchronous':
                # Enable/disable buttons
                self.sync_start_btn.config(state=tk.DISABLED)
                self.sync_stop_btn.config(state=tk.NORMAL)

                # Get parameters
                params = {
                    'H': self.sync_H_var.get(),
                    'D': self.sync_D_var.get(),
                    'P_m': self.sync_Pm_var.get(),
                    'E_fd': self.sync_Efd_var.get(),
                    'omega_s': 2 * np.pi * 60
                }

                t_span = [0, self.sync_time_var.get()]
                solver = self.sync_solver_var.get()

                # Run simulation
                t, y = self.machine_simulator.simulate(
                    model_type='synchronous',
                    solver=solver,
                    params=params,
                    t_span=t_span
                )

                # Plot results
                self.plot_synchronous_results(t, y)

                # Re-enable buttons
                self.sync_start_btn.config(state=tk.NORMAL)
                self.sync_stop_btn.config(state=tk.DISABLED)

                self.status_bar.config(text=f"Synchronous machine simulation completed using {solver.upper()} solver")

            else:  # induction motor
                # Enable/disable buttons
                self.ind_start_btn.config(state=tk.DISABLED)
                self.ind_stop_btn.config(state=tk.NORMAL)

                # Get parameters
                params = {
                    'V_qs': self.ind_Vqs_var.get(),
                    'T_load': self.ind_Tload_var.get(),
                    'Rr': self.ind_Rr_var.get(),
                    'J': self.ind_J_var.get(),
                    'omega_e': 2 * np.pi * 60
                }

                t_span = [0, self.ind_time_var.get()]
                solver = self.ind_solver_var.get()

                # Run simulation
                t, y = self.machine_simulator.simulate(
                    model_type='induction',
                    solver=solver,
                    params=params,
                    t_span=t_span
                )

                # Plot results
                self.plot_induction_results(t, y)

                # Re-enable buttons
                self.ind_start_btn.config(state=tk.NORMAL)
                self.ind_stop_btn.config(state=tk.DISABLED)

                self.status_bar.config(text=f"Induction motor simulation completed using {solver.upper()} solver")

            self.simulation_running = False

        except Exception as e:
            messagebox.showerror("Simulation Error", f"Error during simulation: {str(e)}")
            self.simulation_running = False
            if machine_type == 'synchronous':
                self.sync_start_btn.config(state=tk.NORMAL)
                self.sync_stop_btn.config(state=tk.DISABLED)
            else:
                self.ind_start_btn.config(state=tk.NORMAL)
                self.ind_stop_btn.config(state=tk.DISABLED)

    def plot_synchronous_results(self, t, y):
        """Plot synchronous machine simulation results"""
        self.sync_fig.clear()

        # Create subplots
        gs = self.sync_fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Plot 1: Rotor angle
        ax1 = self.sync_fig.add_subplot(gs[0, 0])
        ax1.plot(t, y[:, 0] * 180 / np.pi, 'cyan', linewidth=2)
        ax1.set_xlabel('Time (s)', color='white')
        ax1.set_ylabel('Rotor Angle δ (degrees)', color='white')
        ax1.set_title('Rotor Angle Response', color='white', fontweight='bold')
        ax1.grid(True, alpha=0.3, color='white')
        ax1.set_facecolor('#2b2b2b')
        ax1.tick_params(colors='white')
        self.style_axes(ax1)

        # Plot 2: Angular velocity
        ax2 = self.sync_fig.add_subplot(gs[0, 1])
        ax2.plot(t, y[:, 1], 'magenta', linewidth=2)
        ax2.set_xlabel('Time (s)', color='white')
        ax2.set_ylabel('Speed Deviation ω (rad/s)', color='white')
        ax2.set_title('Angular Velocity Response', color='white', fontweight='bold')
        ax2.grid(True, alpha=0.3, color='white')
        ax2.set_facecolor('#2b2b2b')
        ax2.tick_params(colors='white')
        self.style_axes(ax2)

        # Plot 3: Transient EMFs
        ax3 = self.sync_fig.add_subplot(gs[1, 0])
        ax3.plot(t, y[:, 2], 'lime', linewidth=2, label="E'q")
        ax3.plot(t, y[:, 3], 'yellow', linewidth=2, label="E'd")
        ax3.set_xlabel('Time (s)', color='white')
        ax3.set_ylabel('Transient EMF (pu)', color='white')
        ax3.set_title('Transient EMF Response', color='white', fontweight='bold')
        ax3.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax3.grid(True, alpha=0.3, color='white')
        ax3.set_facecolor('#2b2b2b')
        ax3.tick_params(colors='white')
        self.style_axes(ax3)

        # Plot 4: Stator currents
        ax4 = self.sync_fig.add_subplot(gs[1, 1])
        ax4.plot(t, y[:, 4], 'orange', linewidth=2, label='id')
        ax4.plot(t, y[:, 5], 'red', linewidth=2, label='iq')
        ax4.set_xlabel('Time (s)', color='white')
        ax4.set_ylabel('Current (pu)', color='white')
        ax4.set_title('Stator Current Response', color='white', fontweight='bold')
        ax4.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax4.grid(True, alpha=0.3, color='white')
        ax4.set_facecolor('#2b2b2b')
        ax4.tick_params(colors='white')
        self.style_axes(ax4)

        # Plot 5: Phase plane (delta vs omega)
        ax5 = self.sync_fig.add_subplot(gs[2, 0])
        ax5.plot(y[:, 0] * 180 / np.pi, y[:, 1], 'cyan', linewidth=2)
        ax5.scatter(y[0, 0] * 180 / np.pi, y[0, 1], color='lime', s=100, marker='o', label='Start', zorder=5)
        ax5.scatter(y[-1, 0] * 180 / np.pi, y[-1, 1], color='red', s=100, marker='s', label='End', zorder=5)
        ax5.set_xlabel('Rotor Angle δ (degrees)', color='white')
        ax5.set_ylabel('Speed Deviation ω (rad/s)', color='white')
        ax5.set_title('Phase Plane Trajectory', color='white', fontweight='bold')
        ax5.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax5.grid(True, alpha=0.3, color='white')
        ax5.set_facecolor('#2b2b2b')
        ax5.tick_params(colors='white')
        self.style_axes(ax5)

        # Plot 6: Power analysis
        ax6 = self.sync_fig.add_subplot(gs[2, 1])
        # Calculate electrical power
        P_e = y[:, 2] * y[:, 5] + y[:, 3] * y[:, 4]
        ax6.plot(t, P_e, 'lime', linewidth=2, label='Electrical Power')
        ax6.axhline(y=self.sync_Pm_var.get(), color='orange', linestyle='--', linewidth=2, label='Mechanical Power')
        ax6.set_xlabel('Time (s)', color='white')
        ax6.set_ylabel('Power (pu)', color='white')
        ax6.set_title('Power Balance', color='white', fontweight='bold')
        ax6.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax6.grid(True, alpha=0.3, color='white')
        ax6.set_facecolor('#2b2b2b')
        ax6.tick_params(colors='white')
        self.style_axes(ax6)

        self.sync_canvas.draw()

    def plot_induction_results(self, t, y):
        """Plot induction motor simulation results"""
        self.ind_fig.clear()

        # Create subplots
        gs = self.ind_fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Plot 1: Rotor speed
        ax1 = self.ind_fig.add_subplot(gs[0, 0])
        # Convert to RPM
        rpm = y[:, 0] * 60 / (2 * np.pi)
        ax1.plot(t, rpm, 'cyan', linewidth=2)
        ax1.set_xlabel('Time (s)', color='white')
        ax1.set_ylabel('Speed (RPM)', color='white')
        ax1.set_title('Rotor Speed Response', color='white', fontweight='bold')
        ax1.grid(True, alpha=0.3, color='white')
        ax1.set_facecolor('#2b2b2b')
        ax1.tick_params(colors='white')
        self.style_axes(ax1)

        # Plot 2: Stator currents
        ax2 = self.ind_fig.add_subplot(gs[0, 1])
        ax2.plot(t, y[:, 1], 'magenta', linewidth=2, label='iqs')
        ax2.plot(t, y[:, 2], 'yellow', linewidth=2, label='ids')
        ax2.set_xlabel('Time (s)', color='white')
        ax2.set_ylabel('Stator Current (A)', color='white')
        ax2.set_title('Stator Current Response', color='white', fontweight='bold')
        ax2.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax2.grid(True, alpha=0.3, color='white')
        ax2.set_facecolor('#2b2b2b')
        ax2.tick_params(colors='white')
        self.style_axes(ax2)

        # Plot 3: Rotor currents
        ax3 = self.ind_fig.add_subplot(gs[1, 0])
        ax3.plot(t, y[:, 3], 'lime', linewidth=2, label='iqr')
        ax3.plot(t, y[:, 4], 'orange', linewidth=2, label='idr')
        ax3.set_xlabel('Time (s)', color='white')
        ax3.set_ylabel('Rotor Current (A)', color='white')
        ax3.set_title('Rotor Current Response', color='white', fontweight='bold')
        ax3.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax3.grid(True, alpha=0.3, color='white')
        ax3.set_facecolor('#2b2b2b')
        ax3.tick_params(colors='white')
        self.style_axes(ax3)

        # Plot 4: Electromagnetic torque
        ax4 = self.ind_fig.add_subplot(gs[1, 1])
        Lm = 0.045
        P = 4
        T_e = (3 * P / 4) * Lm * (y[:, 4] * y[:, 1] - y[:, 3] * y[:, 2])
        ax4.plot(t, T_e, 'red', linewidth=2, label='Electromagnetic Torque')
        ax4.axhline(y=self.ind_Tload_var.get(), color='cyan', linestyle='--', linewidth=2, label='Load Torque')
        ax4.set_xlabel('Time (s)', color='white')
        ax4.set_ylabel('Torque (Nm)', color='white')
        ax4.set_title('Torque Response', color='white', fontweight='bold')
        ax4.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax4.grid(True, alpha=0.3, color='white')
        ax4.set_facecolor('#2b2b2b')
        ax4.tick_params(colors='white')
        self.style_axes(ax4)

        # Plot 5: Total stator current magnitude
        ax5 = self.ind_fig.add_subplot(gs[2, 0])
        i_s = np.sqrt(y[:, 1]**2 + y[:, 2]**2)
        ax5.plot(t, i_s, 'yellow', linewidth=2)
        ax5.set_xlabel('Time (s)', color='white')
        ax5.set_ylabel('|Is| (A)', color='white')
        ax5.set_title('Stator Current Magnitude', color='white', fontweight='bold')
        ax5.grid(True, alpha=0.3, color='white')
        ax5.set_facecolor('#2b2b2b')
        ax5.tick_params(colors='white')
        self.style_axes(ax5)

        # Plot 6: Speed vs Torque characteristic
        ax6 = self.ind_fig.add_subplot(gs[2, 1])
        ax6.plot(T_e, rpm, 'lime', linewidth=2)
        ax6.scatter(T_e[0], rpm[0], color='cyan', s=100, marker='o', label='Start', zorder=5)
        ax6.scatter(T_e[-1], rpm[-1], color='red', s=100, marker='s', label='Steady State', zorder=5)
        ax6.set_xlabel('Torque (Nm)', color='white')
        ax6.set_ylabel('Speed (RPM)', color='white')
        ax6.set_title('Speed-Torque Characteristic', color='white', fontweight='bold')
        ax6.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax6.grid(True, alpha=0.3, color='white')
        ax6.set_facecolor('#2b2b2b')
        ax6.tick_params(colors='white')
        self.style_axes(ax6)

        self.ind_canvas.draw()

    def style_axes(self, ax):
        """Apply consistent styling to axes"""
        for spine in ax.spines.values():
            spine.set_color('white')

    def stop_simulation(self):
        """Stop running simulation"""
        self.simulation_running = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self.status_bar.config(text="Simulation stopped")

    def reset_simulation(self, machine_type):
        """Reset simulation"""
        self.machine_simulator.reset_state()

        if machine_type == 'synchronous':
            self.sync_fig.clear()
            self.sync_canvas.draw()
            self.sync_start_btn.config(state=tk.NORMAL)
            self.sync_stop_btn.config(state=tk.DISABLED)
        else:
            self.ind_fig.clear()
            self.ind_canvas.draw()
            self.ind_start_btn.config(state=tk.NORMAL)
            self.ind_stop_btn.config(state=tk.DISABLED)

        self.status_bar.config(text=f"{machine_type.capitalize()} simulation reset")

    def reset_all(self):
        """Reset all simulations"""
        self.reset_simulation('synchronous')
        self.reset_simulation('induction')
        self.pf_results_text.delete(1.0, tk.END)
        self.pf_fig.clear()
        self.pf_canvas.draw()
        self.status_bar.config(text="All simulations reset")

    def on_resize(self, event):
        """Handle window resize for auto-scaling"""
        # This is automatically handled by grid weight configuration
        pass

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Electrical Engineering Lab
Version 1.0

Features:
• Power Factor Correction Calculator
• Synchronous Machine Dynamic Simulation
• Induction Motor Dynamic Simulation
• ODE Solvers: RK45 (Runge-Kutta) & Euler
• Real-time Visualization
• Auto-scaling GUI

Developed for practical electrical engineering applications.
        """
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    app = AdvancedElectricalLab()
    app.mainloop()


if __name__ == "__main__":
    main()
