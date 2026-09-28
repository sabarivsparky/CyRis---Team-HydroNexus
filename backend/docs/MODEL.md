# CyRIS Actuarial Risk & Decision Engine Specification

> **Document Status:** Authoritative mathematical and operational model documentation for CyRIS.

---

## 1. Mathematical Quantification Engine

### Single Loss Expectancy (SLE)
$$\text{SLE} = L_{\text{downtime}} + L_{\text{breach}} + L_{\text{recovery}} + L_{\text{regulatory}} + L_{\text{operational}} + L_{\text{reputation}}$$

* **Downtime Loss ($L_{\text{downtime}}$):** Hours of downtime based on asset criticality $\times$ hourly revenue dependency.
* **Breach Recovery ($L_{\text{breach}}$):** Forensic recovery cost based on asset data sensitivity tier.
* **Regulatory Fines ($L_{\text{regulatory}}$):** Statutory penalty under SEBI CSCRF, RBI CSF, and DPDP Act 2023.

### Annualized Rate of Occurrence (ARO)
$$\text{ARO} = \text{ATTEMPT\_RATE} \times \max\left(\text{BASELINE\_FLOOR}, P_{\text{vuln}} \times (1 - P_{\text{ctrl}})\right)$$

* $P_{\text{vuln}} = 1 - \prod_{v \in \text{open}} (1 - v.\text{exploitability})$
* $P_{\text{ctrl}} = 1 - \prod_{c \in \text{deployed}} (1 - c.\text{effectiveness} \times c.\text{health})$

---

## 2. What-If & Counterfactual Decision Modeling

### Financial Cost Assumptions
* **Security Control Deployment:** Control cost specified in `Control.cost_inr`. If applied to a subset of covered assets, cost is pro-rated by $\frac{|\text{subset}|}{|\text{covered\_asset\_ids}|}$.
* **Vulnerability Patching (`PATCH_COST_PER_VULN_INR`):** ₹40,000 (₹0.4 Lakhs) per open vulnerability remediated.
* **Exploit Edge Severance (`EDGE_SEVERANCE_COST_INR`):** ₹200,000 (₹2 Lakhs) per severed network exploit path.
* **Zero-Cost Actions:** Control removal, delay patch, and vulnerability additions carry 0 outlay cost (savings/side effects unmodeled).

### Return on Security Investment (ROSI)
$$\text{ROSI} = \frac{(\text{EAL}_{\text{before}} - \text{EAL}_{\text{after}}) - \text{Cost}_{\text{inr}}}{\text{Cost}_{\text{inr}}}$$

* **Payback Period (Months):**
$$\text{Payback Months} = \frac{\text{Cost}_{\text{inr}}}{(\text{EAL}_{\text{before}} - \text{EAL}_{\text{after}}) / 12}$$

### Common Random Numbers (CRN) Variance Reduction
To ensure mathematical exactness in What-If comparisons, CyRIS executes baseline and mutated simulations using **Common Random Numbers (CRN)**. The exact same pseudo-random seed (`42`) and Poisson/Log-Normal draws are reused between before and after runs. This completely eliminates Monte Carlo stochastic noise, ensuring that any measured EAL reduction is strictly caused by the structural intervention.

### Two-Stage Counterfactual Card Engine
1. **Stage 1 — Fast Analytic Screening:** Evaluates candidate control deployments, critical vulnerability patches, and chokepoint edge severances deterministically using $O(V+E)$ `analytic_eal` calculations ($\text{analytic\_EAL} = \sum \text{ARO}_a \times \text{SLE}_a$). Filters out actions with non-positive reduction and ranks top $M=10$ actions by analytic ROSI.
2. **Stage 2 — Monte Carlo Confirmation:** Executes full Monte Carlo simulation with CRN on top 10 candidates to certify exact EAL deltas, VaR 95% reductions, ROSI ratios, and payback periods. Only Stage-2 confirmed metrics are displayed on Counterfactual Cards.
