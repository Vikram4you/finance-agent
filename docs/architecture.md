# Architecture guide

## Tool → Agent → Orchestrator

- **Tools** (`tools/*.py`) are ordinary Python functions. They retrieve financial data, compute ratios/DCF and fetch headlines. The shared ticker snapshot is cached within the process.
- **Agents** (`agents/specialists.py`) combine instructions, a configured LLM and a small tool set.
- **OrchestratorAgent** (`agents/orchestrator.py`) exposes specialists with `.as_tool()` and uses `Runner.run()` to coordinate them.
- **ReportWriterAgent** has no tools and synthesizes only the supplied specialist reports.

## Workflow represented in the reference

1. Financial data, news/sentiment and risk research are independent initial tasks.
2. Valuation reports DCF assumptions and market-multiple context.
3. Report Writer synthesizes the specialist reports.
4. Orchestrator returns the final report.

Parallel specialist calls depend on the selected model's tool-call behavior; the orchestrator instructions request parallel calls where supported but do not guarantee it. If strict concurrency/order is required, replace model-directed tool selection with an explicit Python `asyncio.gather` pipeline.

## Shared data and cache

`get_financial_snapshot()` is cached with `functools.lru_cache`. It avoids repeated retrieval for the same ticker within one process, but has no TTL and is not shared across multiple worker processes. Use timestamp-aware SQLite/Redis caching for a persistent service.

## Financial limitations

The simplified DCF is illustrative and assumes a cash-flow convention that should be reviewed before financial decisions. Peer-company selection and a deterministic rating rubric are not yet implemented. A robust version should calculate ratings from validated valuation, risk and data-quality inputs, not let the report-writing LLM invent them.
