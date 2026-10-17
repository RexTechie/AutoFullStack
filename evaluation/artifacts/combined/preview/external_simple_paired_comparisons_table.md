| Metric | Difference | 95% CI | p | Holm p |
| --- | --- | --- | --- | --- |
| E2E (pp) | +73.3 | [+56.7, +86.7] | 0.002 | 0.006 |
| PFS (points) | +2.83 | [+1.97, +3.67] | 0.002 | 0.006 |
| MFS@4 (pp) | +40.0 | [+13.3, +66.7] | 0.047 | 0.047 |

Notes: All effects are Incremental minus MetaGPT on 10 matched Simple tasks averaged across 3 observed runs per method. Positive quality differences favor Incremental; pp denotes percentage points.

CIs are pointwise 95% percentile intervals from 30,000 paired task-cluster bootstrap samples within the single Simple stratum. All repeats remain inside each sampled task; intervals condition on the observed repeats and are not simultaneous or Holm-adjusted.

Two-sided exact paired tests enumerate all 1,024 whole-task method-label swaps, assuming exchangeability under the null. The p-value is K/1024, where K counts absolute permuted differences at least as large as the observed absolute difference; no Monte Carlo plus-one correction is used.

Holm p adjusts the three external quality comparisons as a separate supplementary family, not jointly with the original eight comparisons. An unadjusted CI excluding zero need not imply Holm-adjusted significance.

Task clusters are treated as independent. Bootstrap RNG seed 12138 is for analysis, not generation. * Zero-width empirical CIs do not imply certainty beyond these tasks/runs.

E2E requires both the front end and back end to pass build/compilation and startup checks; it does not imply complete business functionality.
