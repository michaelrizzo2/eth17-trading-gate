import copy
from evidence import DATA,verify,evaluate,simulate
from app import signals

def test_snapshot_and_frozen_split():
 assert verify();bad=copy.deepcopy(DATA);bad['candles'][0]['close']+=1;assert not verify(bad)
 r=evaluate();assert r['bars']==216 and r['dates'][0]==DATA['candles'][504]['date']
 assert not evaluate('training')['checks'][1]['passed']
def test_no_future_signals_and_costs_reduce_equity():
 p=[c['close'] for c in DATA['candles']]
 assert signals(p)[:600]==signals(p[:600])
 gross=simulate(p,504,720,0,0);net=simulate(p,504,720,26,10)
 assert net['final_equity_usd']<gross['final_equity_usd']
 assert len(net['equity_curve'])==216
 assert evaluate()['allowed']==all(x['passed'] for x in evaluate()['checks'])
def test_cash_flat_market_costs_and_final_liquidation():
 p=[100.]*30
 assert simulate(p,17,30,26,10)['final_equity_usd']==10000
 b=simulate(p,17,30,26,10,True)
 assert b['final_equity_usd']<10000 and b['trades']==1
