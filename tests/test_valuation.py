from fundamental_analysis_agent.tools.valuation_tools import dcf_calculation


def test_dcf_returns_no_value_when_inputs_missing(monkeypatch):
    import fundamental_analysis_agent.tools.valuation_tools as valuation
    monkeypatch.setattr(valuation, "get_financial_snapshot", lambda ticker: {
        "ticker": ticker, "free_cash_flow": None, "shares_outstanding": None,
        "current_price": None, "total_cash": None, "total_debt": None,
    })
    result = dcf_calculation("TEST")
    assert result["status"] == "insufficient_data"
    assert result["intrinsic_value_per_share"] is None


def test_dcf_rejects_discount_rate_below_terminal_growth(monkeypatch):
    import fundamental_analysis_agent.tools.valuation_tools as valuation
    monkeypatch.setattr(valuation, "get_financial_snapshot", lambda ticker: {
        "ticker": ticker,
        "free_cash_flow": {"value": 100, "period": "2025-12-31"},
        "shares_outstanding": 10,
        "current_price": 20,
        "total_cash": 0,
        "total_debt": 0,
    })
    monkeypatch.setenv("DCF_DISCOUNT_RATE", "0.02")
    monkeypatch.setenv("DCF_TERMINAL_GROWTH_RATE", "0.03")
    result = dcf_calculation("TEST")
    assert result["status"] == "invalid_assumptions"
    assert result["intrinsic_value_per_share"] is None


def test_dcf_computes_value_with_positive_fcf(monkeypatch):
    import fundamental_analysis_agent.tools.valuation_tools as valuation
    monkeypatch.setattr(valuation, "get_financial_snapshot", lambda ticker: {
        "ticker": ticker,
        "free_cash_flow": {"value": 100, "period": "2025-12-31"},
        "shares_outstanding": 10,
        "current_price": 20,
        "total_cash": 10,
        "total_debt": 5,
    })
    monkeypatch.setenv("DCF_GROWTH_RATE", "0.05")
    monkeypatch.setenv("DCF_DISCOUNT_RATE", "0.10")
    monkeypatch.setenv("DCF_TERMINAL_GROWTH_RATE", "0.02")
    monkeypatch.setenv("DCF_FORECAST_YEARS", "5")
    result = dcf_calculation("TEST")
    assert result["status"] == "illustrative_estimate"
    assert isinstance(result["intrinsic_value_per_share"], float)
    assert result["upside_downside_pct"] is not None
