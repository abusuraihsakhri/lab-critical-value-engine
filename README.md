# Lab Critical Value Engine

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Lab Critical Value Engine flags critical/panic lab values against age/sex-specific limits with delta-check integration. It provides a stdlib parser/mapper with batch CSV processing and single lookup capabilities.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`lookup()`**: Single lookup using token overlap + substring scoring (no external dependencies). Returns top hits from a built-in lab value dictionary.
- **`process_csv()`** — Processes CSV files with lab value lookups, enriching each row with match results.
- **`build_parser()`** — Constructs the CLI argument parser for the core module.
- **`main()`** — Entry point for CLI-based evaluation.

### 🏗️ Architecture

- **`agents/`** — Enterprise multi-agent orchestration layer with specialized workers:
  - `InvariantQCWorker` — Primary metric threshold monitoring
  - `SafetyEscalationWorker` — Safety boundary and emergency interlock detection
  - `ProtocolConformanceWorker` — Spec conformance and discordance checking
- **`cli.py`** — Full-featured CLI with audit, chat, batch, verify-audit, and serve commands
- **`agents/api.py`** — FastAPI REST server with `/health`, `/metrics`, `/api/audit`, `/api/chat`, `/api/audit/logs` endpoints
- **`enrichment.py`** — Extended analytical engines (Features, Critical Value Alert, QC Dashboard, Turnaround Time, Specimen Rejection, Reference Range Validation, Delta Check, Point-of-Care Compliance)
- **`simulator.py`** — High-throughput batch simulation with adversarial PHI injection testing
- **`agents/metrics.py`** — Prometheus-compatible metrics exporter
- **`agents/streamer.py`** — WebSocket telemetry broadcaster
- **`agents/learning.py`** — Bayesian calibration and active learning feedback engine

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/lab-critical-value-engine.git
cd lab-critical-value-engine

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Audit Evaluation
```bash
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Interactive Chat
```bash
python cli.py chat "Explain critical value thresholds"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### 6. Core Module (standalone)
```bash
python critical_values.py single creatinine
python critical_values.py batch --input sample.csv --output results.csv
```

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOB, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Configurable Audit Secret:** Set `AUDIT_SECRET_KEY` environment variable for production deployments.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 100
```

---

## 🐳 Container Deployment

```bash
# Build and run with Docker
docker build -t lab-critical-value-engine .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key lab-critical-value-engine

# Or use docker-compose
AUDIT_SECRET_KEY=your-secret-key docker-compose up
```

---

## 📁 Project Structure

```
lab-critical-value-engine/
├── agents/                 # Enterprise multi-agent orchestration
│   ├── __init__.py
│   ├── api.py             # FastAPI REST server
│   ├── base.py            # Security, PHI guard, HMAC audit trail
│   ├── learning.py        # Bayesian calibration engine
│   ├── llm_factory.py     # LLM provider factory
│   ├── metrics.py         # Prometheus metrics exporter
│   ├── models.py          # Pydantic data models
│   ├── streamer.py        # WebSocket telemetry
│   ├── supervisor.py      # Master orchestrator
│   └── workers.py         # Specialized domain workers
├── tests/                 # Test suite
│   ├── test_critical_values.py
│   ├── test_enrichment.py
│   └── test_lab_critical_value_engine.py
├── web/                   # Operations console (HTML)
├── cli.py                 # CLI entry point
├── critical_values.py     # Core lookup and CSV processing
├── enrichment.py          # Extended analytical engines
├── simulator.py           # Batch simulation
├── pyproject.toml         # Project configuration
├── Dockerfile             # Container build
├── docker-compose.yml     # Container orchestration
├── sample.csv             # Sample input data
└── benchmark_dataset.json # Benchmark test cases
```
