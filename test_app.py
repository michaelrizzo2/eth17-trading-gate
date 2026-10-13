from fastapi.testclient import TestClient
import app

def test_health_and_ui():
    with TestClient(app.app) as client:
        assert client.get('/api/health').json()['synthetic'] is True
        assert client.get('/').status_code == 200
        assert client.get('/ui.js').status_code == 200

def test_invalid_inputs():
    with TestClient(app.app) as client:
        assert client.post('/api/run', json={'scenario': 'unknown'}).status_code == 422
        assert client.post('/api/run', json={'scenario': 'charging', 'weight': -1}).status_code == 422
        assert client.post('/api/run', json={'scenario': 'charging', 'surprise': 'x'}).status_code == 422
def test_causal_signals():
    prices = app.synthetic_prices('trending')
    assert app.signals(prices)[:100] == app.signals(prices[:100])

def test_fees_and_synthetic_gate():
    prices = app.synthetic_prices('trending')
    assert app.backtest(prices,100)['final_equity_usd'] < app.backtest(prices,0)['final_equity_usd']
    for scenario in ('trending','choppy','declining'):
        result=app.evaluate(scenario)
        assert result['allowed'] is False
        assert result['metrics']['trades'] >= 1

def test_invalid_market_data():
    import pytest
    for prices in ([1]*10,[1]*30+[float('nan')],[1]*30+[0]):
        with pytest.raises(ValueError):
            app.backtest(prices)
