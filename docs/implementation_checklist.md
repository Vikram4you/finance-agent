# Next implementation milestones

- [ ] Configure a Hugging Face Inference Providers token or xAI API key.
- [ ] Confirm the chosen model supports tool/function calling on the configured endpoint.
- [ ] Run the AAPL workflow and inspect missing-data behavior.
- [ ] Verify reported numbers against official company filings.
- [ ] Add year-over-year trends across multiple reporting periods.
- [ ] Add a dedicated news provider with reliable publication timestamps and URLs.
- [ ] Add verified peer-company selection and comparable-company multiples.
- [ ] Add a deterministic rating rubric and data-quality/confidence score.
- [ ] Add bull/base/bear DCF sensitivity analysis.
- [ ] Add Pydantic schemas and JSON report export.
- [ ] Add retries, provider fallback, logging and tracing.
- [ ] Add fixture-based tests that do not call live APIs.
- [ ] Add Streamlit UI after the CLI workflow is stable.
