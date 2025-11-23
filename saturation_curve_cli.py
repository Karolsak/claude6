#!/usr/bin/env python3
"""
DC Generator Saturation Curve Analyzer - Command Line Version
Solves all parts of the saturation curve problem and performs analysis
"""

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


class SaturationCurveAnalyzerCLI:
    """Command-line version for headless environments"""

    def __init__(self):
        # Original data at 1800 rpm
        self.Eg_1800 = np.array([8, 40, 74, 113, 152, 213, 234, 248, 266, 278])
        self.If_original = np.array([0, 0.5, 1.0, 1.5, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0])
        self.N_original = 1800  # rpm

    def get_interpolation_function(self, speed):
        """Create interpolation function for given speed"""
        Eg_adjusted = self.Eg_1800 * (speed / self.N_original)
        interpolator = UnivariateSpline(self.If_original, Eg_adjusted, s=0, k=3)
        return interpolator

    def calculate_voltage_at_current(self, field_current, speed):
        """Calculate voltage for given field current and speed"""
        interpolator = self.get_interpolation_function(speed)

        if field_current < self.If_original[0]:
            return float(interpolator(self.If_original[0]))
        elif field_current > self.If_original[-1]:
            return float(interpolator(self.If_original[-1]))
        else:
            return float(interpolator(field_current))

    def calculate_field_current_for_voltage(self, target_voltage, speed):
        """Calculate required field current for target voltage at given speed"""
        interpolator = self.get_interpolation_function(speed)

        If_range = np.linspace(self.If_original[0], self.If_original[-1], 1000)
        Eg_range = interpolator(If_range)

        idx = np.argmin(np.abs(Eg_range - target_voltage))
        return float(If_range[idx])

    def solve_part_a(self):
        """Part (a): Plot saturation curve at 1500 rpm"""
        print("\n" + "=" * 70)
        print("PART (a): Saturation Curve at 1500 rpm")
        print("=" * 70)

        N_1500 = 1500
        Eg_1500 = self.Eg_1800 * (N_1500 / self.N_original)

        print(f"\nSpeed scaling: Eg(1500) = Eg(1800) × ({N_1500}/{self.N_original})")
        print(f"Scaling factor: {N_1500/self.N_original:.4f}\n")

        print(f"{'If (A)':<10} {'Eg @ 1800rpm (V)':<20} {'Eg @ 1500rpm (V)':<20}")
        print("-" * 70)
        for i in range(len(self.If_original)):
            print(f"{self.If_original[i]:<10.1f} {self.Eg_1800[i]:<20.1f} {Eg_1500[i]:<20.1f}")

        # Generate plot
        self.plot_saturation_curves([1800, 1500], 'part_a_saturation_curves.png')
        print("\n✓ Plot saved as: part_a_saturation_curves.png")

    def solve_part_b(self):
        """Part (b): Calculate voltage at 1000 rpm with If = 4.6 A"""
        print("\n" + "=" * 70)
        print("PART (b): Generated Voltage at 1000 rpm, If = 4.6 A")
        print("=" * 70)

        If_b = 4.6
        speed_b = 1000
        voltage_b = self.calculate_voltage_at_current(If_b, speed_b)

        print(f"\nField Current: {If_b} A")
        print(f"Speed: {speed_b} rpm")
        print(f"\nGenerated Voltage: {voltage_b:.2f} V")

        # Show interpolation steps
        print("\nCalculation steps:")
        print(f"1. Scale saturation curve to {speed_b} rpm")
        print(f"   Eg({speed_b}) = Eg({self.N_original}) × ({speed_b}/{self.N_original})")
        print(f"2. Interpolate at If = {If_b} A using cubic spline")
        print(f"3. Result: {voltage_b:.2f} V")

    def solve_part_c(self):
        """Part (c): Calculate field current for 120V at 900 rpm"""
        print("\n" + "=" * 70)
        print("PART (c): Field Current for 120V at 900 rpm")
        print("=" * 70)

        target_voltage_c = 120
        speed_c = 900
        If_c = self.calculate_field_current_for_voltage(target_voltage_c, speed_c)

        # Verify
        voltage_achieved = self.calculate_voltage_at_current(If_c, speed_c)

        print(f"\nTarget Voltage: {target_voltage_c} V")
        print(f"Speed: {speed_c} rpm")
        print(f"\nRequired Field Current: {If_c:.3f} A")
        print(f"Achieved Voltage: {voltage_achieved:.2f} V")
        print(f"Error: {abs(voltage_achieved - target_voltage_c):.2f} V")

        print("\nCalculation method:")
        print(f"1. Scale saturation curve to {speed_c} rpm")
        print(f"2. Create inverse function (Eg → If)")
        print(f"3. Find If that produces {target_voltage_c} V")
        print(f"4. Result: If = {If_c:.3f} A")

    def solve_part_d(self):
        """Part (d): No-load voltage at 1500 rpm for shunt generator"""
        print("\n" + "=" * 70)
        print("PART (d): No-load Voltage at 1500 rpm (Shunt Generator)")
        print("=" * 70)

        If_d = 4.6
        speed_d = 1500
        voltage_d = self.calculate_voltage_at_current(If_d, speed_d)

        print(f"\nGenerator Configuration: Shunt Generator")
        print(f"Original Operating Point: 1800 rpm, If = {If_d} A")
        print(f"New Speed: {speed_d} rpm")
        print(f"\nField Current: {If_d} A (constant for shunt generator)")
        print(f"No-load Voltage: {voltage_d:.2f} V")

        # Compare with original
        voltage_original = self.calculate_voltage_at_current(If_d, 1800)
        print(f"\nComparison:")
        print(f"  Voltage at 1800 rpm: {voltage_original:.2f} V")
        print(f"  Voltage at 1500 rpm: {voltage_d:.2f} V")
        print(f"  Ratio: {voltage_d/voltage_original:.4f} (= {speed_d}/{self.N_original})")

    def plot_saturation_curves(self, speeds, filename):
        """Plot saturation curves for multiple speeds"""
        fig, ax = plt.subplots(figsize=(12, 8))

        colors = ['b', 'r', 'g', 'm', 'c']

        for i, speed in enumerate(speeds):
            Eg_scaled = self.Eg_1800 * (speed / self.N_original)

            # Plot data points
            ax.plot(self.If_original, Eg_scaled, 'o-',
                   color=colors[i % len(colors)], linewidth=2,
                   markersize=8, label=f'{speed} rpm', alpha=0.7)

            # Plot smooth interpolation
            If_smooth = np.linspace(self.If_original[0], self.If_original[-1], 200)
            interpolator = self.get_interpolation_function(speed)
            Eg_smooth = interpolator(If_smooth)
            ax.plot(If_smooth, Eg_smooth, '--',
                   color=colors[i % len(colors)], linewidth=1, alpha=0.5)

        ax.set_xlabel('Field Current If (A)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Generated Voltage Eg (V)', fontsize=12, fontweight='bold')
        ax.set_title('DC Generator Saturation Curves at Various Speeds',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best', fontsize=11)

        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()

    def analyze_saturation(self):
        """Magnetic saturation analysis"""
        print("\n" + "=" * 70)
        print("MAGNETIC SATURATION ANALYSIS")
        print("=" * 70)

        # Calculate air-gap line (linear region)
        slope_linear = (self.Eg_1800[1] - self.Eg_1800[0]) / \
                      (self.If_original[1] - self.If_original[0])

        If_analysis = np.linspace(0, 6, 100)
        Eg_airgap = slope_linear * If_analysis
        interpolator = self.get_interpolation_function(1800)
        Eg_actual = interpolator(If_analysis)

        saturation_factor = Eg_actual / (Eg_airgap + 0.001)

        # Find knee point
        diff_saturation = np.diff(saturation_factor)
        knee_idx = np.argmax(diff_saturation < -0.01) if any(diff_saturation < -0.01) else 50

        print(f"\nAir-gap line slope: {slope_linear:.2f} V/A")
        print(f"Knee point at If ≈ {If_analysis[knee_idx]:.2f} A")
        print(f"Voltage at knee: {Eg_actual[knee_idx]:.2f} V")

        print("\nSaturation factors at key field currents:")
        print(f"{'If (A)':<12} {'Eg actual (V)':<16} {'Eg linear (V)':<16} {'Sat. Factor':<12}")
        print("-" * 70)
        for i in [10, 25, 50, 75, 99]:
            print(f"{If_analysis[i]:<12.2f} {Eg_actual[i]:<16.2f} "
                  f"{Eg_airgap[i]:<16.2f} {saturation_factor[i]:<12.3f}")

        # Plot
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(If_analysis, Eg_actual, 'b-', linewidth=3, label='Actual Saturation Curve')
        ax.plot(If_analysis, Eg_airgap, 'r--', linewidth=2, label='Air-gap Line (Linear)')
        ax.plot(If_analysis[knee_idx], Eg_actual[knee_idx], 'go',
               markersize=15, label=f'Knee Point ({If_analysis[knee_idx]:.2f}A)', zorder=5)

        ax.set_xlabel('Field Current (A)', fontweight='bold', fontsize=12)
        ax.set_ylabel('Generated Voltage (V)', fontweight='bold', fontsize=12)
        ax.set_title('Magnetic Saturation Characteristics', fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best', fontsize=11)

        plt.tight_layout()
        plt.savefig('saturation_analysis.png', dpi=150)
        plt.close()

        print("\n✓ Plot saved as: saturation_analysis.png")

    def simulate_dynamic_response(self):
        """Simulate dynamic response using ODE solver"""
        print("\n" + "=" * 70)
        print("DYNAMIC SIMULATION (RK45 ODE Solver)")
        print("=" * 70)

        # Parameters
        N = 1800
        Rf = 50
        Ra = 0.5
        La = 0.01
        Lf = 0.1
        RL = 100

        print(f"\nSimulation Parameters:")
        print(f"  Speed: {N} rpm")
        print(f"  Field Resistance: {Rf} Ω")
        print(f"  Armature Resistance: {Ra} Ω")
        print(f"  Load Resistance: {RL} Ω")
        print(f"  Armature Inductance: {La} H")
        print(f"  Field Inductance: {Lf} H")

        def generator_ode(t, state):
            Vt, If, Ia = state

            # Get generated voltage from saturation curve
            Eg = self.calculate_voltage_at_current(If, N)

            dIf_dt = (Vt - If * Rf) / Lf if Lf > 0 else 0
            dIa_dt = (Eg - Vt - Ia * Ra) / La if La > 0 else 0
            dVt_dt = (Ia * RL - Vt) / 0.1

            return [dVt_dt, dIf_dt, dIa_dt]

        # Initial conditions [Vt, If, Ia]
        initial_state = [10.0, 0.1, 0.1]
        t_span = (0, 10)

        print("\nSolving differential equations...")
        sol = solve_ivp(generator_ode, t_span, initial_state,
                       method='RK45', dense_output=True, max_step=0.01)

        print(f"✓ Simulation complete")
        print(f"  Time points: {len(sol.t)}")
        print(f"  Final terminal voltage: {sol.y[0][-1]:.2f} V")
        print(f"  Final field current: {sol.y[1][-1]:.3f} A")
        print(f"  Final armature current: {sol.y[2][-1]:.3f} A")

        # Plot results
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        ax1.plot(sol.t, sol.y[0], 'b-', linewidth=2)
        ax1.set_ylabel('Terminal Voltage (V)', fontweight='bold', fontsize=11)
        ax1.set_title('Dynamic Response - Terminal Voltage', fontweight='bold', fontsize=12)
        ax1.grid(True, alpha=0.3)

        ax2.plot(sol.t, sol.y[2], 'r-', linewidth=2)
        ax2.set_xlabel('Time (s)', fontweight='bold', fontsize=11)
        ax2.set_ylabel('Armature Current (A)', fontweight='bold', fontsize=11)
        ax2.set_title('Dynamic Response - Armature Current', fontweight='bold', fontsize=12)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('dynamic_response.png', dpi=150)
        plt.close()

        print("✓ Plot saved as: dynamic_response.png")

    def run_all_analyses(self):
        """Run all analyses"""
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 12 + "DC GENERATOR SATURATION CURVE ANALYZER" + " " * 18 + "║")
        print("║" + " " * 20 + "Complete Analysis Suite" + " " * 25 + "║")
        print("╚" + "═" * 68 + "╝")

        # Solve all parts
        self.solve_part_a()
        self.solve_part_b()
        self.solve_part_c()
        self.solve_part_d()

        # Advanced analyses
        self.analyze_saturation()
        self.simulate_dynamic_response()

        # Summary
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print("\n✓ All calculations completed successfully")
        print("✓ All plots generated and saved")
        print("\nGenerated files:")
        print("  - part_a_saturation_curves.png")
        print("  - saturation_analysis.png")
        print("  - dynamic_response.png")
        print("\n" + "=" * 70 + "\n")


def main():
    """Main entry point"""
    analyzer = SaturationCurveAnalyzerCLI()
    analyzer.run_all_analyses()


if __name__ == "__main__":
    main()
