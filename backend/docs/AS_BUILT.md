# CyRIS As-Built Architecture Registry

> **Document Status:** Authoritative record of real codebase module paths, function signatures, data structures, and baseline performance benchmarks.

---

## 1. Core Module Registry

### Data Generation & Persistence
* **Module Path:** `app.data.generator`
* **Signatures:**
  ```python
  def generate_dataset(seed: int = DEFAULT_SEED) -> Dataset
  def save_dataset(dataset: Dataset, path: str | Path | None = None) -> Path
  def load_dataset(path: str | Path | None = None) -> Dataset
  ```

### Digital Twin Engine (`TwinEngine`)
* **Module Path:** `app.twin.engine`
* **Class:** `TwinEngine` (wraps NetworkX directed graph topology)
* **Signatures:**
  ```python
  class TwinEngine:
      def __init__(self, dataset: Dataset)
      def get_attack_paths(self, max_cutoff: int = 6) -> list[AttackPath]
      def get_shortest_path_to_crown_jewel(self, start_asset_id: str) -> list[str]
      def get_betweenness_centrality(self) -> dict[str, float]
      def get_twin_graph_view(self) -> TwinGraphView
      def patch_vulnerability(self, vulnerability_id: str) -> TwinEngine
      def delay_patch(self, vulnerability_id: str, days: int) -> TwinEngine
      def toggle_control(self, control_id: str, deployed: bool) -> TwinEngine
      def add_control(self, control: Control) -> TwinEngine
  ```

### TwinStore & State Management
* **Module Path:** `app.state`
* **Class:** `TwinStore`
* **Signatures:**
  ```python
  class TwinStore:
      def live_twin(self) -> TwinEngine
      def baseline(self) -> SimulationResult
      def result_for(self, twin: TwinEngine, n: int | None = None) -> SimulationResult
      def get_fingerprint(self, twin: TwinEngine) -> str
  ```

### Attack Graph Analytics & Severance
* **Module Path:** `app.risk.attack_paths`
* **Signatures:**
  ```python
  def analytic_eal(twin: TwinEngine) -> float
  def build_attack_graph(twin: TwinEngine) -> nx.DiGraph
  def most_likely_paths(twin: TwinEngine, k: int = 5) -> list[AttackPath]
  def active_path(twin: TwinEngine) -> AttackPath | None
  def chokepoints(twin: TwinEngine, limit: int = 5) -> list[dict[str, Any]]
  def vulnerability_contributions(twin: TwinEngine) -> list[dict[str, Any]]
  ```

### What-If Evaluator & Counterfactual Cards
* **Module Path:** `app.decision.evaluator`, `app.decision.costing`, `app.decision.counterfactuals`
* **Signatures:**
  ```python
  def evaluate_mutations(store: TwinStore, mutations: list[dict[str, Any]], n: int | None = None) -> dict[str, Any]
  def cost_of(mutations: list[dict[str, Any]], dataset: Dataset) -> tuple[int, list[dict[str, Any]]]
  def generate_counterfactual_cards(store: TwinStore, limit: int = 10) -> list[dict[str, Any]]
  ```

### Formatting Helpers
* **Module Path:** `app.utils.formatters` / `src/utils/formatINR.ts`
* **Signatures:**
  ```python
  def format_inr_short(amount: int | float) -> str  # e.g. 4800000 -> "₹48 L" / "₹4.8 Cr"
  ```

---

## 2. Dependencies & Environment Settings

* **Installed Packages:**
  - `ortools`: `9.15.6755`
  - `anthropic`: `1.8.0`
  - `cryptography`: `50.0.1`
  - `pydantic`: `2.13.5`
  - `numpy`: `2.5.2`
  - `networkx`: `3.4.2`
  - `fastapi`: `0.115.11`
* **Environment Files:**
  - `.env.example`
  - `.gitignore` (excludes `.env`, `data/keys/`, `data/audit/`, `*.db`)

---

## 3. Measured Preflight Timing Benchmarks

* **Command:** Internal timing script against living twin (`seed=42`, $N=10,000$)
* **Results:**
  - `twin.clone()` (`TwinEngine(copy.deepcopy(live_twin.dataset))`): **1.34 ms**
  - `analytic_eal()` on clone: **0.25 ms**
  - Full `run_simulation()` ($N=10,000$): **224.83 ms**
  - Cold `evaluate_mutations()`: **226.62 ms**

---

## 4. Frontend Component & Mock Shape Inventory

* **Budget Slider (`BudgetOptimizer.tsx`)**:
  - `min`: `0`
  - `max`: `7,500,000` (up to `10,000,000` cap)
  - `step`: `50,000`
  - Current default budget: `INR 5,000,000` (`₹50 L`)
* **Debate Panel (`AgentsPage.tsx`)**:
  - Mock shape: `AgentRecord` (`red`, `blue`, `judge`)
* **NL Query Box (`AskTwin.tsx` / `AgentsPage.tsx`)**:
  - Mock shape: `NLQueryResponse` (`question`, `answer`, `sources`, `suggestions`)
* **Compliance View (`ComplianceTable.tsx`)**:
  - Mock shape: `ComplianceRow` (`finding`, `control`, `framework`, `clause`, `status`, `proof`)
* **Audit Log & Proof (`AuditTrailPage.tsx`)**:
  - Mock shape: `TelemetryEvent` / Audit proof record
