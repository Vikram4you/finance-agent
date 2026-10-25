import json
import os

from agents import function_tool
from .financial_tools import get_financial_snapshot


def dcf_calculation(ticker: str) -> dict:
    """Simplified, explicit DCF. Returns no number when key inputs are unavailable."""
    d = get_financial_snapshot(ticker)
    fcf_item = d.get("free_cash_flow")
    shares = d.get("shares_outstanding")
    price = d.get("current_price")

    if not fcf_item or fcf_item.get("value") is None or not shares or shares <= 0:
        return {
            "ticker": ticker.upper(),
            "status": "insufficient_data",
            "intrinsic_value_per_share": None,
            "reason": "Missing free cash flow or shares outstanding; no DCF estimate produced.",
        }

    fcf = fcf_item["value"]
    growth = float(os.getenv("DCF_GROWTH_RATE", "0.08"))
    discount = float(os.getenv("DCF_DISCOUNT_RATE", "0.10"))
    terminal_growth = float(os.getenv("DCF_TERMINAL_GROWTH_RATE", "0.025"))
    years = int(os.getenv("DCF_FORECAST_YEARS", "5"))

    if years < 1:
        return {"ticker": ticker.upper(), "status": "invalid_assumptions",
                "intrinsic_value_per_share": None, "reason": "Forecast years must be at least one."}
    if discount <= terminal_growth:
        return {"ticker": ticker.upper(), "status": "invalid_assumptions",
                "intrinsic_value_per_share": None, "reason": "Discount rate must exceed terminal growth rate."}
    if fcf <= 0:
        return {"ticker": ticker.upper(), "status": "insufficient_data",
                "intrinsic_value_per_share": None,
                "reason": "Latest free cash flow is non-positive; this simple DCF is unsuitable."}

    projected = [fcf * (1 + growth) ** year for year in range(1, years + 1)]
    pv_cash_flows = sum(cf / (1 + discount) ** year for year, cf in enumerate(projected, 1))
    terminal_value = projected[-1] * (1 + terminal_growth) / (discount - terminal_growth)
    pv_terminal = terminal_value / (1 + discount) ** years

    # This simplified method treats the cash-flow input as FCFF-like. Confirm this
    # convention and enterprise/equity adjustments before using it for decisions.
    cash = d.get("total_cash") or 0
    debt = d.get("total_debt") or 0
    equity_value = pv_cash_flows + pv_terminal + cash - debt
    intrinsic_value = equity_value / shares
    upside = ((intrinsic_value / price) - 1) * 100 if price and price > 0 else None

    return {
        "ticker": ticker.upper(),
        "status": "illustrative_estimate",
        "intrinsic_value_per_share": round(intrinsic_value, 2),
        "current_price": price,
        "upside_downside_pct": round(upside, 2) if upside is not None else None,
        "assumptions": {
            "starting_fcf": fcf,
            "fcf_period": fcf_item.get("period"),
            "growth_rate": growth,
            "discount_rate": discount,
            "terminal_growth_rate": terminal_growth,
            "forecast_years": years,
            "cash_added": cash,
            "debt_subtracted": debt,
        },
        "warning": "Simplified illustrative DCF; verify cash-flow convention, inputs, share count and sensitivity.",
    }


@function_tool
def run_dcf_model(ticker: str) -> str:
    """Run a simplified DCF model and return valuation, assumptions and limitations."""
    return json.dumps(dcf_calculation(ticker))


@function_tool
def get_peer_multiples(ticker: str) -> str:
    """Return target-company valuation multiples; disclose that verified peers are not implemented."""
    d = get_financial_snapshot(ticker)
    return json.dumps({
        "ticker": ticker.upper(),
        "sector": d.get("sector"),
        "industry": d.get("industry"),
        "trailing_pe": d.get("trailing_pe"),
        "forward_pe": d.get("forward_pe"),
        "price_to_book": d.get("price_to_book"),
        "peer_comparison_status": "not_implemented",
        "limitation": "These are target-company multiples, not peer multiples. A verified peer universe is required.",
    })
