# rules/examples
Real kit passages with a verdict (keep, remove, rewrite), each one a fixture: `remove` and `rewrite` must fire their rule, `keep` must not (`tools/selftest.py`).
Format: front matter `landmine`, `rule`, `verdict`, `source` (`kit.md@<git hash>:<line>`); the passage is the first `>` line under `## Passage`.
