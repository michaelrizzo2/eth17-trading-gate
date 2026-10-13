# Strategy evidence gate

Test the evidence before a paper-trading experiment. A public engineering case study by Michael Rizzo.

**Public case study: tested Python implementation and an interactive browser demonstration using synthetic data. Live AI and external API adapters are not connected.**

[Portfolio](https://michaelrizzo2.github.io/#projects) · [Try the interactive demo](https://michaelrizzo2.github.io/#demo-trading) · [Source](https://github.com/michaelrizzo2/eth17-trading-gate)

## Implemented behavior

Uses an illustrative 5/17 moving-average crossover on 240 synthetic hourly closes. Signals at close i−1 execute at close i, fees apply on both sides, and final positions are liquidated with fees. An evidence gate checks provenance, holdout availability, trade count, net return and drawdown. Synthetic provenance and missing holdout block every run. This does not implement or claim to reproduce a previously validated ETH17 strategy. Spread, slippage and real Kraken data remain future work.

## Public demonstration

The linked GitHub Pages demo runs in JavaScript, with no install or credentials required. Its calculations, rankings and gate outcomes were checked against the Python implementation across 32 combined scenario/parameter cases. Browser approval illustrates the review step; the Python repair service owns session and proposal validation.

## Run locally

Python 3.11 or newer:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8014
```

Open http://127.0.0.1:8014. API documentation is at `/docs`; `/api/health` reports the active mode. Production dependencies alone are in `requirements.txt`. No credentials are needed or loaded for this deterministic milestone.

## Architecture

Browser → FastAPI validation → deterministic workflow/ranking/backtest → inspectable structured response.

The application uses a small flat file layout: `app.py` contains the typed request schema and workflow; `ui.html`, `styles.css` and `ui.js` implement the interface; `test_app.py` exercises the important boundaries. This keeps the initial case study easy to clone and run.

## Verification and limitations

Run the tests above. They verify input rejection, domain calculations and the specific decision boundaries, not model accuracy. Synthetic scenarios demonstrate behavior but do not establish real-world business impact or trading performance. No private customer records or credentials belong in this repository.

## Integration design

Add provenance-checked historical Kraken data, a frozen train/holdout split, spread/slippage assumptions and reproducible benchmark comparisons. Explore TypeSafe evidence-completeness checks while keeping all execution/risk gates deterministic. Never treat an AI score as permission to trade.

TypeSafe integration design follows the current [API](https://docs.typesafe.ai/api), [Python SDK](https://docs.typesafe.ai/sdk/python) and [composite scoring](https://docs.typesafe.ai/patterns/composite-scoring) documentation. Model adapter design is separate from the demonstrated deterministic behavior.
