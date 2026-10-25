from agents import Agent

from ..config import build_model
from ..tools.financial_tools import (
    get_income_statement,
    get_balance_sheet,
    get_cash_flow_statement,
    compute_key_ratios,
)
from ..tools.news_tools import search_recent_news
from ..tools.valuation_tools import run_dcf_model, get_peer_multiples

# All agents use the configured provider. Each tool performs the actual retrieval/calculation.
MODEL = build_model()

financial_data_agent = Agent(
    name="FinancialDataAgent",
    model=MODEL,
    instructions=(
        "You are a careful equity financial-data analyst. Call all relevant financial tools. "
        "Return a concise report with company, sector, reporting periods, available revenue/profit/cash flow, "
        "key ratios, and financial-health verdict STRONG, SOLID, MIXED, or WEAK. "
        "Never invent missing data; distinguish missing data from zero and mention source limitations."
    ),
    tools=[get_income_statement, get_balance_sheet, get_cash_flow_statement, compute_key_ratios],
)

news_sentiment_agent = Agent(
    name="NewsAndSentimentAgent",
    model=MODEL,
    instructions=(
        "You are a news-desk analyst. Call search_recent_news. Classify the available headline mood as "
        "STRONGLY BULLISH, BULLISH, NEUTRAL, BEARISH, STRONGLY BEARISH, or UNKNOWN. "
        "Explain evidence and counter-evidence. Headlines are not proof of future returns. "
        "Include source URLs where supplied. If no articles are available, sentiment is UNKNOWN."
    ),
    tools=[search_recent_news],
)

risk_agent = Agent(
    name="RiskAgent",
    model=MODEL,
    instructions=(
        "You are the skeptical risk manager. Call get_balance_sheet, compute_key_ratios and search_recent_news. "
        "Assess only evidence available: leverage/cash, profitability, cash-flow quality, valuation sensitivity, "
        "and supported company/news risks. Assign LOW, MODERATE, ELEVATED, HIGH, or UNKNOWN. "
        "List data gaps. Do not claim a risk without evidence."
    ),
    tools=[get_balance_sheet, compute_key_ratios, search_recent_news],
)

valuation_agent = Agent(
    name="ValuationAgent",
    model=MODEL,
    instructions=(
        "You are the valuation specialist. Call run_dcf_model and get_peer_multiples. "
        "Report DCF value, current price, upside/downside and assumptions if available. "
        "Choose SIGNIFICANTLY UNDERVALUED, SLIGHTLY UNDERVALUED, FAIRLY VALUED, SLIGHTLY OVERVALUED, "
        "SIGNIFICANTLY OVERVALUED, or INSUFFICIENT DATA. Do not call target-company multiples peer multiples. "
        "If data or DCF assumptions are unsuitable, return INSUFFICIENT DATA."
    ),
    tools=[run_dcf_model, get_peer_multiples],
)

report_writer_agent = Agent(
    name="ReportWriterAgent",
    model=MODEL,
    instructions=(
        "You are the managing director writing the final memo. You have NO tools. Use only specialist reports "
        "provided in your input. Produce a readable FUNDAMENTAL ANALYSIS BRIEF with: company/ticker/sector; "
        "investment verdict; valuation verdict; risk verdict; rating; sentiment; intrinsic value/current price/upside "
        "when available; financial health; valuation analysis; risks; news sentiment with URLs; bull/base/bear view; "
        "assumptions, data quality and source limitations. Preserve disagreements, such as bearish valuation with "
        "bullish headlines. Do not manufacture numbers. End with 'Educational purposes only; not financial advice.'"
    ),
)


def specialist_tools():
    """Expose specialists as tools for the OrchestratorAgent, as in the reference diagram."""
    return [
        financial_data_agent.as_tool(
            tool_name="financial_data_research",
            tool_description="Get statements, key ratios and a financial health assessment.",
        ),
        news_sentiment_agent.as_tool(
            tool_name="news_and_sentiment_research",
            tool_description="Retrieve recent headlines and assess headline sentiment.",
        ),
        risk_agent.as_tool(
            tool_name="risk_research",
            tool_description="Independently assess evidence-based financial and headline risks.",
        ),
        valuation_agent.as_tool(
            tool_name="valuation_research",
            tool_description="Run the DCF tool and provide valuation context and assumptions.",
        ),
        report_writer_agent.as_tool(
            tool_name="write_final_brief",
            tool_description="Synthesize all specialist findings into the final fundamental analysis brief.",
        ),
    ]
