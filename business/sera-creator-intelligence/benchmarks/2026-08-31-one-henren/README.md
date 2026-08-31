# 一个狠人 Acquisition Benchmark — 2026-08-31

This directory contains the sanitized, acquisition-only result set for the fixed 10-video sample defined in `ACQUISITION_BENCHMARK.md`.

Included:

- per-video/provider attempt status and quality metrics;
- provider success rates, latency and failure taxonomy;
- the provider recommendation and promotion-gate result.

Intentionally excluded:

- API keys, cookies, proxy endpoints and signed media URLs;
- raw provider responses;
- temporary audio;
- transcript segments and full transcript bodies;
- Creator Intelligence analysis, scores or summaries.

The reusable local runner is in `business/sera-creator-intelligence/benchmark/run_acquisition_benchmark.py`.
