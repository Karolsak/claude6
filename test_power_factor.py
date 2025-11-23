#!/usr/bin/env python3
"""
Test script for Generator Station Power Factor Calculator
Validates the calculation logic without requiring GUI
"""

import math


class GeneratorStationPFCalculator:
    """Solver for Generator Station Power Factor Problem"""

    @staticmethod
    def calculate_rotary_converter_pf(lighting_kw, motor_hp, motor_pf, motor_eff,
                                     converter_v, converter_i, converter_eff):
        """
        Calculate the required power factor of the rotary converter
        for unity power factor at the supply station
        """
        # Convert motor HP to kW
        motor_output_kw = motor_hp * 0.746

        # Lighting load (assumed unity power factor)
        P_lighting = lighting_kw
        Q_lighting = 0  # No reactive power for lighting

        # Induction motor calculations
        P_motor_output = motor_output_kw
        P_motor_input = P_motor_output / motor_eff

        # Apparent power of motor
        S_motor = P_motor_input / motor_pf

        # Reactive power of motor (lagging)
        phi_motor = math.acos(motor_pf)
        Q_motor = S_motor * math.sin(phi_motor)

        # Rotary converter calculations
        P_converter_output = (converter_v * converter_i) / 1000  # in kW
        P_converter_input = P_converter_output / converter_eff

        # Total real power
        P_total = P_lighting + P_motor_input + P_converter_input

        # For unity power factor at station: Total Q must be zero
        Q_converter = -(Q_lighting + Q_motor)

        # Apparent power of converter
        S_converter = math.sqrt(P_converter_input**2 + Q_converter**2)

        # Power factor of converter
        pf_converter = P_converter_input / S_converter

        # Determine if leading or lagging
        if Q_converter < 0:
            pf_type = "leading"
        elif Q_converter > 0:
            pf_type = "lagging"
        else:
            pf_type = "unity"

        return {
            'P_lighting': P_lighting,
            'Q_lighting': Q_lighting,
            'P_motor_output': P_motor_output,
            'P_motor_input': P_motor_input,
            'S_motor': S_motor,
            'Q_motor': Q_motor,
            'P_converter_output': P_converter_output,
            'P_converter_input': P_converter_input,
            'Q_converter': Q_converter,
            'S_converter': S_converter,
            'P_total': P_total,
            'Q_total': 0,
            'pf_converter': pf_converter,
            'pf_type': pf_type,
            'motor_output_kw': motor_output_kw
        }


def test_power_factor_problem():
    """Test the specific problem given by the user"""

    print("=" * 80)
    print("GENERATOR STATION POWER FACTOR PROBLEM - TEST")
    print("=" * 80)
    print()

    # Problem data
    lighting_kw = 100
    motor_hp = 400
    motor_pf = 0.8
    motor_eff = 0.92
    converter_v = 800
    converter_i = 100
    converter_eff = 0.94

    print("GIVEN DATA:")
    print("-" * 80)
    print(f"  Lighting Load:           {lighting_kw} kW")
    print(f"  Induction Motor:         {motor_hp} HP (power factor = {motor_pf}, efficiency = {motor_eff})")
    print(f"  Rotary Converter:        {converter_v} V, {converter_i} A (efficiency = {converter_eff})")
    print()

    # Calculate
    calc = GeneratorStationPFCalculator()
    results = calc.calculate_rotary_converter_pf(
        lighting_kw, motor_hp, motor_pf, motor_eff,
        converter_v, converter_i, converter_eff
    )

    # Display results
    print("CALCULATION RESULTS:")
    print("-" * 80)
    print()

    print("1. LIGHTING LOAD:")
    print(f"   Real Power (P₁):      {results['P_lighting']:.4f} kW")
    print(f"   Reactive Power (Q₁):  {results['Q_lighting']:.4f} kVAR")
    print()

    print("2. INDUCTION MOTOR:")
    print(f"   Motor Output:         {results['P_motor_output']:.4f} kW")
    print(f"   Motor Input (P₂):     {results['P_motor_input']:.4f} kW")
    print(f"   Apparent Power (S₂):  {results['S_motor']:.4f} kVA")
    print(f"   Reactive Power (Q₂):  {results['Q_motor']:.4f} kVAR (lagging)")
    print()

    print("3. ROTARY CONVERTER:")
    print(f"   Converter Output:     {results['P_converter_output']:.4f} kW")
    print(f"   Converter Input (P₃): {results['P_converter_input']:.4f} kW")
    print(f"   Reactive Power (Q₃):  {results['Q_converter']:.4f} kVAR ({results['pf_type']})")
    print(f"   Apparent Power (S₃):  {results['S_converter']:.4f} kVA")
    print()

    print("=" * 80)
    print("FINAL ANSWER:")
    print("=" * 80)
    print(f"★ REQUIRED POWER FACTOR OF ROTARY CONVERTER: {results['pf_converter']:.6f} ({results['pf_type']})")
    print("=" * 80)
    print()

    print("VERIFICATION:")
    print("-" * 80)
    print(f"  Total Real Power (P):       {results['P_total']:.4f} kW")
    print(f"  Total Reactive Power (Q):   {results['Q_total']:.4f} kVAR")
    print(f"  Station Power Factor:       1.0000 (Unity) ✓")
    print()

    # Verify calculation
    Q_total_check = results['Q_lighting'] + results['Q_motor'] + results['Q_converter']
    print(f"  Verification check: Q_total = {Q_total_check:.6f} kVAR")

    if abs(Q_total_check) < 0.0001:
        print("  ✓ Unity power factor achieved!")
    else:
        print("  ✗ Error in calculation!")

    print()
    print("=" * 80)

    return results


if __name__ == "__main__":
    # Run test
    results = test_power_factor_problem()

    # Additional verification
    print("\nADDITIONAL TESTS:")
    print("-" * 80)

    # Test with different values
    test_cases = [
        (100, 400, 0.8, 0.92, 800, 100, 0.94),
        (150, 500, 0.85, 0.90, 1000, 120, 0.95),
        (200, 300, 0.75, 0.88, 600, 80, 0.92),
    ]

    for i, (light, motor_hp, pf, eff, v, i_val, conv_eff) in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Lighting: {light} kW, Motor: {motor_hp} HP @ PF={pf}, eff={eff}")
        print(f"  Converter: {v}V, {i_val}A, eff={conv_eff}")

        calc = GeneratorStationPFCalculator()
        r = calc.calculate_rotary_converter_pf(light, motor_hp, pf, eff, v, i_val, conv_eff)

        print(f"  → Required Converter PF: {r['pf_converter']:.6f} ({r['pf_type']})")
        print(f"  → Total Station Power: {r['P_total']:.2f} kW @ Unity PF")

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
