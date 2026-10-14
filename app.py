CONFIG = {'input_label': 'Synthetic price regime', 'boundary': 'An illustrative backtest, not a trading recommendation. Synthetic data always fails the evidence gate. No real or paper orders are sent.', 'options': [{'id': 'trending', 'label': 'Upward trend'}, {'id': 'choppy', 'label': 'Choppy sideways market'}, {'id': 'declining', 'label': 'Downward trend'}], 'weight_label': 'Fee per side (basis points)', 'default_weight': 26, 'title': 'Strategy evidence gate', 'subtitle': 'Test the evidence before a paper-trading experiment.'}
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).parent
app = FastAPI(title=CONFIG['title'])

class RunRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scenario: str = Field(min_length=1, max_length=60)
    weight: int = Field(default=50, ge=0, le=100)

@app.get('/')
def index():
    return FileResponse(ROOT / 'ui.html')

@app.get('/styles.css')
def styles():
    return FileResponse(ROOT / 'styles.css', media_type='text/css')

@app.get('/ui.js')
def script():
    return FileResponse(ROOT / 'ui.js', media_type='text/javascript')

@app.get('/api/health')
def health():
    return {'status': 'ok', 'mode': 'deterministic', 'synthetic': True}

@app.get('/api/config')
def config():
    return CONFIG
import math

def synthetic_prices(scenario, count=240):
    if scenario not in ('trending', 'choppy', 'declining'):
        raise ValueError('Unknown scenario')
    return [round(2000 + (3*i if scenario == 'trending' else -2*i if scenario == 'declining' else 0) + (60 if scenario == 'choppy' else 25)*math.sin(i/(2 if scenario == 'choppy' else 9)), 2) for i in range(count)]

def signals(prices, fast=5, slow=17):
    if len(prices) < slow + 2 or any(not isinstance(p, (float, int)) or not math.isfinite(p) or p <= 0 for p in prices):
        raise ValueError('Need sufficient positive finite price observations')
    result = []
    for i in range(len(prices)):
        if i < slow - 1:
            result.append(0)
        else:
            result.append(int(sum(prices[i-fast+1:i+1])/fast > sum(prices[i-slow+1:i+1])/slow))
    return result

def backtest(prices, fee_bps=26):
    if not 0 <= fee_bps <= 100:
        raise ValueError('Fee must be between 0 and 100 basis points')
    sig = signals(prices)
    cash, units, peak, max_dd, trades = 10000., 0., 10000., 0., 0
    curve = [cash]
    fee = fee_bps / 10000
    # A signal observed at close i-1 is executed at close i. Never at its own close.
    for i in range(1, len(prices)):
        desired = sig[i-1]
        price = prices[i]
        if desired and not units:
            units = cash / (price*(1+fee))
            cash = 0.
        elif not desired and units:
            cash = units*price*(1-fee)
            units = 0.
            trades += 1
        equity = cash + units*price
        peak = max(peak, equity)
        max_dd = max(max_dd, 1-equity/peak)
        curve.append(round(equity, 6))
    if units:
        cash = units*prices[-1]*(1-fee)
        trades += 1
        curve[-1] = round(cash, 6)
        max_dd = max(max_dd, 1-cash/peak)
    return {'net_return_pct': (cash/10000-1)*100, 'max_drawdown_pct': max_dd*100, 'trades': trades, 'final_equity_usd': round(cash, 2), 'equity_curve': curve}

def evaluate(scenario='trending', fee_bps=26):
    prices = synthetic_prices(scenario)
    metrics = backtest(prices, fee_bps)
    checks = [
        {'label': 'Verified historical data provenance', 'passed': False},
        {'label': 'Untouched holdout evaluation available', 'passed': False},
        {'label': 'At least 20 completed trades', 'passed': metrics['trades'] >= 20},
        {'label': 'Positive return after the selected fees', 'passed': metrics['net_return_pct'] > 0},
        {'label': 'Maximum drawdown at or below 10%', 'passed': metrics['max_drawdown_pct'] <= 10},
    ]
    return {'kind': 'gate', 'mode': 'deterministic', 'synthetic': True, 'allowed': all(c['passed'] for c in checks), 'checks': checks, 'metrics': metrics, 'bars': len(prices), 'fee_bps': fee_bps, 'message': 'Synthetic results demonstrate the gate only. Missing historical provenance and holdout evidence block paper-trading eligibility. No exchange connection or order endpoint exists.', 'strategy': 'Illustrative long/cash 5/17 close-moving-average crossover; not a claim about an existing ETH17 strategy.', 'limitations': ['No spread or slippage model', 'No real market data', 'Not validated for production or financial decisions']}

@app.post('/api/run')
def run(body: RunRequest):
    try:
        return evaluate(body.scenario, body.weight)
    except ValueError as exc:
        raise HTTPException(422, str(exc))

# Enhanced evidence API; legacy synthetic endpoints remain reproducible.
class EvidenceRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scenario: str = 'all'
    weight: int = Field(default=50, ge=0, le=100)
    target: str = 'Northstar N14'
    assumptions: dict[str, int] | None = None
    profile: dict | None = None
    slippage_bps: int = Field(default=10,ge=0,le=100)

@app.post('/api/evidence')
def evidence_run(body: EvidenceRequest):
    from evidence import evaluate
    try:
        return evaluate(body.scenario,body.weight,body.slippage_bps)
    except ValueError as exc:
        raise HTTPException(422,str(exc))

# Explicit public evidence assets; never expose arbitrary project paths.
@app.get('/{asset}')
def evidence_asset(asset: str):
    if asset not in ('demo-engine.js','jobs-data.json','eth-history.json','evaluation-results.json'):
        raise HTTPException(404,'Asset not found')
    return FileResponse(ROOT / asset)
