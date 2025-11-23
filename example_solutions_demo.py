#!/usr/bin/env python3
"""
Demo script showing solutions to Examples 50.74 and 50.75
without requiring GUI - runs in terminal
"""

def solve_example_50_74():
    """
    Example 50.74: Tariff Comparison
    
    A supply undertaking is offering two tariffs:
    Tariff A: Lighting: 20 paise/unit; Power: 5 paise/unit; Meter rent: 30 paise/month
    Tariff B: 12% on rateable value + 3 paise/unit for all purposes
    
    Given: Annual rateable value = Rs 2,500
           Monthly lighting consumption = 40 units
    
    Find: Domestic power consumption that makes both tariffs equal
    """
    print("=" * 80)
    print("EXAMPLE 50.74: ELECTRICITY TARIFF COMPARISON")
    print("=" * 80)
    
    # Given data
    annual_rateable = 2500  # Rs
    lighting_units = 40     # units per month
    
    print("\nGIVEN DATA:")
    print(f"  Annual Rateable Value: Rs {annual_rateable}")
    print(f"  Monthly Lighting Consumption: {lighting_units} units")
    
    print("\nTARIFF STRUCTURES:")
    print("  Tariff A:")
    print("    • Lighting: 20 paise per unit")
    print("    • Domestic Power: 5 paise per unit")
    print("    • Meter Rent: 30 paise per month")
    print("\n  Tariff B:")
    print("    • Fixed Charge: 12% of annual rateable value")
    print("    • Energy Charge: 3 paise per unit (all purposes)")
    
    # Tariff B monthly fixed cost
    tariff_b_fixed_monthly = (0.12 * annual_rateable) / 12
    print(f"\n  Tariff B Monthly Fixed: Rs {tariff_b_fixed_monthly:.2f}")
    
    # Set up equation
    print("\nCALCULATION:")
    print("  Let x = domestic power consumption (units/month)")
    print("\n  Tariff A total cost = 0.20×40 + 0.05×x + 0.30")
    print(f"                      = 8 + 0.05x + 0.30")
    print(f"                      = 8.30 + 0.05x")
    
    print(f"\n  Tariff B total cost = {tariff_b_fixed_monthly:.2f} + 0.03×(40 + x)")
    print(f"                      = {tariff_b_fixed_monthly:.2f} + 1.20 + 0.03x")
    print(f"                      = {tariff_b_fixed_monthly + 1.20:.2f} + 0.03x")
    
    print("\n  Setting them equal:")
    print(f"  8.30 + 0.05x = {tariff_b_fixed_monthly + 1.20:.2f} + 0.03x")
    print(f"  0.05x - 0.03x = {tariff_b_fixed_monthly + 1.20:.2f} - 8.30")
    print(f"  0.02x = {tariff_b_fixed_monthly + 1.20 - 8.30:.2f}")
    
    # Solve for x
    x = (tariff_b_fixed_monthly + 1.20 - 8.30) / 0.02
    
    print(f"  x = {x:.2f} units")
    
    print("\n" + "=" * 80)
    print(f"ANSWER: {x:.2f} units of domestic power consumption makes both tariffs equal")
    print("=" * 80)
    
    # Verification
    print("\nVERIFICATION:")
    cost_a = 0.20 * lighting_units + 0.05 * x + 0.30
    cost_b = tariff_b_fixed_monthly + 0.03 * (lighting_units + x)
    print(f"  Tariff A cost at {x:.2f} units: Rs {cost_a:.2f}")
    print(f"  Tariff B cost at {x:.2f} units: Rs {cost_b:.2f}")
    print(f"  Difference: Rs {abs(cost_a - cost_b):.4f}")
    
    return x


