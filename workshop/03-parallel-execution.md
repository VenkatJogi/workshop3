# Lab 3 — Parallel Execution

`ParallelExecutor` constructs only selected specialists and runs them with `asyncio.gather(..., return_exceptions=True)`. One failure is recorded without discarding successful evidence.

Exercise: make one mocked agent raise an exception. Confirm the other results reach shared state and the workflow emits `agent_failed`.
