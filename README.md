# SupplyChain AI Copilot

A locally runnable, full-stack multi-agent system that turns inventory, order, and supplier Excel workbooks into explainable replenishment decisions and an operational action plan.

## What it does

1. Validates uploaded `.xlsx` workbooks with pandas and openpyxl.
2. Discovers relationships and selects relevant specialists.
3. Runs Inventory, Orders, Demand, Supplier, and Cost Impact agents concurrently.
4. Produces product-level decisions.
5. Uses a critic to detect contradictions and route only the affected agents for revision.
6. Converts approved recommendations into immediate, short-term, and monitoring actions.

The calculations are deterministic Python/pandas logic. With **Conflict demo** disabled, Gemini is called for evidence-grounded decision synthesis using `GEMINI_API_KEY` and `GEMINI_MODEL` from `backend/.env`. The key is never sent to the browser.

## Curated data

No Excel files are required to get started. Select **Use curated sample data** in the UI. The generated workbooks are also available in `data/sample_data/` and through:

- `GET /api/sample-data/inventory.xlsx`
- `GET /api/sample-data/orders.xlsx`
- `GET /api/sample-data/suppliers.xlsx`

Regenerate them with `python data/generate_sample_data.py`.

## Run

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. API documentation is at `http://localhost:8000/docs`.

For live Gemini synthesis, configure:

```env
GEMINI_API_KEY=your_key
GEMINI_MODEL=your_supported_model
DEMO_CONFLICT_MODE=false
```

## Validate

```bash
cd backend && .venv/bin/pytest -q
cd ../frontend && npm run build
```

## API

- `POST /api/workflows` — multipart upload (`business_objective`, `demo_conflict_mode`, `inventory`, `orders`, optional `suppliers`).
- `POST /api/workflows/sample` — start with bundled sample data.
- `GET /api/workflows/{id}` — status, validation, events, plan, and revisions.
- `GET /api/workflows/{id}/agents` — structured agent outputs.
- `GET /api/workflows/{id}/result` — decision, critic review, and action plan.
- `WS /ws/workflows/{id}` — live workflow events.

Workflow storage is in memory and resets when the backend restarts.
