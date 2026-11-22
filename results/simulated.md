| Detector | Threshold (train quantile) | Faults caught | Day | Night | Precision | Recall | F1 | False alarms / cell / day | Median delay (min) |
|---|---|---|---|---|---|---|---|---|---|
| rolling_zscore | 0.9999 | 12/13 | 9/9 | 3/4 | 0.33 | 0.92 | 0.48 | 0.32 | 0 |
| isolation_forest | 0.99 | 7/13 | 5/9 | 2/4 | 0.07 | 0.54 | 0.12 | 4.67 | 29 |
| isolation_forest_time | 0.995 | 11/13 | 7/9 | 4/4 | 0.32 | 0.85 | 0.46 | 3.05 | 17 |
