import argparse
import asyncio

from .agents.orchestrator import run_analysis


def main():
    parser = argparse.ArgumentParser(description="Run the multi-agent fundamental analysis workflow.")
    parser.add_argument("ticker", help="Public-market ticker symbol, e.g. AAPL or MSFT")
    args = parser.parse_args()
    try:
        report = asyncio.run(run_analysis(args.ticker))
        print(report)
    except KeyboardInterrupt:
        raise SystemExit("Cancelled by user.")
    except Exception as exc:
        raise SystemExit(f"Analysis failed: {exc}") from exc


if __name__ == "__main__":
    main()
