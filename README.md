# Optimized Donor Appeal Calculator
This repository is a transparent resource for the Legacy Home of Recovery (LHoR) to improve and automate their internal donor appeal requests. 

## User Instructions

1. download the zip from Releases
2. unzip it
3. double-click the program
4. choose the individual export
5. find LHoR_optimized_asks.csv in that same folder. 

## How Appeals Are Calculated
Two primary features are used in calculating an optimized donor appeal request: 
* Total Year-To-Date donations
* Median regional income

Let $G$ be the donor's gift total for the past 365 days, excluding sponsorship gifts. Let $I$ be the median household income for the donor's ZIP code.

$$
k =
\begin{cases}
1 & \text{if } I \text{ is missing} \\
\operatorname{clip}\!\left(\dfrac{I}{75000},\, 0.5,\, 2\right) & \text{otherwise}
\end{cases}
$$

$$
\operatorname{round}_{25}(x) = 25\left\lfloor \dfrac{x}{25} + \dfrac{1}{2} \right\rfloor
$$

$$
\begin{aligned}
A_2 &= \max\!\left(25,\; \operatorname{round}_{25}(G \cdot k)\right) \\
A_1 &= \max\!\left(25,\; \operatorname{round}_{25}(0.5 \cdot A_2)\right) \\
A_3 &= \max\!\left(25,\; \operatorname{round}_{25}(1.5 \cdot A_2)\right)
\end{aligned}
$$

## Contributions & Updates
* The executable was generated with PyInstaller-v6.22.3 using the following command:
```CMD
py -m PyInstaller --noconfirm --onedir --name DonorAppealOptimizer --paths "scripts\donor_appeal_optimizer" "scripts\donor_appeal_optimizer\optimized_ask_table.py"
```

* Individuals who want to read or change the executable rules can run python scripts/optimized_ask_table.py.
