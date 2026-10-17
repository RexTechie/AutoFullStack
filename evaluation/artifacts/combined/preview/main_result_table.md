| Method | Complexity | E2E | PFS | MFS@4 |
| --- | --- | --- | --- | --- |
| Incremental | Simple | 93.3% ± 5.8% | 3.37 ± 0.32 | 50.0% ± 10.0% |
| Incremental | Medium | 93.3% ± 5.8% | 3.39 ± 0.26 | 51.4% ± 5.7% |
| Incremental | Complex | 90.0% ± 10.0% | 3.24 ± 0.34 | 52.8% ± 5.1% |
| Incremental | Overall | 92.2% ± 6.9% | 3.33 ± 0.28 | 52.1% ± 3.3% |
| Waterfall | Simple | 63.3% ± 15.3% | 2.33 ± 0.50 | 26.7% ± 5.8% |
| Waterfall | Medium | 36.7% ± 11.5% | 1.41 ± 0.59 | 21.0% ± 11.5% |
| Waterfall | Complex | 23.3% ± 5.8% | 0.86 ± 0.11 | 14.4% ± 2.5% |
| Waterfall | Overall | 41.1% ± 6.9% | 1.53 ± 0.24 | 17.8% ± 2.7% |

Notes: Entries are the combined estimate ± sample SD of 3 run-level aggregates (ddof=1), not SE or CI; rate SDs correspond to percentage points.

There are 10 paired tasks per complexity and 30 overall; repeat outcomes are not independent tasks. MFS@4 pools successful modules and module totals.

E2E requires both the front end and back end to pass build/compilation and startup checks; it does not imply complete business functionality.
