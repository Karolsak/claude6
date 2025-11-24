#!/usr/bin/env python3
"""
Test script to verify alternator calculations
"""

import numpy as np
import cmath


def calculate_problem_9_15():
    """Test Problem 9.15"""
    print("=" * 60)
    print("PROBLEM 9.15")
    print("=" * 60)

    # Given data
    Ra = 0.15  # Armature resistance (Ω)
    Eoc = 60  # Open circuit voltage (V)
    Isc = 150  # Short circuit current (A)
    Vt = 200  # Terminal voltage (V)
    Ia = 90  # Armature current (A)
    pf = 0.8  # Power factor (lagging)

    # Calculate synchronous impedance
    Zs = Eoc / Isc
    print(f"\n1. Synchronous Impedance:")
    print(f"   Zs = Eoc / Isc = {Eoc} / {Isc} = {Zs:.4f} Ω")

    # Calculate synchronous reactance
    Xs = np.sqrt(Zs**2 - Ra**2)
    print(f"\n2. Synchronous Reactance:")
    print(f"   Xs = √(Zs² - Ra²)")
    print(f"   Xs = √({Zs}² - {Ra}²)")
    print(f"   Xs = √({Zs**2:.6f} - {Ra**2:.6f})")
    print(f"   Xs = √{Zs**2 - Ra**2:.6f}")
    print(f"   Xs = {Xs:.4f} Ω")

    # Calculate no-load voltage (internal EMF)
    phi = np.arccos(pf)  # Power factor angle (lagging)
    print(f"\n3. No-Load Voltage (Internal EMF):")
    print(f"   Power factor angle: φ = arccos({pf}) = {np.degrees(phi):.2f}°")

    # Phasor calculation
    Vt_complex = complex(Vt, 0)  # Terminal voltage (reference)
    Ia_complex = Ia * complex(np.cos(-phi), np.sin(-phi))  # Current (lagging)
    Z_complex = complex(Ra, Xs)  # Impedance

    print(f"   Vt = {Vt} ∠ 0° V (reference)")
    print(f"   Ia = {Ia} ∠ {-np.degrees(phi):.2f}° A")
    print(f"   Ia = {Ia_complex.real:.2f} - j{abs(Ia_complex.imag):.2f} A")

    # Voltage drop
    voltage_drop = Ia_complex * Z_complex
    print(f"\n   Voltage drop = Ia × Z = Ia × (Ra + jXs)")
    print(f"   Voltage drop = {voltage_drop.real:.2f} + j{voltage_drop.imag:.2f} V")

    # Internal EMF
    E_complex = Vt_complex + voltage_drop
    E_magnitude = abs(E_complex)
    E_angle = np.degrees(cmath.phase(E_complex))

    print(f"\n   E = Vt + Ia×Z")
    print(f"   E = {E_complex.real:.2f} + j{E_complex.imag:.2f} V")
    print(f"   E = {E_magnitude:.2f} ∠ {E_angle:.2f}° V")

    # Additional calculations
    apparent_power = Vt * Ia
    real_power = Vt * Ia * pf
    reactive_power = Vt * Ia * np.sqrt(1 - pf**2)

    print(f"\n4. Power Calculations:")
    print(f"   Apparent Power (S) = {apparent_power:.2f} VA")
    print(f"   Real Power (P) = {real_power:.2f} W")
    print(f"   Reactive Power (Q) = {reactive_power:.2f} VAR (lagging)")

    print("\n" + "=" * 60)
    print("SUMMARY - Problem 9.15:")
    print("=" * 60)
    print(f"Synchronous Impedance (Zs):     {Zs:.4f} Ω")
    print(f"Synchronous Reactance (Xs):     {Xs:.4f} Ω")
    print(f"No-Load Voltage per phase (E):  {E_magnitude:.2f} V")
    print(f"Load Angle (δ):                 {E_angle:.2f}°")
    print("=" * 60)

    return Zs, Xs, E_magnitude, E_angle


