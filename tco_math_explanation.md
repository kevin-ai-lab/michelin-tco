# Michelin B2B TCO Calculator: Math & Logic Explanation

This document breaks down the exact logic driving the **TCO Dashboard**, using a simple 1-Truck default scenario to demonstrate how the math physically maps to the visual chart and KPIs.

## 1. The Baseline Example Scenario
To prove the math, we will assume a fleet with **1 Truck** driving **100,000 miles** per year.

**Fleet Averages:**
- 18 tires per truck
- Base Fuel Efficiency: 6.0 MPG
- Fuel Cost: $4.00 / gallon
- Downtime Cost: 3 hours/event @ $120/hr + $350 Tow = **$710 Total / Event**

**Tire Assumptions:**
- **Michelin:** $550 Price | $75 Casing | 180k Mile Life | 0.8 Events/Yr | 5% Fuel Gain
- **Competitor:** $350 Price | $40 Casing | 100k Mile Life | 1.5 Events/Yr | 0% Fuel Gain

---

## 2. The Chart Components (From Left to Right)

### Box 1: Michelin Upfront Purchase
This is the pure "Day 1" cash outlay required to outfit the truck with Michelin rubber. It deliberately highlights that Michelin is the expensive option today.
> **Math:** 18 tires × $550 = **$9,900**

### Box 2: Competitor Upfront Purchase
This is the Day 1 cash outlay for the budget option. The waterfall line *drops* from $9,900 down to $6,300 to visually acknowledge the initial savings.
> **Math:** 18 tires × $350 = **$6,300**
> *The "Michelin Premium" to overcome is therefore $3,600.*

### Penalty 1: Early Replacement Penalty (Hardware Delta)
A budget tire is cheaper today, but wears out much faster. This calculates the difference in pure Hardware Cost Per Mile (CPM) annualized for a 100,000-mile year.
> **Competitor CPM:** ($350 Price - $40 Casing) / 100,000 Life = $0.0031 / mile
> **Michelin CPM:** ($550 Price - $75 Casing) / 180,000 Life = $0.002638 / mile
> 
> **Annual Hardware Cost:**
> - Competitor: $0.0031 × 100k miles × 18 tires = $5,580 / year
> - Michelin: $0.002638 × 100k miles × 18 tires = $4,748 / year
>
> **Penalty on Chart:** $5,580 - $4,748 = **+$832**

### Penalty 2: Excess Fuel Cost
Michelin’s low rolling resistance yields a 5% fuel gain. Because fuel is the massive operational anchor, this penalty is usually the steepest step on the chart.
> **Michelin Effective Fuel:** 6.0 MPG × 1.05 = 6.3 MPG
>
> **Annual Fuel Spend:**
> - Competitor: (100,000 miles ÷ 6.0 MPG) × $4.00 = $66,666
> - Michelin: (100,000 miles ÷ 6.3 MPG) × $4.00 = $63,492
>
> **Penalty on Chart:** $66,666 - $63,492 = **+$3,174**

### Penalty 3: Excess Downtime Cost
Budget tires blow out more often. This calculates the annualized cost of roadside assistance and idle driver wages.
> - Competitor: 1.5 Events × $710 = $1,065
> - Michelin: 0.8 Events × $710 = $568
>
> **Penalty on Chart:** $1,065 - $568 = **+$497**

### Final Box: Tire-Related Operating Costs & Penalties
This represents the absolute final **Year 1 Total** of choosing the budget tire. It takes the cheap Day 1 purchase price, and stacks all 12 months of penalties on top of it.
> **Math:** $6,300 (Upfront) + $832 (Tire) + $3,174 (Fuel) + $497 (Downtime) = **$10,803**

---

## 3. The Executive Dashboard KPIs

### Fleet Annual Savings (Year 1 Net Cash Flow)
If the Competitor's 1-Year Total is $10,803, and you spent $9,900 on Michelin on Day 1, how much actual cash is left in your pocket at Month 12?
> **Math:** $10,803 (Competitor Total) - $9,900 (Michelin Upfront) = **$903 Savings in Year 1**
> *Scale this number by the "Total Trucks" slider to generate the massive "Fleet Annual Savings" metric.*

**(Why this is brilliant:)** The physical distance on the chart between the top of the Michelin starting bar ($9,900) and the top of the Competitor Red Box ($10,803) is exactly $903. The top left number perfectly aligns with the visual "gap" driving the presentation point.

### Break-Even Mileage (Time to ROI)
How many miles must the truck drive before the $3,600 Michelin Day-1 Premium is mathematically paid off by the cheaper operational costs? 

To find this, we sum up the total annualized operational savings (Hardware + Fuel + Downtime):
> **Total Annualized Savings:** $832 + $3,174 + $497 = $4,503 / year
> **Savings Per Mile:** $4,503 ÷ 100,000 miles = $0.04503 saved for every mile driven.
>
> **Math:** $3,600 Premium ÷ $0.04503/mile = **79,946 Miles**
> *In a 100k-mile year, this truck becomes net-cash-positive in roughly 9.5 months.*
