
# Insight AI

Insight AI is a focused implementation of an agent orchestration framework that demonstrates how purpose-built agents can collaborate to solve complex, multi-step tasks. The system showcases modular agents for planning, execution, critique, and synthesis, integrated with a local retrieval memory (Chroma DB) and a lightweight orchestration layer to coordinate work, iterate on outputs, and produce human-friendly reports.

## Key Features

- Agent-first design: clear separation of concerns between planning, execution, critique, and synthesis agents.
- Reproducible runs: `main.py` provides a straightforward entrypoint for end-to-end orchestrations.
- Vector retrieval memory: local Chroma DB stores embeddings and searchable artifacts for context and continuity.
- Extensible LLM interface: `agents/llm_client.py` centralizes model calls and can be swapped for other providers.

## Repository Structure

- `main.py` — orchestration entrypoint to run scenarios and generate reports
- `requirements.txt` — pinned Python dependencies
- `agents/` — agent implementations and helpers
- `chroma_db/` — local Chroma DB storage (embeddings and collections)
- `report.html` — example generated report

## Quickstart

1. Prerequisites

  - Python 3.10 or newer
  - Optional: create and activate a virtual environment

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment

Set any provider keys required by your chosen LLM. Example (PowerShell):

```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
```

4. Run a sample orchestration

```bash
python main.py
```

By default the run will write artifacts and an example `report.html` in the project folder.

## Development Notes

- Core agent files live under `agents/`:
  - `agents/planner_agent.py` — task decomposition and planning logic
  - `agents/delivery_execution_agent.py` — executes tasks and integrates external tools
  - `agents/critic_agent.py` — evaluates outputs and generates revision feedback
  - `agents/synthesis_agent.py` — synthesizes final deliverables and reports
  - `agents/llm_client.py` — wrapper for model interactions and prompt handling

- `chroma_db/` contains local embedding data; do not include in public forks if you wish to avoid sharing extracted vectors.

## Workflow

This project follows an iterative agentic workflow designed for clarity and reproducibility:

1. Ingest & Contextualize
  - Project inputs (specs, documents, files) are parsed and embedded into Chroma DB for retrieval.

2. Plan
  - The `planner_agent` decomposes goals into ordered tasks and assigns objectives to downstream agents.

3. Execute
  - The `delivery_execution_agent` performs actions, runs tools or prompts models to produce artifacts.

4. Critique
  - The `critic_agent` reviews outputs, identifies gaps or quality issues, and generates actionable feedback.

5. Revise & Iterate
  - Based on critique, the planner or executor updates tasks; the cycle repeats until acceptance criteria are met.

6. Synthesize & Report
  - The `synthesis_agent` composes final deliverables (e.g., `report.html`) and bundles outputs for export.

This loop enables stepwise refinement and human-in-the-loop checks while preserving reproducible state via the retrieval store.

## Testing & Iteration

- Develop and validate agents in isolation using small scenario scripts before running full orchestrations.
- Add targeted tests for parsing, embedding, and agent decision logic to catch regressions early.

