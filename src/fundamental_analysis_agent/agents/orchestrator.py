from agents import Agent, Runner

from ..config import build_model
from .specialists import specialist_tools

orchestrator_agent = Agent(
    name="OrchestratorAgent",
    model=build_model(),
    instructions=(
        "You are the director of research. For the supplied ticker, call financial_data_research, "
        "news_and_sentiment_research, and risk_research as independent research tasks. They may be called "
        "in parallel if the model/runtime supports parallel tool calls. Then call valuation_research, using "
        "the financial report as context. Finally call write_final_brief and provide all four specialist outputs. "
        "Return the ReportWriterAgent's final brief without a preamble or changing its figures. "
        "If a specialist fails or returns missing data, disclose that; never invent findings. "
        "Do not treat sentiment as a substitute for valuation or risk."
    ),
    tools=specialist_tools(),
)


async def run_analysis(ticker: str) -> str:
    ticker = ticker.strip().upper()
    if not ticker or not ticker.replace(".", "").replace("-", "").isalnum():
        raise ValueError("Enter a valid ticker symbol, for example AAPL.")
    result = await Runner.run(
        orchestrator_agent,
        f"Prepare a fundamental analysis brief for public-market ticker {ticker}.",
        max_turns=25,
    )
    return str(result.final_output)