def solve_example_50_75():
    """
    Example 50.75: Equipment Cost Analysis
    
    Transformers: Rs 12 per kVA, efficiency 98%
    LT Motors: Rs 24 per kW, efficiency 90%
    HT Motors: efficiency 89%
    
    Load factor: 30%
    Energy cost: 7 paise per kWh
    Interest & depreciation: 8%
    
    Find: Maximum price per kW for HT motor
    """
    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 50.75: EQUIPMENT COST ANALYSIS")
    print("=" * 80)
    
    # Given data
    transformer_price_per_kva = 12  # Rs
    lt_motor_price_per_kw = 24      # Rs
    transformer_eff = 0.98          # 98%
    lt_motor_eff = 0.90             # 90%
    ht_motor_eff = 0.89             # 89%
    load_factor = 0.30              # 30%
    energy_cost_paise = 7           # paise per kWh
    interest_rate = 0.08            # 8%
    
    print("\nGIVEN DATA:")
    print(f"  Transformer Price: Rs {transformer_price_per_kva} per kVA")
    print(f"  LT Motor Price: Rs {lt_motor_price_per_kw} per kW")
    print(f"  Transformer Efficiency: {transformer_eff*100}%")
    print(f"  LT Motor Efficiency: {lt_motor_eff*100}%")
    print(f"  HT Motor Efficiency: {ht_motor_eff*100}%")
    print(f"  Annual Load Factor: {load_factor*100}%")
    print(f"  Energy Cost: {energy_cost_paise} paise per kWh")
    print(f"  Interest & Depreciation: {interest_rate*100}%")
    
    print("\nCALCULATION (for 1 kW output):")
    print("\nLOW-TENSION SYSTEM (Transformer + LT Motor):")
    
    # Input to LT motor
    input_to_lt_motor = 1.0 / lt_motor_eff
    print(f"  Input to LT Motor = 1 / {lt_motor_eff} = {input_to_lt_motor:.4f} kW")
    
    # Input to transformer
    transformer_input = input_to_lt_motor / transformer_eff
    print(f"  Input to Transformer = {input_to_lt_motor:.4f} / {transformer_eff}")
    print(f"                       = {transformer_input:.4f} kVA")
    
    # Capital costs
    transformer_cost = transformer_price_per_kva * transformer_input
    lt_motor_cost = lt_motor_price_per_kw * 1.0
    lt_system_capital = transformer_cost + lt_motor_cost
    
    print(f"\n  Capital Costs:")
    print(f"    Transformer: {transformer_price_per_kva} × {transformer_input:.4f} = Rs {transformer_cost:.2f}")
    print(f"    LT Motor: {lt_motor_price_per_kw} × 1 = Rs {lt_motor_cost:.2f}")
    print(f"    Total Capital: Rs {lt_system_capital:.2f}")
    
    # Annual charges
    lt_annual_fixed = interest_rate * lt_system_capital
    print(f"\n  Annual Fixed Charges ({interest_rate*100}%): Rs {lt_annual_fixed:.2f}")
    
    # Energy consumption
    annual_hours = 8760 * load_factor
    lt_energy_consumption = transformer_input * annual_hours
    lt_annual_energy_cost = lt_energy_consumption * energy_cost_paise / 100
    
    print(f"\n  Annual Energy Cost:")
    print(f"    Operating Hours: 8760 × {load_factor} = {annual_hours:.0f} hrs")
    print(f"    Energy Consumption: {transformer_input:.4f} × {annual_hours:.0f} = {lt_energy_consumption:.2f} kWh")
    print(f"    Energy Cost: {lt_energy_consumption:.2f} × {energy_cost_paise}/100 = Rs {lt_annual_energy_cost:.2f}")
    
    lt_total_annual = lt_annual_fixed + lt_annual_energy_cost
    print(f"\n  Total Annual Cost (LT System): Rs {lt_total_annual:.2f}")
    
    print("\nHIGH-TENSION MOTOR SYSTEM:")
    
    # HT motor input
    ht_input = 1.0 / ht_motor_eff
    print(f"  Input Required: 1 / {ht_motor_eff} = {ht_input:.4f} kW")
    
    # Energy consumption
    ht_energy_consumption = ht_input * annual_hours
    ht_annual_energy_cost = ht_energy_consumption * energy_cost_paise / 100
    
    print(f"\n  Annual Energy Cost:")
    print(f"    Energy Consumption: {ht_input:.4f} × {annual_hours:.0f} = {ht_energy_consumption:.2f} kWh")
    print(f"    Energy Cost: {ht_energy_consumption:.2f} × {energy_cost_paise}/100 = Rs {ht_annual_energy_cost:.2f}")
    
    print("\n  For equal annual cost:")
    print(f"    Interest × Price + {ht_annual_energy_cost:.2f} = {lt_total_annual:.2f}")
    print(f"    {interest_rate} × Price = {lt_total_annual:.2f} - {ht_annual_energy_cost:.2f}")
    print(f"    {interest_rate} × Price = {lt_total_annual - ht_annual_energy_cost:.2f}")
    
    # Calculate HT motor price
    ht_motor_price = (lt_total_annual - ht_annual_energy_cost) / interest_rate
    
    print(f"    Price = {lt_total_annual - ht_annual_energy_cost:.2f} / {interest_rate}")
    print(f"    Price = Rs {ht_motor_price:.2f} per kW")
    
    print("\n" + "=" * 80)
    print(f"ANSWER: Maximum price for HT motor = Rs {ht_motor_price:.2f} per kW")
    print("=" * 80)
    
    print("\nCOMPARISON:")
    print(f"  LT System Capital Cost: Rs {lt_system_capital:.2f} per kW")
    print(f"  HT System Capital Cost: Rs {ht_motor_price:.2f} per kW")
    print(f"  Difference: Rs {lt_system_capital - ht_motor_price:.2f} per kW")
    print(f"  Percentage: {(lt_system_capital - ht_motor_price)/lt_system_capital*100:.2f}%")
    
    print("\nThe HT motor can cost MORE initially because it saves on:")
    print("  1. Transformer cost (not needed)")
    print("  2. Better efficiency reduces energy costs over lifetime")
    
    return ht_motor_price


def main():
    """Run both example solutions"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "ELECTRICAL ENGINEERING PROBLEM SOLUTIONS" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Solve Example 50.74
    result_74 = solve_example_50_74()
    
    # Solve Example 50.75
    result_75 = solve_example_50_75()
    
    print("\n\n")
    print("=" * 80)
    print("SUMMARY OF RESULTS")
    print("=" * 80)
    print(f"\nExample 50.74: Break-even domestic power = {result_74:.2f} units/month")
    print(f"Example 50.75: HT motor maximum price = Rs {result_75:.2f} per kW")
    print("\n" + "=" * 80)
    print("\nFor interactive simulations and visualizations, run:")
    print("  python3 electrical_engineering_lab.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
