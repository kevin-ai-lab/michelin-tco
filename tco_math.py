# tco_math.py

def calculate_hardware_cost_per_truck(price, casing_value, life_miles, annual_miles, tires_per_truck):
    if life_miles <= 0:
        return 0
    cpm = (price - casing_value) / life_miles
    return cpm * annual_miles * tires_per_truck

def calculate_fuel_cost_per_truck(mpg, annual_miles, fuel_price, fuel_improvement_pct=0):
    if mpg <= 0:
        return 0
    effective_mpg = mpg * (1 + fuel_improvement_pct)
    return (annual_miles / effective_mpg) * fuel_price

def calculate_downtime_cost_per_truck(annual_events, event_cost, downtime_hours, downtime_rate):
    return annual_events * (event_cost + (downtime_hours * downtime_rate))

def calculate_payload_revenue_per_truck(weight_saved, revenue_per_lb, trips):
    return weight_saved * revenue_per_lb * trips

def calculate_tco(fleet_data, comp_tire, mich_tire, extra_rev):
    # Competitor
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

    # Michelin
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
    payload_rev = calculate_payload_revenue_per_truck(
        extra_rev['weightSaved'], extra_rev['revenuePerLb'], extra_rev['annualTrips']
    )
    mich_tco = mich_hardware + mich_fuel + mich_downtime - payload_rev

    # Fleet Savings
    fleet_savings = (comp_tco - mich_tco) * fleet_data['numTrucks']
    
    # Break-Even Mileage
    upfront_delta_per_truck = (mich_tire['price'] - comp_tire['price']) * fleet_data['tiresPerTruck']
    savings_per_mile = (comp_tco - mich_tco) / fleet_data['annualMiles'] if fleet_data['annualMiles'] > 0 else 0
    break_even_miles = (upfront_delta_per_truck / savings_per_mile) if (upfront_delta_per_truck > 0 and savings_per_mile > 0) else 0

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
            'payload': payload_rev,
            'total': mich_tco,
        },
        'fleetSavings': fleet_savings,
        'breakEvenMiles': break_even_miles,
        'upfrontDeltaPerTruck': upfront_delta_per_truck,
        'savingsPerMile': savings_per_mile,
        'annualSavingsPerTruck': comp_tco - mich_tco
    }
