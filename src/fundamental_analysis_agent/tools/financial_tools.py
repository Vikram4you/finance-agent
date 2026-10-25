import json
from functools import lru_cache

import numpy as np
import yfinance as yf
from agents import function_tool


def clean(value):
    """Convert numpy scalar values to JSON-safe Python values."""
    if value is None:
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


@lru_cache(maxsize=128)
def ticker_obj(ticker: str):
    return yf.Ticker(ticker.upper())


@lru_cache(maxsize=128)
def company_info(ticker: str) -> dict:
    try:
        return ticker_obj(ticker).info or {}
    except Exception:
        return {}


def latest_row(frame, key):
    try:
        if frame is None or frame.empty or key not in frame.index:
            return None
        row = frame.loc[key].dropna()
        if row.empty:
            return None
        return {"period": str(row.index[0].date()), "value": clean(row.iloc[0])}
    except Exception:
        return None


@lru_cache(maxsize=128)
def get_financial_snapshot(ticker: str) -> dict:
    """Retrieve common market and statement data once per ticker per process."""
    ticker = ticker.upper().strip()
    info = company_info(ticker)
    company = ticker_obj(ticker)

    try:
        income = company.income_stmt
    except Exception:
        income = None
    try:
        cashflow = company.cashflow
    except Exception:
        cashflow = None

    cfo = latest_row(cashflow, "Operating Cash Flow")
    capex = latest_row(cashflow, "Capital Expenditure")
    free_cash_flow = None
    if cfo and capex and cfo.get("value") is not None and capex.get("value") is not None:
        # Yahoo Finance typically records capex as a negative cash-flow value.
        free_cash_flow = {
            "period": cfo["period"],
            "value": cfo["value"] + capex["value"],
        }

    return {
        "ticker": ticker,
        "company_name": info.get("longName") or info.get("shortName") or ticker,
        "sector": info.get("sector") or "Unknown",
        "industry": info.get("industry") or "Unknown",
        "currency": info.get("currency") or "Unknown",
        "current_price": clean(info.get("currentPrice") or info.get("regularMarketPrice")),
        "market_cap": clean(info.get("marketCap")),
        "shares_outstanding": clean(info.get("sharesOutstanding")),
        "trailing_pe": clean(info.get("trailingPE")),
        "forward_pe": clean(info.get("forwardPE")),
        "price_to_book": clean(info.get("priceToBook")),
        "beta": clean(info.get("beta")),
        "revenue": latest_row(income, "Total Revenue"),
        "gross_profit": latest_row(income, "Gross Profit"),
        "net_income": latest_row(income, "Net Income"),
        "operating_cash_flow": cfo,
        "capital_expenditure": capex,
        "free_cash_flow": free_cash_flow,
        "total_cash": clean(info.get("totalCash")),
        "total_debt": clean(info.get("totalDebt")),
        "return_on_equity": clean(info.get("returnOnEquity")),
        "gross_margin": clean(info.get("grossMargins")),
        "profit_margin": clean(info.get("profitMargins")),
        "data_source": "Yahoo Finance via yfinance",
        "data_limitations": [
            "Data can be delayed, incomplete or revised.",
            "Check reporting periods, units and currency.",
            "Verify material figures against official company filings.",
        ],
    }


@function_tool
def get_income_statement(ticker: str) -> str:
    """Fetch latest available revenue, gross profit and net income with reporting period."""
    d = get_financial_snapshot(ticker)
    keys = ("ticker", "company_name", "revenue", "gross_profit", "net_income", "currency", "data_source")
    return json.dumps({key: d[key] for key in keys})


@function_tool
def get_balance_sheet(ticker: str) -> str:
    """Fetch available cash, debt, market capitalization, shares and valuation context."""
    d = get_financial_snapshot(ticker)
    keys = ("ticker", "total_cash", "total_debt", "market_cap", "shares_outstanding",
            "price_to_book", "currency", "data_source")
    return json.dumps({key: d[key] for key in keys})


@function_tool
def get_cash_flow_statement(ticker: str) -> str:
    """Fetch operating cash flow, capital expenditure and estimated free cash flow."""
    d = get_financial_snapshot(ticker)
    keys = ("ticker", "operating_cash_flow", "capital_expenditure", "free_cash_flow", "currency")
    return json.dumps({key: d[key] for key in keys})


@function_tool
def compute_key_ratios(ticker: str) -> str:
    """Return available margins, ROE, valuation multiples, beta and debt-to-cash ratio."""
    d = get_financial_snapshot(ticker)
    ratios = {
        "gross_margin_pct": round(d["gross_margin"] * 100, 2) if d["gross_margin"] is not None else None,
        "net_margin_pct": round(d["profit_margin"] * 100, 2) if d["profit_margin"] is not None else None,
        "return_on_equity_pct": round(d["return_on_equity"] * 100, 2) if d["return_on_equity"] is not None else None,
        "trailing_pe": d["trailing_pe"],
        "forward_pe": d["forward_pe"],
        "price_to_book": d["price_to_book"],
        "beta": d["beta"],
        "total_debt": d["total_debt"],
        "total_cash": d["total_cash"],
    }
    if d["total_debt"] is not None and d["total_cash"] not in (None, 0):
        ratios["debt_to_cash"] = round(d["total_debt"] / d["total_cash"], 3)
    else:
        ratios["debt_to_cash"] = None
    return json.dumps({"ticker": d["ticker"], "ratios": ratios})