def calculate_problem_9_16():
    """Test Problem 9.16"""
    print("\n\n")
    print("=" * 60)
    print("PROBLEM 9.16")
    print("=" * 60)

    # Given data
    Ra = 0.35  # Armature resistance (Ω)
    Eoc = 500  # Open circuit voltage (V)
    Isc = 180  # Short circuit current (A)
    Vt = 220  # Terminal voltage (V)
    Ia = 60  # Armature current (A)
    pf = 0.85  # Power factor (leading)

    # Calculate synchronous impedance
    Zs = Eoc / Isc
    print(f"\n1. Synchronous Impedance:")
    print(f"   Zs = Eoc / Isc = {Eoc} / {Isc} = {Zs:.4f} Ω")

    # Calculate synchronous reactance
    Xs = np.sqrt(Zs**2 - Ra**2)
    print(f"\n2. Synchronous Reactance:")
    print(f"   Xs = √(Zs² - Ra²)")
    print(f"   Xs = √({Zs}² - {Ra}²)")
    print(f"   Xs = √({Zs**2:.6f} - {Ra**2:.6f})")
    print(f"   Xs = √{Zs**2 - Ra**2:.6f}")
    print(f"   Xs = {Xs:.4f} Ω")

    # Calculate no-load voltage (internal EMF)
    phi = np.arccos(pf)  # Power factor angle (leading)
    print(f"\n3. No-Load Voltage (Internal EMF):")
    print(f"   Power factor angle: φ = arccos({pf}) = {np.degrees(phi):.2f}°")
    print(f"   Note: Current is LEADING (φ is positive in phasor)")

    # Phasor calculation
    Vt_complex = complex(Vt, 0)  # Terminal voltage (reference)
    Ia_complex = Ia * complex(np.cos(phi), np.sin(phi))  # Current (leading)
    Z_complex = complex(Ra, Xs)  # Impedance

    print(f"   Vt = {Vt} ∠ 0° V (reference)")
    print(f"   Ia = {Ia} ∠ +{np.degrees(phi):.2f}° A (leading)")
    print(f"   Ia = {Ia_complex.real:.2f} + j{Ia_complex.imag:.2f} A")

    # Voltage drop
    voltage_drop = Ia_complex * Z_complex
    print(f"\n   Voltage drop = Ia × Z = Ia × (Ra + jXs)")
    print(f"   Voltage drop = {voltage_drop.real:.2f} + j{voltage_drop.imag:.2f} V")

    # Internal EMF
    E_complex = Vt_complex + voltage_drop
    E_magnitude = abs(E_complex)
    E_angle = np.degrees(cmath.phase(E_complex))

    print(f"\n   E = Vt + Ia×Z")
    print(f"   E = {E_complex.real:.2f} + j{E_complex.imag:.2f} V")
    print(f"   E = {E_magnitude:.2f} ∠ {E_angle:.2f}° V")

    # Additional calculations
    apparent_power = Vt * Ia
    real_power = Vt * Ia * pf
    reactive_power = Vt * Ia * np.sqrt(1 - pf**2)

    print(f"\n4. Power Calculations:")
    print(f"   Apparent Power (S) = {apparent_power:.2f} VA")
    print(f"   Real Power (P) = {real_power:.2f} W")
    print(f"   Reactive Power (Q) = {reactive_power:.2f} VAR (leading)")

    print("\n" + "=" * 60)
    print("SUMMARY - Problem 9.16:")
    print("=" * 60)
    print(f"Synchronous Impedance (Zs):     {Zs:.4f} Ω")
    print(f"Synchronous Reactance (Xs):     {Xs:.4f} Ω")
    print(f"No-Load Voltage per phase (E):  {E_magnitude:.2f} V")
    print(f"Load Angle (δ):                 {E_angle:.2f}°")
    print("=" * 60)

    return Zs, Xs, E_magnitude, E_angle


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("ALTERNATOR IMPEDANCE CALCULATION TEST")
    print("=" * 60)

    # Test Problem 9.15
    Zs_1, Xs_1, E_1, angle_1 = calculate_problem_9_15()

    # Test Problem 9.16
    Zs_2, Xs_2, E_2, angle_2 = calculate_problem_9_16()

    # Comparison
    print("\n\n")
    print("=" * 60)
    print("COMPARISON OF RESULTS")
    print("=" * 60)
    print("\nParameter              Problem 9.15    Problem 9.16")
    print("-" * 60)
    print(f"Zs (Ω)                 {Zs_1:8.4f}        {Zs_2:8.4f}")
    print(f"Xs (Ω)                 {Xs_1:8.4f}        {Xs_2:8.4f}")
    print(f"E (V)                  {E_1:8.2f}        {E_2:8.2f}")
    print(f"δ (degrees)            {angle_1:8.2f}        {angle_2:8.2f}")
    print(f"Power Factor Type      Lagging         Leading")
    print("=" * 60)

    print("\n✅ All calculations completed successfully!")
    print("\nKey Observations:")
    print("1. Problem 9.15 (lagging pf): Higher EMF due to demagnetizing effect")
    print("2. Problem 9.16 (leading pf): Lower EMF due to magnetizing effect")
    print("3. Leading power factor reduces excitation requirements")
    print("4. Load angle is positive for both (generating mode)")


if __name__ == "__main__":
    main()
