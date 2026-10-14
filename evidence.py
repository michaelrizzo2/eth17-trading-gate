"""Fixed chronological historical evaluation; no tuning or exchange orders."""
import json,hashlib,math
from pathlib import Path
DATA=json.loads((Path(__file__).parent/'eth-history.json').read_text())
from app import signals
SPLIT=504

def simulate(prices,start,stop,fee_bps,slippage_bps,benchmark=False):
 if len(prices)<19 or not 0<=start<stop<=len(prices):raise ValueError('Invalid interval')
 for value in [fee_bps,slippage_bps]:
  if not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=100:raise ValueError('Invalid friction assumption')
 sig=signals(prices);f=fee_bps/10000;s=slippage_bps/10000
 cash=peak=10000.;units=dd=0.;trades=0;curve=[]
 for i in range(start,stop):
  desired=1 if benchmark else (sig[i-1] if i else 0)
  if desired and not units:units=cash/(prices[i]*(1+s)*(1+f));cash=0
  elif not desired and units:cash=units*prices[i]*(1-s)*(1-f);units=0;trades+=1
  equity=cash+units*prices[i];peak=max(peak,equity);dd=max(dd,1-equity/peak);curve.append(equity)
 if units:cash=units*prices[stop-1]*(1-s)*(1-f);trades+=1;curve[-1]=cash;dd=max(dd,1-cash/peak)
 return {'net_return_pct':(cash/10000-1)*100,'max_drawdown_pct':dd*100,'trades':trades,'final_equity_usd':round(cash,2),'equity_curve':curve}

def verify(data=DATA):
 c=data['candles'];digest=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return digest==data['candles_sha256'] and len(c)==720 and all(math.isfinite(x['close']) and x['close']>0 for x in c) and all(c[i]['timestamp']-c[i-1]['timestamp']==86400 for i in range(1,len(c)))
def evaluate(scenario='holdout',fee_bps=26,slippage_bps=10):
 if scenario not in ['holdout','training']:raise ValueError('Unknown interval')
 c=DATA['candles'];prices=[x['close'] for x in c];start,stop=(SPLIT,len(c)) if scenario=='holdout' else (0,SPLIT)
 metrics=simulate(prices,start,stop,fee_bps,slippage_bps);benchmark=simulate(prices,start,stop,fee_bps,slippage_bps,True);gross=simulate(prices,start,stop,0,0)
 checks=[{'label':'Snapshot checksum and chronological spacing verified','passed':verify()},{'label':'Frozen last-30% holdout selected (no parameter search)','passed':scenario=='holdout'},{'label':'At least 20 completed trades','passed':metrics['trades']>=20},{'label':'Positive return after fees and slippage','passed':metrics['net_return_pct']>0},{'label':'Maximum drawdown at or below 10%','passed':metrics['max_drawdown_pct']<=10},{'label':'Outperforms buy-and-hold under the same costs','passed':metrics['net_return_pct']>benchmark['net_return_pct']}]
 return {'kind':'gate','mode':'Historical evidence audit','synthetic':False,'allowed':all(x['passed'] for x in checks),'checks':checks,'metrics':metrics,'benchmark':benchmark,'gross':gross,'dates':[x['date'] for x in c[start:stop]],'bars':stop-start,'fee_bps':fee_bps,'slippage_bps':slippage_bps,'source':DATA['source_url'],'snapshot_sha256':DATA['candles_sha256'],'split':{'training':504,'holdout':216,'holdout_start':c[SPLIT]['date']},'message':'Actual Kraken ETH/USD daily snapshot. Gate results are research evidence only. No orders or exchange credentials are connected. Exploring cost assumptions reuses the fixed holdout; it does not create fresh out-of-sample evidence.','strategy':'Fixed long/cash 5/17 crossover, signal at prior close executes at next close. 70/30 chronological split; prior observations warm up holdout indicators. Fee plus adverse slippage/spread allowance on both sides, including final liquidation. No latency, liquidity, funding or tax model.'}
