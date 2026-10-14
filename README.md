# Historical strategy evidence gate

[Portfolio](https://michaelrizzo2.github.io/#projects) · [Try the case study](https://michaelrizzo2.github.io/#demo-trading)

Use 720 complete Kraken ETH/USD daily candles, October 23, 2024–October 12, 2026, rather than synthetic prices. `eth-history.json` records provenance and a canonical candle checksum; `kraken-response.json` preserves raw source bytes. The incomplete final API candle was discarded. `SOURCES.md` describes validation.

The pre-existing fixed 5/17 long/cash rule is evaluated with a 70/30 chronological split: 504 earlier observations and 216 held-out closes beginning March 11, 2026. No parameter search or performance tuning occurred. Indicators use prior observations, including pre-holdout warmup; prior-close signals execute at the next close. Fee and adverse spread/slippage assumptions apply on both sides, including final liquidation. Buy-and-hold uses the same costs and interval. Chart axes show dates and USD equity. Gross/net metrics show friction impact.

At default 26-bps fees + 10-bps adverse execution per side, held-out strategy return is 17.88%, versus 18.24% buy-and-hold; drawdown 23.01%, 9 completed trades. It **fails** the trade-count, drawdown and benchmark gates. A positive return alone does not justify trading. `/api/evidence` independently reproduces the browser audit; legacy synthetic `/api/run` remains available.

## Limits

One exchange, daily-close execution assumptions, a small single holdout and illustrative gates. No liquidity, latency, funding, tax, exchange or order system. Exploring costs reuses the holdout; it creates no new out-of-sample evidence. Historical results are not a trading recommendation or future-return forecast.

## Run and verify

Python 3.11+:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8014
```

Open http://127.0.0.1:8014. The shared browser workspace uses published evidence assets; enhanced Python APIs expose independent reproducible calculations. All four browser modes are included to make comparison easy; each repository’s own Python implementation is its named project. Repair live mode additionally needs the separately configured backend on 8021. No credentials are bundled in browser files.

8 Python tests pass for this project. Portfolio tests and 45 enhanced Python/browser parity combinations validate the shared outputs. See `VALIDATION.md`.
