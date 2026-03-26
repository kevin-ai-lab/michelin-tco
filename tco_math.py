def calculate_hardware_cost_per_truck(price, casing_value, life_miles, annual_miles, tires_per_truck):
    """Pillar 1: Hardware Cost Per Mile (CPM)"""
    if life_miles <= 0:
        return 0
    cpm = (price - casing_value) / life_miles
    return cpm * annual_miles * tires_per_truck

def calculate_fuel_cost_per_truck(mpg, annual_miles, fuel_price, fuel_improvement_pct=0):
    """Pillar 2: Fuel Consumption Impact"""
    if mpg <= 0:
        return 0
    
    # Safety check if UI passes '5' instead of '0.05'
    if fuel_improvement_pct > 1:
        fuel_improvement_pct = fuel_improvement_pct / 100.0
        
    effective_mpg = mpg * (1 + fuel_improvement_pct)
    return (annual_miles / effective_mpg) * fuel_price

def calculate_downtime_cost_per_truck(annual_events, event_cost, downtime_hours, downtime_rate):
    """Pillar 3: Downtime & Roadside Assistance"""
    return annual_events * (event_cost + (downtime_hours * downtime_rate))

def calculate_tco(fleet_data, comp_tire, mich_tire):
    """
    Aggregates the three pillars (Hardware, Fuel, Downtime) into final executive metrics.
    """
    # 1. Competitor Base Cost
    comp_hardware = calculate_hardware_cost_per_truck(
        comp_tire['price'], comp_tire['casingValue'], comp_tire['lifeMiles'], 
        fleet_data['annualMiles'], fleet_data['tiresPerTruck']
    )
    comp_fuel = calculate_fuel_cost_per_truck(
        fleet_data['mpg'], fleet_data['annualMiles'], fleet_data['fuelPrice'], 0
    )
    comp_downtime = calculate_downtime_cost_per_truck(
        comp_tire['annualEvents'], comp_tire['eventCost'], 
        fleet_data['downtimeHoursPerEvent'], fleet_data['downtimeCostPerHour']
    )
    comp_tco = comp_hardware + comp_fuel + comp_downtime

    # 2. Michelin Proposed Cost
    mich_hardware = calculate_hardware_cost_per_truck(
        mich_tire['price'], mich_tire['casingValue'], mich_tire['lifeMiles'], 
        fleet_data['annualMiles'], fleet_data['tiresPerTruck']
    )
    mich_fuel = calculate_fuel_cost_per_truck(
        fleet_data['mpg'], fleet_data['annualMiles'], fleet_data['fuelPrice'], 
        mich_tire.get('fuelImprovementPct', 0)
    )
    mich_downtime = calculate_downtime_cost_per_truck(
        mich_tire['annualEvents'], mich_tire['eventCost'], 
        fleet_data['downtimeHoursPerEvent'], fleet_data['downtimeCostPerHour']
    )
    
    mich_tco = mich_hardware + mich_fuel + mich_downtime

    # 3. Final Savings & ROI Math
    # Calculate pure Amortized Annual Savings internally for accurate Break Even math
    amortized_annual_savings = comp_tco - mich_tco
    upfront_delta_per_truck = (mich_tire['price'] - comp_tire['price']) * fleet_data['tiresPerTruck']
    
    # Redefine dashboard KPIs to represent Year 1 Net Cash (to explicitly match the waterfall chart)
    # Year 1 Net Cash = Operating Savings - Upfront Michelin Premium Cash Outlay
    annual_savings_per_truck = amortized_annual_savings - upfront_delta_per_truck
    fleet_savings = annual_savings_per_truck * fleet_data['numTrucks']
    savings_per_mile = annual_savings_per_truck / fleet_data['annualMiles'] if fleet_data['annualMiles'] > 0 else 0
    
    # Break-Even Math updated to perfectly align with the Chart's 3 penalty blocks
    # by using total annualized savings (Hardware + Fuel + Downtime)
    total_savings_per_mile = amortized_annual_savings / fleet_data['annualMiles'] if fleet_data['annualMiles'] > 0 else 0

    # Safe Break-Even Edge Cases
    if upfront_delta_per_truck <= 0:
        # Michelin is cheaper or equal upfront; instant ROI
        break_even_miles = 0 
    elif total_savings_per_mile > 0:
        # Michelin costs more upfront, but saves money comprehensively over time
        break_even_miles = upfront_delta_per_truck / total_savings_per_mile
    else:
        # Michelin costs more upfront AND costs more to run. Never breaks even.
        break_even_miles = None 

    return {
        'competitor': {
            'hardware': comp_hardware,
            'fuel': comp_fuel,
            'downtime': comp_downtime,
            'total': comp_tco,
        },
        'michelin': {
            'hardware': mich_hardware,
            'fuel': mich_fuel,
            'downtime': mich_downtime,
            'total': mich_tco,
        },
        'fleetSavings': fleet_savings,
        'breakEvenMiles': break_even_miles,
        'upfrontDeltaPerTruck': upfront_delta_per_truck,
        'savingsPerMile': savings_per_mile,
        'annualSavingsPerTruck': annual_savings_per_truck
    }
