# Lab Critical Value Engine

A **synthetic-data demonstration** of generic numerical alert rules, basic laboratory terminology lookup, and a Python/FastAPI audit workflow. **Not validated for patient care or clinical laboratory critical-value notifications.**

## What works

- Browser-only demonstration of three generic rules: primary metric >25; secondary index >12 or a manually set critical flag; anomaly keywords in a status descriptor.
- Python supervisor, command-line interface, batch CSV audit processing, and a locally hosted FastAPI API.
- Terminology lookup for five laboratory names with standalone CSV enrichment.
- In-process HMAC-SHA256 audit chain, now verified by checking signatures and predecessor links.

These numbers are arbitrary demonstration thresholds. **There are no validated analyte-specific units, age/sex reference intervals, panic limits, true delta checks, LIS integrations, notification workflows, or persistent regulatory-grade audit records.** A routine demo result does not clear a clinical result.

## Browser demonstration

Open `web/index.html` directly in a modern browser. Enter **synthetic** IDs and values, then click **Evaluate locally**. The page runs JavaScript mirroring the three example Python worker rules. No network requests, server, or Python runtime are required. The browser does not generate signed audit records.

A GitHub Pages deployment workflow is provided in `.github/workflows/pages.yml`. A live URL will be listed here only after deployment is verified.

## Install and test

Python 3.10+ is required.

```bash
git clone https://github.com/abusuraihsakhri/lab-critical-value-engine.git
cd lab-critical-value-engine
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -v
```

## Command line

```bash
lab-critical-value-engine audit --task-id DEMO-1 --target SYNTH-1 --primary 28 --secondary 13
lab-critical-value-engine chat "Describe the demo rules"
lab-critical-value-engine batch -i synthetic-tasks.csv -o results.csv
python critical_values.py single creatinine
python critical_values.py batch --input sample.csv --output results.csv
```

Task CSV columns: `task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag`. For the critical flag, use true/false, 1/0, or yes/no (case-insensitive). The standalone terminology CSV accepts an analyte name in the `query` column. Unknown lookup terms are not forcibly assigned a match.

## API and containers

The FastAPI backend provides public `/health` and `/metrics` endpoints. Calls to `/api/audit`, `/api/chat`, and `/api/audit/logs` require `LAB_API_KEY` in the server environment and the matching `X-API-Key` request header. The API refuses these calls if a key has not been configured.

```bash
export LAB_API_KEY="set-a-long-random-secret"
export AUDIT_SECRET_KEY="set-a-different-long-random-secret"
lab-critical-value-engine serve --host 127.0.0.1 --port 8000
curl -H "X-API-Key: $LAB_API_KEY" http://127.0.0.1:8000/api/audit/logs
```

`docker-compose.yml` requires both environment secrets and binds the service to the local loopback interface. Docker builds from `Dockerfile`. Do not expose the API directly on public networks; add TLS, rate limits, proper identity/access controls, and durable storage before considering a production service.

## Security, privacy, and audit limitations

Use **synthetic data only**. The backend checks some identifier patterns, but regex-based detection is not validated de-identification and cannot guarantee that protected health information is absent. The Python server temporarily holds dossiers and audit entries in memory. The HMAC chain is process-local; its records and ephemeral key (if `AUDIT_SECRET_KEY` is omitted) do not survive restart. Cryptographic link verification is not equivalent to an immutable clinical audit log. The deterministic chat stub does not contact an LLM or clinically verify any response.

## Technology and browser support

Python 3.10+, FastAPI, Pydantic v2, pytest; vanilla HTML/CSS/JavaScript for the browser demonstration. Browser mode runs on current desktop/mobile browsers. **GitHub Pages cannot run the FastAPI backend**; the Pages app is a static, client-side JavaScript demonstration. Pyodide/in-browser Python is not used.

## License

MIT; see [LICENSE](LICENSE).
