# Fundamental Analysis Multi-Agent

A VS Code-ready Python project based on the supplied equity-research architecture. It uses the OpenAI Agents SDK patterns shown in the reference (`Agent`, `@function_tool`, `Agent.as_tool()` and `Runner.run()`), with configurable Hugging Face Inference Providers or xAI/Grok API access.

## Output

For a ticker such as `AAPL`, the system produces a Fundamental Analysis Brief containing:
- Company, sector and financial-data coverage
- Financial health verdict
- DCF estimate, assumptions and upside/downside where data supports it
- Market-multiple context (not falsely labelled as peer multiples)
- Risk verdict and evidence
- Recent headline sentiment with source URLs when available
- Final rating framework, disagreement notes and data limitations

## Architecture

`OrchestratorAgent` is the director of research. It calls these specialist agents as tools:
- `FinancialDataAgent`: statements, key ratios and financial health
- `NewsAndSentimentAgent`: recent headlines and sentiment
- `RiskAgent`: skeptical review of balance sheet, ratios and headlines
- `ValuationAgent`: deterministic DCF calculation and valuation context
- `ReportWriterAgent`: synthesis only, with no tools

Shared Python functions retrieve and cache market data. The agents interpret the returned evidence; Python tools do the numerical calculations.

## Requirements

- Python 3.11 or newer recommended
- VS Code with Python extension
- Internet access for provider calls and Yahoo Finance retrieval
- A Hugging Face Inference Providers token OR an xAI API key

Note: access to Grok on its website/app does not automatically grant xAI API access. Hugging Face free inference has quotas and model/provider availability can change.

## Setup in VS Code (macOS/Linux)

Open this folder in VS Code, then run in the integrated terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and configure ONE provider.

### Hugging Face

```dotenv
LLM_PROVIDER=huggingface
HF_TOKEN=hf_your_token
HF_MODEL=openai/gpt-oss-120b:fastest
```

Select a model currently supported by Hugging Face Inference Providers and capable of tool/function calling. If this model is not available to your account, replace it with a currently supported model ID from the Inference Playground.

### Grok / xAI API

```dotenv
LLM_PROVIDER=grok
XAI_API_KEY=your_xai_api_key
XAI_MODEL=grok-3-mini
```

Confirm the model ID available to your xAI account in the current xAI API documentation.

## Run

```bash
PYTHONPATH=src python -m fundamental_analysis_agent.main AAPL
```

Other tickers:

```bash
PYTHONPATH=src python -m fundamental_analysis_agent.main MSFT
```

Run unit tests:

```bash
PYTHONPATH=src pytest -q
```

## GitHub: first push

Before pushing, verify `.env` is ignored:

```bash
git status --short
git check-ignore .env
```

Then create an empty repository on GitHub and run:

```bash
git init
git add .
git status
git commit -m "Initial multi-agent fundamental analysis project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL. Never commit `.env`, API tokens, downloaded data, or personal credentials.

## Important limitations

- This is a learning/research starter, not an investment recommendation system.
- `yfinance` data may be delayed, incomplete or revised; validate material values against filings.
- DCF assumptions are illustrative defaults. Review them and run sensitivity analysis.
- This starter does not retrieve a verified peer universe. It will explicitly disclose that limitation.
- LLM-generated rating language is not a substitute for a deterministic, validated investment policy.
- The SDK/model endpoint must support tool/function calling. Tool-call support varies by model/provider.
